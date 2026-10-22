import pytest
from app import create_app
from models import db
from init_db import seed_database

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        seed_database(app)
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Client authenticated as Project Manager (yogalakshmi)."""
    with client.session_transaction() as sess:
        sess['user_id'] = 7
        sess['username'] = 'yogalakshmi'
        sess['full_name'] = 'YOGALAKSHMI S (23MIS0383)'
        sess['role'] = 'Project Manager'
    return client

@pytest.fixture
def dev_client(client):
    """Client authenticated as Developer (yuvaraj)."""
    with client.session_transaction() as sess:
        sess['user_id'] = 9
        sess['username'] = 'yuvaraj'
        sess['full_name'] = 'YUVARAJ G (24MIS0403)'
        sess['role'] = 'Developer'
    return client
