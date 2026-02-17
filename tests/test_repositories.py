"""
Unit tests for repository layer.
"""

import pytest
from unittest.mock import Mock

from repositories.todo_repository import ToDoRepository
from repositories.habit_repository import HabitRepository
from repositories.habit_event_repository import HabitEventRepository
from repositories.household_repository import HouseholdRepository
from models.todo import ToDo
from models.habit import Habit
from models.habit_event import HabitEvent
from models.household import Household


class TestToDoRepository:
    """Tests for ToDoRepository"""

    @pytest.fixture
    def todo_repo(self, mock_dynamodb_service):
        """Create ToDoRepository with mocked DynamoDB"""
        return ToDoRepository(dynamodb_service=mock_dynamodb_service)

    def test_create_todo(self, todo_repo, test_todo_data, mock_dynamodb_service):
        """Test creating a todo"""
        todo = ToDo(**test_todo_data)
        
        todo_repo.create(todo)
        
        # Verify put was called
        mock_dynamodb_service.put.assert_called_once()
        call_args = mock_dynamodb_service.put.call_args[0][0]
        assert 'Item' in call_args
        assert call_args['Item']['id'] == test_todo_data['id']

    def test_get_todo(self, todo_repo, test_todo_data, mock_dynamodb_service):
        """Test getting a todo by ID"""
        # Mock DynamoDB response (already unwrapped from DynamoDB format)
        mock_dynamodb_service.get.return_value = {
            'id': test_todo_data['id'],
            'title': test_todo_data['title'],
            'household_id': test_todo_data['household_id'],
            'subject_id': test_todo_data['subject_id'],
            'difficulty': test_todo_data['difficulty'].value,
            'status': test_todo_data['status'].value,
            'date_created': test_todo_data['date_created'],
            'date_modified': test_todo_data['date_modified']
        }
        
        result = todo_repo.get(
            test_todo_data['household_id'],
            test_todo_data['subject_id'],
            test_todo_data['id']
        )
        
        # Verify get was called
        mock_dynamodb_service.get.assert_called_once()
        assert result is not None
        assert result['id'] == test_todo_data['id']

    def test_get_all_todos(self, todo_repo, test_todo_data, mock_dynamodb_service):
        """Test getting all todos for a subject"""
        # Mock DynamoDB query response
        mock_dynamodb_service.query.return_value = {
            'items': [
                {
                    'id': test_todo_data['id'],
                    'title': test_todo_data['title'],
                    'household_id': test_todo_data['household_id'],
                    'subject_id': test_todo_data['subject_id'],
                    'difficulty': test_todo_data['difficulty'].value,
                    'status': test_todo_data['status'].value,
                    'date_created': test_todo_data['date_created'],
                    'date_modified': test_todo_data['date_modified']
                }
            ],
            'lastEvaluatedKey': None
        }
        
        result = todo_repo.get_all(
            test_todo_data['household_id'],
            test_todo_data['subject_id']
        )
        
        # Verify query was called
        mock_dynamodb_service.query.assert_called_once()
        assert 'items' in result
        assert len(result['items']) == 1
        assert result['items'][0]['id'] == test_todo_data['id']

    def test_update_todo(self, todo_repo, test_todo_data, mock_dynamodb_service):
        """Test updating a todo"""
        todo = ToDo(**test_todo_data)
        todo.title = 'Updated Title'
        
        todo_repo.update(todo)
        
        # Verify put was called (update uses put)
        mock_dynamodb_service.put.assert_called_once()
        call_args = mock_dynamodb_service.put.call_args[0][0]
        assert 'Item' in call_args

    def test_delete_todo(self, todo_repo, test_todo_data, mock_dynamodb_service):
        """Test deleting a todo"""
        todo = ToDo(**test_todo_data)
        
        todo_repo.delete(todo)
        
        # Verify delete was called
        mock_dynamodb_service.delete.assert_called_once()
        call_args = mock_dynamodb_service.delete.call_args[0][0]
        assert 'Key' in call_args


class TestHabitRepository:
    """Tests for HabitRepository"""

    @pytest.fixture
    def habit_repo(self, mock_dynamodb_service):
        """Create HabitRepository with mocked DynamoDB"""
        return HabitRepository(dynamodb_service=mock_dynamodb_service)

    def test_create_habit(self, habit_repo, test_habit_data, mock_dynamodb_service):
        """Test creating a habit"""
        habit = Habit(**test_habit_data)
        
        habit_repo.create(habit)
        
        # Verify put was called
        mock_dynamodb_service.put.assert_called_once()
        call_args = mock_dynamodb_service.put.call_args[0][0]
        assert 'Item' in call_args
        assert call_args['Item']['id'] == test_habit_data['id']

    def test_get_habit(self, habit_repo, test_habit_data, mock_dynamodb_service):
        """Test getting a habit by ID"""
        # Mock DynamoDB response
        mock_dynamodb_service.get.return_value = {
            'id': test_habit_data['id'],
            'title': test_habit_data['title'],
            'household_id': test_habit_data['household_id'],
            'subject_id': test_habit_data['subject_id'],
            'counter': test_habit_data['counter'].value,
            'type': test_habit_data['type'].value,
            'status': test_habit_data['status'].value,
            'difficulty': test_habit_data['difficulty'].value,
            'date_created': test_habit_data['date_created'],
            'date_modified': test_habit_data['date_modified']
        }
        
        result = habit_repo.get(
            test_habit_data['household_id'],
            test_habit_data['subject_id'],
            test_habit_data['id']
        )
        
        # Verify get was called
        mock_dynamodb_service.get.assert_called_once()
        assert result is not None
        assert result['id'] == test_habit_data['id']


