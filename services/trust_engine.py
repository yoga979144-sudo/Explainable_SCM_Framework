import json
from datetime import datetime
from models import db
from models.database_models import (
    ChangeRequest, TrustEvaluation, TrustModelVersion, 
    OrganizationalMemory, ActivityLog, ConfigurationItem
)
from services.organizational_memory_service import find_similar_memories

# Category Base Trust Baseline (Risk inherent to CI category)
CATEGORY_BASE_SCORES = {
    "Requirement Documents": 85.0,
    "Design Documents": 82.0,
    "Test Cases": 80.0,
    "Organizational Knowledge Repository": 80.0,
    "Configuration Files": 72.0,
    "Build Scripts": 70.0,
    "Source Code": 68.0,
    "Deployment Scripts": 65.0,
    "Database Schemas": 62.0,
    "Machine Learning Models": 60.0
}

RISK_PENALTIES = {
    "Low": 0.0,
    "Medium": 6.0,
    "High": 14.0,
    "Critical": 22.0
}

def get_or_create_active_model_version():
    active = TrustModelVersion.query.filter_by(is_active=True).first()
    if not active:
        active = TrustModelVersion(
            version_tag="v1.0-adaptive-rules",
            base_weight=20.0,
            memory_outcome_weight=45.0,
            risk_penalty_weight=15.0,
            author_experience_weight=10.0,
            test_readiness_weight=10.0,
            threshold_high=80.0,
            threshold_moderate=60.0,
            is_active=True,
            description="Initial transparent adaptive trust scoring engine with organizational memory feedback."
        )
        db.session.add(active)
        db.session.commit()
    return active

