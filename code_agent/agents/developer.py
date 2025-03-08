from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class DeveloperAgent(BaseSpecializedAgent):
    """Agent specialized in code implementation"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize developer agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "sys", "re", "datetime", "typing"]
        super().__init__("developer", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Implements code based on requirements and architecture designs. "
            "Specializes in writing clean, efficient, and maintainable code "
            "with proper error handling and documentation."
        )
    
    def implement_feature(
        self, 
        feature: Dict[str, Any], 
        architecture: Dict[str, Any], 
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement a feature
        
        Args:
            feature: Feature details
            architecture: Architecture information
            project_structure: Project structure information
            
        Returns:
            Implementation result
        """
        prompt = f"""
        You are a senior software developer. Implement the following feature for our project:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        Priority: {feature['priority']}
        Complexity: {feature['complexity']}
        
        PROJECT ARCHITECTURE:
        {architecture}
        
        PROJECT STRUCTURE:
        {project_structure}
        
        Please:
        1. Determine which files need to be created or modified
        2. Implement the feature with high-quality code
        3. Ensure proper error handling
        4. Add comprehensive docstrings and comments
        5. Follow PEP 8 style guidelines
        6. Make your code testable
        
        For each file you create or modify:
        1. First check if it exists using file_exists or directory_exists
        2. If it exists and you need to modify it, read it first
        3. Create/update the file with your implementation
        
        After implementing the feature, create a branch and commit your changes if GitHub tools are available.
        """
        
        return self.run(prompt) 
