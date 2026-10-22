import pytest
from services.trust_engine import evaluate_change_trust, adapt_model_parameters
from services.organizational_memory_service import find_similar_memories
from services.explainability_service import get_explanation_for_cr

def test_trust_score_calculation_bounds_and_validity(app):
    """Test 14: Trust score calculation produces valid, non-random scores in [0, 100]."""
    with app.app_context():
        res = evaluate_change_trust("CR-001")
        score = res['trust_score']
        assert 0.0 <= score <= 100.0
        assert res['evidence_confidence'] in ['High', 'Medium', 'Low']
        assert res['recommendation'] != ""
        assert len(res['positive_factors']) > 0
        assert 'calculated_trust_score' in res['formula_breakdown']

def test_similarity_retrieval_algorithm(app):
    """Test 15: TF-IDF cosine similarity retrieves relevant historical precedent."""
    with app.app_context():
        matches = find_similar_memories(
            target_description="trust threshold adjustment from 70 to 80",
            target_category="Configuration Files",
            limit=3
        )
        assert len(matches) > 0
        top_match = matches[0]
        assert top_match['similarity_score'] > 30.0
        assert "Threshold" in top_match['memory'].change_type

def test_explainability_diagnostic_output(app):
    """Test 16: Explainability service generates factor breakdown and cited precedents."""
    with app.app_context():
        explanation = get_explanation_for_cr("CR-001")
        assert explanation is not None
        assert explanation['trust_score'] > 0
        assert len(explanation['positive_factors']) > 0
        assert len(explanation['factor_contributions']) >= 3
        assert 'metrics' in explanation

def test_adaptive_model_tuning(app):
    """Test 17: Adaptive tuning creates new model version and adjusts parameters."""
    with app.app_context():
        new_model = adapt_model_parameters(
            new_high_threshold=82.0,
            new_mod_threshold=65.0,
            description="Tuned following regression verification."
        )
        assert new_model.threshold_high == 82.0
        assert new_model.threshold_moderate == 65.0
        assert new_model.is_active is True
