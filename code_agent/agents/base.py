# code_agent/agents/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from smolagents import CodeAgent, HfApiModel

class BaseSpecializedAgent(ABC):
    """Base class for specialized agents"""
    
    def __init__(self, name: str, model: HfApiModel, tools: List[Any], imports: List[str]):
        """
        Initialize base specialized agent
        
        Args:
            name: Agent name
            model: HfApiModel instance
            tools: List of tools
            imports: List of additional authorized imports
        """
        self.name = name
        self.model = model
        self.tools = tools
        self.imports = imports
        self.agent = self._create_agent()
    
    def _create_agent(self) -> CodeAgent:
        """Create the CodeAgent instance"""
        return CodeAgent(
            model=self.model,
            tools=self.tools,
            additional_authorized_imports=self.imports,
            name=self.name,
            description=self.get_description(),
            max_steps=20,
            verbosity_level=1
        )
    
    @abstractmethod
    def get_description(self) -> str:
        """Return the agent description"""
        pass
    
    def run(self, prompt: str) -> Any:
        """
        Run the agent with a prompt
        
        Args:
            prompt: The prompt to run
            
        Returns:
            Agent response
        """
        return self.agent.run(prompt)

# code_agent/agents/architect.py
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

# code_agent/agents/developer.py
from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class DeveloperAgent(BaseSpecializedAgent):
    """Agent specialized in code implementation"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize developer agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "sys", "re", "datetime", "typing"]
        super().__init__("developer", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Implements code based on requirements and architecture designs. "
            "Specializes in writing clean, efficient, and maintainable code "
            "with proper error handling and documentation."
        )
    
    def implement_feature(
        self, 
        feature: Dict[str, Any], 
        architecture: Dict[str, Any], 
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Implement a feature
        
        Args:
            feature: Feature details
            architecture: Architecture information
            project_structure: Project structure information
            
        Returns:
            Implementation result
        """
        prompt = f"""
        You are a senior software developer. Implement the following feature for our project:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        Priority: {feature['priority']}
        Complexity: {feature['complexity']}
        
        PROJECT ARCHITECTURE:
        {architecture}
        
        PROJECT STRUCTURE:
        {project_structure}
        
        Please:
        1. Determine which files need to be created or modified
        2. Implement the feature with high-quality code
        3. Ensure proper error handling
        4. Add comprehensive docstrings and comments
        5. Follow PEP 8 style guidelines
        6. Make your code testable
        
        For each file you create or modify:
        1. First check if it exists using file_exists or directory_exists
        2. If it exists and you need to modify it, read it first
        3. Create/update the file with your implementation
        
        After implementing the feature, create a branch and commit your changes if GitHub tools are available.
        """
        
        return self.run(prompt)

# code_agent/agents/tester.py
from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class TesterAgent(BaseSpecializedAgent):
    """Agent specialized in testing"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize tester agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "pytest", "unittest", "sys"]
        super().__init__("tester", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Creates and runs tests to validate implemented code. "
            "Specializes in writing comprehensive test suites that cover "
            "both normal cases and edge cases to ensure code quality."
        )
    
    def create_tests(self, feature: Dict[str, Any], implementation_files: List[str]) -> Dict[str, Any]:
        """
        Create tests for a feature
        
        Args:
            feature: Feature details
            implementation_files: List of files implemented for the feature
            
        Returns:
            Testing results
        """
        files_str = "\n".join([f"- {file}" for file in implementation_files])
        
        prompt = f"""
        You are a senior QA engineer. Create comprehensive tests for the following feature:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        
        IMPLEMENTATION FILES:
        {files_str}
        
        Please:
        1. Examine each implementation file to understand what needs to be tested
        2. Create appropriate test files using pytest
        3. Write tests for both normal cases and edge cases
        4. Test error handling
        5. Run the tests and report results
        6. Calculate test coverage
        
        For each implementation file:
        1. Create a corresponding test file
        2. Ensure test functions follow pytest naming conventions
        3. Add appropriate assertions
        4. Include test fixtures if needed
        
        Use the test tools to generate, run, and analyze tests.
        """
        
        return self.run(prompt)

# code_agent/agents/reviewer.py
from typing import List, Dict, Any, Optional
from smolagents import HfApiModel

from .base import BaseSpecializedAgent

class ReviewerAgent(BaseSpecializedAgent):
    """Agent specialized in code review and documentation"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize reviewer agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "re"]
        super().__init__("reviewer", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Reviews code quality and generates documentation. "
            "Specializes in identifying potential issues, suggesting improvements, "
            "and ensuring code meets best practices and standards."
        )
    
    def review_code(
        self, 
        feature: Dict[str, Any], 
        implementation_files: List[str], 
        test_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review code for a feature
        
        Args:
            feature: Feature details
            implementation_files: List of files implemented for the feature
            test_results: Results from testing
            
        Returns:
            Review results
        """
        files_str = "\n".join([f"- {file}" for file in implementation_files])
        
        prompt = f"""
        You are a senior code reviewer. Review the implementation of the following feature:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        
        IMPLEMENTATION FILES:
        {files_str}
        
        TEST RESULTS:
        {test_results}
        
        Please perform a comprehensive code review:
        1. Check each file for:
           - Code quality and adherence to PEP 8
           - Potential bugs or edge cases
           - Documentation and docstrings
           - Design patterns and architecture
           - Performance issues
        2. Suggest specific improvements
        3. Highlight any security concerns
        4. Review test coverage and completeness
        
        For each file, read its content first, then provide detailed feedback.
        
        After reviewing, create a pull request if GitHub tools are available.
        """
        
        return self.run(prompt) 
