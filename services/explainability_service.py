import json
from models.database_models import ChangeRequest, TrustEvaluation, OrganizationalMemory
from services.trust_engine import evaluate_change_trust

def get_explanation_for_cr(cr_id):
    cr = ChangeRequest.query.filter_by(cr_id=cr_id).first()
    if not cr:
        return None

    evaluation = TrustEvaluation.query.filter_by(cr_id=cr_id).first()
    if not evaluation:
        # Automatically trigger evaluation if not already evaluated
        eval_result = evaluate_change_trust(cr_id)
        evaluation = eval_result['evaluation']

    breakdown = {}
    try:
        breakdown = json.loads(evaluation.formula_breakdown or '{}')
    except Exception:
        breakdown = {}

    positive_factors = evaluation.get_positive_factors()
    risk_factors = evaluation.get_risk_factors()
    matched_memories = evaluation.get_matched_memory_list()

    # Calculate evidence metrics
    matched_ids = [m['memory_id'] for m in matched_memories if 'memory_id' in m]
    full_memories = OrganizationalMemory.query.filter(OrganizationalMemory.memory_id.in_(matched_ids)).all() if matched_ids else []
    
    success_count = sum(1 for m in full_memories if m.implementation_outcome == 'Success')
    failure_count = sum(1 for m in full_memories if m.implementation_outcome == 'Failure')
    rollback_count = sum(1 for m in full_memories if m.implementation_outcome == 'Rollback')

    # Factor contributions for visualization
    factor_contributions = [
        {
            'factor': f"Category Baseline ({cr.affected_ci_ref.category if cr.affected_ci_ref else 'General'})",
            'impact': 'Positive',
            'points': round(breakdown.get('category_base', 70.0) * (breakdown.get('category_weight', 20.0) / 100.0), 1),
            'description': 'Intrinsic reliability rating of this configuration item class.'
        },
        {
            'factor': 'Historical Organizational Precedents',
            'impact': 'Positive' if breakdown.get('memory_score', 0) >= 50 else 'Negative',
            'points': round(breakdown.get('memory_score', 60.0) * (breakdown.get('memory_weight', 45.0) / 100.0), 1),
            'description': f"Weighted outcome from {len(matched_memories)} retrieved similar historical change(s)."
        },
        {
            'factor': f"Change Risk & Impact Penalty ({cr.risk_level}/{cr.business_impact})",
            'impact': 'Negative',
            'points': -round(breakdown.get('risk_penalty', 0.0), 1),
            'description': 'Deduction scaled to potential system disruption risk.'
        },
        {
            'factor': 'Requester Track Record',
            'impact': 'Positive' if breakdown.get('author_bonus', 0) >= 0 else 'Negative',
            'points': round(breakdown.get('author_bonus', 0.0), 1),
            'description': 'Adjustment based on author historical change approval success rate.'
        },
        {
            'factor': 'Configuration Verification Readiness',
            'impact': 'Positive',
            'points': round(breakdown.get('readiness_bonus', 4.0), 1),
            'description': 'Bonus for comprehensive diff specification and clear rationale.'
        }
    ]

    return {
        'cr': cr,
        'evaluation': evaluation,
        'trust_score': evaluation.calculated_score,
        'evidence_confidence': evaluation.evidence_confidence,
        'recommendation': evaluation.recommendation,
        'suggested_next_step': breakdown.get('suggested_next_step', 'Submit to CCB for review.'),
        'positive_factors': positive_factors,
        'risk_factors': risk_factors,
        'factor_contributions': factor_contributions,
        'matched_memories': matched_memories,
        'full_memories': full_memories,
        'metrics': {
            'total_precedents': len(full_memories),
            'success_count': success_count,
            'failure_count': failure_count,
            'rollback_count': rollback_count
        },
        'formula_breakdown': breakdown
    }
