import pytest
from models.database_models import User

def test_app_startup_and_login_page(client):
    """Test 1: Application startup and login page accessibility."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Sign In" in response.data
    assert b"YOGALAKSHMI S" in response.data

def test_database_initialization_users(app):
    """Test 2: Database user table initialized with demo accounts."""
    with app.app_context():
        users = User.query.all()
        assert len(users) >= 6
        pm = User.query.filter_by(username='pm_user').first()
        assert pm is not None
        assert pm.role == 'Project Manager'
        assert pm.check_password('password123')
        assert not pm.check_password('wrongpass')

def test_user_authentication_success(client):
    """Test 3: Authentication with valid credentials."""
    response = client.post('/login', data={
        'username': 'pm_user',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"SCM Operations Dashboard" in response.data

def test_user_authentication_failure(client):
    """Test 4: Authentication rejection with invalid password."""
    response = client.post('/login', data={
        'username': 'pm_user',
        'password': 'bad_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data

def test_quick_login_switcher(client):
    """Test 5: Quick login demo switcher."""
    response = client.get('/quick-login/analyst_user', follow_redirects=True)
    assert response.status_code == 200
    assert b"ML/Trust Analyst" in response.data

def test_unauthorized_action_restriction(dev_client):
    """Test 6: Developer cannot access Project Manager restricted re-seed route."""
    response = dev_client.post('/settings/reseed-db', follow_redirects=True)
    assert response.status_code == 200
    assert b"Only Project Managers can trigger database reset" in response.data
