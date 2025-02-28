"""
LLM-based chapter detection for books.
Replaces regex-based chapter detection with more accurate LLM analysis.
"""

import logging
from typing import List, Dict, Any, Tuple

from books.semantic_chunker import create_semantic_chunks
from books.book_structure_analyzer import analyze_book_structure

logger = logging.getLogger(__name__)

class LLMChapterDetector:
    """
    Uses LLM-based approaches to detect chapters and other structural elements in books.
    """
    
    def __init__(self):
        logger.info("Initializing LLM Chapter Detector")
    
    def detect_chapters(self, text: str) -> List[Dict[str, Any]]:
        """
        Detects chapters and other structural elements in the provided text.
        
        Args:
            text: The full text of the book
            
        Returns:
            List of dictionaries containing chapter information:
            - title: Chapter title
            - start_index: Start position in the text
            - end_index: End position in the text
            - level: Hierarchy level (1 for chapters, 2 for sections, etc.)
            - content: The chapter content
        """
        logger.info("Detecting chapters using LLM approach")
        
        # First analyze the overall book structure
        book_structure = analyze_book_structure(text)
        
        # Then create semantic chunks based on the structure
        chapters = self._extract_chapters_from_structure(book_structure, text)
        
        logger.info(f"Detected {len(chapters)} chapters/sections")
        return chapters
    
    def _extract_chapters_from_structure(
        self, book_structure: Dict[str, Any], text: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts chapter information from the analyzed book structure.
        
        Args:
            book_structure: The analyzed book structure
            text: The full text of the book
            
        Returns:
            List of chapter dictionaries
        """
        chapters = []
        
        # Process the hierarchical structure
        for item in book_structure.get("items", []):
            if item["type"] in ["chapter", "section", "subsection"]:
                chapter_info = {
                    "title": item.get("title", "Untitled"),
                    "start_index": item.get("start_index", 0),
                    "end_index": item.get("end_index", 0),
                    "level": item.get("level", 1),
                    "content": text[item.get("start_index", 0):item.get("end_index", 0)]
                }
                chapters.append(chapter_info)
                
                # Add any nested sections
                if "children" in item:
                    for child in item["children"]:
                        child_info = {
                            "title": child.get("title", "Untitled"),
                            "start_index": child.get("start_index", 0),
                            "end_index": child.get("end_index", 0),
                            "level": child.get("level", 2),
                            "content": text[child.get("start_index", 0):child.get("end_index", 0)],
                            "parent": item.get("title", "Untitled")
                        }
                        chapters.append(child_info)
        
        return chapters
    
    def get_table_of_contents(self, chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generates a table of contents from the detected chapters.
        
        Args:
            chapters: List of chapter dictionaries
            
        Returns:
            List of TOC entries with title, level, and position
        """
        toc = []
        
        for chapter in chapters:
            toc.append({
                "title": chapter["title"],
                "level": chapter["level"],
                "position": chapter["start_index"]
            })
            
        return sorted(toc, key=lambda x: x["position"])

def detect_chapters(text: str) -> List[Dict[str, Any]]:
    """
    Convenience function to detect chapters using the LLM approach.
    
    Args:
        text: The full text of the book
        
    Returns:
        List of chapter dictionaries
    """
    detector = LLMChapterDetector()
    return detector.detect_chapters(text)
