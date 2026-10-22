from flask import Blueprint, render_template, jsonify
from routes.auth_routes import login_required
from models.database_models import (
    ConfigurationItem, ChangeRequest, OrganizationalMemory, 
    TrustEvaluation, AuditSession, ActivityLog
)
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Calculate real database metrics
    total_cis = ConfigurationItem.query.count()
    approved_cis = ConfigurationItem.query.filter_by(approval_status='Approved').count()
    
    pending_crs = ChangeRequest.query.filter(
        ChangeRequest.current_status.in_(['Submitted', 'Under Evaluation', 'Pending Review'])
    ).count()
    approved_crs = ChangeRequest.query.filter_by(current_status='Approved').count()
    rejected_crs = ChangeRequest.query.filter_by(current_status='Rejected').count()
    
    # Average trust score
    avg_trust_result = TrustEvaluation.query.with_entities(func.avg(TrustEvaluation.calculated_score)).scalar()
    avg_trust = round(avg_trust_result, 1) if avg_trust_result is not None else 0.0

    total_memories = OrganizationalMemory.query.count()
    pending_audits = AuditSession.query.filter(AuditSession.overall_status != 'Passed').count()

    # Recent activities & tables
    recent_changes = ChangeRequest.query.order_by(ChangeRequest.creation_date.desc()).limit(5).all()
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(7).all()
    recent_evaluations = TrustEvaluation.query.order_by(TrustEvaluation.evaluation_date.desc()).limit(5).all()

    # Trust Score Distribution for Chart.js
    # Ranges: High (>=80), Moderate (60-79), Low (<60)
    high_trust_count = TrustEvaluation.query.filter(TrustEvaluation.calculated_score >= 80.0).count()
    moderate_trust_count = TrustEvaluation.query.filter(
        TrustEvaluation.calculated_score >= 60.0,
        TrustEvaluation.calculated_score < 80.0
    ).count()
    low_trust_count = TrustEvaluation.query.filter(TrustEvaluation.calculated_score < 60.0).count()

    # CI Category distribution
    categories_stats = ConfigurationItem.query.with_entities(
        ConfigurationItem.category, func.count(ConfigurationItem.id)
    ).group_by(ConfigurationItem.category).all()

    category_labels = [c[0] for c in categories_stats]
    category_counts = [c[1] for c in categories_stats]

    return render_template(
        'dashboard.html',
        total_cis=total_cis,
        approved_cis=approved_cis,
        pending_crs=pending_crs,
        approved_crs=approved_crs,
        rejected_crs=rejected_crs,
        avg_trust=avg_trust,
        total_memories=total_memories,
        pending_audits=pending_audits,
        recent_changes=recent_changes,
        recent_activities=recent_activities,
        recent_evaluations=recent_evaluations,
        high_trust_count=high_trust_count,
        moderate_trust_count=moderate_trust_count,
        low_trust_count=low_trust_count,
        category_labels=category_labels,
        category_counts=category_counts
    )