def evaluate_change_trust(cr_id, user='System'):
    """
    Evaluates the trust score of a Change Request based on:
    1. Base CI Category baseline reliability
    2. Similar Historical Changes from Organizational Memory (Success/Failure/Rollback rates)
    3. Change Risk Level & Business Impact penalties
    4. Requester Track Record (past approved vs rejected CRs)
    5. Proposed configuration verification readiness
    """
    cr = ChangeRequest.query.filter_by(cr_id=cr_id).first()
    if not cr:
        raise ValueError(f"Change Request {cr_id} not found.")

    ci = ConfigurationItem.query.filter_by(ci_id=cr.affected_ci_id).first()
    ci_category = ci.category if ci else "Configuration Files"

    model_ver = get_or_create_active_model_version()

    # Step 1: Retrieve Similar Historical Changes from Organizational Memory
    similar_matches = find_similar_memories(
        target_description=f"{cr.title} {cr.reason_for_change} {cr.proposed_value}",
        target_category=ci_category,
        target_change_type=cr.title,
        limit=5
    )

    # Step 2: Analyze Evidence Confidence
    match_count = len(similar_matches)
    avg_similarity = (sum(m['similarity_score'] for m in similar_matches) / match_count) if match_count > 0 else 0.0

    if match_count >= 3 and avg_similarity >= 45.0:
        evidence_confidence = "High"
    elif match_count >= 1:
        evidence_confidence = "Medium"
    else:
        evidence_confidence = "Low"

    # Step 3: Compute Memory Outcome Component (Score out of 100)
    positive_factors = []
    risk_factors = []
    
    success_count = 0
    failure_count = 0
    rollback_count = 0
    tests_passed_count = 0

    if match_count > 0:
        total_weighted_points = 0.0
        total_weight = 0.0

        for match in similar_matches:
            mem = match['memory']
            weight = match['similarity_score'] / 100.0
            total_weight += weight

            if mem.implementation_outcome == 'Success':
                success_count += 1
                total_weighted_points += (100.0 * weight)
            elif mem.implementation_outcome == 'Rollback':
                rollback_count += 1
                total_weighted_points += (30.0 * weight)
            else: # Failure
                failure_count += 1
                total_weighted_points += (10.0 * weight)

            if mem.test_result == 'Passed':
                tests_passed_count += 1

        memory_score = (total_weighted_points / total_weight) if total_weight > 0 else 60.0
        
        if success_count > 0:
            positive_factors.append(f"{success_count} similar historical change(s) succeeded in organizational memory.")
        if tests_passed_count > 0:
            positive_factors.append(f"{tests_passed_count} similar precedent(s) verified with passing test results.")
        if rollback_count > 0:
            risk_factors.append(f"{rollback_count} similar precedent required a rollback; caution advised.")
        if failure_count > 0:
            risk_factors.append(f"{failure_count} similar historical change(s) experienced defects/failures.")
    else:
        # Limited evidence defaults to neutral 60.0 with explicit warning
        memory_score = 60.0
        risk_factors.append("No directly matching historical precedent found in organizational memory (low precedent evidence).")

    # Step 4: Category Base Component
    cat_base = CATEGORY_BASE_SCORES.get(ci_category, 70.0)
    positive_factors.append(f"CI Category '{ci_category}' has a baseline stability rating of {cat_base:.0f}/100.")

    # Step 5: Risk & Impact Deduction
    risk_penalty = RISK_PENALTIES.get(cr.risk_level, 6.0)
    if cr.business_impact in ['High', 'Critical']:
        risk_penalty += 4.0
    
    if risk_penalty > 0:
        risk_factors.append(f"Risk level '{cr.risk_level}' with business impact '{cr.business_impact}' deducts {risk_penalty:.1f} penalty points.")
    else:
        positive_factors.append("Low declared risk profile.")

    # Step 6: Requester Track Record
    past_crs = ChangeRequest.query.filter(
        ChangeRequest.requester == cr.requester,
        ChangeRequest.cr_id != cr.cr_id
    ).all()
    
    author_bonus = 0.0
    if past_crs:
        approved_crs = sum(1 for p in past_crs if p.current_status in ['Approved', 'Implemented', 'Tested', 'Closed'])
        author_ratio = approved_crs / len(past_crs)
        if author_ratio >= 0.75:
            author_bonus = 5.0
            positive_factors.append(f"Requester '{cr.requester}' has a strong historical track record ({approved_crs}/{len(past_crs)} approved).")
        elif author_ratio < 0.4:
            author_bonus = -4.0
            risk_factors.append(f"Requester '{cr.requester}' has a low historical change acceptance rate.")
    else:
        author_bonus = 0.0

    # Step 7: Calculate Combined Trust Score using Configured Weights
    # Formula:
    # Score = (cat_base * 0.25) + (memory_score * 0.50) + author_bonus - risk_penalty + readiness_bonus
    readiness_bonus = 4.0 if cr.proposed_value and cr.reason_for_change else 0.0
    if readiness_bonus > 0:
        positive_factors.append("Clear change rationale and concrete proposed configuration provided.")

    raw_score = (
        (cat_base * (model_ver.base_weight / 100.0)) +
        (memory_score * (model_ver.memory_outcome_weight / 100.0)) +
        author_bonus -
        risk_penalty +
        readiness_bonus +
        (15.0) # Base system calibration offset
    )

    trust_score = round(max(5.0, min(98.0, raw_score)), 1)

    # Step 8: Recommendation Determination
    if trust_score >= model_ver.threshold_high:
        recommendation = "High trust; recommend approval review."
        next_step = "Proceed to Change Control Board (CCB) approval."
    elif trust_score >= model_ver.threshold_moderate:
        recommendation = "Moderate trust; recommend additional validation."
        next_step = "Conduct automated regression test or staging dry-run before CCB approval."
    else:
        recommendation = "Low trust; recommend modification or rejection review."
        next_step = "Revise proposed configuration to address known risk factors or conduct in-depth architectural audit."

    # Formula breakdown details for explainability
    formula_breakdown = {
        'model_version': model_ver.version_tag,
        'category_base': cat_base,
        'category_weight': model_ver.base_weight,
        'memory_score': round(memory_score, 1),
        'memory_weight': model_ver.memory_outcome_weight,
        'risk_penalty': risk_penalty,
        'author_bonus': author_bonus,
        'readiness_bonus': readiness_bonus,
        'calculated_trust_score': trust_score,
        'evidence_confidence': evidence_confidence,
        'threshold_high': model_ver.threshold_high,
        'threshold_moderate': model_ver.threshold_moderate,
        'recommendation': recommendation,
        'suggested_next_step': next_step
    }

    matched_memory_data = [
        {
            'memory_id': m['memory'].memory_id,
            'change_type': m['memory'].change_type,
            'outcome': m['memory'].implementation_outcome,
            'test_result': m['memory'].test_result,
            'similarity_score': m['similarity_score'],
            'description': m['memory'].description,
            'lessons_learned': m['memory'].lessons_learned
        }
        for m in similar_matches
    ]

    # Save or update TrustEvaluation in database
    existing_eval = TrustEvaluation.query.filter_by(cr_id=cr_id).first()
    if not existing_eval:
        existing_eval = TrustEvaluation(cr_id=cr_id)
        db.session.add(existing_eval)

    existing_eval.calculated_score = trust_score
    existing_eval.evidence_confidence = evidence_confidence
    existing_eval.recommendation = recommendation
    existing_eval.formula_breakdown = json.dumps(formula_breakdown)
    existing_eval.positive_factors = json.dumps(positive_factors)
    existing_eval.risk_factors = json.dumps(risk_factors)
    existing_eval.matched_memory_ids = json.dumps(matched_memory_data)
    existing_eval.evaluation_date = datetime.utcnow()
    existing_eval.model_version_tag = model_ver.version_tag

    # Update ChangeRequest entity
    cr.trust_score = trust_score
    cr.recommendation = recommendation
    cr.trust_explanation = (
        f"Score: {trust_score}/100 ({evidence_confidence} confidence). "
        f"Recommendation: {recommendation} "
        f"Key factors: {len(positive_factors)} positive, {len(risk_factors)} risk factors identified."
    )
    if cr.current_status in ['Draft', 'Submitted']:
        cr.current_status = 'Under Evaluation'

    log = ActivityLog(
        user=user,
        action="Evaluated Trust Score",
        module="Adaptive Trust Engine",
        details=f"Evaluated {cr_id}: Trust Score {trust_score}/100, Confidence {evidence_confidence}"
    )
    db.session.add(log)
    db.session.commit()

    return {
        'evaluation': existing_eval,
        'cr': cr,
        'trust_score': trust_score,
        'evidence_confidence': evidence_confidence,
        'recommendation': recommendation,
        'positive_factors': positive_factors,
        'risk_factors': risk_factors,
        'matched_memories': matched_memory_data,
        'formula_breakdown': formula_breakdown
    }

