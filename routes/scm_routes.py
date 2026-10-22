from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required, permission_required
from services.version_service import get_all_versions, compare_versions, check_local_git_status
from services.configuration_service import get_all_cis, CI_CATEGORIES, CI_STATUSES
from services.baseline_service import (
    get_all_baselines, get_baseline_by_id, create_baseline,
    get_all_releases, create_release
)
from services.change_request_service import get_all_change_requests
from services.github_service import get_github_integration_overview, update_github_settings
from services.reporting_service import get_status_accounting_report

scm_bp = Blueprint('scm', __name__)

@scm_bp.route('/version-history')
@login_required
def version_history():
    versions = get_all_versions()
    cis = get_all_cis()
    local_git = check_local_git_status()
    return render_template('version_history.html', versions=versions, cis=cis, local_git=local_git)

@scm_bp.route('/version-compare')
@login_required
def version_compare():
    ci_id = request.args.get('ci_id')
    v1 = request.args.get('v1')
    v2 = request.args.get('v2')

    diff_result = None
    if ci_id and v1 and v2:
        diff_result = compare_versions(ci_id, v1, v2)

    cis = get_all_cis()
    return render_template(
        'version_compare.html',
        cis=cis,
        selected_ci=ci_id,
        v1=v1,
        v2=v2,
        diff_result=diff_result
    )

@scm_bp.route('/status-accounting')
@login_required
def status_accounting():
    status = request.args.get('status', 'All')
    category = request.args.get('category', 'All')
    owner = request.args.get('owner', 'All')
    search = request.args.get('search', '').strip()

    cis = get_all_cis(category=category, status=status, search=search)
    if owner and owner != 'All':
        cis = [c for c in cis if c.owner == owner]

    report = get_status_accounting_report()
    all_owners = sorted(list({c.owner for c in report['data'] if c.owner}))

    return render_template(
        'status_accounting.html',
        cis=cis,
        summary=report['summary'],
        categories=CI_CATEGORIES,
        statuses=CI_STATUSES,
        owners=all_owners,
        selected_status=status,
        selected_category=category,
        selected_owner=owner,
        search_query=search
    )

@scm_bp.route('/baselines', methods=['GET', 'POST'])
@login_required
def baselines():
    if request.method == 'POST':
        if session.get('role') not in ['Project Manager', 'Configuration Manager']:
            flash("Only Project Managers and Configuration Managers can create baselines.", "danger")
            return redirect(url_for('scm.baselines'))

        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        selected_ci_ids = request.form.getlist('ci_ids')

        if not name or not selected_ci_ids:
            flash("Baseline name and at least one Configuration Item must be selected.", "warning")
            return redirect(url_for('scm.baselines'))

        ci_version_pairs = []
        for ci_id in selected_ci_ids:
            ver = request.form.get(f'version_{ci_id}', '1.0')
            ci_version_pairs.append({'ci_id': ci_id, 'version_number': ver})

        try:
            bl = create_baseline(
                name=name,
                description=description,
                created_by=session.get('username', 'Configuration Manager'),
                ci_version_pairs=ci_version_pairs,
                user=session.get('username', 'System')
            )
            flash(f"Configuration Baseline {bl.baseline_id} created successfully.", "success")
        except Exception as e:
            flash(f"Error creating baseline: {str(e)}", "danger")

        return redirect(url_for('scm.baselines'))

    baselines_list = get_all_baselines()
    approved_cis = [c for c in get_all_cis() if c.approval_status == 'Approved']
    return render_template('baselines.html', baselines=baselines_list, approved_cis=approved_cis)

@scm_bp.route('/releases', methods=['GET', 'POST'])
@login_required
def releases():
    if request.method == 'POST':
        if session.get('role') not in ['Project Manager', 'Configuration Manager', 'DevOps Engineer']:
            flash("Permission denied for creating software releases.", "danger")
            return redirect(url_for('scm.releases'))

        release_name = request.form.get('release_name', '').strip()
        baseline_id = request.form.get('baseline_id', '').strip()
        included_cr_ids = request.form.get('included_cr_ids', '').strip()
        release_status = request.form.get('release_status', 'Planned').strip()
        test_status = request.form.get('test_status', 'Passed').strip()

        try:
            rel = create_release(
                release_name=release_name,
                baseline_id=baseline_id,
                included_cr_ids=included_cr_ids,
                responsible_user=session.get('full_name', session.get('username', 'Lead')),
                release_status=release_status,
                test_status=test_status,
                user=session.get('username', 'System')
            )
            flash(f"Software Release {rel.release_id} ({rel.release_name}) created successfully.", "success")
        except Exception as e:
            flash(f"Error creating release: {str(e)}", "danger")

        return redirect(url_for('scm.releases'))

    releases_list = get_all_releases()
    baselines_list = get_all_baselines()
    approved_crs = [cr for cr in get_all_change_requests() if cr.current_status in ['Approved', 'Implemented', 'Tested', 'Closed']]
    return render_template('releases.html', releases=releases_list, baselines=baselines_list, approved_crs=approved_crs)

@scm_bp.route('/github-integration', methods=['GET', 'POST'])
@login_required
def github_integration():
    if request.method == 'POST':
        repo_name = request.form.get('repo_name', '').strip()
        api_token = request.form.get('api_token', '').strip()
        update_github_settings(repo_name, api_token, user=session.get('username', 'System'))
        flash("GitHub settings updated.", "info")
        return redirect(url_for('scm.github_integration'))

    overview = get_github_integration_overview()
    return render_template('github_integration.html', overview=overview)

@scm_bp.route('/scm-standards')
@login_required
def scm_standards():
    return render_template('scm_standards.html')
