from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database_models import User, ActivityLog
from models import db

auth_bp = Blueprint('auth', __name__)

# Role definition and permission mappings
ROLE_PERMISSIONS = {
    'Project Manager': ['view', 'create_cr', 'ccb_review', 'create_baseline', 'create_release', 'audit', 'manage_ci', 'view_reports', 'settings'],
    'Configuration Manager': ['view', 'manage_ci', 'create_version', 'create_baseline', 'create_release', 'audit', 'view_reports', 'settings'],
    'Developer': ['view', 'create_cr', 'implement_cr', 'view_reports'],
    'QA Engineer': ['view', 'record_tests', 'audit', 'view_reports'],
    'DevOps Engineer': ['view', 'create_cr', 'create_release', 'view_reports', 'github_sync'],
    'ML/Trust Analyst': ['view', 'evaluate_trust', 'tune_trust', 'manage_memory', 'view_reports']
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in first.", "warning")
                return redirect(url_for('auth.login'))
            user_role = session.get('role', 'Developer')
            allowed_permissions = ROLE_PERMISSIONS.get(user_role, ['view'])
            if permission not in allowed_permissions and user_role != 'Project Manager':
                flash(f"Access Denied: Your role ({user_role}) does not have '{permission}' permission.", "danger")
                return redirect(request.referrer or url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            
            # Log sign-in
            log = ActivityLog(
                user=user.username,
                action="User Logged In",
                module="Authentication",
                details=f"User {user.full_name} signed in with role {user.role}"
            )
            db.session.add(log)
            db.session.commit()

            flash(f"Welcome back, {user.full_name} ({user.role})!", "success")
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard.index'))
        else:
            flash("Invalid username or password. Use demo credentials provided below.", "danger")

    demo_users = User.query.all()
    return render_template('login.html', demo_users=demo_users)

@auth_bp.route('/quick-login/<username>')
def quick_login(username):
    """Convenient demo switcher for professor/review demonstration."""
    user = User.query.filter_by(username=username).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name
        session['role'] = user.role
        flash(f"Switched role to {user.full_name} ({user.role}).", "info")
    return redirect(request.referrer or url_for('dashboard.index'))

@auth_bp.route('/logout')
def logout():
    username = session.get('username', 'Anonymous')
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('auth.login'))
