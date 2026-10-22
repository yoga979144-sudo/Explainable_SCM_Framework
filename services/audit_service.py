from datetime import datetime
from models import db
from models.database_models import AuditSession, AuditChecklistResponse, ActivityLog

FCA_CHECKLIST_TEMPLATE = [
    {"item": 1, "question": "Are all approved change requests correctly implemented in this configuration?", "critical": True},
    {"item": 2, "question": "Are all system requirements mapped to corresponding test cases with traceability?", "critical": True},
    {"item": 3, "question": "Has comprehensive functional and regression testing been executed with passing results?", "critical": True},
    {"item": 4, "question": "Are all critical and high-severity software defects resolved?", "critical": True},
    {"item": 5, "question": "Does the deployed implementation meet all stakeholder acceptance criteria?", "critical": False},
    {"item": 6, "question": "Has the formal Change Control Board (CCB) review and approval been completed?", "critical": True}
]

PCA_CHECKLIST_TEMPLATE = [
    {"item": 1, "question": "Does the source code version and tag exactly match the approved configuration baseline?", "critical": True},
    {"item": 2, "question": "Is the software build identifier and compiled artifact version verified?", "critical": True},
    {"item": 3, "question": "Are all required configuration files and environment parameter files present?", "critical": True},
    {"item": 4, "question": "Are database schema migration scripts and data definitions verified?", "critical": False},
    {"item": 5, "question": "Is the complete user, technical, and SCM documentation included in the release bundle?", "critical": False},
    {"item": 6, "question": "Is the active trust-model version tag and parameter configuration formally recorded?", "critical": False},
    {"item": 7, "question": "Has the organizational knowledge repository been maintained and updated with lessons learned?", "critical": False}
]

def get_all_audits(audit_type=None):
    query = AuditSession.query
    if audit_type and audit_type != 'All':
        query = query.filter(AuditSession.audit_type == audit_type)
    return query.order_by(AuditSession.audit_date.desc()).all()

def get_audit_by_id(audit_id):
    return AuditSession.query.filter_by(audit_id=audit_id).first()

def get_next_audit_id(audit_type):
    prefix = audit_type.upper()
    count = AuditSession.query.filter_by(audit_type=prefix).count()
    return f"{prefix}-{count + 1:03d}"

def calculate_audit_status(audit_type, responses_data):
    """
    Calculates audit outcome based on recorded responses and critical flags:
    - If any critical item is 'No': 'Failed'
    - Else if any non-critical item is 'No': 'Conditional'
    - Else: 'Passed'
    """
    template = FCA_CHECKLIST_TEMPLATE if audit_type.upper() == 'FCA' else PCA_CHECKLIST_TEMPLATE
    critical_items = {item['item'] for item in template if item['critical']}
    
    has_critical_failure = False
    has_non_critical_failure = False
    
    for resp in responses_data:
        item_num = int(resp.get('item_number', 0))
        answer = resp.get('response', 'Yes')
        
        if answer == 'No':
            if item_num in critical_items:
                has_critical_failure = True
            else:
                has_non_critical_failure = True

    if has_critical_failure:
        return 'Failed'
    elif has_non_critical_failure:
        return 'Conditional'
    return 'Passed'

def create_audit_session(audit_type, title, target_baseline_or_ci, auditor, responses_list, summary_notes="", user='System'):
    """
    responses_list: list of dicts:
      [{'item_number': 1, 'question': '...', 'response': 'Yes'/'No'/'N/A', 'remarks': '...', 'evidence': '...'}]
    """
    audit_type = audit_type.upper()
    audit_id = get_next_audit_id(audit_type)
    
    overall_status = calculate_audit_status(audit_type, responses_list)
    
    session = AuditSession(
        audit_id=audit_id,
        audit_type=audit_type,
        title=title,
        target_baseline_or_ci=target_baseline_or_ci,
        auditor=auditor,
        audit_date=datetime.utcnow(),
        overall_status=overall_status,
        summary_notes=summary_notes
    )
    db.session.add(session)

    for item in responses_list:
        resp = AuditChecklistResponse(
            audit_session_id=audit_id,
            item_number=item['item_number'],
            question=item['question'],
            response=item.get('response', 'Yes'),
            remarks=item.get('remarks', ''),
            evidence=item.get('evidence', '')
        )
        db.session.add(resp)

    log = ActivityLog(
        user=user,
        action=f"Conducted {audit_type} Audit",
        module="Configuration Verification & Audit",
        details=f"Conducted {audit_id}: {title} (Result: {overall_status})"
    )
    db.session.add(log)
    db.session.commit()
    return session
