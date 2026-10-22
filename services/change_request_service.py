from datetime import datetime
from models import db
from models.database_models import (
    ChangeRequest, ChangeRequestHistory, ReviewDecision, 
    TestResult, ConfigurationItem, ActivityLog
)
from services.trust_engine import evaluate_change_trust
from services.version_service import create_new_version
from services.organizational_memory_service import add_memory_record

CR_STATUSES = [
    "Draft",
    "Submitted",
    "Under Evaluation",
    "Pending Review",
    "Approved",
    "Rejected",
    "Implemented",
    "Tested",
    "Closed"
]

def get_all_change_requests(status=None, risk=None, search=None):
    query = ChangeRequest.query
    if status and status != 'All':
        query = query.filter(ChangeRequest.current_status == status)
    if risk and risk != 'All':
        query = query.filter(ChangeRequest.risk_level == risk)
    if search:
        term = f"%{search}%"
        query = query.filter(
            (ChangeRequest.cr_id.ilike(term)) |
            (ChangeRequest.title.ilike(term)) |
            (ChangeRequest.requester.ilike(term)) |
            (ChangeRequest.affected_ci_id.ilike(term))
        )
    return query.order_by(ChangeRequest.creation_date.desc()).all()

def get_change_request_by_id(cr_id):
    return ChangeRequest.query.filter_by(cr_id=cr_id).first()

def get_next_cr_id():
    count = ChangeRequest.query.count()
    return f"CR-{count + 1:03d}"

def create_change_request(
    title,
    description,
    requester,
    affected_ci_id,
    proposed_value,
    reason_for_change,
    risk_level='Medium',
    business_impact='Medium',
    assigned_developer=None,
    cr_id=None,
    user='System'
):
    if not cr_id:
        cr_id = get_next_cr_id()

    ci = ConfigurationItem.query.filter_by(ci_id=affected_ci_id).first()
    if not ci:
        raise ValueError(f"Affected Configuration Item {affected_ci_id} not found.")

    current_val = f"# Current Version {ci.current_version}\nstatus: {ci.status}\nowner: {ci.owner}"

    cr = ChangeRequest(
        cr_id=cr_id,
        title=title,
        description=description,
        requester=requester,
        assigned_developer=assigned_developer or requester,
        affected_ci_id=affected_ci_id,
        current_value=current_val,
        proposed_value=proposed_value,
        reason_for_change=reason_for_change,
        risk_level=risk_level,
        business_impact=business_impact,
        current_status='Submitted',
        creation_date=datetime.utcnow()
    )
    db.session.add(cr)

    # Initial history log
    hist = ChangeRequestHistory(
        cr_id=cr_id,
        changed_by=user,
        old_status=None,
        new_status='Submitted',
        action_taken='Change Request Created',
        comments=f"CR created by {requester} targeting {affected_ci_id}"
    )
    db.session.add(hist)

    log = ActivityLog(
        user=user,
        action="Created Change Request",
        module="Change Request Management",
        details=f"Created {cr_id}: {title} targeting {affected_ci_id}"
    )
    db.session.add(log)
    db.session.commit()

    # Automatically run trust evaluation
    try:
        evaluate_change_trust(cr_id, user=user)
    except Exception as e:
        print(f"Initial trust evaluation warning: {e}")

    return cr

def record_ccb_review(cr_id, reviewer, reviewer_role, decision, comments, user='System'):
    """
    CCB Review workflow:
    Decision: 'Approved', 'Rejected', or 'Modification Requested'
    """
    cr = get_change_request_by_id(cr_id)
    if not cr:
        raise ValueError(f"Change Request {cr_id} not found.")

    old_status = cr.current_status
    if decision == 'Approved':
        new_status = 'Approved'
    elif decision == 'Rejected':
        new_status = 'Rejected'
    else:
        new_status = 'Draft' # Send back for modification

    cr.current_status = new_status
    cr.final_decision = decision
    cr.reviewer_comments = comments

    # Save ReviewDecision
    review = ReviewDecision(
        cr_id=cr_id,
        reviewer=reviewer,
        reviewer_role=reviewer_role,
        decision=decision,
        comments=comments,
        decided_at=datetime.utcnow()
    )
    db.session.add(review)

    # Add to History audit trail
    hist = ChangeRequestHistory(
        cr_id=cr_id,
        changed_by=reviewer,
        old_status=old_status,
        new_status=new_status,
        action_taken=f"CCB Decision: {decision}",
        comments=comments
    )
    db.session.add(hist)

    log = ActivityLog(
        user=reviewer,
        action="CCB Review Recorded",
        module="CCB Review",
        details=f"{cr_id} reviewed by {reviewer} ({reviewer_role}): {decision}"
    )
    db.session.add(log)
    db.session.commit()
    return review

