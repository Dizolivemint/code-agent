"""
Model manager for the Code Agent application.
"""

from typing import Dict, Any, Optional
from smolagents import HfApiModel
import os
import dotenv

class ModelManager:
    """
    Manages AI models for the Code Agent application.
    """
    
    def __init__(self):
        """Initialize the model manager and load API tokens."""
        # Load environment variables
        dotenv.load_dotenv()
        
        # Get API tokens from environment
        self.hf_token = os.getenv("HF_TOKEN", "")
        
        # Initialize model instances
        self._models = {}
    
    def get_model(self, model_id: str, provider: Optional[str] = None, 
                 temperature: float = 0.2, max_tokens: int = 4000) -> HfApiModel:
        """
        Get or create a model instance.
        
        Args:
            model_id: The model identifier
            provider: Optional provider name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            HfApiModel instance
        """
        # Create a unique key for this model configuration
        key = f"{model_id}_{provider}_{temperature}_{max_tokens}"
        
        # Return existing model if available
        if key in self._models:
            return self._models[key]
        
        # Create a new model instance
        model = HfApiModel(
            model_id=model_id,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Cache the model instance
        self._models[key] = model
        
        return model
    
    def list_available_models(self) -> Dict[str, Any]:
        """
        List available models for the application.
        
        Returns:
            Dictionary of recommended models by role
        """
        # Return a curated list of recommended models for each agent role
        return {
            "architect": [
                {
                    "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                    "description": "Recommended for architecture planning"
                },
                {
                    "id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "description": "Good alternative for architecture planning"
                }
            ],
            "developer": [
                {
                    "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                    "description": "Recommended for code generation"
                },
                {
                    "id": "codellama/CodeLlama-70b-Instruct-hf",
                    "description": "Specialized for code generation"
                }
            ],
            "tester": [
                {
                    "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                    "description": "Recommended for test generation"
                },
                {
                    "id": "codellama/CodeLlama-34b-Instruct-hf",
                    "description": "Good balance between performance and resource usage"
                }
            ],
            "reviewer": [
                {
                    "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                    "description": "Recommended for code review"
                },
                {
                    "id": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                    "description": "Good alternative for code review"
                }
            ]
        } 
