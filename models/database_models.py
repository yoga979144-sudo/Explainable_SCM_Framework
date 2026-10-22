from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Project Manager, Configuration Manager, Developer, QA Engineer, DevOps Engineer, ML/Trust Analyst
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active
        }


class ConfigurationItem(db.Model):
    __tablename__ = 'configuration_items'
    
    id = db.Column(db.Integer, primary_key=True)
    ci_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # e.g. CI-001
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False) 
    # Categories: Source Code, Requirement Documents, Design Documents, Test Cases, 
    # Build Scripts, Configuration Files, Deployment Scripts, Database Schemas, 
    # Machine Learning Models, Organizational Knowledge Repository
    description = db.Column(db.Text, nullable=True)
    current_version = db.Column(db.String(30), default='1.0')
    owner = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(40), default='Draft') # Draft, In-Review, Approved, Baselined, Released, Deprecated
    approval_status = db.Column(db.String(40), default='Approved') # Pending, Approved, Rejected
    baseline_status = db.Column(db.String(40), default='Unbaselined') # Baselined, Unbaselined
    release_status = db.Column(db.String(40), default='Unreleased') # Released, Unreleased
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = db.relationship('ConfigurationVersion', backref='ci_ref', cascade='all, delete-orphan', lazy='dynamic')
    change_requests = db.relationship('ChangeRequest', backref='affected_ci_ref', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'ci_id': self.ci_id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'current_version': self.current_version,
            'owner': self.owner,
            'status': self.status,
            'approval_status': self.approval_status,
            'baseline_status': self.baseline_status,
            'release_status': self.release_status,
            'last_modified_date': self.last_modified_date.strftime('%Y-%m-%d %H:%M:%S') if self.last_modified_date else ''
        }


class ConfigurationVersion(db.Model):
    __tablename__ = 'configuration_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.String(30), unique=True, nullable=False) # e.g. VER-CI-001-1.0
    ci_id = db.Column(db.String(20), db.ForeignKey('configuration_items.ci_id'), nullable=False, index=True)
    version_number = db.Column(db.String(30), nullable=False)
    change_description = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    previous_version = db.Column(db.String(30), nullable=True)
    current_version = db.Column(db.String(30), nullable=False)
    approval_status = db.Column(db.String(40), default='Approved')
    configuration_content = db.Column(db.Text, nullable=True) # Actual config payload or code/schema diff
    diff_summary = db.Column(db.Text, nullable=True)


class ConfigurationDependency(db.Model):
    __tablename__ = 'configuration_dependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    source_ci_id = db.Column(db.String(20), nullable=False, index=True)
    target_ci_id = db.Column(db.String(20), nullable=False, index=True)
    dependency_type = db.Column(db.String(50), nullable=False) # Depends On, Implements, Verifies, Configures, Deploys
    description = db.Column(db.String(255), nullable=True)


class ChangeRequest(db.Model):
    __tablename__ = 'change_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    cr_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # e.g. CR-001
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requester = db.Column(db.String(100), nullable=False)
    assigned_developer = db.Column(db.String(100), nullable=True)
    affected_ci_id = db.Column(db.String(20), db.ForeignKey('configuration_items.ci_id'), nullable=False, index=True)
    current_value = db.Column(db.Text, nullable=True)
    proposed_value = db.Column(db.Text, nullable=False)
    reason_for_change = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.String(20), default='Medium') # Low, Medium, High, Critical
    business_impact = db.Column(db.String(20), default='Medium') # Low, Medium, High, Critical
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    current_status = db.Column(db.String(40), default='Submitted') 
    # Draft, Submitted, Under Evaluation, Pending Review, Approved, Rejected, Implemented, Tested, Closed
    trust_score = db.Column(db.Float, nullable=True)
    trust_explanation = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.String(100), nullable=True)
    reviewer_comments = db.Column(db.Text, nullable=True)
    final_decision = db.Column(db.String(50), nullable=True) # Approved, Rejected, Modification Requested
    implementation_outcome = db.Column(db.String(50), nullable=True) # Success, Rollback, Failed, Pending
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    evaluations = db.relationship('TrustEvaluation', backref='change_request_ref', cascade='all, delete-orphan', lazy='dynamic')
    reviews = db.relationship('ReviewDecision', backref='change_request_ref', cascade='all, delete-orphan', lazy='dynamic')
    test_results = db.relationship('TestResult', backref='change_request_ref', cascade='all, delete-orphan', lazy='dynamic')
    history = db.relationship('ChangeRequestHistory', backref='change_request_ref', cascade='all, delete-orphan', lazy='dynamic')


