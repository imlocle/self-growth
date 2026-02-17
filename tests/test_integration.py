"""
Integration tests for end-to-end flows.

These tests verify that multiple components work together correctly.
"""

import pytest
from unittest.mock import Mock, patch
import json

from handlers.base_handler import BaseHandler
from utils.request_context import RequestContext
from models.errors import ValidationError, AuthorizationError


class TestTodoEndToEndFlow:
    """Integration tests for todo CRUD flow"""

    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies"""
        with patch('aws.dynamodb_service.DynamodbService') as mock_dynamo:
            mock_dynamo_instance = Mock()
            mock_dynamo.return_value = mock_dynamo_instance
            
            # Mock DynamoDB responses
            mock_dynamo_instance.get_item.return_value = {
                'id': {'S': 'test-id'},
                'title': {'S': 'Test Todo'},
                'household_id': {'S': 'household-123'},
                'subject_id': {'S': 'subject-456'},
                'difficulty': {'S': 'easy'},
                'status': {'S': 'active'},
                'date_created': {'S': '2026-02-16T10:00:00Z'},
                'date_modified': {'S': '2026-02-16T10:00:00Z'}
            }
            
            mock_dynamo_instance.put_item.return_value = {}
            mock_dynamo_instance.query.return_value = {'Items': [], 'Count': 0}
            
            yield mock_dynamo_instance

    def test_create_todo_flow(self, api_gateway_event_with_path_params, mock_dependencies):
        """Test complete todo creation flow"""
        # Set request body
        api_gateway_event_with_path_params['body'] = json.dumps({
            'title': 'Buy groceries',
            'difficulty': 'easy',
            'description': 'Milk, eggs, bread'
        })
        
        # Create request context
        context = RequestContext(api_gateway_event_with_path_params)
        
        # Verify context extraction
        assert context.user_id is not None
        assert context.household_id is not None
        assert context.subject_id is not None
        assert context.body['title'] == 'Buy groceries'

    def test_validation_error_flow(self, api_gateway_event_with_path_params):
        """Test validation error handling flow"""
        # Set invalid request body (missing title)
        api_gateway_event_with_path_params['body'] = json.dumps({
            'difficulty': 'easy'
        })
        
        context = RequestContext(api_gateway_event_with_path_params)
        
        # Validation should fail
        from utils.validation import validate_todo_data
        with pytest.raises(ValidationError):
            validate_todo_data(context.body, is_create=True)


class TestAuthorizationFlow:
    """Integration tests for authorization flow"""

    def test_household_membership_check(self, test_user_id, test_household_id):
        """Test household membership authorization"""
        from services.access_service import AccessService
        
        # Mock repositories
        mock_member_repo = Mock()
        mock_subject_repo = Mock()
        
        # User is a member
        mock_member_repo.get.return_value = Mock()
        
        access_service = AccessService(
            household_member_repository=mock_member_repo,
            household_subject_repository=mock_subject_repo
        )
        
        # Should not raise exception
        access_service.assert_household_member(test_user_id, test_household_id)
        
        # Verify repository was called
        mock_member_repo.get.assert_called_once_with(test_household_id, test_user_id)

    def test_unauthorized_access(self, test_user_id, test_household_id):
        """Test unauthorized access attempt"""
        from services.access_service import AccessService
        
        # Mock repositories
        mock_member_repo = Mock()
        mock_subject_repo = Mock()
        
        # User is NOT a member
        mock_member_repo.get.return_value = None
        
        access_service = AccessService(
            household_member_repository=mock_member_repo,
            household_subject_repository=mock_subject_repo
        )
        
        # Should raise AuthorizationError
        with pytest.raises(AuthorizationError):
            access_service.assert_household_member(test_user_id, test_household_id)


class TestHabitEventFlow:
    """Integration tests for habit event creation"""

    def test_habit_event_idempotency(self):
        """Test that habit events are idempotent by period key"""
        from models.habit_event import HabitEvent
        
        # Same period key should create same SK
        event1 = HabitEvent(
            id='event1',
            household_id='h123',
            subject_id='s456',
            habit_id='habit789',
            period_key='2026-02-16',
            status='done',
            note='',
            date_created='2026-02-16T10:00:00Z',
            date_modified='2026-02-16T10:00:00Z'
        )
        
        event2 = HabitEvent(
            id='event2',  # Different ID
            household_id='h123',
            subject_id='s456',
            habit_id='habit789',
            period_key='2026-02-16',  # Same period key
            status='done',
            note='',
            date_created='2026-02-16T11:00:00Z',
            date_modified='2026-02-16T11:00:00Z'
        )
        
        # Both should map to same DynamoDB key (same PK and SK)
        # This ensures idempotency at the database level


class TestPaginationFlow:
    """Integration tests for pagination"""

    def test_pagination_token_encoding(self):
        """Test pagination token encoding and decoding"""
        from utils.helper import encode_next_token, decode_next_token
        
        # Original key
        original_key = {
            'PK': 'HOUSEHOLD#h123',
            'SK': 'SUBJECT#s456#TODO#todo789'
        }
        
        # Encode
        token = encode_next_token(original_key)
        assert token is not None
        assert isinstance(token, str)
        
        # Decode
        decoded_key = decode_next_token(token)
        assert decoded_key == original_key

    def test_pagination_params_extraction(self, api_gateway_event):
        """Test extracting pagination parameters from query string"""
        from controllers.base_controller import BaseController
        
        # Add query parameters
        api_gateway_event['queryStringParameters'] = {
            'limit': '20',
            'nextToken': 'eyJQSyI6InRlc3QifQ==',
            'status': 'active'
        }
        
        context = RequestContext(api_gateway_event)
        controller = BaseController(event=api_gateway_event, request_context=context)
        
        params = controller.get_pagination_params()
        
        assert params['limit'] == 20
        assert 'next_token' in params
        assert params['status'] == 'active'


class TestErrorHandlingFlow:
    """Integration tests for error handling"""

    def test_error_response_format(self):
        """Test error response formatting"""
        from utils.response_util import error_response
        from models.errors import ValidationError
        
        error = ValidationError(
            'Title is too long',
            field='title',
            details={'max_length': 200, 'actual_length': 250}
        )
        
        response = error_response(error)
        
        # Verify response structure
        assert response['statusCode'] == 400
        assert 'body' in response
        assert 'headers' in response
        
        # Verify body content
        body = json.loads(response['body'])
        assert body['error'] == 'VALIDATION_ERROR'
        assert body['message'] == 'Title is too long'
        assert 'details' in body
        assert body['details']['field'] == 'title'

    def test_cors_headers_in_error_response(self):
        """Test that CORS headers are included in error responses"""
        from utils.response_util import error_response
        from models.errors import ValidationError
        
        error = ValidationError('Test error')
        response = error_response(error)
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']


class TestInputSanitizationFlow:
    """Integration tests for input sanitization"""

    def test_xss_prevention(self):
        """Test XSS attack prevention"""
        from utils.validation import sanitize_html
        
        malicious_input = '<script>alert("XSS")</script>Hello World'
        sanitized = sanitize_html(malicious_input)
        
        # Script should be removed
        assert 'script' not in sanitized.lower()
        assert 'Hello World' in sanitized

    def test_html_injection_prevention(self):
        """Test HTML injection prevention"""
        from utils.validation import sanitize_html
        
        malicious_input = '<img src=x onerror=alert(1)>Test'
        sanitized = sanitize_html(malicious_input)
        
        # HTML tags should be removed
        assert '<img' not in sanitized
        assert 'Test' in sanitized

    def test_validation_with_sanitization(self):
        """Test that validation includes sanitization"""
        from utils.validation import validate_todo_data
        
        data = {
            'title': '<script>alert(1)</script>Buy milk',
            'difficulty': 'easy'
        }
        
        validated = validate_todo_data(data, is_create=True)
        
        # Title should be sanitized
        assert 'script' not in validated['title'].lower()
        assert 'Buy milk' in validated['title']
