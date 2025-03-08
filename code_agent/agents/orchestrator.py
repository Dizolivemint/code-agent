# code_agent/agents/orchestrator.py
from smolagents import CodeAgent, HfApiModel, tool
from typing import List, Dict, Any, Optional, Union, Callable
import os
import json

from ..config import Config
from ..tools.github_tools import GitHubTools
from ..tools.filesystem_tools import FilesystemTools
from ..tools.code_tools import CodeTools
from ..tools.test_tools import TestTools
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
        self.tools = {}
        
        # Initialize tool sets
        self._init_tools()
        
        # Initialize specialized agents
        self._init_agents()
    
    def _init_tools(self):
        """Initialize all tool sets"""
        # GitHub tools
        if self.config.github.token and self.config.github.username:
            self.tools["github"] = GitHubTools(
                token=self.config.github.token,
                username=self.config.github.username,
                repository=self.config.github.repository
            )
        
        # Filesystem tools
        self.tools["filesystem"] = FilesystemTools(base_path=self.project_path)
        
        # Code tools
        self.tools["code"] = CodeTools(project_path=self.project_path)
        
        # Test tools
        self.tools["test"] = TestTools(project_path=self.project_path)
    
    def _init_agents(self):
        """Initialize specialized agents"""
        # Create model instances for each agent
        models = {}
        for agent_name, agent_config in self.config.agents.items():
            models[agent_name] = HfApiModel(
                model_id=agent_config.model_id,
                provider=agent_config.provider,
                temperature=agent_config.temperature,
                max_tokens=agent_config.max_tokens
            )
        
        # Architect agent - responsible for system design and architecture
        self.agents["architect"] = self._create_agent(
            name="architect",
            description="Designs the overall system architecture and component relationships",
            model=models.get("architect"),
            tools=[
                self.tools["filesystem"].list_directory,
                self.tools["filesystem"].read_file,
                self.tools["filesystem"].write_file,
                self.tools["filesystem"].create_directory,
                self.tools["code"].analyze_code,
                self.tools["code"].extract_imports
            ],
            imports=["os", "pathlib", "json"]
        )
        
        # Developer agent - responsible for code implementation
        self.agents["developer"] = self._create_agent(
            name="developer",
            description="Implements code based on requirements and architecture",
            model=models.get("developer"),
            tools=[
                self.tools["filesystem"].list_directory,
                self.tools["filesystem"].read_file,
                self.tools["filesystem"].write_file,
                self.tools["filesystem"].create_directory,
                self.tools["code"].analyze_code,
                self.tools["code"].format_code,
                self.tools["code"].lint_code,
                self.tools["code"].execute_code,
                self.tools["github"].commit_changes if "github" in self.tools else None
            ],
            imports=["os", "pathlib", "json", "sys", "re"]
        )
        
        # Tester agent - responsible for testing
        self.agents["tester"] = self._create_agent(
            name="tester",
            description="Creates and runs tests to validate implemented code",
            model=models.get("tester"),
            tools=[
                self.tools["filesystem"].list_directory,
                self.tools["filesystem"].read_file,
                self.tools["filesystem"].write_file,
                self.tools["test"].generate_test,
                self.tools["test"].run_tests,
                self.tools["test"].run_coverage,
                self.tools["test"].generate_test_suite
            ],
            imports=["os", "pathlib", "json", "pytest"]
        )
        
        # Reviewer agent - responsible for code review and documentation
        self.agents["reviewer"] = self._create_agent(
            name="reviewer",
            description="Reviews code quality and generates documentation",
            model=models.get("reviewer"),
            tools=[
                self.tools["filesystem"].list_directory,
                self.tools["filesystem"].read_file,
                self.tools["filesystem"].write_file,
                self.tools["code"].analyze_code,
                self.tools["code"].lint_code,
                self.tools["code"].extract_docstrings,
                self.tools["github"].create_pull_request if "github" in self.tools else None
            ],
            imports=["os", "pathlib", "json"]
        )
        
        # Manager agent - orchestrates all other agents
        self.agents["manager"] = self._create_agent(
            name="manager",
            description="Manages and coordinates tasks between specialized agents",
            model=models.get("architect"),  # Use architect's model for manager
            tools=[],  # No direct tools, uses managed agents instead
            imports=["os", "pathlib", "json", "sys"],
            managed_agents=[
                self.agents["architect"],
                self.agents["developer"],
                self.agents["tester"],
                self.agents["reviewer"]
            ]
        )
    
    def _create_agent(
        self, 
        name: str, 
        description: str, 
        model: HfApiModel,
        tools: List[Callable], 
        imports: List[str],
        managed_agents: Optional[List[CodeAgent]] = None
    ) -> CodeAgent:
        """
        Create a specialized agent
        
        Args:
            name: Agent name
            description: Agent description
            model: HfApiModel instance
            tools: List of tools
            imports: List of additional authorized imports
            managed_agents: List of managed agents (optional)
            
        Returns:
            CodeAgent instance
        """
        # Filter out None tools (in case GitHub tools aren't available)
        tools = [tool for tool in tools if tool is not None]
        
        agent = CodeAgent(
            model=model,
            tools=tools,
            additional_authorized_imports=imports,
            name=name,
            description=description,
            max_steps=20,
            verbosity_level=1,
            managed_agents=managed_agents
        )
        
        return agent
    
    def set_project_path(self, path: str) -> None:
        """
        Set the project path for all tools
        
        Args:
            path: New project path
        """
        self.project_path = path
        
        # Update project path in tools
        if "filesystem" in self.tools:
            self.tools["filesystem"].set_base_path(path)
        
        if "code" in self.tools:
            self.tools["code"].set_project_path(path)
        
        if "test" in self.tools:
            self.tools["test"].set_project_path(path)
    
    def set_github_repository(self, repository: str) -> None:
        """
        Set the GitHub repository for GitHub tools
        
        Args:
            repository: GitHub repository name
        """
        if "github" in self.tools:
            self.tools["github"].set_repository(repository)
    
    def analyze_requirements(self, requirements: str) -> Dict[str, Any]:
        """
        Analyze project requirements using the architect agent
        
        Args:
            requirements: Project requirements text
            
        Returns:
            Analysis results including features and architecture
        """
        prompt = f"""
        Please analyze the following project requirements and break them down into:
        1. Core features
        2. Component architecture
        3. Data structures
        4. API endpoints (if applicable)
        5. External dependencies
        
        REQUIREMENTS:
        {requirements}
        
        Your output should be a comprehensive analysis that will guide the development team.
        Be specific about:
        - How components should interact
        - Which design patterns to use
        - Directory structure recommendations
        - Any potential technical challenges
        """
        
        result = self.agents["architect"].run(prompt)
        return result
    
    def design_architecture(self, requirements: str, project_name: str) -> Dict[str, Any]:
        """
        Design the project architecture using the architect agent
        
        Args:
            requirements: Project requirements text
            project_name: Name of the project
            
        Returns:
            Architecture design including directory structure and component relationships
        """
        prompt = f"""
        Design a complete architecture for the following project:
        
        Project Name: {project_name}
        
        REQUIREMENTS:
        {requirements}
        
        Please provide a comprehensive architecture design that includes:
        1. Directory structure (create actual directories using filesystem tools)
        2. Key components and their relationships
        3. Data flow diagrams (described in text)
        4. Technology stack decisions
        5. Design patterns to implement
        
        After designing the architecture, create the base project structure by:
        1. Creating necessary directories
        2. Creating basic package files (like __init__.py)
        3. Creating a basic README.md with project overview
        4. Creating a setup.py or pyproject.toml file
        
        Make sure to implement a proper Python package structure and follow best practices.
        """
        
        result = self.agents["architect"].run(prompt)
        return result
    
    def implement_feature(self, feature_name: str, feature_description: str, architecture_info: str) -> Dict[str, Any]:
        """
        Implement a specific feature using the developer agent
        
        Args:
            feature_name: Name of the feature
            feature_description: Detailed description of the feature
            architecture_info: Information about the project architecture
            
        Returns:
            Implementation results including created/modified files
        """
        prompt = f"""
        Implement the following feature for our project:
        
        Feature Name: {feature_name}
        
        Feature Description:
        {feature_description}
        
        Project Architecture Information:
        {architecture_info}
        
        Please follow these steps:
        1. Determine which files need to be created or modified
        2. Implement the feature with high-quality code
        3. Ensure proper error handling and edge cases
        4. Add comprehensive docstrings and comments
        5. Use code analysis tools to verify quality
        
        If GitHub tools are available, create a feature branch and commit your changes.
        If not, just implement the code locally.
        
        Make sure your implementation integrates well with the existing codebase and follows the project architecture.
        """
        
        result = self.agents["developer"].run(prompt)
        return result
    
    def create_tests(self, feature_name: str, implementation_info: str) -> Dict[str, Any]:
        """
        Create tests for an implemented feature using the tester agent
        
        Args:
            feature_name: Name of the feature
            implementation_info: Information about the feature implementation
            
        Returns:
            Testing results including created test files and test runs
        """
        prompt = f"""
        Create comprehensive tests for the following feature:
        
        Feature Name: {feature_name}
        
        Implementation Information:
        {implementation_info}
        
        Please follow these steps:
        1. Analyze the implementation to identify components to test
        2. Create unit tests for all functions and classes
        3. Create integration tests if needed
        4. Run the tests and report results
        5. Calculate test coverage
        
        Make sure to:
        - Test both normal cases and edge cases
        - Test error handling
        - Aim for high test coverage
        - Use pytest best practices
        
        Generate tests, run them, and report the results in detail.
        """
        
        result = self.agents["tester"].run(prompt)
        return result
    
    def review_code(self, feature_name: str, implementation_info: str, test_results: str) -> Dict[str, Any]:
        """
        Review code for an implemented feature using the reviewer agent
        
        Args:
            feature_name: Name of the feature
            implementation_info: Information about the feature implementation
            test_results: Results from testing the feature
            
        Returns:
            Review results including suggested improvements and documentation
        """
        prompt = f"""
        Review the implementation of the following feature:
        
        Feature Name: {feature_name}
        
        Implementation Information:
        {implementation_info}
        
        Test Results:
        {test_results}
        
        Please perform a comprehensive code review:
        1. Check code quality and adherence to best practices
        2. Look for potential bugs or edge cases not covered
        3. Review documentation and docstrings
        4. Suggest improvements and optimizations
        5. Verify test coverage is adequate
        
        If improvements are needed, please suggest specific changes.
        If GitHub tools are available, create a pull request with your review.
        
        Provide a detailed review report that summarizes your findings and recommendations.
        """
        
        result = self.agents["reviewer"].run(prompt)
        return result
    
    def build_application(self, requirements: str, project_name: str) -> Dict[str, Any]:
        """
        Build a complete application using all agents
        
        Args:
            requirements: Project requirements text
            project_name: Name of the project
            
        Returns:
            Build results including all steps of the development process
        """
        # Use the manager agent to orchestrate the entire process
        prompt = f"""
        Build a complete Python application based on the following requirements:
        
        Project Name: {project_name}
        
        REQUIREMENTS:
        {requirements}
        
        You are the project manager responsible for coordinating all agents:
        1. Use the architect agent to design the system architecture
        2. Break down the requirements into individual features
        3. For each feature:
           a. Use the developer agent to implement it
           b. Use the tester agent to create and run tests
           c. Use the reviewer agent to review the code
        4. Ensure all components work together cohesively
        
        Follow these steps:
        1. First, use the architect agent to design the project structure
        2. Have the architect agent create the base project structure
        3. Identify features from the requirements
        4. For each feature:
           a. Have the developer agent implement it
           b. Have the tester agent test it
           c. Have the reviewer agent review it
           d. Address any issues identified in review
        5. Once all features are complete, ensure the application works as a whole
        
        Your goal is to deliver a fully functional, well-tested, and documented application.
        """
        
        result = self.agents["manager"].run(prompt)
        return result 