class ChangeRequestHistory(db.Model):
    __tablename__ = 'change_request_history'
    
    id = db.Column(db.Integer, primary_key=True)
    cr_id = db.Column(db.String(20), db.ForeignKey('change_requests.cr_id'), nullable=False, index=True)
    changed_by = db.Column(db.String(100), nullable=False)
    old_status = db.Column(db.String(40), nullable=True)
    new_status = db.Column(db.String(40), nullable=False)
    action_taken = db.Column(db.String(100), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class OrganizationalMemory(db.Model):
    __tablename__ = 'organizational_memory'
    
    id = db.Column(db.Integer, primary_key=True)
    memory_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # e.g. MEM-001
    project_name = db.Column(db.String(100), default='Enterprise SCM Core')
    category = db.Column(db.String(80), nullable=False)
    change_type = db.Column(db.String(60), nullable=False) # Threshold Modification, Schema Migration, Security Patch, Build Refactor, Deployment Tuning
    description = db.Column(db.Text, nullable=False)
    relevant_characteristics = db.Column(db.Text, nullable=True) # Keywords / attributes
    previous_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    historical_trust_score = db.Column(db.Float, nullable=True)
    test_result = db.Column(db.String(30), default='Passed') # Passed, Failed, Partial
    approval_outcome = db.Column(db.String(30), default='Approved') # Approved, Rejected
    implementation_outcome = db.Column(db.String(30), default='Success') # Success, Rollback, Failure
    failure_success_details = db.Column(db.Text, nullable=True)
    lessons_learned = db.Column(db.Text, nullable=True)
    recorded_date = db.Column(db.DateTime, default=datetime.utcnow)
    source_cr_id = db.Column(db.String(20), nullable=True)

    def to_dict(self):
        return {
            'memory_id': self.memory_id,
            'category': self.category,
            'change_type': self.change_type,
            'description': self.description,
            'historical_trust_score': self.historical_trust_score,
            'test_result': self.test_result,
            'implementation_outcome': self.implementation_outcome,
            'lessons_learned': self.lessons_learned,
            'recorded_date': self.recorded_date.strftime('%Y-%m-%d') if self.recorded_date else ''
        }


class TrustModelVersion(db.Model):
    __tablename__ = 'trust_model_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    version_tag = db.Column(db.String(50), unique=True, nullable=False) # e.g. v1.0-adaptive-rules
    base_weight = db.Column(db.Float, default=20.0)
    memory_outcome_weight = db.Column(db.Float, default=40.0)
    risk_penalty_weight = db.Column(db.Float, default=15.0)
    author_experience_weight = db.Column(db.Float, default=15.0)
    test_readiness_weight = db.Column(db.Float, default=10.0)
    threshold_high = db.Column(db.Float, default=80.0)
    threshold_moderate = db.Column(db.Float, default=60.0)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TrustEvaluation(db.Model):
    __tablename__ = 'trust_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    cr_id = db.Column(db.String(20), db.ForeignKey('change_requests.cr_id'), nullable=False, index=True)
    calculated_score = db.Column(db.Float, nullable=False)
    evidence_confidence = db.Column(db.String(30), nullable=False) # High, Medium, Low
    recommendation = db.Column(db.String(100), nullable=False) 
    formula_breakdown = db.Column(db.Text, nullable=True) # JSON with step-by-step math
    positive_factors = db.Column(db.Text, nullable=True) # JSON list
    risk_factors = db.Column(db.Text, nullable=True) # JSON list
    matched_memory_ids = db.Column(db.Text, nullable=True) # JSON list of matched MEM ids with similarity %
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
    model_version_tag = db.Column(db.String(50), default='v1.0-adaptive-rules')

    def get_positive_factors(self):
        try:
            return json.loads(self.positive_factors or '[]')
        except Exception:
            return []

    def get_risk_factors(self):
        try:
            return json.loads(self.risk_factors or '[]')
        except Exception:
            return []

    def get_matched_memory_list(self):
        try:
            return json.loads(self.matched_memory_ids or '[]')
        except Exception:
            return []


class ReviewDecision(db.Model):
    __tablename__ = 'review_decisions'
    
    id = db.Column(db.Integer, primary_key=True)
    cr_id = db.Column(db.String(20), db.ForeignKey('change_requests.cr_id'), nullable=False, index=True)
    reviewer = db.Column(db.String(100), nullable=False)
    reviewer_role = db.Column(db.String(50), nullable=False)
    decision = db.Column(db.String(50), nullable=False) # Approved, Rejected, Modification Requested
    comments = db.Column(db.Text, nullable=False)
    decided_at = db.Column(db.DateTime, default=datetime.utcnow)


class TestResult(db.Model):
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    cr_id = db.Column(db.String(20), db.ForeignKey('change_requests.cr_id'), nullable=False, index=True)
    test_suite_name = db.Column(db.String(150), nullable=False)
    passed_tests = db.Column(db.Integer, default=0)
    failed_tests = db.Column(db.Integer, default=0)
    test_status = db.Column(db.String(30), default='Passed') # Passed, Failed, Blocked
    test_evidence = db.Column(db.Text, nullable=True)
    executed_by = db.Column(db.String(100), nullable=False)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)


