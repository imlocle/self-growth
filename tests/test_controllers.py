"""
Unit tests for controller layer.
"""

import pytest
from unittest.mock import Mock, patch
import json

from controllers.todo_controller import ToDoController
from controllers.habit_controller import HabitController
from controllers.household_controller import HouseholdController
from utils.request_context import RequestContext
from models.todo import ToDo
from models.habit import Habit
from models.errors import ValidationError, MissingRequiredFieldError


class TestToDoController:
    """Tests for ToDoController"""

    @pytest.fixture
    def todo_controller(self, api_gateway_event_with_path_params):
        """Create ToDoController with mocked service"""
        mock_service = Mock()
        request_context = RequestContext(api_gateway_event_with_path_params)
        return ToDoController(
            event=api_gateway_event_with_path_params,
            request_context=request_context,
            todo_service=mock_service
        )

    def test_create_todo_success(self, todo_controller, test_todo_data):
        """Test successful todo creation"""
        # Set request body
        todo_controller.event['body'] = json.dumps({
            'title': 'Test Todo',
            'difficulty': 'easy'
        })
        todo_controller.request_context._body = None  # Reset cached body
        
        # Mock service response
        mock_todo = Mock(spec=ToDo)
        mock_todo.to_dict.return_value = test_todo_data
        todo_controller.todo_service.create.return_value = mock_todo
        
        result = todo_controller.create()
        
        # Verify service was called
        todo_controller.todo_service.create.assert_called_once()
        assert result == mock_todo

    def test_create_todo_missing_title(self, todo_controller):
        """Test todo creation with missing title"""
        # Set request body without title
        todo_controller.event['body'] = json.dumps({
            'difficulty': 'easy'
        })
        todo_controller.request_context._body = None
        
        # Should raise validation error
        with pytest.raises(MissingRequiredFieldError):
            todo_controller.create()

    def test_create_todo_invalid_difficulty(self, todo_controller):
        """Test todo creation with invalid difficulty"""
        # Set request body with invalid difficulty
        todo_controller.event['body'] = json.dumps({
            'title': 'Test Todo',
            'difficulty': 'invalid'
        })
        todo_controller.request_context._body = None
        
        # Should raise validation error
        with pytest.raises(ValidationError):
            todo_controller.create()

    def test_get_todo(self, todo_controller, test_todo_data):
        """Test getting a todo"""
        # Add todo_id to path parameters
        todo_controller.event['pathParameters']['todoId'] = test_todo_data['id']
        todo_controller.request_context._path_params = None
        
        # Mock service response
        mock_todo = Mock(spec=ToDo)
        mock_todo.to_dict.return_value = test_todo_data
        todo_controller.todo_service.get.return_value = mock_todo
        
        result = todo_controller.get()
        
        # Verify service was called with correct parameters
        todo_controller.todo_service.get.assert_called_once()
        assert result == mock_todo

    def test_get_all_todos(self, todo_controller, test_todo_data):
        """Test getting all todos"""
        # Mock service response
        mock_todo = Mock(spec=ToDo)
        mock_todo.to_dict.return_value = test_todo_data
        todo_controller.todo_service.get_all.return_value = {
            'items': [mock_todo],
            'lastEvaluatedKey': None
        }
        
        result = todo_controller.get_all()
        
        # Verify service was called
        todo_controller.todo_service.get_all.assert_called_once()
        assert 'items' in result
        assert 'nextToken' in result

    def test_update_todo(self, todo_controller, test_todo_data):
        """Test updating a todo"""
        # Add todo_id to path parameters
        todo_controller.event['pathParameters']['todoId'] = test_todo_data['id']
        todo_controller.request_context._path_params = None
        
        # Set request body
        todo_controller.event['body'] = json.dumps({
            'title': 'Updated Title',
            'status': 'completed'
        })
        todo_controller.request_context._body = None
        
        # Mock service response
        mock_todo = Mock(spec=ToDo)
        mock_todo.to_dict.return_value = test_todo_data
        todo_controller.todo_service.update.return_value = mock_todo
        
        result = todo_controller.update()
        
        # Verify service was called
        todo_controller.todo_service.update.assert_called_once()
        assert result == mock_todo

    def test_delete_todo(self, todo_controller, test_todo_data):
        """Test deleting a todo"""
        # Add todo_id to path parameters
        todo_controller.event['pathParameters']['todoId'] = test_todo_data['id']
        todo_controller.request_context._path_params = None
        
        result = todo_controller.delete()
        
        # Verify service was called
        todo_controller.todo_service.delete.assert_called_once()


