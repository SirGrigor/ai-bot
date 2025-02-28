from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path

# Create data directory if it doesn't exist
data_dir = Path(__file__).parent.parent.parent / 'data'
data_dir.mkdir(exist_ok=True)

# Database file path
DB_PATH = os.path.join(data_dir, 'book_retention.db')
DB_URL = f'sqlite:///{DB_PATH}'

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Import all models here to ensure they are registered with Base
    from ai_bot.database.models import User, Book, Chapter, ChapterAnalysis, BookSynthesis, LearningMaterial, UserProgress, ScheduledMessage, UserResponse, TeachingMetric
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
