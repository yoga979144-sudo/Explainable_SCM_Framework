from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required, permission_required
from services.audit_service import (
    get_all_audits, get_audit_by_id, create_audit_session,
    FCA_CHECKLIST_TEMPLATE, PCA_CHECKLIST_TEMPLATE
)
from services.baseline_service import get_all_baselines
from services.configuration_service import get_all_cis

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/fca-audit')
@login_required
def fca_index():
    audits = get_all_audits(audit_type='FCA')
    baselines = get_all_baselines()
    cis = get_all_cis()
    return render_template(
        'fca_audit.html',
        audits=audits,
        checklist=FCA_CHECKLIST_TEMPLATE,
        baselines=baselines,
        cis=cis
    )

@audit_bp.route('/fca-audit/new', methods=['POST'])
@login_required
@permission_required('audit')
def submit_fca():
    title = request.form.get('title', '').strip()
    target = request.form.get('target', '').strip()
    summary_notes = request.form.get('summary_notes', '').strip()
    auditor = session.get('full_name', session.get('username', 'QA Auditor'))

    responses_list = []
    for item in FCA_CHECKLIST_TEMPLATE:
        item_num = item['item']
        resp = request.form.get(f'response_{item_num}', 'Yes')
        remarks = request.form.get(f'remarks_{item_num}', '').strip()
        evidence = request.form.get(f'evidence_{item_num}', '').strip()
        responses_list.append({
            'item_number': item_num,
            'question': item['question'],
            'response': resp,
            'remarks': remarks,
            'evidence': evidence
        })

    try:
        session_obj = create_audit_session(
            audit_type='FCA',
            title=title,
            target_baseline_or_ci=target,
            auditor=auditor,
            responses_list=responses_list,
            summary_notes=summary_notes,
            user=session.get('username', 'QA Auditor')
        )
        flash(f"Functional Configuration Audit {session_obj.audit_id} recorded with status '{session_obj.overall_status}'.", "success")
        return redirect(url_for('audit.audit_detail', audit_id=session_obj.audit_id))
    except Exception as e:
        flash(f"Error recording FCA audit: {str(e)}", "danger")
        return redirect(url_for('audit.fca_index'))

@audit_bp.route('/pca-audit')
@login_required
def pca_index():
    audits = get_all_audits(audit_type='PCA')
    baselines = get_all_baselines()
    cis = get_all_cis()
    return render_template(
        'pca_audit.html',
        audits=audits,
        checklist=PCA_CHECKLIST_TEMPLATE,
        baselines=baselines,
        cis=cis
    )

@audit_bp.route('/pca-audit/new', methods=['POST'])
@login_required
@permission_required('audit')
def submit_pca():
    title = request.form.get('title', '').strip()
    target = request.form.get('target', '').strip()
    summary_notes = request.form.get('summary_notes', '').strip()
    auditor = session.get('full_name', session.get('username', 'Configuration Auditor'))

    responses_list = []
    for item in PCA_CHECKLIST_TEMPLATE:
        item_num = item['item']
        resp = request.form.get(f'response_{item_num}', 'Yes')
        remarks = request.form.get(f'remarks_{item_num}', '').strip()
        evidence = request.form.get(f'evidence_{item_num}', '').strip()
        responses_list.append({
            'item_number': item_num,
            'question': item['question'],
            'response': resp,
            'remarks': remarks,
            'evidence': evidence
        })

    try:
        session_obj = create_audit_session(
            audit_type='PCA',
            title=title,
            target_baseline_or_ci=target,
            auditor=auditor,
            responses_list=responses_list,
            summary_notes=summary_notes,
            user=session.get('username', 'Configuration Auditor')
        )
        flash(f"Physical Configuration Audit {session_obj.audit_id} recorded with status '{session_obj.overall_status}'.", "success")
        return redirect(url_for('audit.audit_detail', audit_id=session_obj.audit_id))
    except Exception as e:
        flash(f"Error recording PCA audit: {str(e)}", "danger")
        return redirect(url_for('audit.pca_index'))

@audit_bp.route('/audits/<audit_id>')
@login_required
def audit_detail(audit_id):
    audit = get_audit_by_id(audit_id)
    if not audit:
        flash(f"Audit {audit_id} not found.", "danger")
        return redirect(url_for('dashboard.index'))
    return render_template('audit_detail.html', audit=audit)
