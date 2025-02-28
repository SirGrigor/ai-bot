"""
LLM-based book processor that enhances the existing book processing pipeline.
Uses LlamaIndex for semantic chunking and structure analysis.
"""

import logging
import json
import os
from typing import Dict, Any, List, Tuple, Optional
import time

from sqlalchemy.orm import Session

from books.book_model import create_book
from books.llm_chapter_detector import LLMChapterDetector
from books.semantic_chunker import SemanticChunker
from books.book_structure_analyzer import BookStructureAnalyzer
from books.file_processor import extract_text, save_uploaded_file

logger = logging.getLogger(__name__)

class LLMBookProcessor:
    """
    Processes books using LLM-based approaches for improved chapter detection,
    semantic chunking, and structure analysis.
    """
    
    def __init__(self):
        self.chapter_detector = LLMChapterDetector()
        self.semantic_chunker = SemanticChunker()
        self.structure_analyzer = BookStructureAnalyzer()
        logger.info("Initialized LLMBookProcessor")
    
    def process_book(
        self, 
        db: Session, 
        user_id: int, 
        file_bytes: bytes, 
        file_name: str,
        telegram_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a book file using LLM-based approaches.
        
        Args:
            db: Database session
            user_id: User ID
            file_bytes: Book file bytes
            file_name: Original file name
            telegram_id: Optional Telegram ID
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing book {file_name} for user {user_id}")
        
        # Track processing progress
        processing_log = []
        
        # Save the uploaded file
        start_time = time.time()
        processing_log.append({"step": "save_file", "status": "started", "timestamp": start_time})
        
        file_path = save_uploaded_file(file_bytes, user_id, file_name)
        
        processing_log.append({
            "step": "save_file", 
            "status": "completed", 
            "timestamp": time.time(),
            "duration": time.time() - start_time
        })
        
        # Extract text from the file
        start_time = time.time()
        processing_log.append({"step": "extract_text", "status": "started", "timestamp": start_time})
        
        text = extract_text(file_path)
        
        processing_log.append({
            "step": "extract_text", 
            "status": "completed", 
            "timestamp": time.time(),
            "duration": time.time() - start_time,
            "text_length": len(text)
        })
        
        # Analyze book structure
        start_time = time.time()
        processing_log.append({"step": "analyze_structure", "status": "started", "timestamp": start_time})
        
        book_structure = self.structure_analyzer.analyze_structure(text)
        
        processing_log.append({
            "step": "analyze_structure", 
            "status": "completed", 
            "timestamp": time.time(),
            "duration": time.time() - start_time,
            "structure_elements": len(book_structure.get("items", []))
        })
        
        # Detect chapters
        start_time = time.time()
        processing_log.append({"step": "detect_chapters", "status": "started", "timestamp": start_time})
        
        chapters = self.chapter_detector.detect_chapters(text)
        
        processing_log.append({
            "step": "detect_chapters", 
            "status": "completed", 
            "timestamp": time.time(),
            "duration": time.time() - start_time,
            "chapters_detected": len(chapters)
        })
        
        # Create book in database
        start_time = time.time()
        processing_log.append({"step": "create_book", "status": "started", "timestamp": start_time})
        
        book_title = book_structure.get("title", os.path.splitext(file_name)[0])
        book_author = book_structure.get("author", "Unknown")
        
        book = create_book(
            db=db,
            user_id=user_id,
            title=book_title,
            author=book_author
        )
        
        # Add enhanced metadata
        book.book_structure = json.dumps(book_structure)
        book.detected_metadata = json.dumps({
            "title": book_title,
            "author": book_author,
            "word_count": book_structure.get("metadata", {}).get("word_count", 0),
            "estimated_reading_time": book_structure.get("metadata", {}).get("estimated_reading_time_minutes", 0),
            "complexity_score": book_structure.get("metadata", {}).get("structure_complexity", 0)
        })
        book.processing_log = json.dumps(processing_log)
        book.structure_complexity_score = book_structure.get("metadata", {}).get("structure_complexity", 0)
        
        db.commit()
        
        processing_log.append({
            "step": "create_book", 
            "status": "completed", 
            "timestamp": time.time(),
            "duration": time.time() - start_time,
            "book_id": book.id
        })
        
        # Return processing results
        return {
            "book_id": book.id,
            "title": book_title,
            "author": book_author,
            "chapters": len(chapters),
            "processing_log": processing_log,
            "structure_complexity": book_structure.get("metadata", {}).get("structure_complexity", 0)
        }

def process_book_with_llm(
    db: Session, 
    user_id: int, 
    file_bytes: bytes, 
    file_name: str,
    telegram_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to process a book using LLM-based approaches.
    
    Args:
        db: Database session
        user_id: User ID
        file_bytes: Book file bytes
        file_name: Original file name
        telegram_id: Optional Telegram ID
        
    Returns:
        Dictionary with processing results
    """
    processor = LLMBookProcessor()
    return processor.process_book(db, user_id, file_bytes, file_name, telegram_id)
