from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required, permission_required
from services.change_request_service import (
    get_all_change_requests, get_change_request_by_id, create_change_request,
    record_ccb_review, implement_change_request, record_test_result, close_and_archive_to_memory,
    CR_STATUSES
)
from services.configuration_service import get_all_cis
from services.trust_engine import evaluate_change_trust
from services.explainability_service import get_explanation_for_cr

change_bp = Blueprint('change', __name__)

@change_bp.route('/change-requests')
@login_required
def index():
    status = request.args.get('status', 'All')
    risk = request.args.get('risk', 'All')
    search = request.args.get('search', '').strip()

    crs = get_all_change_requests(status=status, risk=risk, search=search)
    return render_template(
        'change_requests.html',
        crs=crs,
        statuses=CR_STATUSES,
        selected_status=status,
        selected_risk=risk,
        search_query=search
    )

@change_bp.route('/change-requests/new', methods=['GET', 'POST'])
@login_required
@permission_required('create_cr')
def new_cr():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        affected_ci_id = request.form.get('affected_ci_id', '').strip()
        proposed_value = request.form.get('proposed_value', '').strip()
        reason_for_change = request.form.get('reason_for_change', '').strip()
        risk_level = request.form.get('risk_level', 'Medium').strip()
        business_impact = request.form.get('business_impact', 'Medium').strip()
        assigned_developer = request.form.get('assigned_developer', session.get('username', 'Developer')).strip()

        try:
            cr = create_change_request(
                title=title,
                description=description,
                requester=session.get('username', 'Developer'),
                affected_ci_id=affected_ci_id,
                proposed_value=proposed_value,
                reason_for_change=reason_for_change,
                risk_level=risk_level,
                business_impact=business_impact,
                assigned_developer=assigned_developer,
                user=session.get('username', 'System')
            )
            flash(f"Change Request {cr.cr_id} submitted and evaluated successfully.", "success")
            return redirect(url_for('change.cr_detail', cr_id=cr.cr_id))
        except ValueError as e:
            flash(str(e), "danger")

    cis = get_all_cis()
    return render_template('change_form.html', cis=cis)

@change_bp.route('/change-requests/<cr_id>')
@login_required
def cr_detail(cr_id):
    cr = get_change_request_by_id(cr_id)
    if not cr:
        flash(f"Change Request {cr_id} not found.", "danger")
        return redirect(url_for('change.index'))

    explanation_data = get_explanation_for_cr(cr_id)
    return render_template(
        'change_detail.html',
        cr=cr,
        explanation=explanation_data
    )

@change_bp.route('/change-requests/<cr_id>/evaluate', methods=['POST'])
@login_required
def run_evaluation(cr_id):
    try:
        evaluate_change_trust(cr_id, user=session.get('username', 'System'))
        flash(f"Adaptive trust re-evaluation completed for {cr_id}.", "success")
    except Exception as e:
        flash(f"Trust evaluation error: {str(e)}", "danger")
    return redirect(url_for('change.cr_detail', cr_id=cr_id))

@change_bp.route('/ccb-review')
@login_required
def ccb_review_queue():
    # Fetch pending review requests
    pending_crs = ChangeRequest.query.filter(
        ChangeRequest.current_status.in_(['Pending Review', 'Under Evaluation', 'Submitted'])
    ).order_by(ChangeRequest.creation_date.desc()).all()

    # Also fetch recently reviewed requests
    recent_reviewed = ChangeRequest.query.filter(
        ChangeRequest.current_status.in_(['Approved', 'Rejected'])
    ).order_by(ChangeRequest.updated_at.desc()).limit(10).all()

    return render_template('ccb_review.html', pending_crs=pending_crs, recent_reviewed=recent_reviewed)

@change_bp.route('/change-requests/<cr_id>/review', methods=['POST'])
@login_required
@permission_required('ccb_review')
def submit_ccb_review(cr_id):
    decision = request.form.get('decision', '').strip()
    comments = request.form.get('comments', '').strip()

    if decision not in ['Approved', 'Rejected', 'Modification Requested']:
        flash("Invalid CCB decision selected.", "danger")
        return redirect(url_for('change.cr_detail', cr_id=cr_id))

    try:
        record_ccb_review(
            cr_id=cr_id,
            reviewer=session.get('full_name', session.get('username', 'Reviewer')),
            reviewer_role=session.get('role', 'Project Manager'),
            decision=decision,
            comments=comments,
            user=session.get('username', 'System')
        )
        flash(f"CCB Decision recorded: Change Request {cr_id} marked as '{decision}'.", "success")
    except Exception as e:
        flash(f"Error submitting review: {str(e)}", "danger")

    return redirect(url_for('change.cr_detail', cr_id=cr_id))

@change_bp.route('/change-requests/<cr_id>/implement', methods=['POST'])
@login_required
@permission_required('implement_cr')
def implement_cr(cr_id):
    new_version_number = request.form.get('new_version_number', '').strip()
    commit_message = request.form.get('commit_message', '').strip()

    if not new_version_number:
        flash("Please specify the new target version number.", "warning")
        return redirect(url_for('change.cr_detail', cr_id=cr_id))

    try:
        ver = implement_change_request(
            cr_id=cr_id,
            new_version_number=new_version_number,
            commit_message=commit_message,
            author=session.get('username', 'Developer'),
            user=session.get('username', 'System')
        )
        flash(f"Change Request {cr_id} implemented! Created version {ver.version_id}.", "success")
    except Exception as e:
        flash(f"Implementation error: {str(e)}", "danger")

    return redirect(url_for('change.cr_detail', cr_id=cr_id))

@change_bp.route('/change-requests/<cr_id>/test', methods=['POST'])
@login_required
@permission_required('record_tests')
def submit_test_result(cr_id):
    test_suite_name = request.form.get('test_suite_name', '').strip()
    passed_tests = request.form.get('passed_tests', 0)
    failed_tests = request.form.get('failed_tests', 0)
    test_status = request.form.get('test_status', 'Passed').strip()
    test_evidence = request.form.get('test_evidence', '').strip()

    try:
        record_test_result(
            cr_id=cr_id,
            test_suite_name=test_suite_name,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            test_status=test_status,
            test_evidence=test_evidence,
            executed_by=session.get('username', 'QA Engineer'),
            user=session.get('username', 'System')
        )
        flash(f"Test result ({test_status}) recorded for Change Request {cr_id}.", "success")
    except Exception as e:
        flash(f"Error recording test: {str(e)}", "danger")

    return redirect(url_for('change.cr_detail', cr_id=cr_id))

@change_bp.route('/change-requests/<cr_id>/close', methods=['POST'])
@login_required
@permission_required('ccb_review')
def close_cr(cr_id):
    implementation_outcome = request.form.get('implementation_outcome', 'Success').strip()
    lessons_learned = request.form.get('lessons_learned', '').strip()

    try:
        mem = close_and_archive_to_memory(
            cr_id=cr_id,
            implementation_outcome=implementation_outcome,
            lessons_learned=lessons_learned,
            user=session.get('username', 'System')
        )
        flash(f"CR {cr_id} successfully closed and archived to Organizational Memory as {mem.memory_id}.", "success")
    except Exception as e:
        flash(f"Error closing CR: {str(e)}", "danger")

    return redirect(url_for('change.cr_detail', cr_id=cr_id))