class TestHabitController:
    """Tests for HabitController"""

    @pytest.fixture
    def habit_controller(self, api_gateway_event_with_path_params):
        """Create HabitController with mocked service"""
        mock_service = Mock()
        request_context = RequestContext(api_gateway_event_with_path_params)
        return HabitController(
            event=api_gateway_event_with_path_params,
            request_context=request_context,
            habit_service=mock_service
        )

    def test_create_habit_success(self, habit_controller, test_habit_data):
        """Test successful habit creation"""
        # Set request body
        habit_controller.event['body'] = json.dumps({
            'title': 'Test Habit',
            'counter': 'daily',
            'type': 'build'
        })
        habit_controller.request_context._body = None
        
        # Mock service response
        mock_habit = Mock(spec=Habit)
        mock_habit.to_dict.return_value = test_habit_data
        habit_controller.habit_service.create.return_value = mock_habit
        
        result = habit_controller.create()
        
        # Verify service was called
        habit_controller.habit_service.create.assert_called_once()
        assert result == mock_habit

    def test_create_habit_invalid_counter(self, habit_controller):
        """Test habit creation with invalid counter"""
        # Set request body with invalid counter
        habit_controller.event['body'] = json.dumps({
            'title': 'Test Habit',
            'counter': 'invalid',
            'type': 'build'
        })
        habit_controller.request_context._body = None
        
        # Should raise validation error
        with pytest.raises(ValidationError):
            habit_controller.create()

    def test_get_habit(self, habit_controller, test_habit_data):
        """Test getting a habit"""
        # Add habit_id to path parameters
        habit_controller.event['pathParameters']['habitId'] = test_habit_data['id']
        habit_controller.request_context._path_params = None
        
        # Mock service response
        mock_habit = Mock(spec=Habit)
        mock_habit.to_dict.return_value = test_habit_data
        habit_controller.habit_service.get.return_value = mock_habit
        
        result = habit_controller.get()
        
        # Verify service was called
        habit_controller.habit_service.get.assert_called_once()
        assert result == mock_habit


class TestHouseholdController:
    """Tests for HouseholdController"""

    @pytest.fixture
    def household_controller(self, api_gateway_event):
        """Create HouseholdController with mocked service"""
        mock_service = Mock()
        request_context = RequestContext(api_gateway_event)
        return HouseholdController(
            event=api_gateway_event,
            request_context=request_context,
            household_service=mock_service
        )

    def test_create_household_success(self, household_controller, test_household_data):
        """Test successful household creation"""
        # Set request body
        household_controller.event['body'] = json.dumps({
            'name': 'Test Household'
        })
        household_controller.request_context._body = None
        
        # Mock service response
        from models.household import Household
        mock_household = Mock(spec=Household)
        mock_household.to_dict.return_value = test_household_data
        household_controller.household_service.create.return_value = mock_household
        
        result = household_controller.create()
        
        # Verify service was called
        household_controller.household_service.create.assert_called_once()
        assert result == mock_household

    def test_create_household_missing_name(self, household_controller):
        """Test household creation with missing name"""
        # Set request body without name
        household_controller.event['body'] = json.dumps({})
        household_controller.request_context._body = None
        
        # Should raise validation error
        with pytest.raises(MissingRequiredFieldError):
            household_controller.create()

    def test_get_household(self, household_controller, test_household_data):
        """Test getting a household"""
        # Add household_id to path parameters
        household_controller.event['pathParameters'] = {
            'householdId': test_household_data['id']
        }
        household_controller.request_context._path_params = None
        
        # Mock service response
        from models.household import Household
        mock_household = Mock(spec=Household)
        mock_household.to_dict.return_value = test_household_data
        household_controller.household_service.get.return_value = mock_household
        
        result = household_controller.get()
        
        # Verify service was called
        household_controller.household_service.get.assert_called_once()
        assert result == mock_household


class TestBaseController:
    """Tests for BaseController"""

    def test_get_pagination_params_default(self, api_gateway_event):
        """Test getting pagination params with defaults"""
        from controllers.base_controller import BaseController
        
        request_context = RequestContext(api_gateway_event)
        controller = BaseController(event=api_gateway_event, request_context=request_context)
        
        params = controller.get_pagination_params()
        
        # Should return empty dict when no params provided
        assert params == {}

    def test_get_pagination_params_with_limit(self, api_gateway_event):
        """Test getting pagination params with limit"""
        from controllers.base_controller import BaseController
        
        # Add query parameters
        api_gateway_event['queryStringParameters'] = {'limit': '20'}
        
        request_context = RequestContext(api_gateway_event)
        controller = BaseController(event=api_gateway_event, request_context=request_context)
        
        params = controller.get_pagination_params()
        
        assert params['limit'] == 20

    def test_get_pagination_params_invalid_limit(self, api_gateway_event):
        """Test getting pagination params with invalid limit"""
        from controllers.base_controller import BaseController
        
        # Add invalid limit
        api_gateway_event['queryStringParameters'] = {'limit': '200'}  # Max is 100
        
        request_context = RequestContext(api_gateway_event)
        controller = BaseController(event=api_gateway_event, request_context=request_context)
        
        # Should raise validation error
        with pytest.raises(ValidationError):
            controller.get_pagination_params()
