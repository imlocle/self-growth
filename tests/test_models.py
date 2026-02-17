"""
Unit tests for domain models.
"""

import pytest
from datetime import datetime

from models.todo import ToDo
from models.habit import Habit
from models.habit_event import HabitEvent
from models.household import Household
from models.household_member import HouseholdMember
from models.household_subject import HouseholdSubject
from models.user_profile import UserProfile
from models.blog_post import BlogPost
from models.errors import ValidationError


class TestToDoModel:
    """Tests for ToDo model"""

    def test_create_todo(self, test_todo_data):
        """Test creating a ToDo instance"""
        todo = ToDo(**test_todo_data)
        
        assert todo.id == test_todo_data['id']
        assert todo.title == test_todo_data['title']
        assert todo.household_id == test_todo_data['household_id']
        assert todo.subject_id == test_todo_data['subject_id']
        assert todo.difficulty == test_todo_data['difficulty']
        assert todo.status == test_todo_data['status']

    def test_todo_to_dict(self, test_todo_data):
        """Test ToDo serialization to dict"""
        todo = ToDo(**test_todo_data)
        result = todo.to_dict()
        
        # to_dict() returns snake_case (camelCase conversion happens in response_util)
        assert result['id'] == test_todo_data['id']
        assert result['title'] == test_todo_data['title']
        assert result['household_id'] == test_todo_data['household_id']
        assert result['subject_id'] == test_todo_data['subject_id']
        assert 'date_created' in result
        assert 'date_modified' in result

    def test_todo_from_dynamo(self, test_todo_data):
        """Test ToDo deserialization from DynamoDB"""
        # DynamoDB items don't have the {'S': ...} wrapper when using from_dynamo
        # The repository handles that conversion
        dynamo_item = {
            'id': test_todo_data['id'],
            'title': test_todo_data['title'],
            'household_id': test_todo_data['household_id'],
            'subject_id': test_todo_data['subject_id'],
            'difficulty': test_todo_data['difficulty'],  # String value, not wrapped
            'status': test_todo_data['status'],
            'date_created': test_todo_data['date_created'],
            'date_modified': test_todo_data['date_modified']
        }
        
        todo = ToDo.from_dynamo(dynamo_item)
        
        assert todo.id == test_todo_data['id']
        assert todo.title == test_todo_data['title']


class TestHabitModel:
    """Tests for Habit model"""

    def test_create_habit(self, test_habit_data):
        """Test creating a Habit instance"""
        habit = Habit(**test_habit_data)
        
        assert habit.id == test_habit_data['id']
        assert habit.title == test_habit_data['title']
        assert habit.counter == test_habit_data['counter']
        assert habit.type == test_habit_data['type']
        assert habit.status == test_habit_data['status']

    def test_habit_to_dict(self, test_habit_data):
        """Test Habit serialization"""
        habit = Habit(**test_habit_data)
        result = habit.to_dict()
        
        # to_dict() returns snake_case with enum values as strings
        assert result['id'] == test_habit_data['id']
        assert result['title'] == test_habit_data['title']
        assert result['counter'] == test_habit_data['counter'].value
        assert result['type'] == test_habit_data['type'].value
        assert result['difficulty'] == test_habit_data['difficulty'].value
        assert result['status'] == test_habit_data['status'].value


class TestHabitEventModel:
    """Tests for HabitEvent model"""

    def test_create_habit_event(self, test_habit_event_data):
        """Test creating a HabitEvent instance"""
        event = HabitEvent(**test_habit_event_data)
        
        assert event.id == test_habit_event_data['id']
        assert event.habit_id == test_habit_event_data['habit_id']
        assert event.period_key == test_habit_event_data['period_key']
        assert event.status == test_habit_event_data['status']

    def test_habit_event_to_dict(self, test_habit_event_data):
        """Test HabitEvent serialization"""
        event = HabitEvent(**test_habit_event_data)
        result = event.to_dict()
        
        # to_dict() returns snake_case with enum values as strings
        assert result['id'] == test_habit_event_data['id']
        assert result['habit_id'] == test_habit_event_data['habit_id']
        assert result['period_key'] == test_habit_event_data['period_key']
        assert result['status'] == test_habit_event_data['status'].value


class TestHouseholdModel:
    """Tests for Household model"""

    def test_create_household(self, test_household_data):
        """Test creating a Household instance"""
        household = Household(**test_household_data)
        
        assert household.id == test_household_data['id']
        assert household.name == test_household_data['name']
        assert household.owner_user_id == test_household_data['owner_user_id']

    def test_household_to_dict(self, test_household_data):
        """Test Household serialization"""
        household = Household(**test_household_data)
        result = household.to_dict()
        
        # to_dict() returns snake_case
        assert result['id'] == test_household_data['id']
        assert result['name'] == test_household_data['name']
        assert result['owner_user_id'] == test_household_data['owner_user_id']


class TestHouseholdSubjectModel:
    """Tests for HouseholdSubject model"""

    def test_create_subject(self, test_subject_data):
        """Test creating a HouseholdSubject instance"""
        subject = HouseholdSubject(**test_subject_data)
        
        assert subject.id == test_subject_data['id']
        assert subject.household_id == test_subject_data['household_id']
        assert subject.type == test_subject_data['type']
        assert subject.display_name == test_subject_data['display_name']

    def test_subject_to_dict(self, test_subject_data):
        """Test HouseholdSubject serialization"""
        subject = HouseholdSubject(**test_subject_data)
        result = subject.to_dict()
        
        # to_dict() returns snake_case
        assert result['id'] == test_subject_data['id']
        assert result['household_id'] == test_subject_data['household_id']
        assert result['type'] == test_subject_data['type']
        assert result['display_name'] == test_subject_data['display_name']


class TestUserProfileModel:
    """Tests for UserProfile model"""

    def test_create_user_profile(self, test_user_data):
        """Test creating a UserProfile instance"""
        profile = UserProfile(**test_user_data)
        
        assert profile.id == test_user_data['id']
        assert profile.username == test_user_data['username']
        assert profile.email == test_user_data['email']

    def test_user_profile_to_dict(self, test_user_data):
        """Test UserProfile serialization"""
        profile = UserProfile(**test_user_data)
        result = profile.to_dict()
        
        assert result['id'] == test_user_data['id']
        assert result['username'] == test_user_data['username']
        assert result['email'] == test_user_data['email']
