from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required, permission_required
from models.database_models import TrustEvaluation, TrustModelVersion, ChangeRequest
from services.trust_engine import (
    get_or_create_active_model_version, evaluate_change_trust, adapt_model_parameters
)
from services.explainability_service import get_explanation_for_cr

trust_bp = Blueprint('trust', __name__)

@trust_bp.route('/trust-evaluation')
@login_required
def index():
    active_model = get_or_create_active_model_version()
    all_models = TrustModelVersion.query.order_by(TrustModelVersion.created_at.desc()).all()
    evaluations = TrustEvaluation.query.order_by(TrustEvaluation.evaluation_date.desc()).all()

    return render_template(
        'trust_evaluation.html',
        active_model=active_model,
        all_models=all_models,
        evaluations=evaluations
    )

@trust_bp.route('/explainability')
@trust_bp.route('/explainability/<cr_id>')
@login_required
def explainability_view(cr_id=None):
    all_crs = ChangeRequest.query.order_by(ChangeRequest.creation_date.desc()).all()
    
    # If no CR specified, default to CR-001 (primary academic demo scenario)
    if not cr_id:
        cr_001 = ChangeRequest.query.filter_by(cr_id='CR-001').first()
        target_cr_id = cr_001.cr_id if cr_001 else (all_crs[0].cr_id if all_crs else None)
    else:
        target_cr_id = cr_id

    explanation = None
    if target_cr_id:
        explanation = get_explanation_for_cr(target_cr_id)

    return render_template(
        'explainability.html',
        all_crs=all_crs,
        current_cr_id=target_cr_id,
        explanation=explanation
    )

@trust_bp.route('/trust-model/tune', methods=['POST'])
@login_required
@permission_required('tune_trust')
def tune_parameters():
    threshold_high = request.form.get('threshold_high')
    threshold_moderate = request.form.get('threshold_moderate')
    memory_weight = request.form.get('memory_weight')
    description = request.form.get('description', '').strip()

    try:
        new_high = float(threshold_high) if threshold_high else None
        new_mod = float(threshold_moderate) if threshold_moderate else None
        new_mem_w = float(memory_weight) if memory_weight else None

        new_model = adapt_model_parameters(
            new_high_threshold=new_high,
            new_mod_threshold=new_mod,
            new_memory_weight=new_mem_w,
            description=description,
            user=session.get('username', 'Trust Analyst')
        )
        flash(f"Adapted trust model parameters successfully. Active version: {new_model.version_tag}", "success")
    except Exception as e:
        flash(f"Error updating trust parameters: {str(e)}", "danger")

    return redirect(url_for('trust.index'))
