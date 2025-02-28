import re
from errors.logger import setup_logger

logger = setup_logger(__name__)

def detect_chapters(text):
    """Detect chapter boundaries in text"""
    # Common chapter patterns
    chapter_patterns = [
        r'(?i)^chapter\s+\d+',  # "Chapter 1", "Chapter 2", etc.
        r'(?i)^chapter\s+[ivxlcdm]+',  # "Chapter I", "Chapter II", etc. (Roman numerals)
        r'(?i)^\d+\.\s+',  # "1. ", "2. ", etc.
        r'(?i)^[ivxlcdm]+\.\s+',  # "I. ", "II. ", etc. (Roman numerals)
    ]
    
    # Combine patterns
    combined_pattern = '|'.join(f'({pattern})' for pattern in chapter_patterns)
    
    # Split text by lines
    lines = text.split('\n')
    
    chapters = []
    current_chapter = {"title": "Introduction", "content": ""}
    
    for line in lines:
        # Check if line matches a chapter pattern
        if re.match(combined_pattern, line.strip()):
            # Save current chapter if it has content
            if current_chapter["content"].strip():
                chapters.append(current_chapter)
            
            # Start new chapter
            current_chapter = {"title": line.strip(), "content": line + "\n"}
        else:
            # Add line to current chapter
            current_chapter["content"] += line + "\n"
    
    # Add the last chapter
    if current_chapter["content"].strip():
        chapters.append(current_chapter)
    
    # If no chapters were detected, treat the entire text as one chapter
    if not chapters:
        chapters = [{"title": "Chapter 1", "content": text}]
    
    logger.info(f"Detected {len(chapters)} chapters")
    return chapters
