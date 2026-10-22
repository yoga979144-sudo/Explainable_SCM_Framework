import pytest
from services.audit_service import calculate_audit_status, create_audit_session, get_audit_by_id
from services.reporting_service import (
    get_status_accounting_report, get_ci_report, get_change_request_report,
    get_trust_evaluation_report, generate_csv_string
)

def test_fca_audit_calculation_passed_vs_failed(app):
    """Test 20: FCA calculation correctly flags critical failures vs passed state."""
    # Scenario A: All Yes -> Passed
    passed_responses = [
        {"item_number": 1, "question": "CRs implemented?", "response": "Yes"},
        {"item_number": 2, "question": "Traceability verified?", "response": "Yes"},
        {"item_number": 3, "question": "Tests passed?", "response": "Yes"},
        {"item_number": 4, "question": "Defects resolved?", "response": "Yes"},
        {"item_number": 5, "question": "Acceptance criteria?", "response": "Yes"},
        {"item_number": 6, "question": "CCB review complete?", "response": "Yes"}
    ]
    assert calculate_audit_status('FCA', passed_responses) == 'Passed'

    # Scenario B: Critical item 3 ('Tests passed?') is No -> Failed
    failed_responses = [
        {"item_number": 1, "question": "CRs implemented?", "response": "Yes"},
        {"item_number": 2, "question": "Traceability verified?", "response": "Yes"},
        {"item_number": 3, "question": "Tests passed?", "response": "No"},
        {"item_number": 4, "question": "Defects resolved?", "response": "Yes"},
        {"item_number": 5, "question": "Acceptance criteria?", "response": "Yes"},
        {"item_number": 6, "question": "CCB review complete?", "response": "Yes"}
    ]
    assert calculate_audit_status('FCA', failed_responses) == 'Failed'

    # Scenario C: Non-critical item 5 is No -> Conditional
    conditional_responses = [
        {"item_number": 1, "question": "CRs implemented?", "response": "Yes"},
        {"item_number": 2, "question": "Traceability verified?", "response": "Yes"},
        {"item_number": 3, "question": "Tests passed?", "response": "Yes"},
        {"item_number": 4, "question": "Defects resolved?", "response": "Yes"},
        {"item_number": 5, "question": "Acceptance criteria?", "response": "No"}, # Non-critical
        {"item_number": 6, "question": "CCB review complete?", "response": "Yes"}
    ]
    assert calculate_audit_status('FCA', conditional_responses) == 'Conditional'

def test_audit_session_creation(app):
    """Test 21: Audit session creation with checklist persistence."""
    with app.app_context():
        responses = [
            {"item_number": 1, "question": "Source matches baseline?", "response": "Yes", "remarks": "SHA-256 verified", "evidence": "Tree hash a1"},
            {"item_number": 2, "question": "Build version verified?", "response": "Yes", "remarks": "Build 102", "evidence": "Manifest m1"}
        ]
        session = create_audit_session(
            audit_type='PCA',
            title='Test PCA Session',
            target_baseline_or_ci='Release REL-002',
            auditor='pavithra',
            responses_list=responses
        )
        assert session.audit_id.startswith("PCA-")
        assert session.responses.count() == 2

def test_report_generation_and_csv_export(app):
    """Test 22: Status accounting and report CSV generation with live DB records."""
    with app.app_context():
        csa = get_status_accounting_report()
        assert csa['summary']['total'] >= 10
        assert len(csa['rows']) >= 10

        csv_str = generate_csv_string(csa['headers'], csa['rows'])
        assert "CI ID" in csv_str
        assert "CI-001" in csv_str
        assert "CI-006" in csv_str
