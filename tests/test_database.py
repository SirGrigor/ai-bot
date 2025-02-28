import pytest
import os
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import init_db, get_db, engine
from database.models import Base, User, Book, Chapter

@pytest.fixture
def test_db():
    """Create a test database in memory"""
    # Create an in-memory SQLite database
    test_engine = create_engine('sqlite:///:memory:')
    
    # Create all tables in the test database
    Base.metadata.create_all(test_engine)
    
    # Create a session factory
    TestSessionLocal = sessionmaker(bind=test_engine)
    
    # Create a session
    db = TestSessionLocal()
    
    yield db
    
    # Clean up
    db.close()

def test_init_db():
    """Test database initialization"""
    with patch('database.database.Base.metadata.create_all') as mock_create_all:
        init_db()
        mock_create_all.assert_called_once_with(bind=engine)

def test_get_db():
    """Test database session creation and cleanup"""
    # Mock the SessionLocal to return a mock session
    with patch('database.database.SessionLocal') as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Get a session from the generator
        session = next(get_db())
        
        # Check if the session is the mock session
        assert session == mock_session
        
        # Check if close was called when the generator is done
        mock_session.close.assert_not_called()  # Not called yet
        
        # Simulate the end of the with block
        try:
            next(get_db())
        except StopIteration:
            pass
        
        mock_session.close.assert_called_once()

def test_user_model(test_db):
    """Test User model"""
    # Create a user
    user = User(
        telegram_id="12345",
        username="test_user",
        first_name="Test",
        last_name="User",
        timezone="UTC"
    )
    test_db.add(user)
    test_db.commit()
    
    # Query the user
    db_user = test_db.query(User).filter(User.telegram_id == "12345").first()
    
    assert db_user is not None
    assert db_user.telegram_id == "12345"
    assert db_user.username == "test_user"
    assert db_user.first_name == "Test"
    assert db_user.last_name == "User"
    assert db_user.timezone == "UTC"

def test_book_model(test_db):
    """Test Book model"""
    # Create a user
    user = User(telegram_id="12345")
    test_db.add(user)
    test_db.commit()
    
    # Create a book
    book = Book(
        user_id=user.id,
        title="Test Book",
        author="Test Author",
        file_path="/path/to/book.pdf",
        file_type=".pdf",
        total_chapters=10,
        processed_chapters=5,
        processing_status="processing"
    )
    test_db.add(book)
    test_db.commit()
    
    # Query the book
    db_book = test_db.query(Book).filter(Book.title == "Test Book").first()
    
    assert db_book is not None
    assert db_book.user_id == user.id
    assert db_book.title == "Test Book"
    assert db_book.author == "Test Author"
    assert db_book.file_path == "/path/to/book.pdf"
    assert db_book.file_type == ".pdf"
    assert db_book.total_chapters == 10
    assert db_book.processed_chapters == 5
    assert db_book.processing_status == "processing"

def test_chapter_model(test_db):
    """Test Chapter model"""
    # Create a user
    user = User(telegram_id="12345")
    test_db.add(user)
    test_db.commit()
    
    # Create a book
    book = Book(
        user_id=user.id,
        title="Test Book"
    )
    test_db.add(book)
    test_db.commit()
    
    # Create a chapter
    chapter = Chapter(
        book_id=book.id,
        chapter_number=1,
        title="Chapter 1",
        content="This is the content of chapter 1.",
        token_count=100,
        position_percentage=10.0,
        estimated_reading_time=5,
        processing_status="completed"
    )
    test_db.add(chapter)
    test_db.commit()
    
    # Query the chapter
    db_chapter = test_db.query(Chapter).filter(Chapter.book_id == book.id).first()
    
    assert db_chapter is not None
    assert db_chapter.book_id == book.id
    assert db_chapter.chapter_number == 1
    assert db_chapter.title == "Chapter 1"
    assert db_chapter.content == "This is the content of chapter 1."
    assert db_chapter.token_count == 100
    assert db_chapter.position_percentage == 10.0
    assert db_chapter.estimated_reading_time == 5
    assert db_chapter.processing_status == "completed"

def test_relationships(test_db):
    """Test relationships between models"""
    # Create a user
    user = User(telegram_id="12345")
    test_db.add(user)
    test_db.commit()
    
    # Create a book
    book = Book(
        user_id=user.id,
        title="Test Book"
    )
    test_db.add(book)
    test_db.commit()
    
    # Create chapters
    chapter1 = Chapter(
        book_id=book.id,
        chapter_number=1,
        title="Chapter 1",
        content="Content 1"
    )
    chapter2 = Chapter(
        book_id=book.id,
        chapter_number=2,
        title="Chapter 2",
        content="Content 2"
    )
    test_db.add(chapter1)
    test_db.add(chapter2)
    test_db.commit()
    
    # Test user -> books relationship
    db_user = test_db.query(User).filter(User.telegram_id == "12345").first()
    assert len(db_user.books) == 1
    assert db_user.books[0].title == "Test Book"
    
    # Test book -> user relationship
    db_book = test_db.query(Book).filter(Book.title == "Test Book").first()
    assert db_book.user.telegram_id == "12345"
    
    # Test book -> chapters relationship
    assert len(db_book.chapters) == 2
    assert db_book.chapters[0].title == "Chapter 1"
    assert db_book.chapters[1].title == "Chapter 2"
    
    # Test chapter -> book relationship
    db_chapter = test_db.query(Chapter).filter(Chapter.title == "Chapter 1").first()
    assert db_chapter.book.title == "Test Book"
