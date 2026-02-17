"""
Unit tests for input sanitization functions.

Tests XSS prevention, HTML stripping, and field validation.
"""

import sys
import os

import pytest
from src.utils.validation import (
    sanitize_html,
    sanitize_string,
    validate_todo_data,
    validate_habit_data,
    validate_user_profile_data,
    Validator,
)
from src.models.errors import ValidationError


class TestHTMLSanitization:
    """Test HTML and XSS sanitization"""

    def test_sanitize_html_removes_script_tags(self):
        """Script tags should be completely removed"""
        input_str = '<script>alert("XSS")</script>Hello World'
        result = sanitize_html(input_str)
        assert 'script' not in result.lower()
        assert 'Hello World' in result

    def test_sanitize_html_removes_style_tags(self):
        """Style tags should be completely removed"""
        input_str = '<style>body{color:red}</style>Hello'
        result = sanitize_html(input_str)
        assert 'style' not in result.lower()
        assert 'Hello' in result

    def test_sanitize_html_strips_all_tags(self):
        """All HTML tags should be stripped"""
        input_str = 'Hello <b>bold</b> <i>italic</i> <a href="#">link</a>'
        result = sanitize_html(input_str)
        assert '<' not in result
        assert '>' not in result
        assert 'Hello bold italic link' in result

    def test_sanitize_html_escapes_special_chars(self):
        """Special characters should be escaped"""
        input_str = 'Test & <test> "quotes"'
        result = sanitize_html(input_str)
        assert '&amp;' in result or '&' in result
        assert '<' not in result
        assert '>' not in result

    def test_sanitize_html_removes_null_bytes(self):
        """Null bytes should be removed"""
        input_str = 'Hello\x00World'
        result = sanitize_html(input_str)
        assert '\x00' not in result
        assert 'HelloWorld' in result


class TestStringSanitization:
    """Test general string sanitization"""

    def test_sanitize_string_strips_whitespace(self):
        """Leading/trailing whitespace should be stripped"""
        input_str = '  Hello World  '
        result = sanitize_string(input_str)
        assert result == 'Hello World'

    def test_sanitize_string_preserves_newlines_when_allowed(self):
        """Newlines should be preserved when allow_newlines=True"""
        input_str = 'Line 1\nLine 2\nLine 3'
        result = sanitize_string(input_str, allow_newlines=True)
        assert '\n' in result
        assert 'Line 1' in result
        assert 'Line 2' in result

    def test_sanitize_string_removes_newlines_when_not_allowed(self):
        """Newlines should be removed when allow_newlines=False"""
        input_str = 'Line 1\nLine 2'
        result = sanitize_string(input_str, allow_newlines=False)
        assert '\n' not in result
        assert 'Line 1 Line 2' in result

    def test_sanitize_string_normalizes_multiple_spaces(self):
        """Multiple spaces should be normalized to single space"""
        input_str = 'Hello    World'
        result = sanitize_string(input_str)
        assert result == 'Hello World'

    def test_sanitize_string_removes_html(self):
        """HTML should be removed from strings"""
        input_str = 'Hello <script>bad()</script> World'
        result = sanitize_string(input_str)
        assert 'script' not in result.lower()
        assert 'Hello World' in result


class TestTodoValidation:
    """Test todo data validation with sanitization"""

    def test_validate_todo_sanitizes_title(self):
        """Todo title should be sanitized"""
        data = {
            'title': '<script>alert(1)</script>Buy milk',
            'difficulty': 'easy'
        }
        result = validate_todo_data(data, is_create=True)
        assert 'script' not in result['title'].lower()
        assert 'Buy milk' in result['title']

    def test_validate_todo_sanitizes_description(self):
        """Todo description should be sanitized"""
        data = {
            'title': 'Buy milk',
            'description': 'Get <b>organic</b> milk',
            'difficulty': 'easy'
        }
        result = validate_todo_data(data, is_create=True)
        assert '<b>' not in result['description']
        assert 'organic' in result['description']

    def test_validate_todo_enforces_max_title_length(self):
        """Todo title should not exceed 200 characters"""
        data = {
            'title': 'A' * 201,
            'difficulty': 'easy'
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_todo_data(data, is_create=True)
        assert 'max_length' in str(exc_info.value.details)

    def test_validate_todo_enforces_max_description_length(self):
        """Todo description should not exceed 1000 characters"""
        data = {
            'title': 'Buy milk',
            'description': 'A' * 1001,
            'difficulty': 'easy'
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_todo_data(data, is_create=True)
        assert 'max_length' in str(exc_info.value.details)


class TestHabitValidation:
    """Test habit data validation with sanitization"""

    def test_validate_habit_sanitizes_title(self):
        """Habit title should be sanitized"""
        data = {
            'title': '<img src=x onerror=alert(1)>Exercise',
            'counter': 'daily'
        }
        result = validate_habit_data(data)
        assert '<img' not in result['title']
        assert 'Exercise' in result['title']

    def test_validate_habit_sanitizes_description(self):
        """Habit description should be sanitized"""
        data = {
            'title': 'Exercise',
            'description': '<style>body{}</style>Daily workout',
            'counter': 'daily'
        }
        result = validate_habit_data(data)
        assert '<style>' not in result['description']
        assert 'Daily workout' in result['description']


class TestUserProfileValidation:
    """Test user profile validation with sanitization"""

    def test_validate_username_sanitizes_input(self):
        """Username should be sanitized"""
        data = {
            'username': '  test_user  ',
            'email': 'test@example.com'
        }
        result = validate_user_profile_data(data)
        assert result['username'] == 'test_user'

    def test_validate_email_sanitizes_input(self):
        """Email should be sanitized and normalized"""
        data = {
            'username': 'testuser',
            'email': '  Test@Example.COM  '
        }
        result = validate_user_profile_data(data)
        assert result['email'] == 'test@example.com'

    def test_validate_email_enforces_max_length(self):
        """Email should not exceed 254 characters"""
        long_email = 'a' * 250 + '@example.com'
        validator = Validator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email(long_email)
        assert 'too long' in str(exc_info.value.message).lower()


class TestFieldLengthLimits:
    """Test that all field length limits are enforced"""

    def test_username_length_limits(self):
        """Username should be 3-20 characters"""
        validator = Validator()
        
        # Too short
        with pytest.raises(ValidationError):
            validator.validate_username('ab')
        
        # Too long
        with pytest.raises(ValidationError):
            validator.validate_username('a' * 21)
        
        # Valid
        assert validator.validate_username('abc') == 'abc'
        assert validator.validate_username('a' * 20) == 'a' * 20

    def test_first_name_length_limits(self):
        """First name should be 1-50 characters"""
        validator = Validator()
        
        # Too long
        with pytest.raises(ValidationError):
            validator.validate_string_length('a' * 51, 'first_name', max_length=50)
        
        # Valid
        result = validator.validate_string_length('John', 'first_name', max_length=50)
        assert result == 'John'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
