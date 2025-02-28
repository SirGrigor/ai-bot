"""
Book structure analyzer that identifies chapters, sections, and other structural elements.
Uses LLM-based approaches for more accurate structure detection.
"""

import logging
import re
from typing import Dict, Any, List, Tuple
import json

logger = logging.getLogger(__name__)

class BookStructureAnalyzer:
    """
    Analyzes the structure of a book to identify chapters, sections, and other elements.
    """
    
    def __init__(self):
        logger.info("Initializing BookStructureAnalyzer")
        
        # Common chapter heading patterns (as a fallback)
        self.chapter_patterns = [
            r"(?:Chapter|CHAPTER)\s+(\d+|[IVXLCDM]+)(?:\s*[:.-]\s*)?(.+)?",
            r"(?:Section|SECTION)\s+(\d+|[IVXLCDM]+)(?:\s*[:.-]\s*)?(.+)?",
            r"^\s*(\d+|[IVXLCDM]+)\.\s+(.+)$"
        ]
    
    def analyze_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the structure of the book text.
        
        Args:
            text: The full text of the book
            
        Returns:
            Dictionary containing the book structure:
            - title: Book title (if detected)
            - author: Author name (if detected)
            - items: List of structural elements (chapters, sections, etc.)
            - metadata: Additional metadata
        """
        logger.info("Analyzing book structure")
        
        # Extract potential front matter
        front_matter, main_content = self._extract_front_matter(text)
        
        # Detect book title and author from front matter
        title, author = self._extract_title_author(front_matter)
        
        # Detect chapters and sections
        items = self._detect_structural_elements(main_content)
        
        # Calculate reading time estimates
        reading_time = self._calculate_reading_time(text)
        
        # Assemble the structure
        structure = {
            "title": title,
            "author": author,
            "items": items,
            "metadata": {
                "word_count": len(text.split()),
                "estimated_reading_time_minutes": reading_time,
                "has_front_matter": bool(front_matter),
                "structure_complexity": self._calculate_complexity(items)
            }
        }
        
        logger.info(f"Analyzed structure with {len(items)} elements")
        return structure
    
    def _extract_front_matter(self, text: str) -> Tuple[str, str]:
        """
        Extracts the front matter from the book text.
        
        Args:
            text: The full text of the book
            
        Returns:
            Tuple of (front_matter, main_content)
        """
        # Simple heuristic: front matter is everything before the first chapter
        # In a real implementation, this would use more sophisticated detection
        
        # Look for common chapter start indicators
        chapter_starts = [
            "Chapter 1", "CHAPTER 1", "Chapter One", "CHAPTER ONE",
            "1.", "I.", "Part 1", "PART 1"
        ]
        
        front_matter = ""
        main_content = text
        
        for starter in chapter_starts:
            if starter in text:
                parts = text.split(starter, 1)
                if len(parts) == 2:
                    front_matter = parts[0]
                    main_content = starter + parts[1]
                    break
        
        return front_matter, main_content
    
    def _extract_title_author(self, front_matter: str) -> Tuple[str, str]:
        """
        Extracts the book title and author from front matter.
        
        Args:
            front_matter: The front matter text
            
        Returns:
            Tuple of (title, author)
        """
        # In a real implementation, this would use LLM to extract this information
        # Here we use a simple heuristic
        
        lines = front_matter.strip().split('\n')
        title = "Unknown Title"
        author = "Unknown Author"
        
        if lines:
            # Assume first non-empty line might be the title
            for line in lines:
                if line.strip():
                    title = line.strip()
                    break
            
            # Look for author indicators
            for line in lines:
                if "by " in line.lower() or "author:" in line.lower():
                    author = line.replace("by ", "").replace("By ", "").replace("Author:", "").strip()
                    break
        
        return title, author
    
    def _detect_structural_elements(self, text: str) -> List[Dict[str, Any]]:
        """
        Detects chapters, sections, and other structural elements.
        
        Args:
            text: The book text
            
        Returns:
            List of structural elements
        """
        # In a real implementation, this would use LLM to detect structure
        # Here we use regex patterns as a fallback
        
        items = []
        lines = text.split('\n')
        current_position = 0
        
        for i, line in enumerate(lines):
            for pattern in self.chapter_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    # Found a potential chapter heading
                    chapter_num = match.group(1)
                    chapter_title = match.group(2) if len(match.groups()) > 1 and match.group(2) else f"Chapter {chapter_num}"
                    
                    # Calculate start and end positions
                    start_index = current_position
                    
                    # Find the end of this chapter (start of next chapter or end of text)
                    end_index = len(text)
                    for j in range(i + 1, len(lines)):
                        for p in self.chapter_patterns:
                            if re.match(p, lines[j].strip()):
                                # Found the next chapter
                                next_chapter_pos = sum(len(lines[k]) + 1 for k in range(i + 1, j))
                                end_index = start_index + next_chapter_pos
                                break
                        if end_index != len(text):
                            break
                    
                    # Add the chapter to our structure
                    items.append({
                        "type": "chapter",
                        "title": chapter_title.strip(),
                        "number": chapter_num,
                        "start_index": start_index,
                        "end_index": end_index,
                        "level": 1
                    })
                    
                    break
            
            current_position += len(line) + 1  # +1 for the newline
        
        return items
    
    def _calculate_reading_time(self, text: str) -> int:
        """
        Calculates estimated reading time in minutes.
        
        Args:
            text: The text to analyze
            
        Returns:
            Estimated reading time in minutes
        """
        # Average reading speed: 200-250 words per minute
        # We'll use 225 as a middle ground
        word_count = len(text.split())
        reading_time = round(word_count / 225)
        return max(1, reading_time)  # Minimum 1 minute
    
    def _calculate_complexity(self, items: List[Dict[str, Any]]) -> float:
        """
        Calculates a complexity score for the book structure.
        
        Args:
            items: The structural elements
            
        Returns:
            Complexity score (0-1)
        """
        # Simple complexity heuristic based on number of structural elements
        if not items:
            return 0.0
            
        # More chapters/sections = higher complexity
        return min(1.0, len(items) / 30)

def analyze_book_structure(text: str) -> Dict[str, Any]:
    """
    Convenience function to analyze book structure.
    
    Args:
        text: The full text of the book
        
    Returns:
        Dictionary containing the book structure
    """
    analyzer = BookStructureAnalyzer()
    return analyzer.analyze_structure(text)
