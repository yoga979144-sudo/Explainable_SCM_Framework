import pytest
from services.change_request_service import (
    create_change_request, get_change_request_by_id, record_ccb_review, 
    implement_change_request, record_test_result, close_and_archive_to_memory
)

def test_change_request_creation(app):
    """Test 11: Change request creation and automatic trust evaluation."""
    with app.app_context():
        cr = create_change_request(
            title="Update Database Timeout",
            description="Adjust timeout to 45 seconds",
            requester="yuvaraj",
            affected_ci_id="CI-010",
            proposed_value="query_timeout = 45s",
            reason_for_change="Optimize query performance",
            risk_level="Medium",
            business_impact="Medium"
        )
        assert cr.cr_id.startswith("CR-")
        assert cr.current_status in ['Submitted', 'Under Evaluation']
        assert cr.trust_score is not None
        assert len(cr.history.all()) >= 1

def test_invalid_transition_prevention(app):
    """Test 12: Cannot implement an unapproved change request."""
    with app.app_context():
        # CR-001 is pending review in initial state
        cr = get_change_request_by_id("CR-001")
        assert cr.current_status == "Pending Review"
        
        with pytest.raises(ValueError) as exc:
            implement_change_request(
                cr_id="CR-001",
                new_version_number="1.1",
                commit_message="premature implementation",
                author="yuvaraj"
            )
        assert "Must be 'Approved'" in str(exc.value)

def test_ccb_review_transition(app):
    """Test 13: CCB approval updates status and maintains audit log."""
    with app.app_context():
        rev = record_ccb_review(
            cr_id="CR-001",
            reviewer="YOGALAKSHMI S",
            reviewer_role="Project Manager",
            decision="Approved",
            comments="Approved based on high trust score and verified precedent."
        )
        assert rev.decision == "Approved"

        cr = get_change_request_by_id("CR-001")
        assert cr.current_status == "Approved"
        assert cr.final_decision == "Approved"
