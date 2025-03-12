#!/usr/bin/env python3
import argparse
import os
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

from .tools.development_manager import DevelopmentManager

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
    
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("code_agent_cli.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("code_agent_cli")

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    # Default config path
    if not config_path:
        config_path = os.path.join(str(Path.home()), ".code_agent", "config.json")
    
    # Default configuration
    config = {
        "github_token": os.environ.get("GITHUB_TOKEN", ""),
        "github_username": os.environ.get("GITHUB_USERNAME", ""),
        "model_id": os.environ.get("MODEL_ID", "meta-llama/Meta-Llama-3.1-70B-Instruct"),
        "project_root": os.environ.get("PROJECT_ROOT", os.getcwd())
    }
    
    # Load from file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
    
    return config

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to config file
    """
    # Default config path
    if not config_path:
        config_path = os.path.join(str(Path.home()), ".code_agent", "config.json")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Save config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {str(e)}")

def init_command(args):
    """Initialize Code Agent configuration"""
    print_banner()
    print("=== Code Agent Initialization ===")
    
    # Load existing config
    config = load_config(args.config)
    
    # Get GitHub token
    if args.github_token:
        github_token = args.github_token
    else:
        github_token = input(f"Enter your GitHub token (current: {config.get('github_token', '')[:4] + '...' if config.get('github_token') else 'None'}): ").strip()
        if not github_token:
            github_token = config.get("github_token", "")
    
    # Get GitHub username
    if args.github_username:
        github_username = args.github_username
    else:
        github_username = input(f"Enter your GitHub username (current: {config.get('github_username', 'None')}): ").strip()
        if not github_username:
            github_username = config.get("github_username", "")
    
    # Get model ID
    if args.model_id:
        model_id = args.model_id
    else:
        model_id = input(f"Enter model ID (current: {config.get('model_id', 'meta-llama/Meta-Llama-3.1-70B-Instruct')}): ").strip()
        if not model_id:
            model_id = config.get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
    
    # Get project root
    if args.project_root:
        project_root = args.project_root
    else:
        project_root = input(f"Enter project root directory (current: {config.get('project_root', os.getcwd())}): ").strip()
        if not project_root:
            project_root = config.get("project_root", os.getcwd())
    
    # Update config
    config.update({
        "github_token": github_token,
        "github_username": github_username,
        "model_id": model_id,
        "project_root": project_root
    })
    
    # Save config
    save_config(config, args.config)
    
    print("\nConfiguration saved successfully!")
    print(f"GitHub Token: {'✓ Set' if github_token else '✗ Not Set'}")
    print(f"GitHub Username: {github_username if github_username else '✗ Not Set'}")
    print(f"Model ID: {model_id}")
    print(f"Project Root: {project_root}")

def build_command(args):
    """Build a project from requirements"""
    print_banner()
    print("=== Code Agent Project Builder ===")
    
    # Load config
    config = load_config(args.config)
    
    # Check if GitHub token is set
    if not config.get("github_token") and args.create_repo:
        print("Warning: GitHub token not set. Repository creation disabled.")
        args.create_repo = False
    
    # Get project name
    project_name = args.name
    if not project_name:
        project_name = input("Enter project name: ").strip()
        if not project_name:
            print("Error: Project name is required.")
            return
    
    # Get project description
    project_description = args.description
    if not project_description:
        project_description = input("Enter project description: ").strip()
        if not project_description:
            print("Error: Project description is required.")
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
        print("Enter project requirements (finish with Ctrl+D on Unix or Ctrl+Z on Windows):")
        try:
            requirements_lines = []
            while True:
                try:
                    line = input()
                    requirements_lines.append(line)
                except EOFError:
                    break
            requirements = "\n".join(requirements_lines)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
    
    if not requirements:
        print("Error: No requirements provided.")
        return
    
    # Create development manager
    manager = DevelopmentManager(config)
    
    # Build project
    print(f"\nBuilding project '{project_name}'...")
    print("This may take some time. Please be patient.")
    
    result = manager.build_project(
        name=project_name,
        description=project_description,
        requirements=requirements,
        create_repo=args.create_repo
    )
    
    print("\nProject build completed!")
    print(f"Project directory: {result['project']['project_dir']}")
    
    if args.create_repo and result['project'].get('repository_url'):
        print(f"GitHub repository: {result['project']['repository_url']}")
    
    print(f"\nImplemented {len(result['feature_results'])} features:")
    for feature_result in result['feature_results']:
        feature = feature_result['feature']
        print(f"- {feature['name']}: {feature['description']}")

def feature_command(args):
    """Implement a specific feature"""
    print_banner()
    print("=== Code Agent Feature Implementation ===")
    
    # Load config
    config = load_config(args.config)
    
    # Get project directory
    project_dir = args.project_dir
    if not project_dir:
        project_dir = input("Enter project directory: ").strip()
        if not project_dir:
            print("Error: Project directory is required.")
            return
    
    if not os.path.exists(project_dir):
        print(f"Error: Project directory '{project_dir}' does not exist.")
        return
    
    # Get feature name
    feature_name = args.name
    if not feature_name:
        feature_name = input("Enter feature name: ").strip()
        if not feature_name:
            print("Error: Feature name is required.")
            return
    
    # Get feature description
    feature_description = args.description
    if not feature_description:
        feature_description = input("Enter feature description: ").strip()
        if not feature_description:
            print("Error: Feature description is required.")
            return
    
    # Create development manager
    manager = DevelopmentManager(config)
    
    # Implement feature
    print(f"\nImplementing feature '{feature_name}'...")
    print("This may take some time. Please be patient.")
    
    result = manager.implement_feature(
        project_dir=project_dir,
        feature={"name": feature_name, "description": feature_description}
    )
    
    print("\nFeature implementation completed!")
    
    if "implementation" in result and "tests" in result:
        print("\nImplementation Summary:")
        print(result["implementation"].get("summary", "Feature implemented successfully."))
        
        print("\nTest Summary:")
        print(result["tests"].get("summary", "Tests created and executed."))

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Code Agent - Build complete applications with AI")
    parser.add_argument("--config", help="Path to config file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Code Agent configuration")
    init_parser.add_argument("--github-token", help="GitHub API token")
    init_parser.add_argument("--github-username", help="GitHub username")
    init_parser.add_argument("--model-id", help="Model ID for the agent")
    init_parser.add_argument("--project-root", help="Root directory for project files")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build a project from requirements")
    build_parser.add_argument("--name", help="Project name")
    build_parser.add_argument("--description", help="Project description")
    build_parser.add_argument("--requirements-file", help="Path to requirements file")
    build_parser.add_argument("--create-repo", action="store_true", help="Create GitHub repository")
    
    # Feature command
    feature_parser = subparsers.add_parser("feature", help="Implement a specific feature")
    feature_parser.add_argument("--name", help="Feature name")
    feature_parser.add_argument("--description", help="Feature description")
    feature_parser.add_argument("--project-dir", help="Project directory")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_command(args)
    elif args.command == "build":
        build_command(args)
    elif args.command == "feature":
        feature_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()