class Baseline(db.Model):
    __tablename__ = 'baselines'
    
    id = db.Column(db.Integer, primary_key=True)
    baseline_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # BL-001
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    approval_status = db.Column(db.String(40), default='Approved') # Approved, Pending, Superseded

    items = db.relationship('BaselineItem', backref='baseline_ref', cascade='all, delete-orphan', lazy='dynamic')


class BaselineItem(db.Model):
    __tablename__ = 'baseline_items'
    
    id = db.Column(db.Integer, primary_key=True)
    baseline_id = db.Column(db.String(30), db.ForeignKey('baselines.baseline_id'), nullable=False, index=True)
    ci_id = db.Column(db.String(20), nullable=False)
    ci_name = db.Column(db.String(150), nullable=False)
    version_number = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(40), default='Active')


class Release(db.Model):
    __tablename__ = 'releases'
    
    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # REL-001
    release_name = db.Column(db.String(150), nullable=False)
    baseline_id = db.Column(db.String(30), db.ForeignKey('baselines.baseline_id'), nullable=False)
    included_changes = db.Column(db.Text, nullable=True) # JSON or comma-separated CR IDs
    test_status = db.Column(db.String(30), default='Passed')
    release_status = db.Column(db.String(40), default='Planned') # Planned, Released, Archived
    release_date = db.Column(db.DateTime, default=datetime.utcnow)
    responsible_user = db.Column(db.String(100), nullable=False)


class AuditSession(db.Model):
    __tablename__ = 'audit_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # FCA-001, PCA-001
    audit_type = db.Column(db.String(20), nullable=False) # FCA or PCA
    title = db.Column(db.String(200), nullable=False)
    target_baseline_or_ci = db.Column(db.String(100), nullable=False)
    auditor = db.Column(db.String(100), nullable=False)
    audit_date = db.Column(db.DateTime, default=datetime.utcnow)
    overall_status = db.Column(db.String(30), default='Passed') # Passed, Conditional, Failed
    summary_notes = db.Column(db.Text, nullable=True)

    responses = db.relationship('AuditChecklistResponse', backref='session_ref', cascade='all, delete-orphan', lazy='dynamic')


class AuditChecklistResponse(db.Model):
    __tablename__ = 'audit_checklist_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    audit_session_id = db.Column(db.String(30), db.ForeignKey('audit_sessions.audit_id'), nullable=False, index=True)
    item_number = db.Column(db.Integer, nullable=False)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.String(10), nullable=False) # Yes, No, N/A
    remarks = db.Column(db.Text, nullable=True)
    evidence = db.Column(db.Text, nullable=True)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    module = db.Column(db.String(80), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class GitHubSetting(db.Model):
    __tablename__ = 'github_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    repo_name = db.Column(db.String(150), nullable=True) # owner/repo
    api_token = db.Column(db.String(255), nullable=True)
    sync_issues = db.Column(db.Boolean, default=True)
    sync_pull_requests = db.Column(db.Boolean, default=True)
    last_synced_at = db.Column(db.DateTime, nullable=True)
    status_message = db.Column(db.String(255), default='Not configured')
