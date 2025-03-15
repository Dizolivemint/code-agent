import os
from smolagents import CodeAgent, HfApiModel
from typing import List, Dict, Any, Optional, Union

from ..config import Config
from ..tools import github_tools, filesystem_tools, code_tools, test_tools
from ..utils.logger import logger

class AgentOrchestrator:
    """
    Orchestrator for managing multiple specialized agents
    """
    
    def __init__(self, config: Config, project_path: Optional[str] = None):
        """
        Initialize the agent orchestrator
        
        Args:
            config: Application configuration
            project_path: Path to the project directory (optional)
        """
        # Validate configuration first
        if not config.validate():
            logger.warning("Invalid configuration. GitHub integration may not work properly.")
            
        self.config = config
        self.project_path = project_path if project_path else os.getcwd()
        self.agents = {}
        self.tools_status = {
            "filesystem": False,
            "code": False,
            "test": False,
            "github": False
        }
        
        # Initialize tools
        self._init_tools()
        
        # Initialize specialized agents
        self._init_agents()
        
        logger.info(f"Agent Orchestrator initialized with project path: {self.project_path}")
    
    def _init_tools(self):
        """Initialize all tool sets with status tracking"""
        try:
            # Set project paths in all tool modules
            filesystem_tools.set_base_path(self.project_path)
            self.tools_status["filesystem"] = True
            
            code_tools.set_project_path(self.project_path)
            self.tools_status["code"] = True
            
            test_tools.set_project_path(self.project_path)
            self.tools_status["test"] = True
            
            # Initialize GitHub tools if credentials are available
            if self.config.github.token and self.config.github.username:
                try:
                    github_tools.initialize(
                        token=self.config.github.token,
                        username=self.config.github.username,
                        repository=self.config.github.repository
                    )
                    self.tools_status["github"] = True
                    logger.info("GitHub tools initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize GitHub tools: {str(e)}")
            else:
                logger.warning("GitHub credentials not provided. GitHub integration disabled.")
            
            # Log tools status
            initialized_tools = [k for k, v in self.tools_status.items() if v]
            logger.info(f"Tools initialized: {', '.join(initialized_tools)}")
            
        except Exception as e:
            logger.error(f"Error initializing tools: {str(e)}")
    
    def _init_agents(self):
        """Initialize specialized agents with validation"""
        try:
            # Validate that we have at least filesystem tools
            if not self.tools_status["filesystem"]:
                raise ValueError("Filesystem tools must be initialized before creating agents")
            
            # Create model instances for each agent
            from ..models import ModelManager
            model_manager = ModelManager()
            
            # Validate model IDs
            for agent_name, agent_config in self.config.agents.items():
                if not agent_config.model_id:
                    logger.warning(f"Model ID for {agent_name} agent is not specified")
            
            # Create model instances for each agent using the model manager
            models = {}
            try:
                for agent_name, agent_config in self.config.agents.items():
                    if agent_config.model_id:
                        models[agent_name] = model_manager.get_model(
                            model_id=agent_config.model_id,
                            provider=agent_config.provider,
                            temperature=agent_config.temperature,
                            max_tokens=agent_config.max_tokens
                        )
                logger.info("All models initialized successfully")
            except Exception as e:
                error_msg = f"Failed to initialize models: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Rest of the original _init_agents method
            # Architect agent tools
            architect_tools = [
                filesystem_tools.list_directory,
                filesystem_tools.read_file,
                filesystem_tools.write_file,
                filesystem_tools.create_directory,
                code_tools.analyze_code if self.tools_status["code"] else None
            ]
            architect_tools = [tool for tool in architect_tools if tool is not None]
            
            # Developer agent tools
            developer_tools = [
                filesystem_tools.list_directory,
                filesystem_tools.read_file,
                filesystem_tools.write_file,
                filesystem_tools.create_directory
            ]
            
            if self.tools_status["code"]:
                developer_tools.extend([
                    code_tools.analyze_code,
                    code_tools.format_code
                ])
            
            # Add GitHub tools if available
            if self.tools_status["github"]:
                developer_tools.extend([
                    github_tools.create_issue,
                    github_tools.create_branch,
                    github_tools.commit_changes,
                    github_tools.create_pull_request
                ])
            
            # Tester agent tools
            tester_tools = [
                filesystem_tools.list_directory,
                filesystem_tools.read_file,
                filesystem_tools.write_file
            ]
            
            if self.tools_status["test"]:
                tester_tools.extend([
                    test_tools.generate_test,
                    test_tools.run_tests,
                    test_tools.run_coverage
                ])
            
            # Reviewer agent tools
            reviewer_tools = [
                filesystem_tools.list_directory,
                filesystem_tools.read_file,
                filesystem_tools.write_file
            ]
            
            if self.tools_status["code"]:
                reviewer_tools.append(code_tools.analyze_code)
            
            # Add GitHub tools for reviewer if available
            if self.tools_status["github"]:
                reviewer_tools.extend([
                    github_tools.create_pull_request
                ])
            
            # Create the agents
            self.agents["architect"] = CodeAgent(
                model=models.get("architect"),
                tools=architect_tools,
                additional_authorized_imports=["os", "pathlib", "json", "sys", "re"],
                name="architect",
                description="Designs the overall system architecture and component relationships",
                max_steps=20,
                verbosity_level=1
            )
            
            self.agents["developer"] = CodeAgent(
                model=models.get("developer"),
                tools=developer_tools,
                additional_authorized_imports=["os", "pathlib", "json", "sys", "re", "datetime", "typing"],
                name="developer",
                description="Implements code based on requirements and architecture designs",
                max_steps=20,
                verbosity_level=1
            )
            
            self.agents["tester"] = CodeAgent(
                model=models.get("tester"),
                tools=tester_tools,
                additional_authorized_imports=["os", "pathlib", "json", "pytest", "unittest", "sys"],
                name="tester",
                description="Creates and runs tests to validate implemented code",
                max_steps=20,
                verbosity_level=1
            )
            
            self.agents["reviewer"] = CodeAgent(
                model=models.get("reviewer"),
                tools=reviewer_tools,
                additional_authorized_imports=["os", "pathlib", "json", "re"],
                name="reviewer",
                description="Reviews code quality and generates documentation",
                max_steps=20,
                verbosity_level=1
            )
            
            # Manager agent that can use all other agents
            self.agents["manager"] = CodeAgent(
                model=models.get("architect"),  # Use architect's model for manager
                tools=[],  # No direct tools, uses managed agents instead
                additional_authorized_imports=["os", "pathlib", "json", "sys"],
                name="manager",
                description="Manages and coordinates tasks between specialized agents",
                max_steps=20,
                verbosity_level=1,
                managed_agents=[
                    self.agents["architect"],
                    self.agents["developer"],
                    self.agents["tester"],
                    self.agents["reviewer"]
                ]
            )
            
            logger.info("All agents initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize agents: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def set_project_path(self, path: str) -> None:
        """
        Set the project path for all tools
        
        Args:
            path: New project path
        """
        # Validate the path
        if not os.path.exists(path):
            raise ValueError(f"Project path does not exist: {path}")
        
        # Ensure the path is either absolute or relative to the projects directory
        if not os.path.isabs(path):
            projects_dir = os.path.join(os.getcwd(), "projects")
            path = os.path.join(projects_dir, path)
        
        self.project_path = path
        
        # Update project path in tools
        filesystem_tools.set_base_path(path)
        code_tools.set_project_path(path)
        test_tools.set_project_path(path)
        
        logger.info(f"Project path updated to: {path}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all tests in the project
        
        Returns:
            Test results
        """
        if not self.tools_status["test"]:
            logger.warning("Test tools not available")
            return {"status": "error", "message": "Test tools not available"}
        
        logger.info("Running all tests in the project")
        
        # Find test directory or files
        test_files = []
        
        # Check for common test directories
        for test_dir in ["tests", "test"]:
            test_path = os.path.join(self.project_path, test_dir)
            if os.path.isdir(test_path):
                test_files.append(test_path)
                break
        
        # If no test directory found, look for test files
        if not test_files:
            for root, _, files in os.walk(self.project_path):
                for file in files:
                    if file.startswith("test_") and file.endswith(".py"):
                        test_files.append(os.path.join(root, file))
        
        # Run tests if found
        if test_files:
            logger.info(f"Found {len(test_files)} test files/directories")
            
            all_results = {}
            for test_file in test_files:
                logger.info(f"Running tests in: {test_file}")
                result = test_tools.run_tests(test_file)
                all_results[test_file] = result
            
            # Calculate overall summary
            total_tests = 0
            total_passed = 0
            total_failed = 0
            
            for result in all_results.values():
                if isinstance(result, dict) and "summary" in result:
                    summary = result["summary"]
                    total_tests += summary.get("total", 0)
                    total_passed += summary.get("passed", 0)
                    total_failed += summary.get("failed", 0)
            
            return {
                "test_files": test_files,
                "detailed_results": all_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed": total_passed,
                    "failed": total_failed,
                    "success_rate": f"{(total_passed / total_tests * 100) if total_tests > 0 else 0:.2f}%"
                }
            }
        else:
            logger.warning("No tests found in the project")
            return {
                "test_files": [],
                "detailed_results": {},
                "summary": "No tests found in the project"
            }