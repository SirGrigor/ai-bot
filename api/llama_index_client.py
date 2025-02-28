"""
Client for interacting with LlamaIndex services.
Provides access to LlamaIndex's advanced chunking and indexing capabilities.
"""

import logging
from typing import Dict, Any, List, Optional

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.core import VectorStoreIndex
from llama_index.core.indices.service_context import ServiceContext

logger = logging.getLogger(__name__)

class LlamaIndexClient:
    """
    Client for interacting with LlamaIndex services.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LlamaIndex client.
        
        Args:
            api_key: Optional API key for LlamaIndex services
        """
        self.api_key = api_key
        logger.info("Initialized LlamaIndex client")
    
    def create_semantic_chunks(
        self, 
        text: str, 
        chunk_size: int = 1024, 
        chunk_overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from text using LlamaIndex.
        
        Args:
            text: The text to chunk
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk dictionaries
        """
        logger.info(f"Creating semantic chunks with size={chunk_size}, overlap={chunk_overlap}")
        
        # Create a document
        doc = Document(text=text)
        
        # Create a sentence splitter
        splitter = SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        # Split the document into nodes
        nodes = splitter.get_nodes_from_documents([doc])
        
        # Convert nodes to dictionaries
        chunks = []
        for i, node in enumerate(nodes):
            chunks.append({
                "id": i,
                "text": node.text,
                "start_char_idx": node.start_char_idx if hasattr(node, "start_char_idx") else None,
                "end_char_idx": node.end_char_idx if hasattr(node, "end_char_idx") else None,
            })
        
        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def create_vector_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a vector index from chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Dictionary with index information
        """
        logger.info(f"Creating vector index from {len(chunks)} chunks")
        
        # Convert chunks to documents
        documents = [Document(text=chunk["text"]) for chunk in chunks]
        
        # Create a vector index
        index = VectorStoreIndex.from_documents(documents)
        
        # Return index information
        return {
            "index_id": str(id(index)),
            "num_chunks": len(chunks),
            "status": "created"
        }
    
    def query_index(self, index_id: str, query: str) -> Dict[str, Any]:
        """
        Query a vector index.
        
        Args:
            index_id: The index ID
            query: The query string
            
        Returns:
            Dictionary with query results
        """
        logger.info(f"Querying index {index_id} with query: {query}")
        
        # In a real implementation, we would retrieve the index by ID
        # Here we just return a mock response
        
        return {
            "query": query,
            "results": [
                {
                    "text": f"This is a mock result for query: {query}",
                    "score": 0.95
                }
            ]
        }
