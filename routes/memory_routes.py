from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required, permission_required
from services.organizational_memory_service import (
    get_all_memories, get_memory_by_id, add_memory_record, find_similar_memories
)
from services.configuration_service import CI_CATEGORIES

memory_bp = Blueprint('memory', __name__)

OUTCOMES = ['Success', 'Rollback', 'Failure']

@memory_bp.route('/organizational-memory')
@login_required
def index():
    category = request.args.get('category', 'All')
    outcome = request.args.get('outcome', 'All')
    search = request.args.get('search', '').strip()

    memories = get_all_memories(category=category, outcome=outcome, search=search)
    return render_template(
        'organizational_memory.html',
        memories=memories,
        categories=CI_CATEGORIES,
        outcomes=OUTCOMES,
        selected_category=category,
        selected_outcome=outcome,
        search_query=search
    )

@memory_bp.route('/organizational-memory/new', methods=['GET', 'POST'])
@login_required
@permission_required('manage_memory')
def new_memory():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        change_type = request.form.get('change_type', '').strip()
        description = request.form.get('description', '').strip()
        relevant_characteristics = request.form.get('relevant_characteristics', '').strip()
        previous_value = request.form.get('previous_value', '').strip()
        new_value = request.form.get('new_value', '').strip()
        historical_trust_score = request.form.get('historical_trust_score')
        test_result = request.form.get('test_result', 'Passed').strip()
        approval_outcome = request.form.get('approval_outcome', 'Approved').strip()
        implementation_outcome = request.form.get('implementation_outcome', 'Success').strip()
        failure_success_details = request.form.get('failure_success_details', '').strip()
        lessons_learned = request.form.get('lessons_learned', '').strip()

        try:
            score = float(historical_trust_score) if historical_trust_score else None
            mem = add_memory_record(
                category=category,
                change_type=change_type,
                description=description,
                relevant_characteristics=relevant_characteristics,
                previous_value=previous_value,
                new_value=new_value,
                historical_trust_score=score,
                test_result=test_result,
                approval_outcome=approval_outcome,
                implementation_outcome=implementation_outcome,
                failure_success_details=failure_success_details,
                lessons_learned=lessons_learned,
                user=session.get('username', 'System')
            )
            flash(f"Organizational Memory Record {mem.memory_id} saved successfully.", "success")
            return redirect(url_for('memory.index'))
        except Exception as e:
            flash(f"Error saving memory record: {str(e)}", "danger")

    return render_template('memory_form.html', categories=CI_CATEGORIES, outcomes=OUTCOMES)

@memory_bp.route('/organizational-memory/<memory_id>')
@login_required
def memory_detail(memory_id):
    mem = get_memory_by_id(memory_id)
    if not mem:
        flash(f"Memory record {memory_id} not found.", "danger")
        return redirect(url_for('memory.index'))
    return render_template('memory_detail.html', mem=mem)

@memory_bp.route('/organizational-memory/similarity-test', methods=['GET', 'POST'])
@login_required
def similarity_test():
    """Interactive tool allowing students/reviewers to test similarity retrieval on arbitrary text."""
    results = None
    query_text = ""
    category = "Configuration Files"

    if request.method == 'POST':
        query_text = request.form.get('query_text', '').strip()
        category = request.form.get('category', 'Configuration Files').strip()
        if query_text:
            results = find_similar_memories(
                target_description=query_text,
                target_category=category,
                limit=6
            )

    return render_template(
        'similarity_test.html',
        categories=CI_CATEGORIES,
        query_text=query_text,
        selected_category=category,
        results=results
    )
