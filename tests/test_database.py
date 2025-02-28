import pytest
import os
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from ai_bot.database.database import init_db, get_db, engine, Base
from ai_bot.database.models import User, Book, Chapter

@pytest.fixture
def test_db():
    """Create a test database in memory"""
    # Create tables in memory database
    Base.metadata.create_all(engine)
    
    # Create a session
    db = next(get_db())
    
    yield db
    
    # Clean up
    db.close()

def test_init_db():
    """Test database initialization"""
    with patch('ai_bot.database.database.Base.metadata.create_all') as mock_create_all:
        init_db()
        mock_create_all.assert_called_once_with(bind=engine)

def test_get_db():
    """Test database session creation and cleanup"""
    db = next(get_db())
    assert isinstance(db, Session)
    db.close()

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