def adapt_model_parameters(new_high_threshold=None, new_mod_threshold=None, new_memory_weight=None, description="", user='System'):
    """
    Adaptive learning: update scoring parameters based on verified feedback.
    """
    current = get_or_create_active_model_version()
    current.is_active = False

    new_ver_num = int(current.version_tag.split('-')[0].replace('v', '').split('.')[1]) + 1
    new_tag = f"v1.{new_ver_num}-adaptive-tuned"

    new_model = TrustModelVersion(
        version_tag=new_tag,
        base_weight=current.base_weight,
        memory_outcome_weight=new_memory_weight if new_memory_weight is not None else current.memory_outcome_weight,
        risk_penalty_weight=current.risk_penalty_weight,
        author_experience_weight=current.author_experience_weight,
        test_readiness_weight=current.test_readiness_weight,
        threshold_high=new_high_threshold if new_high_threshold is not None else current.threshold_high,
        threshold_moderate=new_mod_threshold if new_mod_threshold is not None else current.threshold_moderate,
        is_active=True,
        description=description or f"Tuned trust thresholds based on empirical change outcomes.",
        created_at=datetime.utcnow()
    )
    db.session.add(new_model)

    log = ActivityLog(
        user=user,
        action="Adapted Trust Scoring Model",
        module="Adaptive Trust Engine",
        details=f"Activated model {new_tag} (High: {new_model.threshold_high}, Mod: {new_model.threshold_moderate})"
    )
    db.session.add(log)
    db.session.commit()
    return new_model
