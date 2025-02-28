from sqlalchemy.orm import Session
from ai_bot.database.models import Book, Chapter
from ai_bot.books.file_processor import extract_text, save_uploaded_file
from ai_bot.books.chapter_detector import detect_chapters
from datetime import datetime
import os
from ai_bot.errors.logger import setup_logger

logger = setup_logger(__name__)

def create_book(db: Session, user_id: int, title: str, author: str = None):
    """Create a new book entry without file"""
    db_book = Book(
        user_id=user_id,
        title=title,
        author=author,
        processing_status='pending',
        created_at=datetime.utcnow()
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def process_book_file(db: Session, user_id: int, telegram_id: str, file_bytes, file_name):
    """Process an uploaded book file"""
    # Save file
    file_path = save_uploaded_file(file_bytes, telegram_id, file_name)
    
    # Extract title and author from filename (simple approach)
    title = os.path.splitext(file_name)[0]
    author = None
    
    # Create book entry
    db_book = Book(
        user_id=user_id,
        title=title,
        author=author,
        file_path=file_path,
        file_type=os.path.splitext(file_name)[1].lower(),
        processing_status='processing',
        created_at=datetime.utcnow()
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    # Extract text
    text = extract_text(file_path)
    if not text:
        db_book.processing_status = 'error'
        db.commit()
        return None
    
    # Detect chapters
    chapters = detect_chapters(text)
    
    # Save chapters
    db_book.total_chapters = len(chapters)
    db_book.processed_chapters = 0
    
    for i, chapter in enumerate(chapters):
        # Calculate position percentage
        position_percentage = (i / len(chapters)) * 100
        
        # Estimate reading time (rough estimate: 200 words per minute)
        word_count = len(chapter["content"].split())
        estimated_reading_time = word_count // 200
        
        db_chapter = Chapter(
            book_id=db_book.id,
            chapter_number=i+1,
            title=chapter["title"],
            content=chapter["content"],
            token_count=len(chapter["content"].split()),  # Simple token count
            position_percentage=position_percentage,
            estimated_reading_time=estimated_reading_time,
            processing_status='pending'
        )
        db.add(db_chapter)
        db_book.processed_chapters += 1
    
    db_book.processing_status = 'completed'
    db.commit()
    db.refresh(db_book)
    
    return db_book

def get_user_books(db: Session, user_id: int):
    """Get all books for a user"""
    return db.query(Book).filter(Book.user_id == user_id).all()

def get_book(db: Session, book_id: int):
    """Get a book by ID"""
    return db.query(Book).filter(Book.id == book_id).first()

def get_book_chapters(db: Session, book_id: int):
    """Get all chapters for a book"""
    return db.query(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.chapter_number).all()
