from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth_routes import login_required, permission_required
from services.configuration_service import (
    get_all_cis, get_ci_by_id, create_ci, update_ci, 
    add_dependency, get_ci_dependencies, get_traceability_graph,
    CI_CATEGORIES, CI_STATUSES
)
from services.version_service import get_versions_for_ci

config_bp = Blueprint('configuration', __name__)

@config_bp.route('/configuration-items')
@login_required
def index():
    category = request.args.get('category', 'All')
    status = request.args.get('status', 'All')
    search = request.args.get('search', '').strip()

    cis = get_all_cis(category=category, status=status, search=search)
    return render_template(
        'configuration_items.html',
        cis=cis,
        categories=CI_CATEGORIES,
        statuses=CI_STATUSES,
        selected_category=category,
        selected_status=status,
        search_query=search
    )

@config_bp.route('/configuration-items/new', methods=['GET', 'POST'])
@login_required
@permission_required('manage_ci')
def new_ci():
    if request.method == 'POST':
        ci_id = request.form.get('ci_id', '').strip()
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        owner = request.form.get('owner', session.get('username', 'User')).strip()
        current_version = request.form.get('current_version', '1.0').strip()
        status = request.form.get('status', 'Approved').strip()
        file_path = request.form.get('file_path', '').strip()

        try:
            ci = create_ci(
                ci_id=ci_id,
                name=name,
                category=category,
                description=description,
                owner=owner,
                status=status,
                current_version=current_version,
                file_path=file_path,
                user=session.get('username', 'System')
            )
            flash(f"Configuration Item {ci.ci_id} ({ci.name}) created successfully.", "success")
            return redirect(url_for('configuration.ci_detail', ci_id=ci.ci_id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('configuration_form.html', categories=CI_CATEGORIES, statuses=CI_STATUSES, is_edit=False)

@config_bp.route('/configuration-items/<ci_id>')
@login_required
def ci_detail(ci_id):
    ci = get_ci_by_id(ci_id)
    if not ci:
        flash(f"Configuration Item {ci_id} not found.", "danger")
        return redirect(url_for('configuration.index'))

    versions = get_versions_for_ci(ci_id)
    dependencies = get_ci_dependencies(ci_id)
    all_other_cis = [c for c in get_all_cis() if c.ci_id != ci_id]

    return render_template(
        'configuration_detail.html',
        ci=ci,
        versions=versions,
        dependencies=dependencies,
        all_other_cis=all_other_cis,
        categories=CI_CATEGORIES,
        statuses=CI_STATUSES
    )

@config_bp.route('/configuration-items/<ci_id>/edit', methods=['POST'])
@login_required
@permission_required('manage_ci')
def edit_ci(ci_id):
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    owner = request.form.get('owner', '').strip()
    status = request.form.get('status', '').strip()

    try:
        update_ci(
            ci_id=ci_id,
            name=name,
            category=category,
            description=description,
            owner=owner,
            status=status,
            user=session.get('username', 'System')
        )
        flash(f"Configuration Item {ci_id} updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating {ci_id}: {str(e)}", "danger")

    return redirect(url_for('configuration.ci_detail', ci_id=ci_id))

@config_bp.route('/configuration-items/<ci_id>/add-dependency', methods=['POST'])
@login_required
@permission_required('manage_ci')
def add_ci_dependency(ci_id):
    target_ci_id = request.form.get('target_ci_id', '').strip()
    dependency_type = request.form.get('dependency_type', 'Depends On').strip()
    description = request.form.get('description', '').strip()

    if target_ci_id:
        add_dependency(
            source_ci_id=ci_id,
            target_ci_id=target_ci_id,
            dependency_type=dependency_type,
            description=description,
            user=session.get('username', 'System')
        )
        flash(f"Added traceability link: {ci_id} -> {target_ci_id} ({dependency_type})", "success")
    else:
        flash("Target Configuration Item is required.", "warning")

    return redirect(url_for('configuration.ci_detail', ci_id=ci_id))

@config_bp.route('/traceability')
@login_required
def traceability():
    graph_data = get_traceability_graph()
    cis = get_all_cis()
    return render_template('traceability.html', graph_data=graph_data, cis=cis)
