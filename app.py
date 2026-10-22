import os
from flask import Flask, render_template
from config import config_by_name
from models import db
from models.database_models import User, ChangeRequest, AuditSession

# Import blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.configuration_routes import config_bp
from routes.change_routes import change_bp
from routes.memory_routes import memory_bp
from routes.trust_routes import trust_bp
from routes.audit_routes import audit_bp
from routes.scm_routes import scm_bp
from routes.report_routes import report_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(change_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(trust_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(scm_bp)
    app.register_blueprint(report_bp)

    # Template filters
    @app.template_filter('status_badge')
    def status_badge(status):
        badge_classes = {
            'Approved': 'bg-success',
            'Success': 'bg-success',
            'Passed': 'bg-success',
            'Released': 'bg-success',
            'Baselined': 'bg-primary',
            'Active': 'bg-primary',
            'Submitted': 'bg-info text-dark',
            'Under Evaluation': 'bg-info text-dark',
            'Pending Review': 'bg-warning text-dark',
            'Pending': 'bg-warning text-dark',
            'Conditional': 'bg-warning text-dark',
            'Draft': 'bg-secondary',
            'Implemented': 'bg-purple text-white',
            'Tested': 'bg-teal text-white',
            'Closed': 'bg-dark',
            'Rejected': 'bg-danger',
            'Failure': 'bg-danger',
            'Failed': 'bg-danger',
            'Rollback': 'bg-danger'
        }
        return badge_classes.get(status, 'bg-secondary')

    @app.template_filter('trust_badge')
    def trust_badge(score):
        if score is None:
            return 'bg-secondary'
        if score >= 80.0:
            return 'bg-success'
        elif score >= 60.0:
            return 'bg-warning text-dark'
        return 'bg-danger'

    # Global context variables
    @app.context_processor
    def inject_global_data():
        pending_cr_count = 0
        try:
            pending_cr_count = ChangeRequest.query.filter(
                ChangeRequest.current_status.in_(['Submitted', 'Under Evaluation', 'Pending Review'])
            ).count()
        except Exception:
            pass
        return {
            'pending_cr_count': pending_cr_count,
            'app_title': 'Explainable SCM Framework',
            'team_members': [
                {'name': 'YOGALAKSHMI S', 'reg': '23MIS0383'},
                {'name': 'PAVITHRA L', 'reg': '23MIS0160'},
                {'name': 'YUVARAJ G', 'reg': '24MIS0403'}
            ]
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # Ensure tables exist and seed initial demo data if empty
    with app.app_context():
        db.create_all()
        try:
            if not User.query.first():
                from init_db import seed_database
                seed_database(app)
        except Exception as e:
            print(f"Auto-seeder note: {e}")

    return app

if __name__ == '__main__':
    application = create_app('development')
    print("=" * 70)
    print(" Explainable Organizational Memory-Driven SCM Framework")
    print(" Team: YOGALAKSHMI S (23MIS0383), PAVITHRA L (23MIS0160), YUVARAJ G (24MIS0403)")
    print(" Application running at: http://127.0.0.1:5000")
    print("=" * 70)
    application.run(host='127.0.0.1', port=5000, debug=True)
