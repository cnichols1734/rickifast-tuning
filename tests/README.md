# Integration Tests for Aqua Force CRM

This directory contains integration tests for the Aqua Force CRM application, specifically focusing on the clients route functionality.

## Setup

1. **Install Test Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   The testing dependencies (pytest, pytest-flask, pytest-cov) are included in the main requirements.txt file.

2. **Run Tests**
   ```bash
   # Run all tests
   python run_tests.py
   
   # Run specific test file
   python run_tests.py tests/test_clients_integration.py
   
   # Run tests matching a pattern
   python run_tests.py -k test_create
   
   # Run tests with coverage report
   python -m pytest --cov=app --cov-report=html
   ```

## Test Structure

### conftest.py
Contains pytest fixtures and configuration:
- **app**: Creates a Flask application instance with test configuration
- **client**: Provides a test client for making HTTP requests
- **auth**: Helper class for authentication in tests
- **test_user**: Creates a test user for authentication
- **test_client_data**: Creates a single test client
- **multiple_test_clients**: Creates multiple test clients for list testing

### test_clients_integration.py
Comprehensive integration tests for the clients blueprint covering:

#### Authentication Tests
- All routes require login (`@login_required` decorator)
- Unauthenticated requests redirect to login page

#### CRUD Operations
- **Create**: Test client creation with valid/invalid data
- **Read**: Test listing clients, viewing individual clients
- **Update**: Test editing client information
- **Delete**: Test client deletion

#### Business Logic Tests
- Clients are ordered alphabetically by name
- Form validation works correctly
- Database transactions are handled properly
- 404 errors for non-existent clients

#### HTTP Method Tests
- GET requests for forms
- POST requests for data submission
- Method restrictions (DELETE only accepts POST)

## Key Features

### Isolated Testing
- Each test uses a temporary SQLite database
- Database is created fresh for each test
- No test data pollution between tests

### Seeded Data
- Tests automatically create required test data using fixtures
- Test user for authentication
- Sample client data for testing operations
- Multiple clients for testing list functionality

### Realistic Testing
- Tests actual HTTP requests and responses
- Validates database state changes
- Tests form validation and error handling
- Covers authentication flows

## Test Data

The tests use the following seeded data:

### Test User
- Username: `testuser`
- Password: `testpass`
- Email: `test@example.com`

### Test Client Data
- Name: `Test Client`
- Email: `client@example.com`
- Phone: `555-1234`
- Address: `123 Test St`
- City: `Test City`
- State: `Test State`
- Postal Code: `12345`

## Running Individual Test Categories

```bash
# Test authentication
python run_tests.py -k "requires_login"

# Test CRUD operations
python run_tests.py -k "create or edit or delete"

# Test form validation
python run_tests.py -k "validation"

# Test database operations
python run_tests.py -k "success"
```

## Configuration

The test configuration disables:
- CSRF protection (for easier testing)
- Email sending (testing mode)
- Uses in-memory SQLite database

## Benefits of This Approach

1. **Complete Integration Testing**: Tests the entire request/response cycle
2. **Database Testing**: Validates actual database operations
3. **Authentication Testing**: Ensures security requirements work
4. **Form Testing**: Validates form processing and validation
5. **Isolation**: Each test runs independently
6. **Realistic**: Tests behave like real user interactions

## Adding New Tests

To add new tests:

1. Add test methods to `TestClientsIntegration` class
2. Use existing fixtures for common setup
3. Follow naming convention: `test_<action>_<condition>`
4. Include assertions for both HTTP responses and database state
5. Test both success and failure scenarios 