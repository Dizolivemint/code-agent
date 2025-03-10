# code_agent/tools/test_tools.py
from smolagents import tool
import os
import subprocess
import tempfile
import shutil
import sys
from typing import List, Dict, Any, Optional, Union
import ast
import importlib.util
import re

# Module-level variable for project path
_project_path = None

def set_project_path(path: str) -> None:
    """
    Set the project path
    
    Args:
        path: New project path
    """
    global _project_path
    _project_path = path

def _resolve_path(path: str) -> str:
    """
    Resolve a path relative to the project path
    
    Args:
        path: Relative or absolute path
        
    Returns:
        Absolute path
    """
    if os.path.isabs(path):
        return path
    return os.path.join(_project_path or os.getcwd(), path)

@tool
def generate_test(code_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a pytest test file for a given Python file
    
    Args:
        code_path: Path to the Python file to test
        test_path: Optional path where to save the test file
        
    Returns:
        Generated test code
    """
    code_full_path = _resolve_path(code_path)
    
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
            test_full_path = _resolve_path(test_path)
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
        return {
            "status": "error",
            "error": f"Failed to generate test for {code_path}: {str(e)}"
        }

@tool
def run_tests(test_path: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Run pytest tests on a file or directory
    
    Args:
        test_path: Path to test file or directory
        verbose: Whether to run tests in verbose mode
        
    Returns:
        Test results with pass/fail status
    """
    full_path = _resolve_path(test_path)
    
    if not os.path.exists(full_path):
        return {
            "status": "error",
            "error": f"Test path not found: {test_path}"
        }
    
    try:
        # Build pytest arguments
        pytest_args = ["-xvs" if verbose else "-x", full_path]
        
        # Use subprocess to run pytest
        result = subprocess.run(
            [sys.executable, "-m", "pytest"] + pytest_args,
            capture_output=True,
            text=True
        )
        
        # Parse test results from stdout
        tests_passed = 0
        tests_failed = 0
        tests_skipped = 0
        
        # Simple parser for pytest output
        for line in result.stdout.split('\n'):
            if " passed " in line:
                # Try to extract numbers like "5 passed"
                match = re.search(r'(\d+) passed', line)
                if match:
                    tests_passed = int(match.group(1))
            if " failed " in line:
                match = re.search(r'(\d+) failed', line)
                if match:
                    tests_failed = int(match.group(1))
            if " skipped " in line:
                match = re.search(r'(\d+) skipped', line)
                if match:
                    tests_skipped = int(match.group(1))
        
        return {
            "exit_code": result.returncode,
            "status": "success" if result.returncode == 0 else "failure",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "summary": {
                "passed": tests_passed,
                "failed": tests_failed,
                "skipped": tests_skipped,
                "total": tests_passed + tests_failed + tests_skipped
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to run tests: {str(e)}"
        }

@tool
def run_coverage(test_path: str, source_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Run tests with coverage analysis
    
    Args:
        test_path: Path to test file or directory
        source_path: Path to source code to measure coverage (defaults to project path)
        
    Returns:
        Coverage results
    """
    full_test_path = _resolve_path(test_path)
    
    if not os.path.exists(full_test_path):
        return {
            "status": "error",
            "error": f"Test path not found: {test_path}"
        }
    
    # Use source path if provided, otherwise use project path
    if source_path:
        full_source_path = _resolve_path(source_path)
    else:
        full_source_path = _project_path or os.getcwd()
    
    try:
        # Create a temporary directory for coverage data
        temp_dir = tempfile.mkdtemp(prefix="code_agent_coverage_")
        coverage_data_file = os.path.join(temp_dir, ".coverage")
        
        # Use pytest-cov to run tests with coverage
        pytest_args = [
            full_test_path,
            f"--cov={full_source_path}",
            "--cov-report=term",
            f"--cov-config={coverage_data_file}",
            "--cov-branch"
        ]
        
        # Run pytest with coverage
        result = subprocess.run(
            [sys.executable, "-m", "pytest"] + pytest_args,
            capture_output=True,
            text=True
        )
        
        # Parse coverage output
        coverage_data = {
            "total": 0.0,
            "files": [],
            "summary": {
                "statements": 0,
                "missing": 0,
                "covered": 0
            }
        }
        
        # Extract coverage percentage from output
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if "TOTAL" in line and "%" in line:
                # Parse the TOTAL line which typically looks like:
                # "TOTAL                             123     23    81%"
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        statements = int(parts[-3])
                        missing = int(parts[-2])
                        percentage = float(parts[-1].strip('%'))
                        coverage_data["total"] = percentage
                        coverage_data["summary"] = {
                            "statements": statements,
                            "missing": missing,
                            "covered": statements - missing
                        }
                    except (ValueError, IndexError):
                        pass
            
            # Extract per-file coverage
            elif ".py" in line and "%" in line:
                # Parse file lines which typically look like:
                # "module/file.py                     123     23    81%"
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        file_path = parts[0]
                        statements = int(parts[-3])
                        missing = int(parts[-2])
                        percentage = float(parts[-1].strip('%'))
                        coverage_data["files"].append({
                            "file": file_path,
                            "statements": statements,
                            "missing": missing,
                            "covered": statements - missing,
                            "coverage_percent": percentage
                        })
                    except (ValueError, IndexError):
                        pass
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
        return {
            "coverage": coverage_data,
            "test_result": {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            },
            "status": "success" if result.returncode == 0 else "failure"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to run coverage analysis: {str(e)}"
        }

@tool
def generate_test_suite(module_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive test suite for a Python module or package
    
    Args:
        module_path: Path to the module or package
        output_dir: Directory to save test files (defaults to 'tests')
        
    Returns:
        Information about generated test files
    """
    full_module_path = _resolve_path(module_path)
    
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
    os.makedirs(_resolve_path(output_dir), exist_ok=True)
    
    try:
        generated_tests = []
        
        # Handle both files and directories
        if os.path.isfile(full_module_path) and full_module_path.endswith('.py'):
            # Single file
            rel_path = os.path.relpath(full_module_path, _project_path or os.getcwd())
            test_filename = f"test_{os.path.basename(full_module_path)}"
            test_path = os.path.join(output_dir, test_filename)
            
            # Generate the test
            result = generate_test(rel_path, test_path)
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
                        rel_path = os.path.relpath(file_path, _project_path or os.getcwd())
                        
                        # Determine test path
                        rel_to_module = os.path.relpath(file_path, full_module_path)
                        test_dir = os.path.join(output_dir, os.path.dirname(rel_to_module))
                        os.makedirs(_resolve_path(test_dir), exist_ok=True)
                        
                        test_filename = f"test_{file}"
                        test_path = os.path.join(test_dir, test_filename)
                        
                        # Generate the test
                        result = generate_test(rel_path, test_path)
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
        return {
            "status": "error",
            "error": f"Failed to generate test suite: {str(e)}"
        }