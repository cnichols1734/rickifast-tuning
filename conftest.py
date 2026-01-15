import pytest
import tempfile
import os
from app import create_app, db
from app.models.models import User, Client, Quote, Invoice, Service


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Use in-memory SQLite database for each test
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # In-memory database
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        },
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
        "SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        # Create all tables fresh for each test
        db.create_all()
        yield app
        # Clean up
        db.session.remove()
        db.drop_all()
        # Close all connections
        db.engine.dispose()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username='testuser', password='testpass'):
            return self._client.post(
                '/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/logout')

    return AuthActions(client)


@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        db.session.close()  # Explicitly close the session
        
    # Return user ID instead of the object to avoid session issues
    return user_id


@pytest.fixture(scope='function')
def test_client_data(app, test_user):
    """Create test client data."""
    with app.app_context():
        client = Client(
            name='Test Client',
            email='client@example.com',
            phone='555-1234',
            address='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            notes='Test notes'
        )
        db.session.add(client)
        db.session.commit()
        client_id = client.id
        db.session.close()  # Explicitly close the session
        
    # Return client ID instead of the object to avoid session issues
    return client_id


@pytest.fixture(scope='function')
def multiple_test_clients(app, test_user):
    """Create multiple test clients for list testing."""
    with app.app_context():
        clients = []
        for i in range(3):
            client = Client(
                name=f'Test Client {i+1}',
                email=f'client{i+1}@example.com',
                phone=f'555-123{i}',
                address=f'12{i} Test St',
                city='Test City',
                state='Test State',
                postal_code=f'1234{i}',
                notes=f'Test notes {i+1}'
            )
            clients.append(client)
            db.session.add(client)
        db.session.commit()
        client_ids = [c.id for c in clients]
        db.session.close()  # Explicitly close the session
        
    # Return client IDs instead of objects to avoid session issues
    return client_ids 