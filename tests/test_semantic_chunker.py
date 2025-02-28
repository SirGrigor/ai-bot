"""
Tests for the semantic chunker.
"""

import pytest
from unittest.mock import patch, MagicMock

from books.semantic_chunker import SemanticChunker, create_semantic_chunks

class TestSemanticChunker:
    """Test suite for SemanticChunker."""
    
    def test_initialization(self):
        """Test that the chunker initializes correctly."""
        chunker = SemanticChunker(chunk_size=500, chunk_overlap=100)
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 100
    
    @patch('books.semantic_chunker.SentenceSplitter')
    def test_create_chunks(self, mock_splitter_class):
        """Test that create_chunks calls the right methods and returns expected results."""
        # Mock the splitter
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        
        # Mock the nodes
        mock_node1 = MagicMock()
        mock_node1.text = "This is chunk 1"
        mock_node1.start_char_idx = 0
        mock_node1.end_char_idx = 14
        
        mock_node2 = MagicMock()
        mock_node2.text = "This is chunk 2"
        mock_node2.start_char_idx = 15
        mock_node2.end_char_idx = 29
        
        mock_splitter.get_nodes_from_documents.return_value = [mock_node1, mock_node2]
        
        # Create a sample text
        sample_text = "This is a sample text for testing chunking."
        
        # Create the chunker
        chunker = SemanticChunker(chunk_size=500, chunk_overlap=100)
        
        # Call create_chunks
        chunks = chunker.create_chunks(sample_text)
        
        # Check that the splitter was called
        mock_splitter.get_nodes_from_documents.assert_called_once()
        
        # Check the results
        assert len(chunks) == 2
        assert chunks[0]["text"] == "This is chunk 1"
        assert chunks[0]["start_index"] == 0
        assert chunks[0]["end_index"] == 14
        assert chunks[1]["text"] == "This is chunk 2"
        assert chunks[1]["start_index"] == 15
        assert chunks[1]["end_index"] == 29
    
    @patch('books.semantic_chunker.SentenceSplitter')
    def test_chunk_chapter(self, mock_splitter_class):
        """Test that chunk_chapter adds chapter metadata to chunks."""
        # Mock the splitter
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        
        # Mock the nodes
        mock_node = MagicMock()
        mock_node.text = "This is a chunk"
        mock_node.start_char_idx = 0
        mock_node.end_char_idx = 15
        
        mock_splitter.get_nodes_from_documents.return_value = [mock_node]
        
        # Create a sample chapter
        chapter = {
            "title": "Test Chapter",
            "content": "This is the chapter content",
            "level": 1,
            "start_index": 0
        }
        
        # Create the chunker
        chunker = SemanticChunker()
        
        # Call chunk_chapter
        chunks = chunker.chunk_chapter(chapter)
        
        # Check the results
        assert len(chunks) == 1
        assert chunks[0]["text"] == "This is a chunk"
        assert chunks[0]["chapter"] == "Test Chapter"
        assert chunks[0]["metadata"]["title"] == "Test Chapter"
        assert chunks[0]["metadata"]["level"] == 1
    
    @patch('books.semantic_chunker.SentenceSplitter')
    def test_convenience_function(self, mock_splitter_class):
        """Test the convenience function create_semantic_chunks."""
        # Mock the splitter
        mock_splitter = MagicMock()
        mock_splitter_class.return_value = mock_splitter
        
        # Mock the nodes
        mock_node = MagicMock()
        mock_node.text = "This is a chunk"
        mock_node.start_char_idx = 0
        mock_node.end_char_idx = 15
        
        mock_splitter.get_nodes_from_documents.return_value = [mock_node]
        
        # Create a sample text
        sample_text = "This is a sample text for testing chunking."
        
        # Call the convenience function
        chunks = create_semantic_chunks(sample_text, chunk_size=800, chunk_overlap=150)
        
        # Check that the splitter was created with the right parameters
        mock_splitter_class.assert_called_once_with(chunk_size=800, chunk_overlap=150)
        
        # Check the results
        assert len(chunks) == 1
        assert chunks[0]["text"] == "This is a chunk"
