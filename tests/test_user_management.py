import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import pytz
from ai_bot.users.user_model import get_user, create_user, update_user_activity, update_user_preferences

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.telegram_id = "12345"
    user.username = "test_user"
    user.first_name = "Test"
    user.last_name = "User"
    user.timezone = "UTC"
    user.notification_time = "09:00"
    user.notification_enabled = True
    return user

def test_get_user(mock_db, mock_user):
    """Test getting a user by Telegram ID"""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    result = get_user(mock_db, "12345")
    
    mock_db.query.assert_called_once()
    mock_db.query.return_value.filter.assert_called_once()
    assert result == mock_user

def test_create_user(mock_db):
    """Test creating a new user"""
    telegram_id = "12345"
    username = "test_user"
    first_name = "Test"
    last_name = "User"
    timezone = "America/New_York"
    
    result = create_user(mock_db, telegram_id, username, first_name, last_name, timezone)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    assert result == mock_db.refresh.call_args[0][0]
    assert result.telegram_id == telegram_id
    assert result.username == username
    assert result.first_name == first_name
    assert result.last_name == last_name
    assert result.timezone == timezone

def test_create_user_invalid_timezone(mock_db):
    """Test creating a user with invalid timezone defaults to UTC"""
    telegram_id = "12345"
    timezone = "Invalid/Timezone"
    
    result = create_user(mock_db, telegram_id, timezone=timezone)
    
    assert result.timezone == "UTC"

def test_update_user_activity(mock_db, mock_user):
    """Test updating user activity"""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    before_time = datetime.utcnow()
    result = update_user_activity(mock_db, "12345")
    after_time = datetime.utcnow()
    
    assert result == mock_user
    assert before_time <= mock_user.last_active <= after_time
    mock_db.commit.assert_called_once()

def test_update_user_activity_nonexistent(mock_db):
    """Test updating activity for nonexistent user"""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = update_user_activity(mock_db, "12345")
    
    assert result is None
    mock_db.commit.assert_not_called()

def test_update_user_preferences(mock_db, mock_user):
    """Test updating user preferences"""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    notification_time = "18:00"
    notification_enabled = False
    timezone = "Europe/London"
    
    result = update_user_preferences(
        mock_db, "12345", 
        notification_time=notification_time,
        notification_enabled=notification_enabled,
        timezone=timezone
    )
    
    assert result == mock_user
    assert result.notification_time == notification_time
    assert result.notification_enabled == notification_enabled
    assert result.timezone == timezone
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_update_user_preferences_invalid_timezone(mock_db, mock_user):
    """Test updating user with invalid timezone keeps original"""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    original_timezone = mock_user.timezone
    
    result = update_user_preferences(mock_db, "12345", timezone="Invalid/Timezone")
    
    assert result.timezone == original_timezone
