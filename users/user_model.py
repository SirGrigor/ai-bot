from sqlalchemy.orm import Session
from ai_bot.database.models import User
from datetime import datetime
import pytz

def get_user(db: Session, telegram_id: str):
    """Get a user by Telegram ID"""
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: str, username: str = None, 
                first_name: str = None, last_name: str = None, timezone: str = 'UTC'):
    """Create a new user"""
    # Validate timezone
    try:
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        timezone = 'UTC'
        
    db_user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        timezone=timezone,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_activity(db: Session, telegram_id: str):
    """Update user's last active timestamp"""
    user = get_user(db, telegram_id)
    if user:
        user.last_active = datetime.utcnow()
        db.commit()
        return user
    return None

def update_user_preferences(db: Session, telegram_id: str, 
                           notification_time: str = None, 
                           notification_enabled: bool = None,
                           timezone: str = None):
    """Update user preferences"""
    user = get_user(db, telegram_id)
    if not user:
        return None
        
    if notification_time is not None:
        user.notification_time = notification_time
        
    if notification_enabled is not None:
        user.notification_enabled = notification_enabled
        
    if timezone is not None:
        try:
            pytz.timezone(timezone)
            user.timezone = timezone
        except pytz.exceptions.UnknownTimeZoneError:
            pass
            
    db.commit()
    db.refresh(user)
    return user
