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
        imports = ["os", "pathlib", "json", "re", "ast", "inspect"]
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
    
    def generate_documentation(
        self,
        feature: Dict[str, Any],
        implementation_files: List[str]
    ) -> Dict[str, Any]:
        """
        Generate documentation for a feature
        
        Args:
            feature: Feature details
            implementation_files: List of files implemented for the feature
            
        Returns:
            Documentation results
        """
        files_str = "\n".join([f"- {file}" for file in implementation_files])
        
        prompt = f"""
        You are a technical documentation specialist. Generate comprehensive documentation for the following feature:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        
        IMPLEMENTATION FILES:
        {files_str}
        
        Please:
        1. Extract relevant information from each file
        2. Document the feature's architecture and design decisions
        3. Create usage examples
        4. Document public APIs and interfaces
        5. Identify any configuration or environment requirements
        
        For each file, read its content first to understand the implementation.
        
        Generate the documentation in Markdown format and save it to an appropriate location in the docs directory.
        """
        
        return self.run(prompt)
    
    def create_pull_request(
        self,
        feature: Dict[str, Any],
        branch_name: str,
        review_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a pull request for a feature
        
        Args:
            feature: Feature details
            branch_name: Name of the feature branch
            review_results: Results from code review
            
        Returns:
            Pull request results
        """
        prompt = f"""
        You are a DevOps engineer. Create a pull request for the following feature:
        
        FEATURE:
        Name: {feature['name']}
        Description: {feature['description']}
        
        BRANCH:
        {branch_name}
        
        REVIEW RESULTS:
        {review_results}
        
        Please:
        1. Create a detailed pull request title and description
        2. Include a summary of changes made
        3. Reference any issues addressed by this PR
        4. Highlight test coverage and results
        5. Note any important implementation details or design decisions
        
        Use the GitHub tools to create the pull request from the feature branch to the main branch.
        """
        
        return self.run(prompt)
    
    def check_security_issues(
        self,
        implementation_files: List[str]
    ) -> Dict[str, Any]:
        """
        Check for security issues in implemented code
        
        Args:
            implementation_files: List of files to check
            
        Returns:
            Security analysis results
        """
        files_str = "\n".join([f"- {file}" for file in implementation_files])
        
        prompt = f"""
        You are a security analyst. Check the following files for security issues:
        
        IMPLEMENTATION FILES:
        {files_str}
        
        Please:
        1. Identify any potential security vulnerabilities
           - Input validation issues
           - Authentication flaws
           - Authorization problems
           - Data exposure risks
           - Injection vulnerabilities
           - Cryptographic issues
        2. Suggest specific fixes for each issue
        3. Rate the severity of each issue (low, medium, high, critical)
        
        For each file, read its content first to understand the implementation.
        
        Provide a comprehensive security analysis report.
        """
        
        return self.run(prompt)
    
    def review_project_architecture(
        self,
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Review the overall project architecture
        
        Args:
            project_structure: Project structure details
            
        Returns:
            Architecture review results
        """
        prompt = f"""
        You are a software architect. Review the overall project architecture:
        
        PROJECT STRUCTURE:
        {project_structure}
        
        Please:
        1. Evaluate the overall architecture
           - Component organization
           - Separation of concerns
           - Modularity
           - Dependency management
        2. Identify any architectural issues or anti-patterns
        3. Suggest improvements to enhance maintainability and scalability
        4. Assess the project's adherence to design principles (SOLID, DRY, etc.)
        
        Provide a detailed architecture review with specific recommendations.
        """
        
        return self.run(prompt)
    
    def generate_api_documentation(
        self,
        api_files: List[str]
    ) -> Dict[str, Any]:
        """
        Generate API documentation for REST APIs or libraries
        
        Args:
            api_files: List of API implementation files
            
        Returns:
            API documentation results
        """
        files_str = "\n".join([f"- {file}" for file in api_files])
        
        prompt = f"""
        You are an API documentation specialist. Generate comprehensive API documentation for the following files:
        
        API FILES:
        {files_str}
        
        Please:
        1. Extract API endpoints, parameters, and return values
        2. Document request and response formats
        3. Provide usage examples for each endpoint
        4. Note any authentication or authorization requirements
        5. Document error responses and status codes
        
        For each file, read its content first to understand the implementation.
        
        Generate the API documentation in Markdown format and save it to the docs/api directory.
        """
        
        return self.run(prompt) 
