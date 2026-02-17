"""
Unit tests for service layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.todo_service import ToDoService
from services.habit_service import HabitService
from services.habit_event_service import HabitEventService
from services.habit_analytics_service import HabitAnalyticsService
from services.household_service import HouseholdService
from services.access_service import AccessService
from models.todo import ToDo
from models.habit import Habit
from models.habit_event import HabitEvent
from models.errors import AuthorizationError, NotFoundError


class TestAccessService:
    """Tests for AccessService"""

    @pytest.fixture
    def access_service(self):
        """Create AccessService with mocked repository"""
        mock_member_repo = Mock()
        mock_subject_repo = Mock()
        return AccessService(
            member_repo=mock_member_repo,
            subject_repo=mock_subject_repo
        )

    def test_assert_household_member_success(self, access_service, test_user_id, test_household_id):
        """Test successful household membership validation"""
        # Mock member exists
        access_service.member_repo.get.return_value = Mock()
        
        # Should not raise exception
        access_service.assert_household_member(test_user_id, test_household_id)
        
        # Verify get was called
        access_service.member_repo.get.assert_called_once_with(
            household_id=test_household_id, user_id=test_user_id
        )

    def test_assert_household_member_failure(self, access_service, test_user_id, test_household_id):
        """Test household membership validation failure"""
        from models.errors import HouseholdMembershipError
        # Mock member does not exist
        access_service.member_repo.get.return_value = None
        
        # Should raise HouseholdMembershipError
        with pytest.raises(HouseholdMembershipError):
            access_service.assert_household_member(test_user_id, test_household_id)

    def test_assert_subject_in_household_success(self, access_service, test_household_id, test_subject_id):
        """Test successful subject validation"""
        # Mock subject exists
        access_service.subject_repo.get.return_value = Mock()
        
        # Should not raise exception
        access_service.assert_subject_in_household(test_household_id, test_subject_id)

    def test_assert_subject_in_household_failure(self, access_service, test_household_id, test_subject_id):
        """Test subject validation failure"""
        from models.errors import SubjectNotFoundError
        # Mock subject does not exist
        access_service.subject_repo.get.return_value = None
        
        # Should raise SubjectNotFoundError
        with pytest.raises(SubjectNotFoundError):
            access_service.assert_subject_in_household(test_household_id, test_subject_id)


class TestToDoService:
    """Tests for ToDoService"""

    @pytest.fixture
    def todo_service(self, mock_access_service):
        """Create ToDoService with mocked dependencies"""
        mock_repo = Mock()
        return ToDoService(
            todo_repo=mock_repo,
            access_service=mock_access_service
        )

    def test_create_todo(self, todo_service, test_user_id, test_household_id, test_subject_id):
        """Test creating a todo"""
        data = {
            'title': 'Test Todo',
            'difficulty': 'easy',
            'status': 'active'
        }
        
        # Mock repository create (returns None, modifies object in place)
        todo_service.todo_repo.create.return_value = None
        
        result = todo_service.create(test_user_id, test_household_id, test_subject_id, data)
        
        # Verify authorization was checked
        todo_service.access.assert_household_member.assert_called_once_with(
            user_id=test_user_id, household_id=test_household_id
        )
        todo_service.access.assert_subject_in_household.assert_called_once_with(
            household_id=test_household_id, subject_id=test_subject_id
        )
        
        # Verify repository create was called
        todo_service.todo_repo.create.assert_called_once()
        assert isinstance(result, ToDo)

    def test_get_todo(self, todo_service, test_user_id, test_household_id, test_subject_id, test_todo_id, test_todo_data):
        """Test getting a todo"""
        # Mock repository response (returns dict from DynamoDB)
        todo_service.todo_repo.get.return_value = {
            'id': test_todo_id,
            'title': 'Test Todo',
            'household_id': test_household_id,
            'subject_id': test_subject_id,
            'difficulty': 'easy',
            'status': 'active',
            'date_created': test_todo_data['date_created'],
            'date_modified': test_todo_data['date_modified']
        }
        
        result = todo_service.get(test_user_id, test_household_id, test_subject_id, test_todo_id)
        
        # Verify authorization was checked
        todo_service.access.assert_household_member.assert_called_once()
        
        # Verify repository get was called
        todo_service.todo_repo.get.assert_called_once_with(
            household_id=test_household_id, subject_id=test_subject_id, todo_id=test_todo_id
        )
        assert isinstance(result, ToDo)

    def test_get_all_todos(self, todo_service, test_user_id, test_household_id, test_subject_id, test_todo_data):
        """Test getting all todos"""
        # Mock repository response
        todo_service.todo_repo.get_all.return_value = {
            'items': [{
                'id': test_todo_data['id'],
                'title': 'Test Todo',
                'household_id': test_household_id,
                'subject_id': test_subject_id,
                'difficulty': 'easy',
                'status': 'active',
                'date_created': test_todo_data['date_created'],
                'date_modified': test_todo_data['date_modified']
            }],
            'lastEvaluatedKey': None
        }
        
        result = todo_service.get_all(test_user_id, test_household_id, test_subject_id)
        
        # Verify authorization was checked
        todo_service.access.assert_household_member.assert_called_once()
        
        # Verify repository get_all was called
        todo_service.todo_repo.get_all.assert_called_once()
        assert 'items' in result
        assert len(result['items']) == 1

    def test_update_todo(self, todo_service, test_user_id, test_household_id, test_subject_id, test_todo_id, test_todo_data):
        """Test updating a todo"""
        data = {'title': 'Updated Title'}
        
        # Mock get to return existing todo
        todo_service.todo_repo.get.return_value = {
            'id': test_todo_id,
            'title': 'Test Todo',
            'household_id': test_household_id,
            'subject_id': test_subject_id,
            'difficulty': 'easy',
            'status': 'active',
            'date_created': test_todo_data['date_created'],
            'date_modified': test_todo_data['date_modified']
        }
        
        # Mock update (returns None)
        todo_service.todo_repo.update.return_value = None
        
        result = todo_service.update(test_user_id, test_household_id, test_subject_id, test_todo_id, data)
        
        # Verify authorization was checked
        todo_service.access.assert_household_member.assert_called_once()
        
        # Verify repository update was called
        todo_service.todo_repo.update.assert_called_once()
        assert isinstance(result, ToDo)

    def test_delete_todo(self, todo_service, test_user_id, test_household_id, test_subject_id, test_todo_id, test_todo_data):
        """Test deleting a todo (soft delete)"""
        # Mock get to return existing todo
        todo_service.todo_repo.get.return_value = {
            'id': test_todo_id,
            'title': 'Test Todo',
            'household_id': test_household_id,
            'subject_id': test_subject_id,
            'difficulty': 'easy',
            'status': 'active',
            'date_created': test_todo_data['date_created'],
            'date_modified': test_todo_data['date_modified']
        }
        
        # Mock update (soft delete uses update)
        todo_service.todo_repo.update.return_value = None
        
        result = todo_service.delete(test_user_id, test_household_id, test_subject_id, test_todo_id)
        
        # Verify authorization was checked
        todo_service.access.assert_household_member.assert_called_once()
        
        # Verify repository update was called (soft delete)
        todo_service.todo_repo.update.assert_called_once()
        assert result is None


class TestHabitService:
    """Tests for HabitService"""

    @pytest.fixture
    def habit_service(self, mock_access_service):
        """Create HabitService with mocked dependencies"""
        mock_repo = Mock()
        return HabitService(
            habit_repo=mock_repo,
            access_service=mock_access_service
        )

    def test_create_habit(self, habit_service, test_user_id, test_household_id, test_subject_id):
        """Test creating a habit"""
        from models.enum import HabitCounterEnum, HabitTypeEnum, HabitStatusEnum, DifficultyEnum
        data = {
            'title': 'Test Habit',
            'counter': HabitCounterEnum.DAILY,
            'type': HabitTypeEnum.BUILD,
            'status': HabitStatusEnum.ACTIVE,
            'difficulty': DifficultyEnum.EASY
        }
        
        # Mock repository create (returns None)
        habit_service.habit_repo.create.return_value = None
        
        result = habit_service.create(test_user_id, test_household_id, test_subject_id, data)
        
        # Verify authorization was checked
        habit_service.access.assert_household_member.assert_called_once()
        habit_service.access.assert_subject_in_household.assert_called_once()
        
        # Verify repository create was called
        habit_service.habit_repo.create.assert_called_once()
        assert isinstance(result, Habit)

    def test_get_habit(self, habit_service, test_user_id, test_household_id, test_subject_id, test_habit_id, test_habit_data):
        """Test getting a habit"""
        # Mock repository response (returns dict from DynamoDB)
        habit_service.habit_repo.get.return_value = {
            'id': test_habit_id,
            'title': 'Test Habit',
            'household_id': test_household_id,
            'subject_id': test_subject_id,
            'counter': 'daily',
            'type': 'build',
            'status': 'active',
            'difficulty': 'easy',
            'date_created': test_habit_data['date_created'],
            'date_modified': test_habit_data['date_modified']
        }
        
        result = habit_service.get(test_user_id, test_household_id, test_subject_id, test_habit_id)
        
        # Verify authorization was checked
        habit_service.access.assert_household_member.assert_called_once()
        
        # Verify repository get was called
        habit_service.habit_repo.get.assert_called_once()
        assert isinstance(result, Habit)


class TestHabitEventService:
    """Tests for HabitEventService"""

    @pytest.fixture
    def event_service(self, mock_access_service):
        """Create HabitEventService with mocked dependencies"""
        mock_event_repo = Mock()
        mock_habit_repo = Mock()
        return HabitEventService(
            event_repo=mock_event_repo,
            habit_repo=mock_habit_repo,
            access_service=mock_access_service
        )

    def test_create_habit_event(self, event_service, test_user_id, test_household_id, test_subject_id, test_habit_id, test_habit_data):
        """Test creating a habit event"""
        from models.enum import HabitEventStatusEnum
        data = {
            'status': HabitEventStatusEnum.DONE,
            'note': 'Completed successfully'
        }
        
        # Mock habit exists
        event_service.habit_repo.get.return_value = {
            'id': test_habit_id,
            'title': 'Test Habit',
            'household_id': test_household_id,
            'subject_id': test_subject_id,
            'counter': 'daily',
            'type': 'build',
            'status': 'active',
            'difficulty': 'easy',
            'date_created': test_habit_data['date_created'],
            'date_modified': test_habit_data['date_modified']
        }
        
        # Mock event creation
        event_service.event_repo.create.return_value = None
        
        result = event_service.create(test_user_id, test_household_id, test_subject_id, test_habit_id, data)
        
        # Verify authorization was checked
        event_service.access.assert_household_member.assert_called_once()
        
        # Verify habit was fetched
        event_service.habit_repo.get.assert_called_once()
        
        # Verify event was created
        event_service.event_repo.create.assert_called_once()
        assert isinstance(result, HabitEvent)

class TestHabitAnalyticsService:
    """Tests for HabitAnalyticsService - Skipped for now"""
    pass


class TestHouseholdService:
    """Tests for HouseholdService - Skipped for now"""
    pass
