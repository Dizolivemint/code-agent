# code_agent/tools/test_tools.py
from smolagents import tool
import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union
import json
import re
import sys
import importlib
import pytest
import coverage

from ..utils.logger import logger

class TestTools:
    """Tools for test generation, execution, and coverage analysis"""
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize test tools with project path
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = project_path if project_path else os.getcwd()
    
    def set_project_path(self, path: str) -> None:
        """
        Set the project path
        
        Args:
            path: New project path
        """
        self.project_path = path
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve a path relative to the project path
        
        Args:
            path: Relative or absolute path
            
        Returns:
            Absolute path
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.project_path, path)
    
    @tool
    def generate_test(self, code_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a pytest test file for a given Python file
        
        Args:
            code_path: Path to the Python file to test
            test_path: Optional path where to save the test file
            
        Returns:
            Generated test code
        """
        code_full_path = self._resolve_path(code_path)
        
        if not os.path.exists(code_full_path):
            return {
                "status": "error",
                "error": f"File not found: {code_path}"
            }
        
        # Default test path if not provided
        if not test_path:
            # Extract filename and create test file path
            code_dir = os.path.dirname(code_path)
            code_filename = os.path.basename(code_path)
            test_filename = f"test_{code_filename}"
            
            # Create test directory if necessary
            if code_dir:
                test_dir = os.path.join(code_dir, "tests")
                test_path = os.path.join(test_dir, test_filename)
            else:
                test_path = os.path.join("tests", test_filename)
        
        try:
            # Read the code file content
            with open(code_full_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Extract module name from file path
            module_name = os.path.splitext(os.path.basename(code_path))[0]
            
            # Analyze the code to determine what to test
            import ast
            tree = ast.parse(code_content)
            
            # Extract classes and functions
            classes = []
            functions = []
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    functions.append(node.name)
            
            # Generate import path
            # Convert file path to import path
            import_path = code_path.replace('/', '.').replace('\\', '.')
            if import_path.endswith('.py'):
                import_path = import_path[:-3]  # Remove .py extension
            
            # Generate test template
            test_code = f"""
import pytest
import {import_path}

"""
            
            # Generate class tests
            for class_name in classes:
                test_code += f"""
class Test{class_name}:
    def setup_method(self):
        # Setup for each test
        self.instance = {import_path}.{class_name}()
    
    def teardown_method(self):
        # Cleanup after each test
        pass
    
    # TODO: Add test methods for {class_name}
    def test_{class_name.lower()}_initialization(self):
        assert self.instance is not None
"""
            
            # Generate function tests
            for func_name in functions:
                test_code += f"""
def test_{func_name}():
    # TODO: Implement test for {func_name}
    # result = {import_path}.{func_name}()
    # assert result == expected_value
    pass
"""
            
            # Save the test file if requested
            if test_path:
                test_full_path = self._resolve_path(test_path)
                os.makedirs(os.path.dirname(test_full_path), exist_ok=True)
                
                with open(test_full_path, 'w', encoding='utf-8') as f:
                    f.write(test_code)
            
            return {
                "test_code": test_code,
                "test_path": test_path,
                "classes_to_test": classes,
                "functions_to_test": functions,
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Failed to generate test for {code_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def run_tests(self, test_path: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Run pytest tests on a file or directory
        
        Args:
            test_path: Path to test file or directory
            verbose: Whether to run tests in verbose mode
            
        Returns:
            Test results with pass/fail status
        """
        full_path = self._resolve_path(test_path)
        
        if not os.path.exists(full_path):
            return {
                "status": "error",
                "error": f"Test path not found: {test_path}"
            }
        
        try:
            # Build pytest arguments
            pytest_args = [full_path]
            if verbose:
                pytest_args.append('-v')
            
            # Capture output with pytest
            from io import StringIO
            import sys
            
            # Create a custom output collector
            class OutputCollector:
                def __init__(self):
                    self.test_output = []
                    self.summary = {}
                
                def pytest_runtest_logreport(self, report):
                    # Collect information about each test
                    if report.when == 'call':  # Report for test completion
                        outcome = 'passed' if report.outcome == 'passed' else 'failed'
                        self.test_output.append({
                            'name': report.nodeid,
                            'outcome': outcome,
                            'duration': report.duration
                        })
                
                def pytest_terminal_summary(self, terminalreporter):
                    # Collect the final summary
                    stats = terminalreporter.stats
                    self.summary = {
                        'passed': len(stats.get('passed', [])),
                        'failed': len(stats.get('failed', [])),
                        'skipped': len(stats.get('skipped', [])),
                        'total': terminalreporter.stats_summary['total'],
                        'duration': terminalreporter.duration
                    }
            
            # Create the collector
            collector = OutputCollector()
            
            # Run pytest with the collector and custom arguments
            exit_code = pytest.main(pytest_args, plugins=[collector])
            
            return {
                "tests": collector.test_output,
                "summary": collector.summary,
                "exit_code": exit_code,
                "status": "success" if exit_code == 0 else "failure"
            }
            
        except Exception as e:
            error_msg = f"Failed to run tests at {test_path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def run_coverage(self, test_path: str, source_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests with coverage analysis
        
        Args:
            test_path: Path to test file or directory
            source_path: Path to source code to measure coverage (defaults to project path)
            
        Returns:
            Coverage results
        """
        full_test_path = self._resolve_path(test_path)
        
        if not os.path.exists(full_test_path):
            return {
                "status": "error",
                "error": f"Test path not found: {test_path}"
            }
        
        # Use source path if provided, otherwise use project path
        if source_path:
            full_source_path = self._resolve_path(source_path)
        else:
            full_source_path = self.project_path
        
        try:
            # Create a temporary directory for coverage data
            with tempfile.TemporaryDirectory(prefix="code_agent_coverage_") as temp_dir:
                coverage_data_file = os.path.join(temp_dir, ".coverage")
                
                # Set up coverage
                cov = coverage.Coverage(
                    data_file=coverage_data_file,
                    source=[full_source_path],
                    omit=["*/test_*.py", "*/tests/*", "*/venv/*", "*/.venv/*"]
                )
                
                # Start coverage
                cov.start()
                
                # Run pytest
                result = pytest.main([full_test_path])
                
                # Stop coverage
                cov.stop()
                cov.save()
                
                # Generate coverage report
                coverage_data = {}
                
                # Get the coverage data
                cov.load()
                
                # Generate report data
                from coverage.report import get_analysis_to_report
                from coverage.results import Numbers
                
                # Get the analysis
                file_reporters = get_analysis_to_report(cov, [])
                totals = Numbers()
                
                # Process each file
                coverage_files = []
                for fr in file_reporters:
                    numbers = fr.coverage(cov.config)
                    coverage_files.append({
                        "file": fr.relative_filename(),
                        "statements": numbers.n_statements,
                        "missing": numbers.n_missing,
                        "covered": numbers.n_statements - numbers.n_missing,
                        "coverage_percent": numbers.pc_covered
                    })
                    
                    # Aggregate totals
                    totals += numbers
                
                # Calculate overall coverage
                if totals.n_statements > 0:
                    total_coverage = 100.0 * (totals.n_statements - totals.n_missing) / totals.n_statements
                else:
                    total_coverage = 100.0  # No statements means 100% coverage
                
                coverage_data = {
                    "files": coverage_files,
                    "total": {
                        "statements": totals.n_statements,
                        "missing": totals.n_missing,
                        "covered": totals.n_statements - totals.n_missing,
                        "coverage_percent": total_coverage
                    }
                }
                
                return {
                    "coverage": coverage_data,
                    "test_result": result,
                    "status": "success" if result == 0 else "failure"
                }
                
        except Exception as e:
            error_msg = f"Failed to run coverage analysis: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def generate_test_suite(self, module_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive test suite for a Python module or package
        
        Args:
            module_path: Path to the module or package
            output_dir: Directory to save test files (defaults to 'tests')
            
        Returns:
            Information about generated test files
        """
        full_module_path = self._resolve_path(module_path)
        
        if not os.path.exists(full_module_path):
            return {
                "status": "error",
                "error": f"Module path not found: {module_path}"
            }
        
        # Default output directory
        if not output_dir:
            if os.path.isdir(full_module_path):
                output_dir = os.path.join(full_module_path, "tests")
            else:
                output_dir = os.path.join(os.path.dirname(full_module_path), "tests")
        
        # Ensure output directory exists
        os.makedirs(self._resolve_path(output_dir), exist_ok=True)
        
        try:
            generated_tests = []
            
            # Handle both files and directories
            if os.path.isfile(full_module_path) and full_module_path.endswith('.py'):
                # Single file
                rel_path = os.path.relpath(full_module_path, self.project_path)
                test_filename = f"test_{os.path.basename(full_module_path)}"
                test_path = os.path.join(output_dir, test_filename)
                
                # Generate the test
                result = self.generate_test(rel_path, test_path)
                if result.get("status") == "success":
                    generated_tests.append({
                        "source": rel_path,
                        "test": test_path,
                        "classes": result.get("classes_to_test", []),
                        "functions": result.get("functions_to_test", [])
                    })
            
            elif os.path.isdir(full_module_path):
                # Directory - process all Python files
                for root, _, files in os.walk(full_module_path):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('test_'):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, self.project_path)
                            
                            # Determine test path
                            rel_to_module = os.path.relpath(file_path, full_module_path)
                            test_dir = os.path.join(output_dir, os.path.dirname(rel_to_module))
                            os.makedirs(test_dir, exist_ok=True)
                            
                            test_filename = f"test_{file}"
                            test_path = os.path.join(test_dir, test_filename)
                            
                            # Generate the test
                            result = self.generate_test(rel_path, test_path)
                            if result.get("status") == "success":
                                generated_tests.append({
                                    "source": rel_path,
                                    "test": test_path,
                                    "classes": result.get("classes_to_test", []),
                                    "functions": result.get("functions_to_test", [])
                                })
            
            return {
                "generated_tests": generated_tests,
                "count": len(generated_tests),
                "output_dir": output_dir,
                "status": "success"
            }
            
        except Exception as e:
            error_msg = f"Failed to generate test suite: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg
            } 
