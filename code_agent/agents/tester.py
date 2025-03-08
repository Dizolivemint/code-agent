from typing import List, Dict, Any, Optional
from smolagents import HfApiModel, CodeAgent

from .base import BaseSpecializedAgent

class TesterAgent(BaseSpecializedAgent):
    """Agent specialized in test creation and execution"""
    
    def __init__(self, model: HfApiModel, tools: List[Any]):
        """
        Initialize tester agent
        
        Args:
            model: HfApiModel instance
            tools: List of tools
        """
        imports = ["os", "pathlib", "json", "pytest", "unittest", "sys", "re"]
        super().__init__("tester", model, tools, imports)
    
    def get_description(self) -> str:
        """Return the agent description"""
        return (
            "Creates and runs tests to validate implemented code. "
            "Specializes in writing comprehensive test suites that cover "
            "both normal cases and edge cases to ensure code quality."
        )
    
    def create_tests(self, feature_name: str, implementation_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create tests for a feature
        
        Args:
            feature_name: Feature name
            implementation_info: Dictionary containing implementation details
            
        Returns:
            Test results
        """
        # Extract files from implementation info if available
        files = implementation_info.get("files", [])
        files_str = "\n".join([f"- {file.get('path', file)}" for file in files]) if files else "No files provided."
        
        prompt = f"""
        You are a senior QA engineer. Create comprehensive tests for the following feature:
        
        FEATURE: {feature_name}
        
        IMPLEMENTATION FILES:
        {files_str}
        
        Please:
        1. Examine each implementation file to understand what needs to be tested
        2. Create appropriate test files using pytest
        3. Write tests for both normal cases and edge cases
        4. Test error handling and boundary conditions
        5. Run the tests and report results
        6. Calculate test coverage
        
        For each implementation file:
        1. Create a corresponding test file
        2. Ensure test functions follow pytest naming conventions
        3. Add appropriate assertions
        4. Include test fixtures if needed
        
        Specific steps to follow:
        1. First explore the project structure using filesystem_tools to locate the implementation files
        2. Read each implementation file to understand its functionality
        3. Generate test files with pytest test cases for each component
        4. Organize tests in a proper directory structure
        5. Use test_tools to run tests and measure coverage
        6. Provide a detailed report of test results
        
        Focus on testing functionality, edge cases, and error conditions.
        """
        
        return self.run(prompt)
    
    def run_tests(self, test_paths: List[str]) -> Dict[str, Any]:
        """
        Run existing tests
        
        Args:
            test_paths: List of paths to test files or directories
            
        Returns:
            Test results
        """
        paths_str = "\n".join([f"- {path}" for path in test_paths])
        
        prompt = f"""
        Run the tests in the following locations:
        
        TEST PATHS:
        {paths_str}
        
        Please:
        1. Use the test_tools.run_tests function for each path
        2. Collect and analyze the results
        3. Generate a coverage report
        4. Identify any failing tests
        5. Summarize the overall test quality
        
        Report back with:
        1. Test pass/fail statistics
        2. Coverage metrics
        3. Failing test details if any
        4. Recommendations for test improvements
        """
        
        return self.run(prompt)
    
    def analyze_coverage(self, feature_name: str, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test coverage for a feature
        
        Args:
            feature_name: Feature name
            test_results: Previous test results
            
        Returns:
            Coverage analysis
        """
        prompt = f"""
        Analyze the test coverage for feature "{feature_name}" based on the test results.
        
        TEST RESULTS:
        {test_results}
        
        Please:
        1. Calculate code coverage statistics
        2. Identify any untested code paths
        3. Recommend additional tests to improve coverage
        4. Evaluate the quality of existing tests
        
        Consider:
        - Line coverage
        - Branch coverage
        - Exception handling coverage
        - Edge case coverage
        
        Use test_tools.run_coverage to gather detailed coverage information.
        
        Provide a comprehensive coverage report with recommendations for improvement.
        """
        
        return self.run(prompt)
    
    def generate_test_suite(self, module_path: str, feature_description: str) -> Dict[str, Any]:
        """
        Generate a complete test suite for a module
        
        Args:
            module_path: Path to the module
            feature_description: Description of the feature to test
            
        Returns:
            Generated test suite
        """
        prompt = f"""
        Generate a comprehensive test suite for the module at path "{module_path}".
        
        FEATURE DESCRIPTION:
        {feature_description}
        
        Please:
        1. Examine the module structure using filesystem_tools
        2. Generate test files for all components in the module
        3. Include unit tests, integration tests, and edge case tests
        4. Organize tests in a logical directory structure
        5. Implement proper test fixtures and setup/teardown
        6. Add docstrings and comments to explain test coverage
        
        Use test_tools.generate_test_suite to automate test generation.
        Ensure the test suite covers:
        - All public methods and functions
        - Error handling paths
        - Edge cases and boundary conditions
        - Input validation
        - Integration between components
        
        Implement the tests, run them, and report the results.
        """
        
        return self.run(prompt) 
