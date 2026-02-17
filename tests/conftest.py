"""
Pytest configuration and shared fixtures for all tests.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# =========================================================================
# Mock AWS Services
# =========================================================================

@pytest.fixture
def mock_dynamodb_client():
    """Mock DynamoDB client"""
    client = Mock()
    client.get_item.return_value = {'Item': {}}
    client.put_item.return_value = {}
    client.update_item.return_value = {}
    client.delete_item.return_value = {}
    client.query.return_value = {'Items': [], 'Count': 0}
    return client


@pytest.fixture
def mock_cognito_client():
    """Mock Cognito client"""
    client = Mock()
    client.sign_up.return_value = {
        'UserSub': 'test-user-id',
        'UserConfirmed': False,
        'CodeDeliveryDetails': {
            'DeliveryMedium': 'EMAIL',
            'Destination': 't***@example.com'
        }
    }
    client.confirm_sign_up.return_value = {}
    client.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'test-access-token',
            'IdToken': 'test-id-token',
            'RefreshToken': 'test-refresh-token',
            'ExpiresIn': 3600
        }
    }
    return client


# =========================================================================
# Test Data Fixtures
# =========================================================================

@pytest.fixture
def test_user_id():
    """Test user ID"""
    return "test-user-123"


@pytest.fixture
def test_household_id():
    """Test household ID"""
    return "household-456"


@pytest.fixture
def test_subject_id():
    """Test subject ID"""
    return "subject-789"


@pytest.fixture
def test_todo_id():
    """Test todo ID"""
    return "todo-abc"


@pytest.fixture
def test_habit_id():
    """Test habit ID"""
    return "habit-def"


@pytest.fixture
def test_user_data(test_user_id, test_household_id, test_subject_id):
    """Test user profile data"""
    return {
        'id': test_user_id,
        'username': 'testuser',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '+11234567890',
        'household_id': test_household_id,
        'subject_id': test_subject_id,
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_household_data(test_household_id, test_user_id):
    """Test household data"""
    return {
        'id': test_household_id,
        'name': 'Test Household',
        'owner_user_id': test_user_id,
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_subject_data(test_subject_id, test_household_id):
    """Test subject data"""
    return {
        'id': test_subject_id,
        'household_id': test_household_id,
        'type': 'self',
        'display_name': 'Test Subject',
        'dob': '1990-01-01',
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_todo_data(test_todo_id, test_household_id, test_subject_id):
    """Test todo data"""
    from models.enum import DifficultyEnum, ToDoStatusEnum
    return {
        'id': test_todo_id,
        'household_id': test_household_id,
        'subject_id': test_subject_id,
        'title': 'Test Todo',
        'description': 'Test description',
        'difficulty': DifficultyEnum.EASY,
        'status': ToDoStatusEnum.ACTIVE,
        'date_due': '2026-12-31',
        'checklist': ['Item 1', 'Item 2'],
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_habit_data(test_habit_id, test_household_id, test_subject_id):
    """Test habit data"""
    from models.enum import HabitCounterEnum, DifficultyEnum, HabitTypeEnum, HabitStatusEnum
    return {
        'id': test_habit_id,
        'household_id': test_household_id,
        'subject_id': test_subject_id,
        'title': 'Test Habit',
        'description': 'Test habit description',
        'counter': HabitCounterEnum.DAILY,
        'difficulty': DifficultyEnum.MEDIUM,
        'type': HabitTypeEnum.BUILD,
        'status': HabitStatusEnum.ACTIVE,
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


@pytest.fixture
def test_habit_event_data(test_habit_id, test_household_id, test_subject_id):
    """Test habit event data"""
    from models.enum import HabitEventStatusEnum
    return {
        'id': 'event-123',
        'household_id': test_household_id,
        'subject_id': test_subject_id,
        'habit_id': test_habit_id,
        'period_key': '2026-02-16',
        'status': HabitEventStatusEnum.DONE,
        'note': 'Completed successfully',
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat()
    }


# =========================================================================
# Lambda Event Fixtures
# =========================================================================

@pytest.fixture
def lambda_context():
    """Mock Lambda context"""
    context = Mock()
    context.function_name = 'test-function'
    context.function_version = '1'
    context.invoked_function_arn = 'arn:aws:lambda:us-west-1:123456789012:function:test'
    context.memory_limit_in_mb = 128
    context.aws_request_id = 'test-request-id'
    context.log_group_name = '/aws/lambda/test'
    context.log_stream_name = '2026/02/16/[$LATEST]test'
    return context


@pytest.fixture
def api_gateway_event(test_user_id):
    """Mock API Gateway event"""
    return {
        'version': '2.0',
        'routeKey': 'POST /test',
        'rawPath': '/test',
        'rawQueryString': '',
        'headers': {
            'content-type': 'application/json',
            'authorization': 'Bearer test-token'
        },
        'requestContext': {
            'accountId': '123456789012',
            'apiId': 'test-api',
            'domainName': 'test.execute-api.us-west-1.amazonaws.com',
            'domainPrefix': 'test',
            'http': {
                'method': 'POST',
                'path': '/test',
                'protocol': 'HTTP/1.1',
                'sourceIp': '127.0.0.1',
                'userAgent': 'test-agent'
            },
            'requestId': 'test-request-id',
            'routeKey': 'POST /test',
            'stage': 'dev',
            'time': '16/Feb/2026:10:00:00 +0000',
            'timeEpoch': 1708084800000,
            'authorizer': {
                'jwt': {
                    'claims': {
                        'sub': test_user_id,
                        'email': 'test@example.com',
                        'cognito:username': 'testuser'
                    }
                }
            }
        },
        'body': '{}',
        'pathParameters': {},
        'queryStringParameters': {},
        'isBase64Encoded': False
    }


@pytest.fixture
def api_gateway_event_with_path_params(api_gateway_event, test_household_id, test_subject_id):
    """API Gateway event with path parameters"""
    event = api_gateway_event.copy()
    event['pathParameters'] = {
        'householdId': test_household_id,
        'subjectId': test_subject_id
    }
    event['rawPath'] = f'/households/{test_household_id}/subjects/{test_subject_id}/todos'
    return event


@pytest.fixture
def api_gateway_event_with_query_params(api_gateway_event):
    """API Gateway event with query parameters"""
    event = api_gateway_event.copy()
    event['queryStringParameters'] = {
        'limit': '20',
        'status': 'active'
    }
    event['rawQueryString'] = 'limit=20&status=active'
    return event


# =========================================================================
# Mock Service Fixtures
# =========================================================================

@pytest.fixture
def mock_access_service():
    """Mock AccessService"""
    service = Mock()
    # Create mock methods directly to avoid 'assert' keyword issues
    service.assert_household_member = Mock(return_value=None)
    service.assert_subject_in_household = Mock(return_value=None)
    return service


@pytest.fixture
def mock_dynamodb_service(mock_dynamodb_client):
    """Mock DynamodbService"""
    service = Mock()
    service.client = mock_dynamodb_client
    service.table_name = 'test-table'
    service.get.return_value = {}
    service.put.return_value = {}
    service.update.return_value = {}
    service.delete.return_value = {}
    service.query.return_value = {'items': [], 'lastEvaluatedKey': None}
    service.scan.return_value = {'items': [], 'lastEvaluatedKey': None}
    return service


# =========================================================================
# Environment Variables
# =========================================================================

@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Set up environment variables for all tests"""
    monkeypatch.setenv('SELF_GROWTH_TABLE', 'test-table')
    monkeypatch.setenv('COGNITO_USER_POOL_ID', 'test-pool-id')
    monkeypatch.setenv('COGNITO_CLIENT_ID', 'test-client-id')
    monkeypatch.setenv('AWS_REGION', 'us-west-1')
    monkeypatch.setenv('ENVIRONMENT', 'test')
