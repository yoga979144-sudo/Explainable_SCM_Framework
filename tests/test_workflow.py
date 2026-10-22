import pytest
from services.change_request_service import (
    get_change_request_by_id, record_ccb_review, implement_change_request,
    record_test_result, close_and_archive_to_memory
)
from services.configuration_service import get_ci_by_id
from services.baseline_service import create_baseline, create_release, get_all_baselines
from services.organizational_memory_service import get_all_memories

def test_complete_demonstration_scenario_lifecycle(app):
    """
    Test 18: Full End-to-End Execution of the Primary Project Scenario:
    CR-001 (Configuration Trust Threshold Change 70 -> 80)
    1. Evaluate & inspect CR-001
    2. CCB review approval
    3. Implementation & version increment on CI-006 (1.0 -> 1.1)
    4. Recording test verification results
    5. Close & archive to Organizational Memory!
    """
    with app.app_context():
        # Step 1: Verify Initial State of CR-001 and CI-006
        cr = get_change_request_by_id("CR-001")
        assert cr is not None
        assert cr.affected_ci_id == "CI-006"
        ci = get_ci_by_id("CI-006")
        assert ci.current_version == "1.0"

        # Step 2: CCB Review Approval
        rev = record_ccb_review(
            cr_id="CR-001",
            reviewer="YOGALAKSHMI S",
            reviewer_role="Project Manager",
            decision="Approved",
            comments="Approved based on empirical memory precedent MEM-001 and high trust evaluation."
        )
        assert cr.current_status == "Approved"

        # Step 3: Implementation
        ver = implement_change_request(
            cr_id="CR-001",
            new_version_number="1.1",
            commit_message="Applied verified trust threshold increase to 80",
            author="yuvaraj"
        )
        assert cr.current_status == "Implemented"
        assert ci.current_version == "1.1"

        # Step 4: Record Test Result
        test_res = record_test_result(
            cr_id="CR-001",
            test_suite_name="Automated Trust Regression Suite",
            passed_tests=35,
            failed_tests=0,
            test_status="Passed",
            test_evidence="Log checksum ab84f2",
            executed_by="qa_user"
        )
        assert cr.current_status == "Tested"
        assert test_res.test_status == "Passed"

        # Step 5: Close & Archive to Organizational Memory
        initial_mem_count = len(get_all_memories())
        mem = close_and_archive_to_memory(
            cr_id="CR-001",
            implementation_outcome="Success",
            lessons_learned="Raising threshold to 80 successfully filtered low-confidence drift without blocking valid changes."
        )
        assert cr.current_status == "Closed"
        assert len(get_all_memories()) == initial_mem_count + 1
        assert mem.source_cr_id == "CR-001"

def test_baseline_and_release_creation(app):
    """Test 19: Baseline creation and Release linkage with approval verification."""
    with app.app_context():
        bl = create_baseline(
            name="Baseline 3.0 Verification Test",
            description="Integration baseline",
            created_by="pavithra",
            ci_version_pairs=[
                {"ci_id": "CI-001", "version_number": "2.1"},
                {"ci_id": "CI-006", "version_number": "1.0"}
            ]
        )
        assert bl.baseline_id.startswith("BL-")

        rel = create_release(
            release_name="Enterprise SCM v3.0.0 Test Release",
            baseline_id=bl.baseline_id,
            included_cr_ids="CR-002,CR-003",
            responsible_user="yogalakshmi",
            release_status="Released"
        )
        assert rel.release_id.startswith("REL-")
        assert rel.release_status == "Released"
