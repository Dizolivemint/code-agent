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
        
        # Validate configuration during initialization
        if not self.config.validate():
            logger.warning("Configuration is incomplete. Please run initialization.")
    
    def initialize(self, 
                  github_token: Optional[str] = None, 
                  github_username: Optional[str] = None,
                  github_repository: Optional[str] = None) -> bool:
        """
        Initialize the application configuration
        
        Args:
            github_token: GitHub API token (optional)
            github_username: GitHub username (optional)
            github_repository: GitHub repository name (optional)
            
        Returns:
            True if initialization was successful, False otherwise
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
        
        # Validate configuration after updates
        if not self.config.validate():
            logger.error("Configuration is still incomplete after initialization.")
            return False
            
        logger.info("Application initialized successfully")
        return True
    
    def set_project(self, name: str, description: str, root_dir: str) -> None:
        """
        Set the current project
        
        Args:
            name: Project name
            description: Project description
            root_dir: Project root directory
        """
        # Validate project directory
        if not os.path.exists(root_dir):
            error_msg = f"Project directory does not exist: {root_dir}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Check if we have write permissions
        if not os.access(root_dir, os.W_OK):
            error_msg = f"No write permission for project directory: {root_dir}"
            logger.error(error_msg)
            raise PermissionError(error_msg)
        
        self.config.set_project(name, description, root_dir)
        
        # Initialize orchestrator if not already initialized
        if self.orchestrator is None:
            self.orchestrator = AgentOrchestrator(self.config, root_dir)
        else:
            # Update project path in orchestrator
            self.orchestrator.set_project_path(root_dir)
        
        logger.info(f"Project set to '{name}' at '{root_dir}'")
    
    def _ensure_project_set(self) -> None:
        """
        Ensure that a project is set before performing operations
        
        Raises:
            ValueError: If no project is set
        """
        if not self.orchestrator:
            raise ValueError("Project not set. Call set_project first.")
    
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
        # Use provided output directory or create one based on project name in the projects directory
        if not output_dir:
            projects_dir = os.path.join(os.getcwd(), "projects")
            output_dir = os.path.join(projects_dir, project_name)
        
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
        # Ensure project is set
        self._ensure_project_set()
        
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
        # Ensure project is set
        self._ensure_project_set()
        
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
        # Ensure project is set
        self._ensure_project_set()
        
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
        # Ensure project is set
        self._ensure_project_set()
        
        # Process the request with the manager agent
        result = self.orchestrator.agents["manager"].run(request)
        
        logger.info("Request processed successfully")
        
        return result
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run all tests in the project
        
        Returns:
            Test results
        """
        # Ensure project is set
        self._ensure_project_set()
        
        # Run tests
        result = self.orchestrator.run_all_tests()
        
        logger.info("All tests completed")
        
        return result
    
    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate the environment for all required dependencies
        
        Returns:
            Validation results
        """
        results = {
            "config_valid": self.config.validate(),
            "github_configured": bool(self.config.github.token and self.config.github.username),
            "project_set": self.config.project is not None,
            "dependencies_installed": self._check_dependencies()
        }
        
        return results
    
    def _check_dependencies(self) -> bool:
        """
        Check if all required Python packages are installed
        
        Returns:
            True if all dependencies are installed, False otherwise
        """
        required_packages = [
            "smolagents",
            "pygithub",
            "pytest",
            "python-dotenv"
        ]
        
        try:
            import pkg_resources
            pkg_resources.require(required_packages)
            return True
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            return False


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