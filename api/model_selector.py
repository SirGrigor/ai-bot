"""
Model selector for choosing the appropriate LLM based on document characteristics.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    Selects the appropriate LLM model based on document characteristics.
    """
    
    def __init__(self):
        logger.info("Initializing ModelSelector")
        
        # Define available models with their characteristics
        self.available_models = {
            "claude-3-5-sonnet": {
                "context_window": 200000,
                "capabilities": ["chapter_detection", "summarization", "concept_extraction"],
                "cost_per_token": 0.000003,
                "quality": 0.9
            },
            "claude-3-haiku": {
                "context_window": 100000,
                "capabilities": ["chapter_detection", "summarization"],
                "cost_per_token": 0.000001,
                "quality": 0.8
            },
            "gpt-4o": {
                "context_window": 128000,
                "capabilities": ["chapter_detection", "summarization", "concept_extraction"],
                "cost_per_token": 0.000005,
                "quality": 0.95
            },
            "gpt-3.5-turbo": {
                "context_window": 16000,
                "capabilities": ["summarization"],
                "cost_per_token": 0.0000005,
                "quality": 0.7
            }
        }
    
    def select_model(
        self, 
        task: str, 
        document_size: int, 
        complexity: float = 0.5,
        budget_constrained: bool = False
    ) -> Dict[str, Any]:
        """
        Select the appropriate model for a given task and document.
        
        Args:
            task: The task to perform (e.g., "chapter_detection", "summarization")
            document_size: Size of the document in characters
            complexity: Estimated complexity of the document (0-1)
            budget_constrained: Whether to prioritize cost over quality
            
        Returns:
            Dictionary with selected model information
        """
        logger.info(f"Selecting model for task={task}, size={document_size}, complexity={complexity}")
        
        # Filter models that can handle the document size
        suitable_models = {}
        for name, model in self.available_models.items():
            # Approximate token count (rough estimate: 4 chars per token)
            estimated_tokens = document_size / 4
            
            if estimated_tokens <= model["context_window"] and task in model["capabilities"]:
                suitable_models[name] = model
        
        if not suitable_models:
            logger.warning(f"No suitable models found for task={task}, size={document_size}")
            return {"model": None, "reason": "No suitable models available"}
        
        # Select the best model based on criteria
        if budget_constrained:
            # Sort by cost (ascending)
            sorted_models = sorted(suitable_models.items(), key=lambda x: x[1]["cost_per_token"])
        else:
            # Sort by quality (descending)
            sorted_models = sorted(suitable_models.items(), key=lambda x: x[1]["quality"], reverse=True)
        
        selected_model_name, selected_model = sorted_models[0]
        
        logger.info(f"Selected model {selected_model_name} for task={task}")
        
        return {
            "model": selected_model_name,
            "context_window": selected_model["context_window"],
            "quality": selected_model["quality"],
            "cost_per_token": selected_model["cost_per_token"],
            "estimated_cost": (document_size / 4) * selected_model["cost_per_token"]
        }
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available models.
        
        Returns:
            Dictionary of model information
        """
        return self.available_models
