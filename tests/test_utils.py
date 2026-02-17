"""
Unit tests for utility functions.
"""

import pytest
import json
from datetime import datetime

from utils.request_context import RequestContext
from utils.helper import generate_id, encode_next_token, decode_next_token
from utils.response_util import success_response, error_response
from models.errors import ValidationError, MissingRequiredFieldError


class TestRequestContext:
    """Tests for RequestContext"""

    def test_extract_user_id(self, api_gateway_event, test_user_id):
        """Test extracting user ID from JWT claims"""
        context = RequestContext(api_gateway_event)
        
        assert context.user_id == test_user_id

    def test_extract_path_parameters(self, api_gateway_event_with_path_params, test_household_id, test_subject_id):
        """Test extracting path parameters"""
        context = RequestContext(api_gateway_event_with_path_params)
        
        assert context.household_id == test_household_id
        assert context.subject_id == test_subject_id

    def test_extract_query_parameters(self, api_gateway_event_with_query_params):
        """Test extracting query parameters"""
        context = RequestContext(api_gateway_event_with_query_params)
        
        assert context.get_query_param('limit') == '20'
        assert context.get_query_param('status') == 'active'

    def test_extract_body(self, api_gateway_event):
        """Test extracting request body"""
        body_data = {'title': 'Test', 'description': 'Test description'}
        api_gateway_event['body'] = json.dumps(body_data)
        
        context = RequestContext(api_gateway_event)
        
        assert context.body == body_data

    def test_require_auth_success(self, api_gateway_event, test_user_id):
        """Test requiring authentication with valid token"""
        context = RequestContext(api_gateway_event)
        
        auth_user = context.require_auth()
        
        assert auth_user.user_id == test_user_id
        assert auth_user.email == 'test@example.com'

    def test_require_auth_missing(self, api_gateway_event):
        """Test requiring authentication without token"""
        # Remove authorizer from event
        del api_gateway_event['requestContext']['authorizer']
        
        context = RequestContext(api_gateway_event)
        
        # Should raise error
        from models.errors import AuthenticationError
        with pytest.raises(AuthenticationError):
            context.require_auth()

    def test_require_household_id_success(self, api_gateway_event_with_path_params, test_household_id):
        """Test requiring household ID"""
        context = RequestContext(api_gateway_event_with_path_params)
        
        household_id = context.require_household_id()
        
        assert household_id == test_household_id

    def test_require_household_id_missing(self, api_gateway_event):
        """Test requiring household ID when missing"""
        context = RequestContext(api_gateway_event)
        
        # Should raise error
        with pytest.raises(MissingRequiredFieldError):
            context.require_household_id()

    def test_require_subject_id_success(self, api_gateway_event_with_path_params, test_subject_id):
        """Test requiring subject ID"""
        context = RequestContext(api_gateway_event_with_path_params)
        
        subject_id = context.require_subject_id()
        
        assert subject_id == test_subject_id

    def test_require_subject_id_missing(self, api_gateway_event):
        """Test requiring subject ID when missing"""
        context = RequestContext(api_gateway_event)
        
        # Should raise error
        with pytest.raises(MissingRequiredFieldError):
            context.require_subject_id()


class TestHelperFunctions:
    """Tests for helper functions"""

    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id()
        id2 = generate_id()
        
        # IDs should be unique
        assert id1 != id2
        
        # IDs should be strings
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        
        # IDs should have reasonable length
        assert len(id1) > 10

    def test_encode_decode_next_token(self):
        """Test encoding and decoding pagination tokens"""
        original_key = {'PK': 'test-pk', 'SK': 'test-sk'}
        
        # Encode
        token = encode_next_token(original_key)
        
        # Should be a string
        assert isinstance(token, str)
        
        # Decode
        decoded_key = decode_next_token(token)
        
        # Should match original
        assert decoded_key == original_key

    def test_encode_next_token_none(self):
        """Test encoding None as next token"""
        token = encode_next_token(None)
        
        # Should return None
        assert token is None

    def test_decode_next_token_none(self):
        """Test decoding None next token"""
        key = decode_next_token(None)
        
        # Should return None
        assert key is None


class TestResponseUtil:
    """Tests for response utility functions"""

    def test_success_response(self):
        """Test creating success response"""
        data = {'id': '123', 'title': 'Test'}
        
        response = success_response(data, status_code=200)
        
        assert response['statusCode'] == 200
        assert 'body' in response
        assert 'headers' in response
        
        # Body should be JSON string
        body = json.loads(response['body'])
        assert body == data

    def test_success_response_with_custom_status(self):
        """Test creating success response with custom status code"""
        data = {'id': '123'}
        
        response = success_response(data, status_code=201)
        
        assert response['statusCode'] == 201

    def test_error_response(self):
        """Test creating error response"""
        error = ValidationError('Invalid input', field='title')
        
        response = error_response(error)
        
        assert response['statusCode'] == 400
        assert 'body' in response
        assert 'headers' in response
        
        # Body should contain error details
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'message' in body
        assert body['error'] == 'VALIDATION_ERROR'

    def test_error_response_with_details(self):
        """Test creating error response with details"""
        error = ValidationError(
            'Field too long',
            field='title',
            details={'max_length': 200, 'actual_length': 250}
        )
        
        response = error_response(error)
        
        body = json.loads(response['body'])
        assert 'details' in body
        assert body['details']['max_length'] == 200

    def test_cors_headers_in_response(self):
        """Test that CORS headers are included in responses"""
        data = {'test': 'data'}
        
        response = success_response(data)
        
        # Should have CORS headers
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']
        assert 'Access-Control-Allow-Headers' in response['headers']


class TestErrorModels:
    """Tests for error models"""

    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError('Invalid input', field='title', value='test')
        
        assert error.message == 'Invalid input'
        assert error.http_status == 400
        assert error.details['field'] == 'title'

    def test_missing_required_field_error(self):
        """Test MissingRequiredFieldError"""
        error = MissingRequiredFieldError('title')
        
        assert 'title' in error.message
        assert error.http_status == 400
        assert error.details['field'] == 'title'

    def test_authorization_error(self):
        """Test AuthorizationError"""
        from models.errors import AuthorizationError
        
        error = AuthorizationError('Access denied', user_id='user123', resource='household')
        
        assert error.message == 'Access denied'
        assert error.http_status == 403
        assert error.details['user_id'] == 'user123'

    def test_not_found_error(self):
        """Test NotFoundError"""
        from models.errors import NotFoundError
        
        error = NotFoundError('Resource not found', resource_type='todo', resource_id='123')
        
        assert error.message == 'Resource not found'
        assert error.http_status == 404
        assert error.details['resource_type'] == 'todo'

    def test_error_to_dict(self):
        """Test error serialization to dict"""
        error = ValidationError('Invalid input', field='title')
        
        error_dict = error.to_dict()
        
        assert 'error' in error_dict
        assert 'message' in error_dict
        assert 'details' in error_dict
        assert error_dict['error'] == 'VALIDATION_ERROR'

    def test_error_to_json(self):
        """Test error serialization to JSON"""
        error = ValidationError('Invalid input', field='title')
        
        error_json = error.to_json()
        
        # Should be valid JSON
        parsed = json.loads(error_json)
        assert parsed['error'] == 'VALIDATION_ERROR'
