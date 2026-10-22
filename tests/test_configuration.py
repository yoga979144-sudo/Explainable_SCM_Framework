import pytest
from services.configuration_service import (
    create_ci, get_ci_by_id, update_ci, add_dependency, get_ci_dependencies, get_all_cis
)
from services.version_service import create_new_version, compare_versions, get_versions_for_ci

def test_configuration_item_creation(app):
    """Test 7: Configuration Item creation and initial baseline version generation."""
    with app.app_context():
        ci = create_ci(
            ci_id="CI-099",
            name="Telemetry Service",
            category="Source Code",
            description="Microservice capturing metrics",
            owner="yuvaraj",
            status="Approved",
            current_version="1.0"
        )
        assert ci.ci_id == "CI-099"
        assert ci.current_version == "1.0"
        assert ci.approval_status == "Approved"

        # Check version record automatically created
        versions = get_versions_for_ci("CI-099")
        assert len(versions) == 1
        assert versions[0].version_number == "1.0"

def test_duplicate_ci_id_prevention(app):
    """Test 8: System prevents duplicate CI ID creation."""
    with app.app_context():
        with pytest.raises(ValueError) as exc:
            create_ci(
                ci_id="CI-001", # Existing
                name="Duplicate Core",
                category="Source Code",
                description="Duplicate",
                owner="dev"
            )
        assert "already exists" in str(exc.value)

def test_version_progression_and_diff(app):
    """Test 9: Version history creation and line-by-line diff comparison."""
    with app.app_context():
        v2 = create_new_version(
            ci_id="CI-006",
            new_version_number="1.1",
            change_description="Incremented trust threshold to 80",
            author="pavithra",
            configuration_content="{\n  \"trust_threshold\": 80,\n  \"confidence_min_samples\": 2\n}"
        )
        assert v2.version_number == "1.1"

        ci = get_ci_by_id("CI-006")
        assert ci.current_version == "1.1"

        diff = compare_versions("CI-006", "1.0", "1.1")
        assert "error" not in diff
        assert "trust_threshold" in diff['raw_diff']

def test_configuration_dependencies_traceability(app):
    """Test 10: Establishing and querying traceability links."""
    with app.app_context():
        dep = add_dependency(
            source_ci_id="CI-005",
            target_ci_id="CI-006",
            dependency_type="Tests",
            description="Test suite validates trust threshold parameters"
        )
        assert dep.id is not None

        deps = get_ci_dependencies("CI-005")
        assert any(d.target_ci_id == "CI-006" for d in deps['outgoing'])
