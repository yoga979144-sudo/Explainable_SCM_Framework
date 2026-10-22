from datetime import datetime, timedelta
import json
from flask import Flask
from config import config_by_name
from models import db
from models.database_models import (
    User, ConfigurationItem, ConfigurationVersion, ConfigurationDependency,
    ChangeRequest, ChangeRequestHistory, OrganizationalMemory,
    TrustModelVersion, TrustEvaluation, ReviewDecision, TestResult,
    Baseline, BaselineItem, Release, AuditSession, AuditChecklistResponse,
    ActivityLog, GitHubSetting
)
from services.trust_engine import evaluate_change_trust

def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    return app

def seed_database(app):
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if already seeded
        if User.query.first():
            print("Database already contains data. Skipping re-seeding.")
            return

        print("Seeding demo data into SQLite database...")

        # 1. Seed Demo Users (All 6 Roles + Student accounts)
        demo_users = [
            # Standard Role Accounts
            {"username": "pm_user", "email": "pm@scmframework.org", "name": "Sarah Connor", "role": "Project Manager"},
            {"username": "cm_user", "email": "cm@scmframework.org", "name": "Marcus Wright", "role": "Configuration Manager"},
            {"username": "dev_user", "email": "dev@scmframework.org", "name": "Alex Murphy", "role": "Developer"},
            {"username": "qa_user", "email": "qa@scmframework.org", "name": "Ellen Ripley", "role": "QA Engineer"},
            {"username": "devops_user", "email": "devops@scmframework.org", "name": "Miles Dyson", "role": "DevOps Engineer"},
            {"username": "analyst_user", "email": "analyst@scmframework.org", "name": "Grace Hopper", "role": "ML/Trust Analyst"},
            # Student Team Accounts
            {"username": "yogalakshmi", "email": "yogalakshmi.s@vit.ac.in", "name": "YOGALAKSHMI S (23MIS0383)", "role": "Project Manager"},
            {"username": "pavithra", "email": "pavithra.l@vit.ac.in", "name": "PAVITHRA L (23MIS0160)", "role": "Configuration Manager"},
            {"username": "yuvaraj", "email": "yuvaraj.g@vit.ac.in", "name": "YUVARAJ G (24MIS0403)", "role": "Developer"}
        ]

        for u in demo_users:
            user_obj = User(
                username=u["username"],
                email=u["email"],
                full_name=u["name"],
                role=u["role"],
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=60)
            )
            user_obj.set_password("password123")
            db.session.add(user_obj)
        db.session.commit()
        print("-> Users seeded.")

        # 2. Seed Trust Model Version
        model_v1 = TrustModelVersion(
            version_tag="v1.0-adaptive-rules",
            base_weight=20.0,
            memory_outcome_weight=45.0,
            risk_penalty_weight=15.0,
            author_experience_weight=10.0,
            test_readiness_weight=10.0,
            threshold_high=80.0,
            threshold_moderate=60.0,
            is_active=True,
            description="Initial transparent adaptive trust scoring engine with organizational memory feedback.",
            created_at=datetime.utcnow() - timedelta(days=90)
        )
        db.session.add(model_v1)
        db.session.commit()

        # 3. Seed Configuration Items (12 CIs covering all 10 categories)
        ci_definitions = [
            {
                "ci_id": "CI-001",
                "name": "Core SCM Server Engine",
                "category": "Source Code",
                "description": "Central orchestration and versioning engine handling lifecycle events and repository hooks.",
                "current_version": "2.1",
                "owner": "yuvaraj",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "src/core/server_engine.py"
            },
            {
                "ci_id": "CI-002",
                "name": "Authentication & RBAC Service",
                "category": "Source Code",
                "description": "Role-Based Access Control and session management with password hashing and authorization tokens.",
                "current_version": "1.3",
                "owner": "yuvaraj",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "src/auth/rbac_service.py"
            },
            {
                "ci_id": "CI-003",
                "name": "Software Requirements Specification",
                "category": "Requirement Documents",
                "description": "Formal functional and non-functional requirements documentation complying with IEEE 830 / ISO 12207.",
                "current_version": "2.0",
                "owner": "yogalakshmi",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "docs/requirements/srs_v2.0.pdf"
            },
            {
                "ci_id": "CI-004",
                "name": "System Architecture & Data Flow Design",
                "category": "Design Documents",
                "description": "High-level component diagrams, CCB review state machine, and data flow specifications.",
                "current_version": "1.2",
                "owner": "yogalakshmi",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "docs/architecture/system_design.pdf"
            },
            {
                "ci_id": "CI-005",
                "name": "Automated Regression & Verification Suite",
                "category": "Test Cases",
                "description": "End-to-end automated unit, integration, and security regression test scenarios.",
                "current_version": "1.5",
                "owner": "qa_user",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "tests/test_suite_v1.5.py"
            },
            {
                "ci_id": "CI-006",
                "name": "Trust Evaluation Configuration",
                "category": "Configuration Files",
                "description": "Core threshold parameters and weighting matrix for the adaptive configuration trust engine.",
                "current_version": "1.0",
                "owner": "pavithra",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "config/trust_engine_params.json"
            },
            {
                "ci_id": "CI-007",
                "name": "Enterprise Application Settings",
                "category": "Configuration Files",
                "description": "Database connection pools, cache timeouts, logging verbosity, and secret references.",
                "current_version": "1.4",
                "owner": "pavithra",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "config/app_settings.yaml"
            },
            {
                "ci_id": "CI-008",
                "name": "Multi-stage CI Build Automation Script",
                "category": "Build Scripts",
                "description": "Automated build recipe compiling dependencies, verifying checksums, and building deployment wheels.",
                "current_version": "1.1",
                "owner": "devops_user",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "build/build_automation.py"
            },
            {
                "ci_id": "CI-009",
                "name": "Docker & Kubernetes Deployment Manifests",
                "category": "Deployment Scripts",
                "description": "Production container specification, service ingress routing, and pod scaling definitions.",
                "current_version": "1.0",
                "owner": "devops_user",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "deploy/k8s-manifest.yaml"
            },
            {
                "ci_id": "CI-010",
                "name": "Relational Database Migration Schemas",
                "category": "Database Schemas",
                "description": "DDL definitions and alembic migration steps for relational configuration and memory entities.",
                "current_version": "2.0",
                "owner": "pavithra",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "database/schema_v2.0.sql"
            },
            {
                "ci_id": "CI-011",
                "name": "Configuration Risk Classification Model",
                "category": "Machine Learning Models",
                "description": "Trained TF-IDF vectorizer and historical outcome estimator used to rank change impact.",
                "current_version": "1.0",
                "owner": "analyst_user",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "models/ml_risk_classifier.pkl"
            },
            {
                "ci_id": "CI-012",
                "name": "Corporate SCM Knowledge Repository",
                "category": "Organizational Knowledge Repository",
                "description": "Curated lessons learned, post-mortem findings, and architectural configuration guidelines.",
                "current_version": "1.2",
                "owner": "yogalakshmi",
                "status": "Approved",
                "approval_status": "Approved",
                "baseline_status": "Baselined",
                "release_status": "Released",
                "file_path": "knowledge/scm_guidelines.md"
            }
        ]

        for cid in ci_definitions:
            ci_obj = ConfigurationItem(
                ci_id=cid["ci_id"],
                name=cid["name"],
                category=cid["category"],
                description=cid["description"],
                current_version=cid["current_version"],
                owner=cid["owner"],
                status=cid["status"],
                approval_status=cid["approval_status"],
                baseline_status=cid["baseline_status"],
                release_status=cid["release_status"],
                file_path=cid["file_path"],
                created_at=datetime.utcnow() - timedelta(days=60),
                last_modified_date=datetime.utcnow() - timedelta(days=10)
            )
            db.session.add(ci_obj)
        db.session.commit()
        print("-> Configuration Items seeded.")

        # 4. Seed Configuration Versions
        version_records = [
            # CI-006 (Demonstration Scenario Target)
            {
                "version_id": "VER-CI-006-1.0",
                "ci_id": "CI-006",
                "version_number": "1.0",
                "change_description": "Initial baseline of trust evaluation parameters.",
                "author": "pavithra",
                "timestamp": datetime.utcnow() - timedelta(days=45),
                "previous_version": None,
                "current_version": "1.0",
                "approval_status": "Approved",
                "configuration_content": "{\n  \"trust_threshold\": 70,\n  \"confidence_min_samples\": 2,\n  \"penalty_risk_high\": 14,\n  \"enable_memory_retrieval\": true\n}"
            },
            # CI-001
            {
                "version_id": "VER-CI-001-1.0",
                "ci_id": "CI-001",
                "version_number": "1.0",
                "change_description": "Initial core server baseline release.",
                "author": "yuvaraj",
                "timestamp": datetime.utcnow() - timedelta(days=60),
                "previous_version": None,
                "current_version": "1.0",
                "approval_status": "Approved",
                "configuration_content": "# SCM Core v1.0\nPORT = 5000\nDEBUG = False\nWORKERS = 2"
            },
            {
                "version_id": "VER-CI-001-2.0",
                "ci_id": "CI-001",
                "version_number": "2.0",
                "change_description": "Implemented async event bus and state auditing.",
                "author": "yuvaraj",
                "timestamp": datetime.utcnow() - timedelta(days=30),
                "previous_version": "1.0",
                "current_version": "2.0",
                "approval_status": "Approved",
                "configuration_content": "# SCM Core v2.0\nPORT = 5000\nDEBUG = False\nWORKERS = 4\nEVENT_BUS = 'active'"
            },
            {
                "version_id": "VER-CI-001-2.1",
                "ci_id": "CI-001",
                "version_number": "2.1",
                "change_description": "Enhanced socket reconnection timeout and telemetry.",
                "author": "yuvaraj",
                "timestamp": datetime.utcnow() - timedelta(days=12),
                "previous_version": "2.0",
                "current_version": "2.1",
                "approval_status": "Approved",
                "configuration_content": "# SCM Core v2.1\nPORT = 5000\nDEBUG = False\nWORKERS = 4\nEVENT_BUS = 'active'\nSOCKET_TIMEOUT = 30"
            },
            # CI-002
            {
                "version_id": "VER-CI-002-1.0",
                "ci_id": "CI-002",
                "version_number": "1.0",
                "change_description": "Initial RBAC definitions.",
                "author": "yuvaraj",
                "timestamp": datetime.utcnow() - timedelta(days=55),
                "previous_version": None,
                "current_version": "1.0",
                "approval_status": "Approved",
                "configuration_content": "TOKEN_EXPIRY = 3600\nROLES = ['Admin', 'User']"
            },
            {
                "version_id": "VER-CI-002-1.3",
                "ci_id": "CI-002",
                "version_number": "1.3",
                "change_description": "Added all 6 SCM stakeholder roles and session security.",
                "author": "yuvaraj",
                "timestamp": datetime.utcnow() - timedelta(days=20),
                "previous_version": "1.0",
                "current_version": "1.3",
                "approval_status": "Approved",
                "configuration_content": "TOKEN_EXPIRY = 7200\nROLES = ['Project Manager', 'Configuration Manager', 'Developer', 'QA Engineer', 'DevOps Engineer', 'ML/Trust Analyst']\nSTRICT_SESSIONS = True"
            },
            # CI-003, CI-004, CI-005, CI-007, CI-008, CI-010
            {
                "version_id": "VER-CI-003-2.0",
                "ci_id": "CI-003",
                "version_number": "2.0",
                "change_description": "Approved SRS Document Baseline.",
                "author": "yogalakshmi",
                "timestamp": datetime.utcnow() - timedelta(days=40),
                "previous_version": "1.0",
                "current_version": "2.0",
                "approval_status": "Approved",
                "configuration_content": "SRS Section 3: Traceability and Trust Learning Requirements."
            },
            {
                "version_id": "VER-CI-004-1.2",
                "ci_id": "CI-004",
                "version_number": "1.2",
                "change_description": "Updated CCB Review state transition machine.",
                "author": "yogalakshmi",
                "timestamp": datetime.utcnow() - timedelta(days=35),
                "previous_version": "1.0",
                "current_version": "1.2",
                "approval_status": "Approved",
                "configuration_content": "State transition: Draft -> Submitted -> Evaluated -> CCB Review -> Approved/Rejected."
            },
            {
                "version_id": "VER-CI-005-1.5",
                "ci_id": "CI-005",
                "version_number": "1.5",
                "change_description": "Added 35 comprehensive trust verification test assertions.",
                "author": "qa_user",
                "timestamp": datetime.utcnow() - timedelta(days=25),
                "previous_version": "1.0",
                "current_version": "1.5",
                "approval_status": "Approved",
                "configuration_content": "pytest tests/ --cov=services"
            },
            {
                "version_id": "VER-CI-007-1.4",
                "ci_id": "CI-007",
                "version_number": "1.4",
                "change_description": "Configured database connection pool and logging levels.",
                "author": "pavithra",
                "timestamp": datetime.utcnow() - timedelta(days=15),
                "previous_version": "1.0",
                "current_version": "1.4",
                "approval_status": "Approved",
                "configuration_content": "db_pool_size: 25\nmax_overflow: 10\nlog_level: INFO"
            },
            {
                "version_id": "VER-CI-010-2.0",
                "ci_id": "CI-010",
                "version_number": "2.0",
                "change_description": "Added foreign keys for trust evaluations and audit sessions.",
                "author": "pavithra",
                "timestamp": datetime.utcnow() - timedelta(days=18),
                "previous_version": "1.0",
                "current_version": "2.0",
                "approval_status": "Approved",
                "configuration_content": "CREATE TABLE trust_evaluations (...);\nCREATE TABLE audit_sessions (...);"
            }
        ]

        for vr in version_records:
            v_obj = ConfigurationVersion(
                version_id=vr["version_id"],
                ci_id=vr["ci_id"],
                version_number=vr["version_number"],
                change_description=vr["change_description"],
                author=vr["author"],
                timestamp=vr["timestamp"],
                previous_version=vr["previous_version"],
                current_version=vr["current_version"],
                approval_status=vr["approval_status"],
                configuration_content=vr["configuration_content"],
                diff_summary=f"Baseline configuration content established for {vr['version_id']}."
            )
            db.session.add(v_obj)
        db.session.commit()
        print("-> Configuration Versions seeded.")

        # 5. Seed Traceability Dependencies
        dependencies = [
            ("CI-001", "CI-003", "Implements", "Core server implements functional requirements in SRS"),
            ("CI-002", "CI-003", "Implements", "RBAC service implements security access requirements"),
            ("CI-005", "CI-001", "Tests", "Automated test suite verifies server engine stability"),
            ("CI-005", "CI-002", "Tests", "Test suite validates authentication and role permissions"),
            ("CI-006", "CI-001", "Configures", "Trust configuration dictates validation thresholds for engine"),
            ("CI-007", "CI-010", "Depends On", "Application settings rely on relational schema definitions"),
            ("CI-008", "CI-001", "Deploys", "CI build script packages server engine binaries"),
            ("CI-009", "CI-008", "Depends On", "Deployment manifests deploy containers built by automation scripts")
        ]
        for src, tgt, dtype, desc in dependencies:
            dep_obj = ConfigurationDependency(
                source_ci_id=src,
                target_ci_id=tgt,
                dependency_type=dtype,
                description=desc
            )
            db.session.add(dep_obj)
        db.session.commit()
        print("-> Traceability Dependencies seeded.")

        # 6. Seed Organizational Memory Repository (8 realistic records)
        memory_records = [
            {
                "memory_id": "MEM-001",
                "project_name": "Enterprise SCM Core",
                "category": "Configuration Files",
                "change_type": "Trust Threshold Tuning",
                "description": "Adjusted trust score acceptance threshold from 65 to 70 after regression analysis.",
                "relevant_characteristics": "trust_threshold, verification, false_positive_reduction",
                "previous_value": "trust_threshold = 65",
                "new_value": "trust_threshold = 70",
                "historical_trust_score": 82.0,
                "test_result": "Passed",
                "approval_outcome": "Approved",
                "implementation_outcome": "Success",
                "failure_success_details": "Successfully decreased false approvals of unverified code changes by 18%.",
                "lessons_learned": "Incrementing trust thresholds in steps of 5-10 points maintains pipeline throughput while improving reliability.",
                "recorded_date": datetime.utcnow() - timedelta(days=95)
            },
            {
                "memory_id": "MEM-002",
                "project_name": "Enterprise SCM Core",
                "category": "Configuration Files",
                "change_type": "Trust Threshold Optimization",
                "description": "Raised trust threshold from 70 to 75 for staging pipeline verification gate.",
                "relevant_characteristics": "trust_threshold, gate_enforcement, high_confidence",
                "previous_value": "trust_threshold = 70",
                "new_value": "trust_threshold = 75",
                "historical_trust_score": 85.0,
                "test_result": "Passed",
                "approval_outcome": "Approved",
                "implementation_outcome": "Success",
                "failure_success_details": "Zero production configuration regressions observed over 45 days of deployment.",
                "lessons_learned": "Changes backed by historical precedent and automated test cases yield consistent high reliability.",
                "recorded_date": datetime.utcnow() - timedelta(days=70)
            },
            {
                "memory_id": "MEM-003",
                "project_name": "Enterprise SCM Core",
                "category": "Configuration Files",
                "change_type": "Aggressive Trust Threshold Overhaul",
                "description": "Attempted to raise trust threshold abruptly from 60 to 95 across all CI categories.",
                "relevant_characteristics": "extreme_threshold, pipeline_blockage, over-constraining",
                "previous_value": "trust_threshold = 60",
                "new_value": "trust_threshold = 95",
                "historical_trust_score": 45.0,
                "test_result": "Failed",
                "approval_outcome": "Rejected",
                "implementation_outcome": "Failure",
                "failure_success_details": "Threshold was unrealistically high, blocking 92% of valid bug-fix change requests.",
                "lessons_learned": "Never increase trust threshold beyond 85 without providing extensive automated test coverage and confidence calibration.",
                "recorded_date": datetime.utcnow() - timedelta(days=60)
            },
            {
                "memory_id": "MEM-004",
                "project_name": "Enterprise SCM Core",
                "category": "Database Schemas",
                "change_type": "Connection Pool Expansion",
                "description": "Increased database pool max_connections from 20 to 80 for concurrent audit processing.",
                "relevant_characteristics": "database_pool, concurrency, postgresql, performance",
                "previous_value": "max_connections: 20",
                "new_value": "max_connections: 80",
                "historical_trust_score": 78.0,
                "test_result": "Passed",
                "approval_outcome": "Approved",
                "implementation_outcome": "Success",
                "failure_success_details": "Eliminated database connection timeout errors during end-of-quarter SCM audits.",
                "lessons_learned": "Database pool increases must be matched with appropriate OS file descriptor limits.",
                "recorded_date": datetime.utcnow() - timedelta(days=50)
            },
            {
                "memory_id": "MEM-005",
                "project_name": "Enterprise SCM Core",
                "category": "Database Schemas",
                "change_type": "Aggressive Connection Timeout Reduction",
                "description": "Reduced database query timeout from 60 seconds to 3 seconds.",
                "relevant_characteristics": "timeout_reduction, premature_termination, transaction_failure",
                "previous_value": "query_timeout = 60s",
                "new_value": "query_timeout = 3s",
                "historical_trust_score": 52.0,
                "test_result": "Partial",
                "approval_outcome": "Approved",
                "implementation_outcome": "Rollback",
                "failure_success_details": "Large status-accounting analytical reports timed out and corrupted CSV exports.",
                "lessons_learned": "Analytical reporting queries require separate timeout thresholds distinct from transactional API routes.",
                "recorded_date": datetime.utcnow() - timedelta(days=40)
            },
            {
                "memory_id": "MEM-006",
                "project_name": "Enterprise SCM Core",
                "category": "Build Scripts",
                "change_type": "Parallel Test Execution Automation",
                "description": "Configured pytest-xdist to distribute test execution across 4 CPU cores in CI runner.",
                "relevant_characteristics": "build_optimization, parallel_testing, ci_speedup",
                "previous_value": "pytest tests/",
                "new_value": "pytest tests/ -n 4",
                "historical_trust_score": 88.0,
                "test_result": "Passed",
                "approval_outcome": "Approved",
                "implementation_outcome": "Success",
                "failure_success_details": "Reduced test suite execution time from 14 minutes down to 3.8 minutes.",
                "lessons_learned": "Test suites must isolate SQLite database instances per thread to avoid database locked errors.",
                "recorded_date": datetime.utcnow() - timedelta(days=32)
            },
            {
                "memory_id": "MEM-007",
                "project_name": "Enterprise SCM Core",
                "category": "Deployment Scripts",
                "change_type": "Pod Container Memory Limit Reduction",
                "description": "Trimmed Kubernetes container RAM allocation from 4GB down to 1GB to cut infrastructure cost.",
                "relevant_characteristics": "memory_limit, oom_killed, kubernetes_tuning",
                "previous_value": "memory: 4Gi",
                "new_value": "memory: 1Gi",
                "historical_trust_score": 38.0,
                "test_result": "Failed",
                "approval_outcome": "Rejected",
                "implementation_outcome": "Rollback",
                "failure_success_details": "Containers were terminated by Linux kernel OOM-killer during TF-IDF vectorization.",
                "lessons_learned": "ML feature extraction and similarity ranking requires at least 2GB of memory overhead.",
                "recorded_date": datetime.utcnow() - timedelta(days=22)
            },
            {
                "memory_id": "MEM-008",
                "project_name": "Enterprise SCM Core",
                "category": "Source Code",
                "change_type": "Strict Session Authentication Filter",
                "description": "Implemented cryptographic session verification on all CCB decision submission routes.",
                "relevant_characteristics": "security_hardening, session_check, rbac_integrity",
                "previous_value": "permissive_mode = True",
                "new_value": "permissive_mode = False, strict_hmac = True",
                "historical_trust_score": 91.0,
                "test_result": "Passed",
                "approval_outcome": "Approved",
                "implementation_outcome": "Success",
                "failure_success_details": "Blocked unauthenticated POST requests and ensured audit integrity for all reviews.",
                "lessons_learned": "Security enforcement changes with comprehensive regression suites achieve top-tier trust ratings.",
                "recorded_date": datetime.utcnow() - timedelta(days=14)
            }
        ]

        for m in memory_records:
            m_obj = OrganizationalMemory(
                memory_id=m["memory_id"],
                project_name=m["project_name"],
                category=m["category"],
                change_type=m["change_type"],
                description=m["description"],
                relevant_characteristics=m["relevant_characteristics"],
                previous_value=m["previous_value"],
                new_value=m["new_value"],
                historical_trust_score=m["historical_trust_score"],
                test_result=m["test_result"],
                approval_outcome=m["approval_outcome"],
                implementation_outcome=m["implementation_outcome"],
                failure_success_details=m["failure_success_details"],
                lessons_learned=m["lessons_learned"],
                recorded_date=m["recorded_date"]
            )
            db.session.add(m_obj)
        db.session.commit()
        print("-> Organizational Memory Repository seeded.")

        # 7. Seed Change Requests (5 requests including the primary demonstration scenario)
        crs = [
            # CR-001: PRIMARY DEMONSTRATION SCENARIO
            {
                "cr_id": "CR-001",
                "title": "CONFIGURATION TRUST THRESHOLD CHANGE",
                "description": "Increase adaptive trust threshold from 70 to 80 to enhance reliability of configuration change evaluations.",
                "requester": "yuvaraj",
                "assigned_developer": "yuvaraj",
                "affected_ci_id": "CI-006",
                "current_value": "{\n  \"trust_threshold\": 70,\n  \"confidence_min_samples\": 2,\n  \"penalty_risk_high\": 14,\n  \"enable_memory_retrieval\": true\n}",
                "proposed_value": "{\n  \"trust_threshold\": 80,\n  \"confidence_min_samples\": 2,\n  \"penalty_risk_high\": 14,\n  \"enable_memory_retrieval\": true\n}",
                "reason_for_change": "Improve the reliability of configuration-change validation and prevent unverified deployments.",
                "risk_level": "Medium",
                "business_impact": "Medium",
                "current_status": "Pending Review",
                "creation_date": datetime.utcnow() - timedelta(days=2)
            },
            # CR-002: Connection Pool Expansion
            {
                "cr_id": "CR-002",
                "title": "PostgreSQL Database Connection Pool Expansion",
                "description": "Increase maximum pool connections from 25 to 50 for CI status accounting reporting.",
                "requester": "pavithra",
                "assigned_developer": "pavithra",
                "affected_ci_id": "CI-010",
                "current_value": "db_pool_size: 25\nmax_overflow: 10",
                "proposed_value": "db_pool_size: 50\nmax_overflow: 20",
                "reason_for_change": "Eliminate connection wait locks during large status accounting exports.",
                "risk_level": "Low",
                "business_impact": "Medium",
                "current_status": "Approved",
                "creation_date": datetime.utcnow() - timedelta(days=8)
            },
            # CR-003: Pytest Runner Upgrade
            {
                "cr_id": "CR-003",
                "title": "Upgrade Pytest Runner to Version 8.0 with Xdist",
                "description": "Upgrade testing harness to support parallel test execution in CI/CD pipeline.",
                "requester": "devops_user",
                "assigned_developer": "devops_user",
                "affected_ci_id": "CI-008",
                "current_value": "pytest==7.4.0\npytest-cov==4.1.0",
                "proposed_value": "pytest==8.1.1\npytest-xdist==3.5.0\npytest-cov==5.0.0",
                "reason_for_change": "Reduce pipeline turnaround time and enable modern test markers.",
                "risk_level": "Low",
                "business_impact": "Low",
                "current_status": "Implemented",
                "creation_date": datetime.utcnow() - timedelta(days=12)
            },
            # CR-004: Insecure Token Extension (Rejected scenario)
            {
                "cr_id": "CR-004",
                "title": "Relax Authentication Token Expiration to 30 Days",
                "description": "Extend authentication session token lifetime from 2 hours to 30 continuous days.",
                "requester": "dev_user",
                "assigned_developer": "dev_user",
                "affected_ci_id": "CI-002",
                "current_value": "TOKEN_EXPIRY = 7200\nSTRICT_SESSIONS = True",
                "proposed_value": "TOKEN_EXPIRY = 2592000\nSTRICT_SESSIONS = False",
                "reason_for_change": "Avoid frequent user logouts during development testing sessions.",
                "risk_level": "Critical",
                "business_impact": "High",
                "current_status": "Rejected",
                "creation_date": datetime.utcnow() - timedelta(days=16)
            },
            # CR-005: Requirements Specification Baseline Update
            {
                "cr_id": "CR-005",
                "title": "Update Requirements Specification for SCM Standards Audit",
                "description": "Document compliance matrices for IEEE 828, ISO/IEC 12207, and SWEBOK SCM knowledge areas.",
                "requester": "yogalakshmi",
                "assigned_developer": "yogalakshmi",
                "affected_ci_id": "CI-003",
                "current_value": "Requirements Version 1.0 (Draft)",
                "proposed_value": "Requirements Version 2.0 (Complete SCM Standards Traceability Matrix)",
                "reason_for_change": "Fulfill final academic review configuration accounting standards requirements.",
                "risk_level": "Low",
                "business_impact": "Medium",
                "current_status": "Closed",
                "creation_date": datetime.utcnow() - timedelta(days=25)
            }
        ]

        for cr_data in crs:
            cr_obj = ChangeRequest(
                cr_id=cr_data["cr_id"],
                title=cr_data["title"],
                description=cr_data["description"],
                requester=cr_data["requester"],
                assigned_developer=cr_data["assigned_developer"],
                affected_ci_id=cr_data["affected_ci_id"],
                current_value=cr_data["current_value"],
                proposed_value=cr_data["proposed_value"],
                reason_for_change=cr_data["reason_for_change"],
                risk_level=cr_data["risk_level"],
                business_impact=cr_data["business_impact"],
                current_status=cr_data["current_status"],
                creation_date=cr_data["creation_date"]
            )
            db.session.add(cr_obj)
            
            # Seed change history
            hist = ChangeRequestHistory(
                cr_id=cr_data["cr_id"],
                changed_by=cr_data["requester"],
                old_status=None,
                new_status="Submitted",
                action_taken="Change Request Created",
                comments=f"CR created targeting {cr_data['affected_ci_id']}",
                timestamp=cr_data["creation_date"]
            )
            db.session.add(hist)
        db.session.commit()
        print("-> Change Requests seeded.")

        # 8. Evaluate Trust Scores for all Seeded CRs
        for cr_data in crs:
            try:
                evaluate_change_trust(cr_data["cr_id"], user="System")
            except Exception as e:
                print(f"Error evaluating trust for {cr_data['cr_id']}: {e}")
        db.session.commit()
        print("-> Trust Evaluations computed.")

        # 9. Seed CCB Review Decisions
        reviews = [
            {
                "cr_id": "CR-002",
                "reviewer": "yogalakshmi",
                "reviewer_role": "Project Manager",
                "decision": "Approved",
                "comments": "Approved based on favorable historical memory precedent (MEM-004) and verified database scaling requirements."
            },
            {
                "cr_id": "CR-003",
                "reviewer": "pavithra",
                "reviewer_role": "Configuration Manager",
                "decision": "Approved",
                "comments": "Approved for build script pipeline optimization. Testing passed on local developer staging."
            },
            {
                "cr_id": "CR-004",
                "reviewer": "yogalakshmi",
                "reviewer_role": "Project Manager",
                "decision": "Rejected",
                "comments": "REJECTED. Trust score is low (34/100). Severe security risk violating organizational session compliance policies."
            }
        ]
        for r in reviews:
            rev_obj = ReviewDecision(
                cr_id=r["cr_id"],
                reviewer=r["reviewer"],
                reviewer_role=r["reviewer_role"],
                decision=r["decision"],
                comments=r["comments"],
                decided_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(rev_obj)

            # Update CR final decision
            cr = ChangeRequest.query.filter_by(cr_id=r["cr_id"]).first()
            if cr:
                cr.final_decision = r["decision"]
                cr.reviewer_comments = r["comments"]
        db.session.commit()
        print("-> Review Decisions seeded.")

        # 10. Seed Test Results
        test_results = [
            {
                "cr_id": "CR-002",
                "test_suite_name": "Database Concurrency & Stress Suite",
                "passed_tests": 18,
                "failed_tests": 0,
                "test_status": "Passed",
                "test_evidence": "All 18 connection pool stress tests completed without leak or starvation.",
                "executed_by": "qa_user"
            },
            {
                "cr_id": "CR-003",
                "test_suite_name": "CI Runner Multi-Core Execution Tests",
                "passed_tests": 42,
                "failed_tests": 0,
                "test_status": "Passed",
                "test_evidence": "Pytest 8.1 runner completed full test suite across 4 workers in 3.4 seconds.",
                "executed_by": "qa_user"
            },
            {
                "cr_id": "CR-005",
                "test_suite_name": "Documentation & Traceability Verification",
                "passed_tests": 12,
                "failed_tests": 0,
                "test_status": "Passed",
                "test_evidence": "Requirement-to-code traceability verified for all 12 configuration items.",
                "executed_by": "qa_user"
            }
        ]
        for tr in test_results:
            tr_obj = TestResult(
                cr_id=tr["cr_id"],
                test_suite_name=tr["test_suite_name"],
                passed_tests=tr["passed_tests"],
                failed_tests=tr["failed_tests"],
                test_status=tr["test_status"],
                test_evidence=tr["test_evidence"],
                executed_by=tr["executed_by"],
                executed_at=datetime.utcnow() - timedelta(days=4)
            )
            db.session.add(tr_obj)
        db.session.commit()
        print("-> Test Results seeded.")

        # 11. Seed Baselines
        bl1 = Baseline(
            baseline_id="BL-001",
            name="Baseline 1.0 - Core System Foundation",
            description="Initial baseline capturing foundation architecture, requirements, and server engine.",
            created_by="pavithra",
            approval_status="Approved",
            creation_date=datetime.utcnow() - timedelta(days=45)
        )
        db.session.add(bl1)

        bl2 = Baseline(
            baseline_id="BL-002",
            name="Baseline 2.0 - Security & SCM Compliant Baseline",
            description="Production baseline including adaptive trust learning engine and full traceability.",
            created_by="pavithra",
            approval_status="Approved",
            creation_date=datetime.utcnow() - timedelta(days=10)
        )
        db.session.add(bl2)
        db.session.commit()

        # Seed Baseline Items
        all_cis = ConfigurationItem.query.all()
        for ci in all_cis:
            bi = BaselineItem(
                baseline_id="BL-002",
                ci_id=ci.ci_id,
                ci_name=ci.name,
                version_number=ci.current_version,
                status="Active"
            )
            db.session.add(bi)
        db.session.commit()
        print("-> Baselines seeded.")

        # 12. Seed Releases
        rel1 = Release(
            release_id="REL-001",
            release_name="Enterprise SCM v1.0.0 GA",
            baseline_id="BL-001",
            included_changes="Initial foundation release with core version management",
            test_status="Passed",
            release_status="Released",
            release_date=datetime.utcnow() - timedelta(days=40),
            responsible_user="yogalakshmi"
        )
        db.session.add(rel1)

        rel2 = Release(
            release_id="REL-002",
            release_name="Enterprise SCM v2.0.0-RC1",
            baseline_id="BL-002",
            included_changes="CR-002,CR-003,CR-005",
            test_status="Passed",
            release_status="Released",
            release_date=datetime.utcnow() - timedelta(days=7),
            responsible_user="yogalakshmi"
        )
        db.session.add(rel2)
        db.session.commit()
        print("-> Releases seeded.")

        # 13. Seed Configuration Audit Sessions (1 FCA and 1 PCA)
        fca_audit = AuditSession(
            audit_id="FCA-001",
            audit_type="FCA",
            title="Functional Configuration Audit on Baseline 2.0",
            target_baseline_or_ci="Baseline BL-002 (Enterprise SCM v2.0)",
            auditor="qa_user",
            audit_date=datetime.utcnow() - timedelta(days=6),
            overall_status="Passed",
            summary_notes="Functional audit verified: All approved change requests CR-002 and CR-003 are correctly implemented and all regression tests passed."
        )
        db.session.add(fca_audit)

        fca_responses = [
            (1, "Are all approved change requests correctly implemented in this configuration?", "Yes", "Verified CR-002 and CR-003 implementation in repo.", "Git commit history and version logs."),
            (2, "Are all system requirements mapped to corresponding test cases with traceability?", "Yes", "SRS Section 3 maps 100% to test suite CI-005.", "Traceability matrix table."),
            (3, "Has comprehensive functional and regression testing been executed with passing results?", "Yes", "42 unit tests and 18 integration tests passed.", "Pytest report logs."),
            (4, "Are all critical and high-severity software defects resolved?", "Yes", "Zero open blocker or critical issues in queue.", "Bug tracker status."),
            (5, "Does the deployed implementation meet all stakeholder acceptance criteria?", "Yes", "Complies with academic review specifications.", "Project Review Milestone Checklist."),
            (6, "Has the formal Change Control Board (CCB) review and approval been completed?", "Yes", "CCB approvals signed by Project Manager.", "ReviewDecision table records.")
        ]
        for num, q, ans, rem, ev in fca_responses:
            db.session.add(AuditChecklistResponse(
                audit_session_id="FCA-001",
                item_number=num,
                question=q,
                response=ans,
                remarks=rem,
                evidence=ev
            ))

        pca_audit = AuditSession(
            audit_id="PCA-001",
            audit_type="PCA",
            title="Physical Configuration Audit on Release Bundle v2.0.0-RC1",
            target_baseline_or_ci="Release REL-002 (Bundle Archive)",
            auditor="pavithra",
            audit_date=datetime.utcnow() - timedelta(days=5),
            overall_status="Passed",
            summary_notes="Physical audit verified: Source code SHA-256 matches baseline, configuration files are present, and schema migration is verified."
        )
        db.session.add(pca_audit)

        pca_responses = [
            (1, "Does the source code version and tag exactly match the approved configuration baseline?", "Yes", "Tag v2.0.0-RC1 matches baseline BL-002.", "Git tree hash check."),
            (2, "Is the software build identifier and compiled artifact version verified?", "Yes", "Wheel build artifact checksum matches.", "CI build automation manifest."),
            (3, "Are all required configuration files and environment parameter files present?", "Yes", "All 12 configuration items present on disk.", "Directory inspection."),
            (4, "Are database schema migration scripts and data definitions verified?", "Yes", "Alembic schema migration version 2.0 verified.", "SQLite schema inspection."),
            (5, "Is the complete user, technical, and SCM documentation included in the release bundle?", "Yes", "README.md, SRS, and architecture diagrams included.", "Bundle manifest."),
            (6, "Is the active trust-model version tag and parameter configuration formally recorded?", "Yes", "Model tag v1.0-adaptive-rules recorded in database.", "TrustModelVersion table."),
            (7, "Has the organizational knowledge repository been maintained and updated with lessons learned?", "Yes", "8 historical cases recorded and indexed for similarity search.", "OrganizationalMemory table.")
        ]
        for num, q, ans, rem, ev in pca_responses:
            db.session.add(AuditChecklistResponse(
                audit_session_id="PCA-001",
                item_number=num,
                question=q,
                response=ans,
                remarks=rem,
                evidence=ev
            ))
        db.session.commit()
        print("-> Audits seeded.")

        # 14. Seed Initial Activity Logs
        activities = [
            ("yogalakshmi", "System Initialized", "System", "SCM Framework initialized with default demonstration dataset."),
            ("pavithra", "Established Baseline BL-002", "Baseline Management", "Baseline 2.0 created with 12 Configuration Items."),
            ("yuvaraj", "Submitted Change Request CR-001", "Change Management", "Trust threshold modification submitted for CCB review."),
            ("qa_user", "Completed FCA-001 Audit", "Configuration Verification", "Functional configuration audit passed with 100% compliance."),
            ("pavithra", "Completed PCA-001 Audit", "Configuration Verification", "Physical configuration audit passed for Release REL-002.")
        ]
        for usr, act, mod, det in activities:
            db.session.add(ActivityLog(
                user=usr,
                action=act,
                module=mod,
                details=det,
                timestamp=datetime.utcnow() - timedelta(hours=12)
            ))
        db.session.commit()
        print("-> Activity Logs seeded.")

        # 15. Seed GitHub Setting Default
        gh = GitHubSetting(
            repo_name="yogalakshmi-vit/Explainable-SCM-Framework",
            api_token="",
            sync_issues=True,
            sync_pull_requests=True,
            status_message="Running in internal SCM demonstration mode. Set API token in Settings to enable live GitHub API sync."
        )
        db.session.add(gh)
        db.session.commit()
        print("-> GitHub Settings initialized.")
        print("DATABASE INITIALIZATION AND SEEDING COMPLETE!")

if __name__ == "__main__":
    app = create_app("development")
    seed_database(app)
