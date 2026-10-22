import io
import csv
from models.database_models import (
    ConfigurationItem, ConfigurationVersion, ChangeRequest, 
    TrustEvaluation, OrganizationalMemory, Baseline, Release, 
    AuditSession, AuditChecklistResponse
)

def generate_csv_string(headers, rows):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return output.getvalue()

def get_ci_report():
    cis = ConfigurationItem.query.order_by(ConfigurationItem.ci_id.asc()).all()
    headers = ['CI ID', 'Name', 'Category', 'Version', 'Owner', 'Status', 'Approval Status', 'Baseline Status', 'Release Status', 'Last Modified']
    rows = [
        [c.ci_id, c.name, c.category, c.current_version, c.owner, c.status, c.approval_status, c.baseline_status, c.release_status, c.last_modified_date.strftime('%Y-%m-%d %H:%M:%S') if c.last_modified_date else '']
        for c in cis
    ]
    return {'headers': headers, 'rows': rows, 'data': cis}

def get_version_history_report():
    versions = ConfigurationVersion.query.order_by(ConfigurationVersion.timestamp.desc()).all()
    headers = ['Version ID', 'CI ID', 'Version Number', 'Author', 'Approval Status', 'Timestamp', 'Change Description']
    rows = [
        [v.version_id, v.ci_id, v.version_number, v.author, v.approval_status, v.timestamp.strftime('%Y-%m-%d %H:%M:%S'), v.change_description]
        for v in versions
    ]
    return {'headers': headers, 'rows': rows, 'data': versions}

def get_change_request_report():
    crs = ChangeRequest.query.order_by(ChangeRequest.creation_date.desc()).all()
    headers = ['CR ID', 'Title', 'Requester', 'CI ID', 'Risk', 'Impact', 'Trust Score', 'Status', 'Final Decision', 'Created Date']
    rows = [
        [cr.cr_id, cr.title, cr.requester, cr.affected_ci_id, cr.risk_level, cr.business_impact, cr.trust_score or 'N/A', cr.current_status, cr.final_decision or 'Pending', cr.creation_date.strftime('%Y-%m-%d')]
        for cr in crs
    ]
    return {'headers': headers, 'rows': rows, 'data': crs}

def get_trust_evaluation_report():
    evals = TrustEvaluation.query.order_by(TrustEvaluation.evaluation_date.desc()).all()
    headers = ['CR ID', 'Trust Score', 'Confidence', 'Recommendation', 'Model Version', 'Evaluation Date']
    rows = [
        [e.cr_id, e.calculated_score, e.evidence_confidence, e.recommendation, e.model_version_tag, e.evaluation_date.strftime('%Y-%m-%d %H:%M:%S')]
        for e in evals
    ]
    return {'headers': headers, 'rows': rows, 'data': evals}

def get_organizational_memory_report():
    memories = OrganizationalMemory.query.order_by(OrganizationalMemory.recorded_date.desc()).all()
    headers = ['Memory ID', 'Category', 'Change Type', 'Implementation Outcome', 'Test Result', 'Approval', 'Trust Score', 'Recorded Date', 'Lessons Learned']
    rows = [
        [m.memory_id, m.category, m.change_type, m.implementation_outcome, m.test_result, m.approval_outcome, m.historical_trust_score or 'N/A', m.recorded_date.strftime('%Y-%m-%d'), m.lessons_learned or '']
        for m in memories
    ]
    return {'headers': headers, 'rows': rows, 'data': memories}

def get_status_accounting_report():
    cis = ConfigurationItem.query.all()
    
    # Summary metrics
    total = len(cis)
    approved = sum(1 for c in cis if c.approval_status == 'Approved')
    in_progress = sum(1 for c in cis if c.status in ['Draft', 'In-Review'])
    baselined = sum(1 for c in cis if c.baseline_status == 'Baselined')
    released = sum(1 for c in cis if c.release_status == 'Released')
    rejected = sum(1 for c in cis if c.approval_status == 'Rejected')

    headers = ['CI ID', 'Name', 'Category', 'Current Version', 'Owner', 'Lifecycle Status', 'Approval Status', 'Baseline Status', 'Release Status', 'Last Modified']
    rows = [
        [c.ci_id, c.name, c.category, c.current_version, c.owner, c.status, c.approval_status, c.baseline_status, c.release_status, c.last_modified_date.strftime('%Y-%m-%d %H:%M:%S') if c.last_modified_date else '']
        for c in cis
    ]

    summary = {
        'total': total,
        'approved': approved,
        'in_progress': in_progress,
        'baselined': baselined,
        'released': released,
        'rejected': rejected
    }

    return {'headers': headers, 'rows': rows, 'data': cis, 'summary': summary}

def get_audit_report(audit_type='FCA'):
    sessions = AuditSession.query.filter_by(audit_type=audit_type.upper()).order_by(AuditSession.audit_date.desc()).all()
    headers = ['Audit ID', 'Type', 'Title', 'Target CI / Baseline', 'Auditor', 'Audit Date', 'Overall Status', 'Summary Notes']
    rows = [
        [s.audit_id, s.audit_type, s.title, s.target_baseline_or_ci, s.auditor, s.audit_date.strftime('%Y-%m-%d'), s.overall_status, s.summary_notes or '']
        for s in sessions
    ]
    return {'headers': headers, 'rows': rows, 'data': sessions}

def get_baseline_release_report():
    releases = Release.query.order_by(Release.release_date.desc()).all()
    headers = ['Release ID', 'Release Name', 'Baseline ID', 'Included Changes', 'Test Status', 'Release Status', 'Release Date', 'Responsible User']
    rows = [
        [r.release_id, r.release_name, r.baseline_id, r.included_changes, r.test_status, r.release_status, r.release_date.strftime('%Y-%m-%d'), r.responsible_user]
        for r in releases
    ]
    return {'headers': headers, 'rows': rows, 'data': releases}
