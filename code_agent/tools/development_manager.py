from typing import Dict, Any, Optional, List, Union
import os
import json
from pathlib import Path
import logging
from datetime import datetime

from smolagents import CodeAgent, HfApiModel
from github import Github

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("code_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("code_agent")

class DevelopmentManager:
    """
    Development Manager that orchestrates the code generation workflow
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the development manager
        
        Args:
            config: Configuration dictionary with:
                - github_token: GitHub API token
                - github_username: GitHub username
                - model_id: Model ID for the agent
                - project_root: Root directory for project files
        """
        self.config = config
        self.project_root = config.get("project_root", os.getcwd())
        self.github_token = config.get("github_token", "")
        self.github_username = config.get("github_username", "")
        self.model_id = config.get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
        
        # Initialize the model
        from code_agent.models import ModelManager
        model_manager = ModelManager()
        self.model = model_manager.get_model(
            model_id=self.model_id,
            temperature=0.2, # Lower the temperature for more deterministic outputs
            max_tokens=4000
        )
        
        # Initialize agents and tools
        self._initialize_tools()
        self._initialize_agents()
        
        logger.info("Development Manager initialized")
    
    def _initialize_tools(self):
        """Initialize all tools required by the agents"""
        # Import all required tools
        from code_agent.tools.github_tools import create_github_tools
        from code_agent.tools.filesystem_tools import set_base_path, list_directory, read_file, create_directory, write_file
        from code_agent.tools.code_tools import set_project_path as set_code_project_path, analyze_code, format_code
        from code_agent.tools.test_tools import set_project_path as set_test_project_path, generate_test, run_tests
        
        # Set up GitHub tools
        self.github_tools = create_github_tools(
            token=self.github_token,
            username=self.github_username
        )
        
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Set base paths for all tools
        set_base_path(projects_dir)
        set_code_project_path(projects_dir)
        set_test_project_path(projects_dir)
        
        # Store tool references for agent initialization
        self.filesystem_tools = {
            "list_directory": list_directory,
            "read_file": read_file,
            "create_directory": create_directory,
            "write_file": write_file
        }
        
        self.code_tools = {
            "analyze_code": analyze_code,
            "format_code": format_code
        }
        
        self.test_tools = {
            "generate_test": generate_test,
            "run_tests": run_tests
        }
        
        logger.info("Tools initialized")
    
    def _initialize_agents(self):
        """Initialize specialized agents"""
        # Common imports for all agents
        common_imports = ["os", "pathlib", "json", "sys", "re"]
        
        # Architect agent tools and imports
        architect_tools = [
            self.filesystem_tools["list_directory"],
            self.filesystem_tools["read_file"],
            self.filesystem_tools["create_directory"],
            self.filesystem_tools["write_file"],
            self.code_tools["analyze_code"]
        ]
        architect_imports = common_imports + []
        
        # Developer agent tools and imports
        developer_tools = [
            self.filesystem_tools["list_directory"],
            self.filesystem_tools["read_file"],
            self.filesystem_tools["create_directory"],
            self.filesystem_tools["write_file"],
            self.code_tools["analyze_code"],
            self.code_tools["format_code"]
        ]
        developer_imports = common_imports + ["datetime", "typing"]
        
        # Tester agent tools and imports
        tester_tools = [
            self.filesystem_tools["list_directory"],
            self.filesystem_tools["read_file"],
            self.filesystem_tools["write_file"],
            self.test_tools["generate_test"],
            self.test_tools["run_tests"]
        ]
        tester_imports = common_imports + ["pytest", "unittest"]
        
        # Create the agents
        self.architect_agent = CodeAgent(
            model=self.model,
            tools=architect_tools,
            additional_authorized_imports=architect_imports,
            name="architect",
            description="Designs the overall system architecture and component relationships",
            max_steps=30,
            verbosity_level=1
        )
        
        self.developer_agent = CodeAgent(
            model=self.model,
            tools=developer_tools,
            additional_authorized_imports=developer_imports,
            name="developer",
            description="Implements code based on requirements and architecture designs",
            max_steps=30,
            verbosity_level=1
        )
        
        self.tester_agent = CodeAgent(
            model=self.model,
            tools=tester_tools,
            additional_authorized_imports=tester_imports,
            name="tester",
            description="Creates and runs tests to validate implemented code",
            max_steps=30,
            verbosity_level=1
        )
        
        logger.info("Agents initialized")
    
    def create_project(self, name: str, description: str, requirements: str, create_repo: bool = False) -> Dict[str, Any]:
        """
        Create a new project based on requirements
        
        Args:
            name: Project name
            description: Project description
            requirements: Detailed project requirements
            create_repo: Whether to create a GitHub repository
            
        Returns:
            Project details and status
        """
        logger.info(f"Creating project: {name}")
        
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Create project directory within projects directory
        project_dir = os.path.join(projects_dir, name.replace(" ", "_").lower())
        os.makedirs(project_dir, exist_ok=True)
        
        # Set the base path for filesystem tools to the project directory
        from code_agent.tools.filesystem_tools import set_base_path
        set_base_path(project_dir)
        
        # Create GitHub repository if requested
        repo_info = {}
        if create_repo and self.github_token and self.github_username:
            repo_info = self.github_tools.create_repository(
                name=name.replace(" ", "-").lower(),
                description=description,
                private=False
            )
            
            if repo_info.get("status") == "error":
                logger.error(f"Failed to create repository: {repo_info.get('message')}")
            else:
                logger.info(f"Created repository: {repo_info.get('repo_name')}")
                
                # Clone the repository
                clone_result = self.github_tools.clone_repository(project_dir)
                if clone_result.get("status") == "error":
                    logger.error(f"Failed to clone repository: {clone_result.get('message')}")
        
        # Save project requirements to a separate file
        project_requirements_path = os.path.join(project_dir, "project_requirements.md")
        with open(project_requirements_path, "w") as f:
            f.write(f"""# Project Requirements

## Project Name
{name}

## Description
{description}

## Requirements
{requirements}
""")
        
        # Generate project architecture using the architect agent
        try:
            architecture_result = self.architect_agent.run(
                f"""
                You are a senior software architect. You need to design a project architecture based on these requirements:
                
                PROJECT NAME: {name}
                DESCRIPTION: {description}
                
                REQUIREMENTS:
                {requirements}
                
                Follow these steps:
                
                1. Analyze the requirements and break them down into core features
                2. Define the main components and their responsibilities
                3. Create a directory structure that follows Python best practices
                4. Create essential files like README.md, setup.py, requirements.txt, etc.
                5. Define the data models needed
                6. Outline the API endpoints (if applicable)
                7. Determine required Python package dependencies and their versions
                
                IMPORTANT: Use the filesystem tools provided to you to create directories and files:
                - Use create_directory to create new directories
                - Use write_file to create and write content to files
                - DO NOT use direct os module calls
                
                The filesystem tools will automatically handle the correct base path and ensure files are created in the right location.
                
                Create the directory structure and essential files using the filesystem tools.
                Return a detailed architecture document that explains your design decisions.
                """
            )
            
        except Exception as e:
            logger.error(f"Failed to generate architecture: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to generate project architecture: {str(e)}",
                "project_dir": project_dir
            }
        
        # Extract features from the architecture result
        features = self._extract_features_from_results(architecture_result)
        
        # Create a development plan
        development_plan = {
            "name": name,
            "description": description,
            "repository": repo_info.get("repo_name", ""),
            "repository_url": repo_info.get("repo_url", ""),
            "features": features,
            "architecture": architecture_result,
            "project_dir": project_dir,
            "created_at": datetime.now().isoformat()
        }
        
        # Save development plan
        plan_path = os.path.join(project_dir, "development_plan.json")
        with open(plan_path, "w") as f:
            json.dump(development_plan, f, indent=2)
        
        logger.info(f"Project created at: {project_dir}")
        return development_plan
    
    def implement_feature(self, project_dir: str, feature: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement a specific feature
        
        Args:
            project_dir: Project directory
            feature: Feature details including name and description
            
        Returns:
            Implementation results
        """
        feature_name = feature.get("name", "")
        feature_description = feature.get("description", "")
        
        logger.info(f"Implementing feature: {feature_name}")
        
        # Create a branch for the feature
        branch_name = f"feature/{feature_name.lower().replace(' ', '-')}"
        
        # Create branch if we have GitHub tools set up
        if hasattr(self.github_tools, "repository") and self.github_tools.repository:
            branch_result = self.github_tools.create_branch(branch_name, "main")
            if branch_result.get("status") == "error":
                logger.error(f"Failed to create branch: {branch_result.get('message')}")
        
        # Get implementation from developer agent
        implementation_result = self.developer_agent.implement_feature(
            feature=feature,
            architecture=self.architecture,
            project_structure=self.project_structure
        )
        
        # Execute the implementation
        if "code" in implementation_result:
            execution_result = execute_code(implementation_result["code"])
            if execution_result["status"] == "error":
                # Send the error back to the developer agent
                error_prompt = f"""
                The following code generated an error when executed:
                
                ```python
                {execution_result["code"]}
                ```
                
                Error: {execution_result["error"]}
                
                Please fix the code and return the corrected version. Make sure to:
                1. Fix any syntax errors
                2. Handle all edge cases
                3. Include all necessary imports
                4. Fix any runtime errors
                
                Return only the corrected code with no additional explanation.
                """
                
                fixed_code = self.developer_agent.run(error_prompt)
                if "code" in fixed_code:
                    # Try executing the fixed code
                    execution_result = execute_code(fixed_code["code"])
                    if execution_result["status"] == "error":
                        logger.error(f"Failed to execute implementation after fix attempt: {execution_result['error']}")
                        return {
                            "status": "error",
                            "error": execution_result["error"],
                            "feature": feature
                        }
                    implementation_result["code"] = fixed_code["code"]
                else:
                    logger.error("Failed to get fixed code from developer agent")
                    return {
                        "status": "error",
                        "error": "Failed to fix code",
                        "feature": feature
                    }
        
        # Create tests for the implementation
        test_result = self.tester_agent.create_tests(
            feature=feature,
            implementation=implementation_result
        )
        
        # Run the tests
        if "test_code" in test_result:
            test_execution = execute_code(test_result["test_code"])
            if test_execution["status"] == "error":
                # Send the error back to the tester agent
                error_prompt = f"""
                The following test code generated an error when executed:
                
                ```python
                {test_execution["code"]}
                ```
                
                Error: {test_execution["error"]}
                
                Please fix the test code and return the corrected version. Make sure to:
                1. Fix any syntax errors
                2. Include all necessary imports
                3. Fix any runtime errors
                
                Return only the corrected code with no additional explanation.
                """
                
                fixed_code = self.tester_agent.run(error_prompt)
                if "code" in fixed_code:
                    # Try executing the fixed code
                    test_execution = execute_code(fixed_code["code"])
                    if test_execution["status"] == "error":
                        logger.error(f"Failed to execute tests after fix attempt: {test_execution['error']}")
                        return {
                            "status": "error",
                            "error": test_execution["error"],
                            "feature": feature,
                            "implementation": implementation_result
                        }
                    test_result["test_code"] = fixed_code["code"]
                else:
                    logger.error("Failed to get fixed code from tester agent")
                    return {
                        "status": "error",
                        "error": "Failed to fix test code",
                        "feature": feature,
                        "implementation": implementation_result
                    }
        
        # Commit changes if we have GitHub tools set up
        if hasattr(self.github_tools, "repository") and self.github_tools.repository:
            commit_result = self.github_tools.commit_changes(
                message=f"Implement {feature_name} feature with tests",
                branch=branch_name
            )
            
            if commit_result.get("status") == "error":
                logger.error(f"Failed to commit changes: {commit_result.get('message')}")
            else:
                # Create pull request
                pr_result = self.github_tools.create_pull_request(
                    title=f"Implement {feature_name}",
                    body=f"""
                    # Feature: {feature_name}
                    
                    {feature_description}
                    
                    ## Implementation Details
                    
                    {implementation_result.get('summary', 'Feature implemented successfully.')}
                    
                    ## Test Results
                    
                    {test_result.get('summary', 'Tests created and executed.')}
                    """,
                    head_branch=branch_name,
                    base_branch="main"
                )
                
                if pr_result.get("status") == "error":
                    logger.error(f"Failed to create pull request: {pr_result.get('message')}")
                else:
                    logger.info(f"Created pull request: {pr_result.get('pr_url')}")
        
        return {
            "status": "success",
            "feature": feature,
            "implementation": implementation_result,
            "tests": test_result
        }
    
    def build_project(self, name: str, description: str, requirements: str, create_repo: bool = False) -> Dict[str, Any]:
        """
        Build a complete project from requirements
        
        Args:
            name: Project name
            description: Project description
            requirements: Detailed project requirements
            create_repo: Whether to create a GitHub repository
            
        Returns:
            Project details and build results
        """
        # Create the project
        project = self.create_project(name, description, requirements, create_repo)
        
        # Implement each feature
        feature_results = []
        for feature in project.get("features", []):
            result = self.implement_feature(project.get("project_dir"), feature)
            feature_results.append(result)
        
        return {
            "project": project,
            "feature_results": feature_results
        }
    
    def _extract_features_from_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract features from agent results
        
        Args:
            results: Agent results
            
        Returns:
            List of features
        """
        # This is a simplified implementation - in a real system, you would 
        # parse the agent's output more thoroughly
        features = []
        
        # Try to find a features list in the results
        if isinstance(results, dict):
            if "features" in results:
                features = results["features"]
            elif "components" in results:
                # Convert components to features
                features = [{"name": comp, "description": "Component implementation"} for comp in results["components"]]
        
        # If we couldn't find features, create a default one
        if not features:
            features = [{"name": "Core Functionality", "description": "Implement core functionality based on requirements"}]
        
        return features
    
    def cleanup(self):
        """Clean up resources"""
        # Nothing to clean up in this implementation
        pass