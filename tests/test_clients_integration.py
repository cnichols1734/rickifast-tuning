import pytest
from flask import url_for
from app import db
from app.models.models import Client


class TestClientsIntegration:
    """Integration tests for the clients blueprint."""

    def test_clients_index_requires_login(self, client):
        """Test that the clients index page requires authentication."""
        response = client.get('/clients/')
        assert response.status_code == 302  # Redirect to login
        assert '/login' in response.location

    def test_clients_index_with_auth(self, client, auth, test_user, multiple_test_clients):
        """Test that authenticated users can view the clients index."""
        auth.login()
        response = client.get('/clients/')
        assert response.status_code == 200
        assert b'Test Client 1' in response.data
        assert b'Test Client 2' in response.data
        assert b'Test Client 3' in response.data

    def test_clients_index_empty(self, client, auth, test_user):
        """Test the clients index page when no clients exist."""
        auth.login()
        response = client.get('/clients/')
        assert response.status_code == 200
        # Should still render the page successfully even with no clients

    def test_create_client_get_requires_login(self, client):
        """Test that the create client page requires authentication."""
        response = client.get('/clients/create')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_create_client_get_with_auth(self, client, auth, test_user):
        """Test that authenticated users can access the create client form."""
        auth.login()
        response = client.get('/clients/create')
        assert response.status_code == 200
        assert b'Add New Client' in response.data or b'Client Name' in response.data

    def test_create_client_post_success(self, client, auth, test_user, app):
        """Test successfully creating a new client."""
        auth.login()
        
        client_data = {
            'name': 'New Test Client',
            'email': 'newclient@example.com',
            'phone': '555-9876',
            'address': '456 New St',
            'city': 'New City',
            'state': 'New State',
            'postal_code': '54321',
            'notes': 'New client notes'
        }
        
        response = client.post('/clients/create', data=client_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check that the client was created in the database
        with app.app_context():
            new_client = Client.query.filter_by(email='newclient@example.com').first()
            assert new_client is not None
            assert new_client.name == 'New Test Client'
            assert new_client.phone == '555-9876'

    def test_create_client_post_validation_error(self, client, auth, test_user):
        """Test creating a client with invalid data."""
        auth.login()
        
        # Missing required fields
        client_data = {
            'name': '',  # Empty name should fail validation
            'email': 'invalid-email',  # Invalid email format
        }
        
        response = client.post('/clients/create', data=client_data)
        assert response.status_code == 200  # Should return form with errors
        # Form should be re-rendered with validation errors

    def test_view_client_requires_login(self, client, test_client_data):
        """Test that viewing a client requires authentication."""
        response = client.get(f'/clients/{test_client_data}')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_view_client_with_auth(self, client, auth, test_user, test_client_data):
        """Test viewing a specific client when authenticated."""
        auth.login()
        response = client.get(f'/clients/{test_client_data}')
        assert response.status_code == 200
        assert b'Test Client' in response.data
        assert b'client@example.com' in response.data

    def test_view_client_not_found(self, client, auth, test_user):
        """Test viewing a non-existent client returns 404."""
        auth.login()
        response = client.get('/clients/99999')
        assert response.status_code == 404

    def test_edit_client_get_requires_login(self, client, test_client_data):
        """Test that the edit client page requires authentication."""
        response = client.get(f'/clients/{test_client_data}/edit')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_edit_client_get_with_auth(self, client, auth, test_user, test_client_data):
        """Test that authenticated users can access the edit client form."""
        auth.login()
        response = client.get(f'/clients/{test_client_data}/edit')
        assert response.status_code == 200
        assert b'Edit Client' in response.data or b'Test Client' in response.data

    def test_edit_client_post_success(self, client, auth, test_user, test_client_data, app):
        """Test successfully editing a client."""
        auth.login()
        
        updated_data = {
            'name': 'Updated Client Name',
            'email': 'updated@example.com',
            'phone': '555-0000',
            'address': '789 Updated St',
            'city': 'Updated City',
            'state': 'Updated State',
            'postal_code': '99999',
            'notes': 'Updated notes'
        }
        
        response = client.post(f'/clients/{test_client_data}/edit', 
                              data=updated_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check that the client was updated in the database
        with app.app_context():
            updated_client = db.session.get(Client, test_client_data)
            assert updated_client.name == 'Updated Client Name'
            assert updated_client.email == 'updated@example.com'
            assert updated_client.phone == '555-0000'

    def test_edit_client_not_found(self, client, auth, test_user):
        """Test editing a non-existent client returns 404."""
        auth.login()
        response = client.get('/clients/99999/edit')
        assert response.status_code == 404

    def test_delete_client_requires_login(self, client, test_client_data):
        """Test that deleting a client requires authentication."""
        response = client.post(f'/clients/{test_client_data}/delete')
        assert response.status_code == 302
        assert '/login' in response.location

    def test_delete_client_success(self, client, auth, test_user, test_client_data, app):
        """Test successfully deleting a client."""
        auth.login()
        client_id = test_client_data
        
        response = client.post(f'/clients/{client_id}/delete', follow_redirects=True)
        assert response.status_code == 200
        
        # Check that the client was deleted from the database
        with app.app_context():
            deleted_client = db.session.get(Client, client_id)
            assert deleted_client is None

    def test_delete_client_not_found(self, client, auth, test_user):
        """Test deleting a non-existent client returns 404."""
        auth.login()
        response = client.post('/clients/99999/delete')
        assert response.status_code == 404

    def test_delete_client_wrong_method(self, client, auth, test_user, test_client_data):
        """Test that delete only accepts POST method."""
        auth.login()
        response = client.get(f'/clients/{test_client_data}/delete')
        assert response.status_code == 405  # Method not allowed

    def test_clients_are_ordered_by_name(self, client, auth, test_user, app):
        """Test that clients are displayed in alphabetical order by name."""
        # Create clients with names that would test ordering
        with app.app_context():
            clients_data = [
                ('Zebra Client', 'zebra@example.com'),
                ('Alpha Client', 'alpha@example.com'),
                ('Beta Client', 'beta@example.com')
            ]
            
            for name, email in clients_data:
                test_client = Client(name=name, email=email)
                db.session.add(test_client)
            db.session.commit()
        
        auth.login()
        response = client.get('/clients/')
        assert response.status_code == 200
        
        # Check that Alpha appears before Beta which appears before Zebra
        content = response.data.decode('utf-8')
        alpha_pos = content.find('Alpha Client')
        beta_pos = content.find('Beta Client')
        zebra_pos = content.find('Zebra Client')
        
        assert alpha_pos < beta_pos < zebra_pos

    def test_client_form_csrf_protection_disabled_in_tests(self, client, auth, test_user):
        """Test that CSRF protection is properly disabled in test environment."""
        auth.login()
        
        # This should work without CSRF token in test mode
        client_data = {
            'name': 'CSRF Test Client',
            'email': 'csrf@example.com'
        }
        
        response = client.post('/clients/create', data=client_data, follow_redirects=True)
        assert response.status_code == 200
        # The form should process without CSRF errors in test mode 