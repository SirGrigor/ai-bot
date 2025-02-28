from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    timezone = Column(String, default='UTC')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active = Column(DateTime, default=datetime.datetime.utcnow)
    notification_time = Column(String, default='09:00')  # Time for daily notifications
    notification_enabled = Column(Boolean, default=True)
    
    books = relationship("Book", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    responses = relationship("UserResponse", back_populates="user")

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=True)  # PDF, EPUB, etc.
    total_chapters = Column(Integer, default=0)
    processed_chapters = Column(Integer, default=0)
    processing_status = Column(String, default='pending')  # pending, processing, completed, error
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="books")
    chapters = relationship("Chapter", back_populates="book")
    syntheses = relationship("BookSynthesis", back_populates="book")
    learning_materials = relationship("LearningMaterial", back_populates="book")

class Chapter(Base):
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    chapter_number = Column(Integer)
    title = Column(String, nullable=True)
    content = Column(Text)
    token_count = Column(Integer, default=0)
    position_percentage = Column(Float)  # Position in book (percentage)
    estimated_reading_time = Column(Integer)  # In minutes
    processing_status = Column(String, default='pending')  # pending, processing, completed, error
    
    book = relationship("Book", back_populates="chapters")
    analyses = relationship("ChapterAnalysis", back_populates="chapter")

class ChapterAnalysis(Base):
    __tablename__ = 'chapter_analyses'
    
    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    main_arguments = Column(Text)
    key_concepts = Column(Text)
    supporting_evidence = Column(Text)
    knowledge_graph = Column(Text)  # JSON representation
    terminology = Column(Text)  # JSON list of terms
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    chapter = relationship("Chapter", back_populates="analyses")

class BookSynthesis(Base):
    __tablename__ = 'book_syntheses'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    concept_hierarchy = Column(Text)  # JSON representation
    cross_chapter_themes = Column(Text)
    summary_short = Column(Text)
    summary_medium = Column(Text)
    summary_detailed = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    book = relationship("Book", back_populates="syntheses")

class LearningMaterial(Base):
    __tablename__ = 'learning_materials'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    interval_type = Column(String)  # day1, day3, day7, day30
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    book = relationship("Book", back_populates="learning_materials")

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    completion_percentage = Column(Float, default=0.0)
    current_interval = Column(String)  # day1, day3, day7, day30
    last_interaction = Column(DateTime)
    concept_mastery = Column(Float, default=0.0)  # Percentage of mastered concepts
    
    user = relationship("User", back_populates="progress")

class ScheduledMessage(Base):
    __tablename__ = 'scheduled_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    interval_type = Column(String)  # day1, day3, day7, day30
    scheduled_time = Column(DateTime)
    content_id = Column(Integer)  # ID from the corresponding content table
    status = Column(String, default='pending')  # pending, sent, failed
    
class UserResponse(Base):
    __tablename__ = 'user_responses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    question_id = Column(Integer)
    response_text = Column(Text)
    is_correct = Column(Boolean)
    confidence_score = Column(Float)
    response_time = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="responses")

class TeachingMetric(Base):
    __tablename__ = 'teaching_metrics'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    concept = Column(String)
    explanation = Column(Text)
    clarity_score = Column(Float)
    accuracy_score = Column(Float)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
