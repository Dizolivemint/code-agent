from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class EnvironmentSetupAgent(BaseSpecializedAgent):
    """Agent specialized in environment and dependency setup"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize environment setup agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "sys", "subprocess", "venv"]
        super().__init__("environment_setup", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Sets up Python environments and manages dependencies for projects. "
            "Handles virtual environment creation, package installation, and "
            "dependency validation."
        )
    
    def setup_environment(self, project_dir: str, requirements_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Set up a Python environment for the project
        
        Args:
            project_dir: Project directory path
            requirements_path: Path to requirements.txt file (optional)
            
        Returns:
            Environment setup results
        """
        prompt = f"""
        You are a DevOps engineer specializing in Python environments. You need to set up a 
        Python environment for the following project:
        
        PROJECT DIRECTORY: {project_dir}
        
        Follow these steps:
        
        1. Determine if requirements.txt exists in the project directory
        2. If it doesn't exist, create a requirements.txt file based on imports in the code
        3. Set up a virtual environment for the project
        4. Install dependencies from the requirements.txt file
        5. Verify the installation was successful
        
        Return a detailed report of the environment setup process.
        """
        
        return self.run(prompt)