"""
Semantic chunking for book content using LlamaIndex.
Provides more meaningful content segmentation than simple text splitting.
"""

import logging
from typing import List, Dict, Any, Optional
from llama_index.core.node_parser import SentenceSplitter

logger = logging.getLogger(__name__)

class SemanticChunker:
    """
    Uses LlamaIndex to create semantic chunks from book content.
    """
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 200):
        """
        Initialize the semantic chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        logger.info(f"Initialized SemanticChunker with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def create_chunks(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from the provided text.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to include with each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        logger.info(f"Creating semantic chunks from text of length {len(text)}")
        
        # Use LlamaIndex to create nodes
        nodes = self.splitter.get_nodes_from_documents([{"text": text}])
        
        # Convert nodes to our chunk format
        chunks = []
        for i, node in enumerate(nodes):
            chunk = {
                "id": i,
                "text": node.text,
                "start_index": node.start_char_idx if hasattr(node, "start_char_idx") else None,
                "end_index": node.end_char_idx if hasattr(node, "end_char_idx") else None,
            }
            
            # Add metadata if provided
            if metadata:
                chunk["metadata"] = metadata
                
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def chunk_chapter(self, chapter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from a chapter.
        
        Args:
            chapter: Chapter dictionary with title, content, etc.
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chapter_metadata = {
            "title": chapter.get("title", "Untitled"),
            "level": chapter.get("level", 1),
            "chapter_index": chapter.get("start_index", 0)
        }
        
        chunks = self.create_chunks(chapter["content"], chapter_metadata)
        
        # Add chapter reference to each chunk
        for chunk in chunks:
            chunk["chapter"] = chapter["title"]
            
        return chunks

def create_semantic_chunks(text: str, chunk_size: int = 1024, chunk_overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Convenience function to create semantic chunks from text.
    
    Args:
        text: The text to chunk
        chunk_size: Target size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of chunk dictionaries
    """
    chunker = SemanticChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return chunker.create_chunks(text)
