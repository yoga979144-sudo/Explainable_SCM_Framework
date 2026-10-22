from flask import Blueprint, render_template, request, Response, flash, redirect, url_for, session
from routes.auth_routes import login_required
from services.reporting_service import (
    generate_csv_string, get_ci_report, get_version_history_report,
    get_change_request_report, get_trust_evaluation_report,
    get_organizational_memory_report, get_status_accounting_report,
    get_audit_report, get_baseline_release_report
)
from services.trust_engine import get_or_create_active_model_version
from services.github_service import get_github_settings
from models.database_models import User, ActivityLog
from models import db

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports')
@login_required
def index():
    report_type = request.args.get('type', 'status_accounting')
    
    report_data = None
    if report_type == 'ci':
        report_data = get_ci_report()
    elif report_type == 'version':
        report_data = get_version_history_report()
    elif report_type == 'change':
        report_data = get_change_request_report()
    elif report_type == 'trust':
        report_data = get_trust_evaluation_report()
    elif report_type == 'memory':
        report_data = get_organizational_memory_report()
    elif report_type == 'fca':
        report_data = get_audit_report('FCA')
    elif report_type == 'pca':
        report_data = get_audit_report('PCA')
    elif report_type == 'baseline':
        report_data = get_baseline_release_report()
    else: # status_accounting
        report_type = 'status_accounting'
        report_data = get_status_accounting_report()

    return render_template(
        'reports.html',
        selected_type=report_type,
        report_data=report_data
    )

@report_bp.route('/reports/export/<report_type>')
@login_required
def export_csv(report_type):
    generator_map = {
        'ci': (get_ci_report, 'configuration_items_report.csv'),
        'version': (get_version_history_report, 'version_history_report.csv'),
        'change': (get_change_request_report, 'change_requests_report.csv'),
        'trust': (get_trust_evaluation_report, 'trust_evaluations_report.csv'),
        'memory': (get_organizational_memory_report, 'organizational_memory_report.csv'),
        'status_accounting': (get_status_accounting_report, 'status_accounting_report.csv'),
        'fca': (lambda: get_audit_report('FCA'), 'fca_audits_report.csv'),
        'pca': (lambda: get_audit_report('PCA'), 'pca_audits_report.csv'),
        'baseline': (get_baseline_release_report, 'baseline_release_report.csv')
    }

    if report_type not in generator_map:
        flash("Invalid report type specified.", "danger")
        return redirect(url_for('report.index'))

    fetcher, filename = generator_map[report_type]
    data = fetcher()
    csv_content = generate_csv_string(data['headers'], data['rows'])

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@report_bp.route('/settings')
@login_required
def settings():
    active_model = get_or_create_active_model_version()
    gh_settings = get_github_settings()
    users_count = User.query.count()
    activity_count = ActivityLog.query.count()

    return render_template(
        'settings.html',
        active_model=active_model,
        gh_settings=gh_settings,
        users_count=users_count,
        activity_count=activity_count
    )

@report_bp.route('/settings/reseed-db', methods=['POST'])
@login_required
def reseed_database():
    """Admin utility to safely reset demo data if requested during academic presentation."""
    if session.get('role') != 'Project Manager':
        flash("Only Project Managers can trigger database reset.", "danger")
        return redirect(url_for('report.settings'))

    from init_db import seed_database
    from flask import current_app
    db.drop_all()
    seed_database(current_app)
    flash("Database successfully reset and re-seeded with demonstration scenario dataset.", "success")
    return redirect(url_for('dashboard.index'))
