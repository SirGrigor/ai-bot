"""
Tests for the LLM-based chapter detector.
"""

import pytest
from unittest.mock import patch, MagicMock

from books.llm_chapter_detector import LLMChapterDetector, detect_chapters

class TestLLMChapterDetector:
    """Test suite for LLMChapterDetector."""
    
    def test_initialization(self):
        """Test that the detector initializes correctly."""
        detector = LLMChapterDetector()
        assert isinstance(detector, LLMChapterDetector)
    
    @patch('books.llm_chapter_detector.analyze_book_structure')
    def test_detect_chapters(self, mock_analyze_structure):
        """Test that detect_chapters calls the right methods and returns expected results."""
        # Mock the book structure analysis
        mock_analyze_structure.return_value = {
            "items": [
                {
                    "type": "chapter",
                    "title": "Chapter 1",
                    "start_index": 0,
                    "end_index": 1000,
                    "level": 1
                },
                {
                    "type": "chapter",
                    "title": "Chapter 2",
                    "start_index": 1001,
                    "end_index": 2000,
                    "level": 1
                }
            ]
        }
        
        # Create a sample text
        sample_text = "This is a sample text for testing chapter detection."
        
        # Create the detector
        detector = LLMChapterDetector()
        
        # Call detect_chapters
        chapters = detector.detect_chapters(sample_text)
        
        # Check that analyze_book_structure was called
        mock_analyze_structure.assert_called_once_with(sample_text)
        
        # Check the results
        assert len(chapters) == 2
        assert chapters[0]["title"] == "Chapter 1"
        assert chapters[0]["start_index"] == 0
        assert chapters[0]["end_index"] == 1000
        assert chapters[0]["level"] == 1
        assert chapters[1]["title"] == "Chapter 2"
    
    def test_get_table_of_contents(self):
        """Test that get_table_of_contents returns the expected TOC."""
        # Create sample chapters
        chapters = [
            {
                "title": "Chapter 1",
                "start_index": 100,
                "end_index": 1000,
                "level": 1
            },
            {
                "title": "Chapter 2",
                "start_index": 1001,
                "end_index": 2000,
                "level": 1
            }
        ]
        
        # Create the detector
        detector = LLMChapterDetector()
        
        # Get the TOC
        toc = detector.get_table_of_contents(chapters)
        
        # Check the results
        assert len(toc) == 2
        assert toc[0]["title"] == "Chapter 1"
        assert toc[0]["position"] == 100
        assert toc[0]["level"] == 1
        assert toc[1]["title"] == "Chapter 2"
        assert toc[1]["position"] == 1001
        assert toc[1]["level"] == 1
    
    @patch('books.llm_chapter_detector.analyze_book_structure')
    def test_convenience_function(self, mock_analyze_structure):
        """Test the convenience function detect_chapters."""
        # Mock the book structure analysis
        mock_analyze_structure.return_value = {
            "items": [
                {
                    "type": "chapter",
                    "title": "Chapter 1",
                    "start_index": 0,
                    "end_index": 1000,
                    "level": 1
                }
            ]
        }
        
        # Create a sample text
        sample_text = "This is a sample text for testing chapter detection."
        
        # Call the convenience function
        chapters = detect_chapters(sample_text)
        
        # Check that analyze_book_structure was called
        mock_analyze_structure.assert_called_once_with(sample_text)
        
        # Check the results
        assert len(chapters) == 1
        assert chapters[0]["title"] == "Chapter 1"
