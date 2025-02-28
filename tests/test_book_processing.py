import pytest
import os
from unittest.mock import MagicMock, patch, mock_open
from ai_bot.books.file_processor import save_uploaded_file, extract_text_from_pdf, extract_text_from_epub, extract_text_from_txt, extract_text
from ai_bot.books.chapter_detector import detect_chapters
from ai_bot.books.book_model import create_book, process_book_file, get_user_books, get_book, get_book_chapters

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

def test_save_uploaded_file(tmp_path):
    """Test saving an uploaded file"""
    with patch('ai_bot.books.file_processor.data_dir', tmp_path):
        file_bytes = b"test content"
        user_id = "12345"
        file_name = "test.pdf"
        
        result = save_uploaded_file(file_bytes, user_id, file_name)
        
        # Check if user directory was created
        user_dir = tmp_path / user_id
        assert user_dir.exists()
        
        # Check if file was saved
        file_path = user_dir / file_name
        assert file_path.exists()
        assert file_path.read_bytes() == file_bytes
        
        # Check if correct path was returned
        assert result == str(file_path)

def test_extract_text_from_pdf():
    """Test extracting text from PDF"""
    with patch('PyPDF2.PdfReader') as mock_pdf_reader:
        # Mock PDF reader
        mock_reader = MagicMock()
        mock_pdf_reader.return_value = mock_reader
        
        # Mock pages
        page1 = MagicMock()
        page1.extract_text.return_value = "Page 1 content"
        page2 = MagicMock()
        page2.extract_text.return_value = "Page 2 content"
        mock_reader.pages = [page1, page2]
        
        # Mock open
        with patch('builtins.open', mock_open()) as mock_file:
            result = extract_text_from_pdf("test.pdf")
            
            # Check if file was opened
            mock_file.assert_called_once_with("test.pdf", 'rb')
            
            # Check if text was extracted
            assert "Page 1 content" in result
            assert "Page 2 content" in result

def test_extract_text_from_txt():
    """Test extracting text from TXT"""
    content = "This is a test text file."
    
    # Mock open
    with patch('builtins.open', mock_open(read_data=content)) as mock_file:
        result = extract_text_from_txt("test.txt")
        
        # Check if file was opened
        mock_file.assert_called_once_with("test.txt", 'r', encoding='utf-8')
        
        # Check if text was extracted
        assert result == content

def test_extract_text():
    """Test extract_text function with different file types"""
    with patch('ai_bot.books.file_processor.extract_text_from_pdf') as mock_pdf, \
         patch('ai_bot.books.file_processor.extract_text_from_epub') as mock_epub, \
         patch('ai_bot.books.file_processor.extract_text_from_txt') as mock_txt:
        
        mock_pdf.return_value = "PDF content"
        mock_epub.return_value = "EPUB content"
        mock_txt.return_value = "TXT content"
        
        # Test PDF
        assert extract_text("test.pdf") == "PDF content"
        mock_pdf.assert_called_once_with("test.pdf")
        
        # Test EPUB
        assert extract_text("test.epub") == "EPUB content"
        mock_epub.assert_called_once_with("test.epub")
        
        # Test TXT
        assert extract_text("test.txt") == "TXT content"
        mock_txt.assert_called_once_with("test.txt")
        
        # Test unsupported
        assert extract_text("test.doc") is None

def test_detect_chapters():
    """Test chapter detection"""
    text = """
    Chapter 1
    This is the content of chapter 1.
    It has multiple lines.
    
    Chapter 2
    This is the content of chapter 2.
    It also has multiple lines.
    
    Chapter 3
    This is the final chapter.
    """
    
    chapters = detect_chapters(text)
    
    assert len(chapters) == 3
    assert chapters[0]["title"] == "Chapter 1"
    assert "content of chapter 1" in chapters[0]["content"]
    assert chapters[1]["title"] == "Chapter 2"
    assert "content of chapter 2" in chapters[1]["content"]
    assert chapters[2]["title"] == "Chapter 3"
    assert "final chapter" in chapters[2]["content"]

def test_detect_chapters_no_chapters():
    """Test chapter detection with no chapter markers"""
    text = "This is just plain text with no chapter markers."
    
    chapters = detect_chapters(text)
    
    assert len(chapters) == 1
    assert chapters[0]["title"] == "Chapter 1"
    assert text in chapters[0]["content"]

def test_create_book(mock_db):
    """Test creating a book"""
    user_id = 1
    title = "Test Book"
    author = "Test Author"
    
    result = create_book(mock_db, user_id, title, author)
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()
    
    assert result.user_id == user_id
    assert result.title == title
    assert result.author == author
    assert result.processing_status == 'pending'

@patch('ai_bot.books.book_model.save_uploaded_file')
@patch('ai_bot.books.book_model.extract_text')
@patch('ai_bot.books.book_model.detect_chapters')
def test_process_book_file(mock_detect_chapters, mock_extract_text, mock_save_file, mock_db):
    """Test processing a book file"""
    user_id = 1
    telegram_id = "12345"
    file_bytes = b"test content"
    file_name = "test.pdf"
    
    # Mock save_uploaded_file
    mock_save_file.return_value = "/path/to/test.pdf"
    
    # Mock extract_text
    mock_extract_text.return_value = "Book content"
    
    # Mock detect_chapters
    mock_detect_chapters.return_value = [
        {"title": "Chapter 1", "content": "Chapter 1 content"},
        {"title": "Chapter 2", "content": "Chapter 2 content"}
    ]
    
    result = process_book_file(mock_db, user_id, telegram_id, file_bytes, file_name)
    
    # Check if book was created
    mock_db.add.assert_called()
    mock_db.commit.assert_called()
    
    # Check if file was saved
    mock_save_file.assert_called_once_with(file_bytes, telegram_id, file_name)
    
    # Check if text was extracted
    mock_extract_text.assert_called_once_with("/path/to/test.pdf")
    
    # Check if chapters were detected
    mock_detect_chapters.assert_called_once_with("Book content")
    
    # Check if chapters were added to database
    assert mock_db.add.call_count >= 3  # Book + 2 chapters
    
    # Check book properties
    assert result.user_id == user_id
    assert result.title == "test"  # From filename without extension
    assert result.file_path == "/path/to/test.pdf"
    assert result.file_type == ".pdf"
    assert result.total_chapters == 2
    assert result.processed_chapters == 2
    assert result.processing_status == 'completed'
