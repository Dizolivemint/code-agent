# code_agent/cli.py
import argparse
import os
import sys
import textwrap
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import readline  # Add command history and editing

from .config import Config
from .agents.orchestrator import AgentOrchestrator
from .utils.logger import logger

def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text to specified width"""
    return "\n".join(textwrap.wrap(text, width=width))

def print_banner():
    """Print the application banner"""
    banner = """
    ╭───────────────────────────────────────╮
    │                                       │
    │            CODE AGENT                 │
    │                                       │
    │      AI-Powered Development Team      │
    │                                       │
    ╰───────────────────────────────────────╯
    """
    print(banner)

def init_command(args):
    """Initialize the Code Agent configuration"""
    config = Config()
    
    # Get GitHub token
    if args.github_token:
        github_token = args.github_token
    else:
        github_token = input("Enter your GitHub token (leave blank to skip): ").strip()
    
    # Get GitHub username
    if args.github_username:
        github_username = args.github_username
    else:
        github_username = input("Enter your GitHub username (leave blank to skip): ").strip()
    
    # Get GitHub repository
    if args.github_repo:
        github_repo = args.github_repo
    else:
        github_repo = input("Enter your GitHub repository name (leave blank to skip): ").strip()
    
    # Set GitHub config
    if github_token:
        config.github.token = github_token
    if github_username:
        config.github.username = github_username
    if github_repo:
        config.github.repository = github_repo
    
    # Save configuration
    config.save()
    
    print("\nConfiguration saved successfully!")
    print("You can now use Code Agent to build projects.")

def build_command(args):
    """Build a project from requirements"""
    config = Config()
    
    # Verify configuration
    if not config.validate():
        print("Error: Invalid configuration. Please run 'code-agent init' to set up your configuration.")
        return
    
    # Get requirements
    requirements = ""
    if args.requirements_file:
        try:
            with open(args.requirements_file, 'r') as f:
                requirements = f.read()
        except Exception as e:
            print(f"Error reading requirements file: {str(e)}")
            return
    else:
        print("Enter project requirements (press Ctrl+D on a new line when done):")
        try:
            requirements = sys.stdin.read().strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
    
    if not requirements:
        print("Error: No requirements provided.")
        return
    
    # Get project name
    project_name = args.project_name
    if not project_name:
        project_name = input("Enter project name: ").strip()
        if not project_name:
            print("Error: Project name is required.")
            return
    
    # Get project path
    project_path = args.output_dir
    if not project_path:
        project_path = input(f"Enter project directory path (default: ./{project_name}): ").strip()
        if not project_path:
            project_path = f"./{project_name}"
    
    # Create project directory if it doesn't exist
    os.makedirs(project_path, exist_ok=True)
    
    # Set up project configuration
    config.set_project(project_name, requirements, project_path)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config, project_path)
    
    print(f"\nBuilding project '{project_name}'...")
    print("This may take some time. Please be patient.")
    
    # Build the application
    result = orchestrator.build_application(requirements, project_name)
    
    print("\nProject build completed!")
    print(f"Project is available at: {os.path.abspath(project_path)}")

def chat_command(args):
    """Start a chat session with the Code Agent"""
    config = Config()
    
    # Verify configuration
    if not config.validate():
        print("Error: Invalid configuration. Please run 'code-agent init' to set up your configuration.")
        return
    
    # Get project path
    project_path = args.project_dir
    if not project_path:
        if config.project and config.project.root_dir:
            project_path = str(config.project.root_dir)
        else:
            project_path = input("Enter project directory path (default: current directory): ").strip()
            if not project_path:
                project_path = os.getcwd()
    
    if not os.path.exists(project_path):
        print(f"Error: Project directory '{project_path}' does not exist.")
        return
    
    # Set project path as current directory
    os.chdir(project_path)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config, project_path)
    
    print_banner()
    print("\nWelcome to Code Agent Chat!")
    print("You can ask the agent to perform development tasks.")
    print("Type 'exit' or 'quit' to end the session.")
    print("Type 'help' to see available commands.")
    print(f"Working directory: {os.path.abspath(project_path)}")
    
    # Chat loop
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  help           - Show this help message")
                print("  exit, quit     - Exit the chat session")
                print("  analyze        - Analyze project requirements")
                print("  implement      - Implement a feature")
                print("  test           - Create and run tests")
                print("  review         - Review code")
                print("\nYou can also type any natural language request.")
                continue
            
            if user_input.lower() == 'analyze':
                requirements = input("Enter project requirements: ").strip()
                if requirements:
                    print("\nAnalyzing requirements...")
                    result = orchestrator.analyze_requirements(requirements)
                    print(f"\nAnalysis result:\n{result}")
                continue
            
            if user_input.lower() == 'implement':
                feature_name = input("Enter feature name: ").strip()
                feature_description = input("Enter feature description: ").strip()
                if feature_name and feature_description:
                    print(f"\nImplementing feature '{feature_name}'...")
                    result = orchestrator.implement_feature(
                        feature_name, 
                        feature_description, 
                        "Use the filesystem tools to explore the project structure."
                    )
                    print(f"\nImplementation result:\n{result}")
                continue
            
            if user_input.lower() == 'test':
                feature_name = input("Enter feature name to test: ").strip()
                if feature_name:
                    print(f"\nCreating tests for feature '{feature_name}'...")
                    result = orchestrator.create_tests(
                        feature_name,
                        "Use the filesystem tools to explore the project structure and implementation."
                    )
                    print(f"\nTest result:\n{result}")
                continue
            
            if user_input.lower() == 'review':
                feature_name = input("Enter feature name to review: ").strip()
                if feature_name:
                    print(f"\nReviewing feature '{feature_name}'...")
                    result = orchestrator.review_code(
                        feature_name,
                        "Use the filesystem tools to explore the project structure and implementation.",
                        "Use the test tools to analyze test coverage."
                    )
                    print(f"\nReview result:\n{result}")
                continue
            
            # Process general request with the manager agent
            if user_input:
                print("\nProcessing your request...")
                result = orchestrator.agents["manager"].run(user_input)
                print(f"\nResult:\n{result}")
            
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            continue
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            logger.error(f"Error in chat command: {str(e)}", exc_info=True)

def feature_command(args):
    """Implement a specific feature"""
    config = Config()
    
    # Verify configuration
    if not config.validate():
        print("Error: Invalid configuration. Please run 'code-agent init' to set up your configuration.")
        return
    
    # Get project path
    project_path = args.project_dir
    if not project_path:
        if config.project and config.project.root_dir:
            project_path = str(config.project.root_dir)
        else:
            print("Error: Project directory not specified.")
            return
    
    if not os.path.exists(project_path):
        print(f"Error: Project directory '{project_path}' does not exist.")
        return
    
    # Get feature details
    feature_name = args.name
    if not feature_name:
        print("Error: Feature name is required.")
        return
    
    feature_description = args.description
    if not feature_description:
        feature_description = input("Enter feature description: ").strip()
        if not feature_description:
            print("Error: Feature description is required.")
            return
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config, project_path)
    
    print(f"\nImplementing feature '{feature_name}'...")
    print("This may take some time. Please be patient.")
    
    # Implement the feature
    result = orchestrator.implement_feature(
        feature_name, 
        feature_description, 
        "Use the filesystem tools to explore the project structure."
    )
    
    print("\nFeature implementation completed!")
    if args.test:
        print("\nCreating and running tests...")
        test_result = orchestrator.create_tests(feature_name, str(result))
        print("\nTests completed!")
        
        if args.review:
            print("\nReviewing implementation...")
            review_result = orchestrator.review_code(feature_name, str(result), str(test_result))
            print("\nReview completed!")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Code Agent - AI-Powered Development Team")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Code Agent configuration")
    init_parser.add_argument("--github-token", help="GitHub API token")
    init_parser.add_argument("--github-username", help="GitHub username")
    init_parser.add_argument("--github-repo", help="GitHub repository name")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build a project from requirements")
    build_parser.add_argument("--requirements-file", help="Path to requirements file")
    build_parser.add_argument("--project-name", help="Project name")
    build_parser.add_argument("--output-dir", help="Output directory for the project")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start a chat session with Code Agent")
    chat_parser.add_argument("--project-dir", help="Project directory path")
    
    # Feature command
    feature_parser = subparsers.add_parser("feature", help="Implement a specific feature")
    feature_parser.add_argument("--name", help="Feature name")
    feature_parser.add_argument("--description", help="Feature description")
    feature_parser.add_argument("--project-dir", help="Project directory path")
    feature_parser.add_argument("--test", action="store_true", help="Create and run tests after implementation")
    feature_parser.add_argument("--review", action="store_true", help="Review code after implementation")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_command(args)
    elif args.command == "build":
        build_command(args)
    elif args.command == "chat":
        chat_command(args)
    elif args.command == "feature":
        feature_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# code_agent/main.py
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
