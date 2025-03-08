from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class ArchitectAgent(BaseSpecializedAgent):
    """Agent specialized in system architecture design"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize architect agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "sys", "re"]
        super().__init__("architect", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Designs the overall system architecture and component relationships. "
            "Specializes in creating efficient, maintainable software structures "
            "and determining the best design patterns for the requirements."
        )
    
    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze project requirements
        
        Args:
            requirements: Project requirements text
            
        Returns:
            Analysis results
        """
        prompt = f"""
        You are a senior system architect. Please analyze the following project requirements 
        and break them down into:
        
        1. Core features (as a list of distinct features)
        2. Component architecture (how the system should be structured)
        3. Data structures (what data models are needed)
        4. API endpoints (if applicable)
        5. External dependencies (what libraries or services are needed)
        6. Potential technical challenges
        
        REQUIREMENTS:
        {requirements}
        
        For each feature identified, provide:
        - A clear name
        - A brief description
        - Priority (high/medium/low)
        - Technical complexity (high/medium/low)
        
        Be thorough in your analysis, as this will guide the entire development process.
        Think step by step.
        """
        
        return self.run(prompt)
    
    def design_project_structure(self, requirements: str, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Design project directory structure
        
        Args:
            requirements: Project requirements
            features: List of features from the requirements analysis
            
        Returns:
            Directory structure design
        """
        features_str = "\n".join([
            f"- {f['name']}: {f['description']} (Priority: {f['priority']}, Complexity: {f['complexity']})"
            for f in features
        ])
        
        prompt = f"""
        You are a senior system architect. Based on the following project requirements and features,
        design an optimal directory structure for a Python project.
        
        REQUIREMENTS:
        {requirements}
        
        FEATURES:
        {features_str}
        
        Please:
        1. Create a complete directory structure with all necessary files
        2. For each directory, explain its purpose
        3. For key files, explain what they should contain
        4. Create the base structure using filesystem tools
        5. Create essential files like README.md, setup.py, etc.
        
        Make sure to follow Python best practices for project organization.
        The structure should be clean, maintainable, and scalable.
        
        After designing the structure, implement it by creating the actual directories and files.
        """
        
        return self.run(prompt) 