class TestHabitEventRepository:
    """Tests for HabitEventRepository"""

    @pytest.fixture
    def event_repo(self, mock_dynamodb_service):
        """Create HabitEventRepository with mocked DynamoDB"""
        return HabitEventRepository(dynamodb_service=mock_dynamodb_service)

    def test_create_habit_event(self, event_repo, test_habit_event_data, mock_dynamodb_service):
        """Test creating a habit event"""
        event = HabitEvent(**test_habit_event_data)
        
        event_repo.create(event)
        
        # Verify put was called
        mock_dynamodb_service.put.assert_called_once()
        call_args = mock_dynamodb_service.put.call_args[0][0]
        assert 'Item' in call_args
        assert call_args['Item']['id'] == test_habit_event_data['id']

    def test_get_habit_event(self, event_repo, test_habit_event_data, mock_dynamodb_service):
        """Test getting a habit event by period key"""
        # Mock DynamoDB response
        mock_dynamodb_service.get.return_value = {
            'id': test_habit_event_data['id'],
            'habit_id': test_habit_event_data['habit_id'],
            'household_id': test_habit_event_data['household_id'],
            'subject_id': test_habit_event_data['subject_id'],
            'period_key': test_habit_event_data['period_key'],
            'status': test_habit_event_data['status'].value,
            'date_created': test_habit_event_data['date_created'],
            'date_modified': test_habit_event_data['date_modified']
        }
        
        result = event_repo.get(
            test_habit_event_data['household_id'],
            test_habit_event_data['subject_id'],
            test_habit_event_data['habit_id'],
            test_habit_event_data['period_key']
        )
        
        # Verify get was called
        mock_dynamodb_service.get.assert_called_once()
        assert result is not None
        assert result['period_key'] == test_habit_event_data['period_key']

    def test_get_all_habit_events(self, event_repo, test_habit_event_data, mock_dynamodb_service):
        """Test getting all events for a habit"""
        # Mock DynamoDB query response
        mock_dynamodb_service.query.return_value = {
            'items': [
                {
                    'id': test_habit_event_data['id'],
                    'habit_id': test_habit_event_data['habit_id'],
                    'household_id': test_habit_event_data['household_id'],
                    'subject_id': test_habit_event_data['subject_id'],
                    'period_key': test_habit_event_data['period_key'],
                    'status': test_habit_event_data['status'].value,
                    'date_created': test_habit_event_data['date_created'],
                    'date_modified': test_habit_event_data['date_modified']
                }
            ],
            'lastEvaluatedKey': None
        }
        
        result = event_repo.get_all(
            test_habit_event_data['household_id'],
            test_habit_event_data['subject_id'],
            test_habit_event_data['habit_id']
        )
        
        # Verify query was called
        mock_dynamodb_service.query.assert_called_once()
        assert 'items' in result
        assert len(result['items']) == 1


class TestHouseholdRepository:
    """Tests for HouseholdRepository"""

    @pytest.fixture
    def household_repo(self, mock_dynamodb_service):
        """Create HouseholdRepository with mocked DynamoDB"""
        return HouseholdRepository(dynamodb_service=mock_dynamodb_service)

    def test_create_household(self, household_repo, test_household_data, mock_dynamodb_service):
        """Test creating a household"""
        household = Household(**test_household_data)
        
        household_repo.create(household)
        
        # Verify put was called
        mock_dynamodb_service.put.assert_called_once()
        call_args = mock_dynamodb_service.put.call_args[0][0]
        assert 'Item' in call_args
        assert call_args['Item']['id'] == test_household_data['id']

    def test_get_household(self, household_repo, test_household_data, mock_dynamodb_service):
        """Test getting a household by ID"""
        # Mock DynamoDB response
        mock_dynamodb_service.get.return_value = {
            'id': test_household_data['id'],
            'name': test_household_data['name'],
            'owner_user_id': test_household_data['owner_user_id'],
            'date_created': test_household_data['date_created'],
            'date_modified': test_household_data['date_modified']
        }
        
        result = household_repo.get(test_household_data['id'])
        
        # Verify get was called
        mock_dynamodb_service.get.assert_called_once()
        assert result is not None
        assert result['id'] == test_household_data['id']
