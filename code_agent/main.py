import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .config import Config
from .agents.orchestrator import AgentOrchestrator
from .utils.logger import logger

class CodeAgentApp:
    """Main Code Agent application class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Code Agent application
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = Config(config_path)
        self.orchestrator = None
    
    def initialize(self, 
                  github_token: Optional[str] = None, 
                  github_username: Optional[str] = None,
                  github_repository: Optional[str] = None) -> None:
        """
        Initialize the application configuration
        
        Args:
            github_token: GitHub API token (optional)
            github_username: GitHub username (optional)
            github_repository: GitHub repository name (optional)
        """
        # Update GitHub configuration if provided
        if github_token:
            self.config.github.token = github_token
        if github_username:
            self.config.github.username = github_username
        if github_repository:
            self.config.github.repository = github_repository
        
        # Save configuration
        self.config.save()
        
        logger.info("Application initialized successfully")
    
    def set_project(self, name: str, description: str, root_dir: str) -> None:
        """
        Set the current project
        
        Args:
            name: Project name
            description: Project description
            root_dir: Project root directory
        """
        self.config.set_project(name, description, root_dir)
        
        # Initialize orchestrator if not already initialized
        if self.orchestrator is None:
            self.orchestrator = AgentOrchestrator(self.config, root_dir)
        else:
            # Update project path in orchestrator
            self.orchestrator.set_project_path(root_dir)
        
        logger.info(f"Project set to '{name}' at '{root_dir}'")
    
    def build_project(self, requirements: str, project_name: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Build a project from requirements
        
        Args:
            requirements: Project requirements text
            project_name: Project name
            output_dir: Output directory (optional)
            
        Returns:
            Build results
        """
        # Use provided output directory or create one based on project name
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), project_name)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set project
        self.set_project(project_name, requirements, output_dir)
        
        # Build the application
        result = self.orchestrator.build_application(requirements, project_name)
        
        logger.info(f"Project '{project_name}' built successfully at '{output_dir}'")
        
        return result
    
    def implement_feature(self, feature_name: str, feature_description: str) -> Dict[str, Any]:
        """
        Implement a specific feature
        
        Args:
            feature_name: Feature name
            feature_description: Feature description
            
        Returns:
            Implementation results
        """
        if not self.orchestrator:
            raise ValueError("Project not set. Call set_project first.")
        
        # Implement the feature
        result = self.orchestrator.implement_feature(
            feature_name, 
            feature_description, 
            "Use the filesystem tools to explore the project structure."
        )
        
        logger.info(f"Feature '{feature_name}' implemented successfully")
        
        return result
    
    def create_tests(self, feature_name: str, implementation_info: str) -> Dict[str, Any]:
        """
        Create tests for an implemented feature
        
        Args:
            feature_name: Feature name
            implementation_info: Information about the feature implementation
            
        Returns:
            Testing results
        """
        if not self.orchestrator:
            raise ValueError("Project not set. Call set_project first.")
        
        # Create tests
        result = self.orchestrator.create_tests(feature_name, implementation_info)
        
        logger.info(f"Tests created for feature '{feature_name}'")
        
        return result
    
    def review_code(self, feature_name: str, implementation_info: str, test_results: str) -> Dict[str, Any]:
        """
        Review code for an implemented feature
        
        Args:
            feature_name: Feature name
            implementation_info: Information about the feature implementation
            test_results: Results from testing the feature
            
        Returns:
            Review results
        """
        if not self.orchestrator:
            raise ValueError("Project not set. Call set_project first.")
        
        # Review code
        result = self.orchestrator.review_code(feature_name, implementation_info, test_results)
        
        logger.info(f"Code review completed for feature '{feature_name}'")
        
        return result
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Process a general request using the manager agent
        
        Args:
            request: User request text
            
        Returns:
            Processing results
        """
        if not self.orchestrator:
            raise ValueError("Project not set. Call set_project first.")
        
        # Process the request with the manager agent
        result = self.orchestrator.agents["manager"].run(request)
        
        logger.info("Request processed successfully")
        
        return result

# Function to simplify imports for users
def create_app(config_path: Optional[str] = None) -> CodeAgentApp:
    """
    Create and return a CodeAgentApp instance
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        CodeAgentApp instance
    """
    return CodeAgentApp(config_path) 
