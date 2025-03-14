# orchestrator.py
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
        self.config = config
        self.project_path = project_path if project_path else os.getcwd()
        self.agents = {}
        
        # Initialize tools
        self._init_tools()
        
        # Initialize specialized agents
        self._init_agents()
    
    def _init_tools(self):
        """Initialize all tool sets"""
        # Set project paths in all tool modules
        filesystem_tools.set_base_path(self.project_path)
        code_tools.set_project_path(self.project_path)
        test_tools.set_project_path(self.project_path)
        
        # Initialize GitHub tools if credentials are available
        if self.config.github.token and self.config.github.username:
            github_tools.initialize(
                token=self.config.github.token,
                username=self.config.github.username,
                repository=self.config.github.repository
            )
    
    def _init_agents(self):
        """Initialize specialized agents"""
        # Create model instances for each agent
        from ..models import ModelManager
        model_manager = ModelManager()
        
        # Create model instances for each agent using the model manager
        models = {}
        for agent_name, agent_config in self.config.agents.items():
            models[agent_name] = model_manager.get_model(
                model_id=agent_config.model_id,
                provider=agent_config.provider,
                temperature=agent_config.temperature,
                max_tokens=agent_config.max_tokens
            )
        
        # Architect agent tools
        architect_tools = [
            filesystem_tools.list_directory,
            filesystem_tools.read_file,
            filesystem_tools.write_file,
            filesystem_tools.create_directory,
            code_tools.analyze_code,
            code_tools.extract_imports
        ]
        
        # Developer agent tools
        developer_tools = [
            filesystem_tools.list_directory,
            filesystem_tools.read_file,
            filesystem_tools.write_file,
            filesystem_tools.create_directory,
            code_tools.analyze_code,
            code_tools.format_code,
            code_tools.lint_code,
            code_tools.execute_code
        ]
        
        # Add GitHub tools if available
        if self.config.github.token:
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
            filesystem_tools.write_file,
            test_tools.generate_test,
            test_tools.run_tests,
            test_tools.run_coverage
        ]
        
        # Reviewer agent tools
        reviewer_tools = [
            filesystem_tools.list_directory,
            filesystem_tools.read_file,
            filesystem_tools.write_file,
            code_tools.analyze_code,
            code_tools.lint_code,
            code_tools.extract_docstrings
        ]
        
        # Add GitHub tools for reviewer if available
        if self.config.github.token:
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
    
    def set_project_path(self, path: str) -> None:
        """
        Set the project path for all tools
        
        Args:
            path: New project path
        """
        # Ensure the path is either absolute or relative to the projects directory
        if not os.path.isabs(path):
            projects_dir = os.path.join(os.getcwd(), "projects")
            path = os.path.join(projects_dir, path)
        
        self.project_path = path
        
        # Update project path in tools
        filesystem_tools.set_base_path(path)
        code_tools.set_project_path(path)
        test_tools.set_project_path(path)