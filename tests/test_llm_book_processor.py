"""
Tests for the LLM book processor.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from books.llm_book_processor import LLMBookProcessor, process_book_with_llm

class TestLLMBookProcessor:
    """Test suite for LLMBookProcessor."""
    
    def test_initialization(self):
        """Test that the processor initializes correctly."""
        processor = LLMBookProcessor()
        assert hasattr(processor, "chapter_detector")
        assert hasattr(processor, "semantic_chunker")
        assert hasattr(processor, "structure_analyzer")
    
    @patch('books.llm_book_processor.save_uploaded_file')
    @patch('books.llm_book_processor.extract_text')
    @patch('books.llm_book_processor.create_book')
    def test_process_book(self, mock_create_book, mock_extract_text, mock_save_file):
        """Test that process_book calls the right methods and returns expected results."""
        # Mock dependencies
        mock_save_file.return_value = "/path/to/file.pdf"
        mock_extract_text.return_value = "This is the book content."
        
        mock_book = MagicMock()
        mock_book.id = 123
        mock_create_book.return_value = mock_book
        
        # Mock the database session
        mock_db = MagicMock()
        
        # Create the processor with mocked components
        processor = LLMBookProcessor()
        processor.structure_analyzer = MagicMock()
        processor.structure_analyzer.analyze_structure.return_value = {
            "title": "Test Book",
            "author": "Test Author",
            "items": [{"type": "chapter", "title": "Chapter 1"}],
            "metadata": {
                "word_count": 100,
                "estimated_reading_time_minutes": 1,
                "structure_complexity": 0.5
            }
        }
        
        processor.chapter_detector = MagicMock()
        processor.chapter_detector.detect_chapters.return_value = [
            {"title": "Chapter 1", "content": "Chapter 1 content"}
        ]
        
        # Call process_book
        result = processor.process_book(
            db=mock_db,
            user_id=1,
            file_bytes=b"file content",
            file_name="test.pdf",
            telegram_id="123456"
        )
        
        # Check that the dependencies were called
        mock_save_file.assert_called_once_with(b"file content", 1, "test.pdf")
        mock_extract_text.assert_called_once_with("/path/to/file.pdf")
        mock_create_book.assert_called_once_with(
            db=mock_db,
            user_id=1,
            title="Test Book",
            author="Test Author"
        )
        
        # Check that the book was updated
        assert mock_book.book_structure is not None
        assert mock_book.detected_metadata is not None
        assert mock_book.processing_log is not None
        assert mock_book.structure_complexity_score == 0.5
        
        # Check that the database was committed
        mock_db.commit.assert_called_once()
        
        # Check the result
        assert result["book_id"] == 123
        assert result["title"] == "Test Book"
        assert result["author"] == "Test Author"
        assert result["chapters"] == 1
        assert "processing_log" in result
        assert result["structure_complexity"] == 0.5
    
    @patch('books.llm_book_processor.LLMBookProcessor')
    def test_convenience_function(self, mock_processor_class):
        """Test the convenience function process_book_with_llm."""
        # Mock the processor
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        mock_processor.process_book.return_value = {"book_id": 123}
        
        # Mock the database session
        mock_db = MagicMock()
        
        # Call the convenience function
        result = process_book_with_llm(
            db=mock_db,
            user_id=1,
            file_bytes=b"file content",
            file_name="test.pdf",
            telegram_id="123456"
        )
        
        # Check that the processor was created
        mock_processor_class.assert_called_once()
        
        # Check that process_book was called
        mock_processor.process_book.assert_called_once_with(
            mock_db, 1, b"file content", "test.pdf", "123456"
        )
        
        # Check the result
        assert result["book_id"] == 123