def implement_change_request(cr_id, new_version_number, commit_message, author, user='System'):
    """
    Implement an approved change request:
    Generates a new ConfigurationVersion and sets status to 'Implemented'.
    """
    cr = get_change_request_by_id(cr_id)
    if not cr:
        raise ValueError(f"Change Request {cr_id} not found.")

    if cr.current_status not in ['Approved']:
        raise ValueError(f"Cannot implement CR {cr_id}: status is {cr.current_status}. Must be 'Approved' by CCB first.")

    old_status = cr.current_status
    cr.current_status = 'Implemented'
    cr.implementation_outcome = 'Success'

    # Create new version record for CI
    ver = create_new_version(
        ci_id=cr.affected_ci_id,
        new_version_number=new_version_number,
        change_description=f"[{cr.cr_id}] {commit_message or cr.title}",
        author=author,
        configuration_content=cr.proposed_value,
        approval_status='Approved',
        user=user
    )

    hist = ChangeRequestHistory(
        cr_id=cr_id,
        changed_by=user,
        old_status=old_status,
        new_status='Implemented',
        action_taken='Implemented into Codebase / CI',
        comments=f"Incremented {cr.affected_ci_id} to version {new_version_number}"
    )
    db.session.add(hist)

    log = ActivityLog(
        user=user,
        action="Implemented Change Request",
        module="Change Request Management",
        details=f"Implemented {cr_id} on {cr.affected_ci_id} (New v{new_version_number})"
    )
    db.session.add(log)
    db.session.commit()
    return ver

def record_test_result(cr_id, test_suite_name, passed_tests, failed_tests, test_status, test_evidence, executed_by, user='System'):
    """
    Record test execution results for an implemented change request.
    """
    cr = get_change_request_by_id(cr_id)
    if not cr:
        raise ValueError(f"Change Request {cr_id} not found.")

    if cr.current_status not in ['Implemented', 'Tested']:
        raise ValueError(f"Cannot test CR {cr_id}: current status is {cr.current_status}. Must be 'Implemented' first.")

    old_status = cr.current_status
    cr.current_status = 'Tested'

    test_res = TestResult(
        cr_id=cr_id,
        test_suite_name=test_suite_name,
        passed_tests=int(passed_tests),
        failed_tests=int(failed_tests),
        test_status=test_status,
        test_evidence=test_evidence,
        executed_by=executed_by,
        executed_at=datetime.utcnow()
    )
    db.session.add(test_res)

    hist = ChangeRequestHistory(
        cr_id=cr_id,
        changed_by=executed_by,
        old_status=old_status,
        new_status='Tested',
        action_taken=f"Tests Completed: {test_status}",
        comments=f"Passed: {passed_tests}, Failed: {failed_tests}. Suite: {test_suite_name}"
    )
    db.session.add(hist)

    log = ActivityLog(
        user=executed_by,
        action="Recorded Test Result",
        module="Change Verification",
        details=f"{cr_id} test {test_status} ({passed_tests} pass, {failed_tests} fail)"
    )
    db.session.add(log)
    db.session.commit()
    return test_res

def close_and_archive_to_memory(cr_id, implementation_outcome, lessons_learned, user='System'):
    """
    Closes the change request and stores its historical record into Organizational Memory
    so future adaptive trust evaluations benefit from the outcome!
    """
    cr = get_change_request_by_id(cr_id)
    if not cr:
        raise ValueError(f"Change Request {cr_id} not found.")

    old_status = cr.current_status
    cr.current_status = 'Closed'
    cr.implementation_outcome = implementation_outcome

    ci = ConfigurationItem.query.filter_by(ci_id=cr.affected_ci_id).first()
    category = ci.category if ci else "Configuration Files"

    # Get latest test status
    latest_test = TestResult.query.filter_by(cr_id=cr_id).order_by(TestResult.executed_at.desc()).first()
    test_result_str = latest_test.test_status if latest_test else 'Passed'

    # Save into Organizational Memory
    mem = add_memory_record(
        category=category,
        change_type=cr.title,
        description=f"[{cr.cr_id}] {cr.description}",
        relevant_characteristics=f"Risk: {cr.risk_level}, CI: {cr.affected_ci_id}",
        previous_value=cr.current_value,
        new_value=cr.proposed_value,
        historical_trust_score=cr.trust_score,
        test_result=test_result_str,
        approval_outcome=cr.final_decision or 'Approved',
        implementation_outcome=implementation_outcome,
        failure_success_details=f"Outcome: {implementation_outcome}. Reviewer: {cr.reviewer_comments or 'N/A'}",
        lessons_learned=lessons_learned or f"Change successfully verified and closed.",
        source_cr_id=cr.cr_id,
        user=user
    )

    hist = ChangeRequestHistory(
        cr_id=cr_id,
        changed_by=user,
        old_status=old_status,
        new_status='Closed',
        action_taken=f"Closed & Archived to Organizational Memory ({mem.memory_id})",
        comments=lessons_learned
    )
    db.session.add(hist)

    log = ActivityLog(
        user=user,
        action="Archived Change to Memory",
        module="Organizational Memory",
        details=f"Archived {cr_id} into memory {mem.memory_id} ({implementation_outcome})"
    )
    db.session.add(log)
    db.session.commit()
    return mem
