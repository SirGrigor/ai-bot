"""
Client for interacting with Anthropic's Claude API.
Provides enhanced prompting for book analysis.
"""

import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AnthropicClient:
    """
    Client for interacting with Anthropic's Claude API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Optional API key for Anthropic services
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("No Anthropic API key provided")
        
        logger.info("Initialized Anthropic client")
    
    def analyze_chapter(
        self, 
        chapter_text: str, 
        chapter_title: str,
        book_context: Optional[Dict[str, Any]] = None,
        model: str = "claude-3-5-sonnet"
    ) -> Dict[str, Any]:
        """
        Analyze a chapter using Claude.
        
        Args:
            chapter_text: The chapter text
            chapter_title: The chapter title
            book_context: Optional context about the book
            model: The Claude model to use
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing chapter '{chapter_title}' with model {model}")
        
        # In a real implementation, this would call the Anthropic API
        # Here we return a mock response
        
        # Create a hierarchical-aware prompt
        prompt = self._create_chapter_analysis_prompt(chapter_text, chapter_title, book_context)
        
        # Mock response
        return {
            "summary": f"This is a mock summary of chapter '{chapter_title}'.",
            "key_concepts": ["concept1", "concept2", "concept3"],
            "characters": ["character1", "character2"],
            "themes": ["theme1", "theme2"],
            "important_quotes": ["quote1", "quote2"],
            "analysis_model": model
        }
    
    def generate_book_summary(
        self,
        book_structure: Dict[str, Any],
        chapter_summaries: List[Dict[str, Any]],
        model: str = "claude-3-5-sonnet"
    ) -> Dict[str, Any]:
        """
        Generate a book summary using Claude.
        
        Args:
            book_structure: The book structure
            chapter_summaries: List of chapter summaries
            model: The Claude model to use
            
        Returns:
            Dictionary with summary results
        """
        logger.info(f"Generating book summary with model {model}")
        
        # In a real implementation, this would call the Anthropic API
        # Here we return a mock response
        
        # Create a hierarchical-aware prompt
        prompt = self._create_book_summary_prompt(book_structure, chapter_summaries)
        
        # Mock response
        return {
            "summary": "This is a mock book summary.",
            "key_themes": ["theme1", "theme2", "theme3"],
            "main_characters": ["character1", "character2"],
            "plot_arc": "This is a description of the plot arc.",
            "analysis_model": model
        }
    
    def _create_chapter_analysis_prompt(
        self,
        chapter_text: str,
        chapter_title: str,
        book_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a prompt for chapter analysis.
        
        Args:
            chapter_text: The chapter text
            chapter_title: The chapter title
            book_context: Optional context about the book
            
        Returns:
            Prompt string
        """
        # Create a hierarchical-aware prompt
        prompt = f"""
        <book_context>
        Title: {book_context.get('title', 'Unknown') if book_context else 'Unknown'}
        Author: {book_context.get('author', 'Unknown') if book_context else 'Unknown'}
        </book_context>
        
        <chapter>
        Title: {chapter_title}
        
        Content:
        {chapter_text[:1000]}... [content truncated for brevity]
        </chapter>
        
        Please analyze this chapter and provide:
        1. A concise summary (3-5 sentences)
        2. Key concepts and ideas presented
        3. Important characters mentioned
        4. Main themes explored
        5. Notable quotes or passages
        6. How this chapter connects to the overall narrative structure
        
        Focus on the most important elements that a reader should remember.
        """
        
        return prompt
    
    def _create_book_summary_prompt(
        self,
        book_structure: Dict[str, Any],
        chapter_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Create a prompt for book summary generation.
        
        Args:
            book_structure: The book structure
            chapter_summaries: List of chapter summaries
            
        Returns:
            Prompt string
        """
        # Extract book metadata
        title = book_structure.get("title", "Unknown")
        author = book_structure.get("author", "Unknown")
        
        # Create a list of chapter summaries
        chapter_summary_text = ""
        for i, summary in enumerate(chapter_summaries):
            chapter_summary_text += f"""
            Chapter {i+1}: {summary.get('title', f'Chapter {i+1}')}
            Summary: {summary.get('summary', 'No summary available')}
            Key concepts: {', '.join(summary.get('key_concepts', []))}
            """
        
        # Create the prompt
        prompt = f"""
        <book_metadata>
        Title: {title}
        Author: {author}
        </book_metadata>
        
        <chapter_summaries>
        {chapter_summary_text}
        </chapter_summaries>
        
        Based on the chapter summaries above, please generate:
        1. A comprehensive book summary (1-2 paragraphs)
        2. The key themes explored throughout the book
        3. Main characters and their significance
        4. The overall plot arc and structure
        5. The main ideas or arguments presented
        
        Focus on creating a cohesive overview that captures the essence of the entire book.
        """
        
        return prompt
