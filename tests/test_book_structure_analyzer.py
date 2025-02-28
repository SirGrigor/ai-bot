"""
Tests for the book structure analyzer.
"""

import pytest
from unittest.mock import patch, MagicMock

from books.book_structure_analyzer import BookStructureAnalyzer, analyze_book_structure

class TestBookStructureAnalyzer:
    """Test suite for BookStructureAnalyzer."""
    
    def test_initialization(self):
        """Test that the analyzer initializes correctly."""
        analyzer = BookStructureAnalyzer()
        assert isinstance(analyzer, BookStructureAnalyzer)
    
    def test_analyze_structure(self):
        """Test that analyze_structure returns the expected structure."""
        # Create a sample text with chapters
        sample_text = """
        Book Title
        By Author Name
        
        Chapter 1: Introduction
        
        This is the content of chapter 1.
        
        Chapter 2: Main Concepts
        
        This is the content of chapter 2.
        """
        
        # Create the analyzer
        analyzer = BookStructureAnalyzer()
        
        # Analyze the structure
        structure = analyzer.analyze_structure(sample_text)
        
        # Check the results
        assert "title" in structure
        assert "author" in structure
        assert "items" in structure
        assert "metadata" in structure
        
        # Check metadata
        assert "word_count" in structure["metadata"]
        assert "estimated_reading_time_minutes" in structure["metadata"]
        assert "structure_complexity" in structure["metadata"]
    
    def test_extract_front_matter(self):
        """Test that _extract_front_matter correctly separates front matter."""
        # Create a sample text with front matter
        sample_text = """
        Book Title
        By Author Name
        
        Copyright 2025
        
        Chapter 1: Introduction
        
        This is the content of chapter 1.
        """
        
        # Create the analyzer
        analyzer = BookStructureAnalyzer()
        
        # Extract front matter
        front_matter, main_content = analyzer._extract_front_matter(sample_text)
        
        # Check the results
        assert "Book Title" in front_matter
        assert "By Author Name" in front_matter
        assert "Copyright" in front_matter
        assert "Chapter 1: Introduction" in main_content
    
    def test_extract_title_author(self):
        """Test that _extract_title_author correctly extracts title and author."""
        # Create a sample front matter
        front_matter = """
        Book Title
        By Author Name
        
        Copyright 2025
        """
        
        # Create the analyzer
        analyzer = BookStructureAnalyzer()
        
        # Extract title and author
        title, author = analyzer._extract_title_author(front_matter)
        
        # Check the results
        assert title == "Book Title"
        assert "Author Name" in author
    
    def test_detect_structural_elements(self):
        """Test that _detect_structural_elements correctly identifies chapters."""
        # Create a sample text with chapters
        sample_text = """
        Chapter 1: Introduction
        
        This is the content of chapter 1.
        
        Chapter 2: Main Concepts
        
        This is the content of chapter 2.
        """
        
        # Create the analyzer
        analyzer = BookStructureAnalyzer()
        
        # Detect structural elements
        items = analyzer._detect_structural_elements(sample_text)
        
        # Check the results
        assert len(items) > 0
        assert items[0]["type"] == "chapter"
        assert "Introduction" in items[0]["title"]
    
    def test_calculate_reading_time(self):
        """Test that _calculate_reading_time returns a reasonable estimate."""
        # Create a sample text
        sample_text = " ".join(["word"] * 1000)  # 1000 words
        
        # Create the analyzer
        analyzer = BookStructureAnalyzer()
        
        # Calculate reading time
        reading_time = analyzer._calculate_reading_time(sample_text)
        
        # Check the results (1000 words at 225 wpm should be about 4-5 minutes)
        assert 3 <= reading_time <= 5
    
    def test_convenience_function(self):
        """Test the convenience function analyze_book_structure."""
        # Create a sample text
        sample_text = """
        Book Title
        By Author Name
        
        Chapter 1: Introduction
        
        This is the content of chapter 1.
        """
        
        # Call the convenience function
        structure = analyze_book_structure(sample_text)
        
        # Check the results
        assert "title" in structure
        assert "author" in structure
        assert "items" in structure
        assert "metadata" in structure
