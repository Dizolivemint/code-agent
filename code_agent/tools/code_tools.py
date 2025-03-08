 # code_agent/tools/code_tools.py
from smolagents import tool
import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union
import ast
import importlib.util
import sys
import re
import black
import json

from ..utils.logger import logger

class CodeTools:
    """Tools for code generation, analysis, and validation"""
    
    def __init__(self, project_path: Optional[str] = None):
        """
        Initialize code tools with project path
        
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
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code for structure and quality
        
        Args:
            code: Python code to analyze
            
        Returns:
            Analysis results including imports, functions, classes, etc.
        """
        result = {
            "imports": [],
            "functions": [],
            "classes": [],
            "variables": [],
            "errors": []
        }
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["imports"].append({
                            "module": name.name,
                            "alias": name.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        result["imports"].append({
                            "module": f"{node.module}.{name.name}" if node.module else name.name,
                            "alias": name.asname
                        })
                elif isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    result["functions"].append({
                        "name": node.name,
                        "args": args,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    bases = [self._get_name(base) for base in node.bases]
                    methods = [method.name for method in node.body if isinstance(method, ast.FunctionDef)]
                    
                    result["classes"].append({
                        "name": node.name,
                        "bases": bases,
                        "methods": methods,
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            result["variables"].append({
                                "name": target.id,
                                "type": self._infer_type(node.value)
                            })
            
            return result
            
        except SyntaxError as e:
            error_msg = f"Syntax error in code: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
        except Exception as e:
            error_msg = f"Error analyzing code: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
            return result
    
    def _get_name(self, node):
        """Get the name of a node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"
    
    def _infer_type(self, node):
        """Infer the type of a node (basic inference)"""
        if isinstance(node, ast.Num):
            return "int" if isinstance(node.n, int) else "float"
        elif isinstance(node, ast.Str):
            return "str"
        elif isinstance(node, ast.List):
            return "list"
        elif isinstance(node, ast.Dict):
            return "dict"
        elif isinstance(node, ast.Set):
            return "set"
        elif isinstance(node, ast.Tuple):
            return "tuple"
        elif isinstance(node, ast.NameConstant) and node.value is None:
            return "None"
        elif isinstance(node, ast.NameConstant):
            return "bool" if isinstance(node.value, bool) else "unknown"
        return "unknown"
    
    @tool
    def format_code(self, code: str) -> Dict[str, Any]:
        """
        Format Python code using Black
        
        Args:
            code: Python code to format
            
        Returns:
            Formatted code
        """
        try:
            formatted_code = black.format_str(
                code,
                mode=black.Mode(
                    line_length=88,
                    string_normalization=True,
                    is_pyi=False,
                )
            )
            
            return {
                "formatted_code": formatted_code,
                "status": "success"
            }
        except Exception as e:
            error_msg = f"Failed to format code: {str(e)}"
            logger.error(error_msg)
            return {
                "formatted_code": code,  # Return original code
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def lint_code(self, code: str, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Lint Python code using flake8
        
        Args:
            code: Python code to lint
            path: Optional file path to use in reports
            
        Returns:
            Linting results
        """
        try:
            # Save code to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
                temp_path = temp.name
                temp.write(code.encode('utf-8'))
            
            # Run flake8 on the temporary file
            result = subprocess.run(
                ['flake8', temp_path],
                capture_output=True,
                text=True
            )
            
            # Process the output
            issues = []
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line:
                        # Format: "path:line:col: code message"
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            _, line_num, col, rest = parts
                            code_msg = rest.strip().split(' ', 1)
                            code = code_msg[0] if len(code_msg) > 0 else ""
                            msg = code_msg[1] if len(code_msg) > 1 else ""
                            
                            issues.append({
                                "line": int(line_num),
                                "column": int(col),
                                "code": code,
                                "message": msg
                            })
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return {
                "issues": issues,
                "count": len(issues),
                "status": "success" if len(issues) == 0 else "warning"
            }
        except Exception as e:
            error_msg = f"Failed to lint code: {str(e)}"
            logger.error(error_msg)
            return {
                "issues": [],
                "count": 0,
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def execute_code(self, code: str, inputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute Python code in a sandbox environment
        
        Args:
            code: Python code to execute
            inputs: Optional list of inputs to provide to the code
            
        Returns:
            Execution results including stdout, stderr, and return value
        """
        try:
            # Create a temporary directory for execution
            temp_dir = tempfile.mkdtemp(prefix="code_agent_exec_")
            temp_file = os.path.join(temp_dir, "temp_code.py")
            
            # Save code to a temporary file
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Set up process for execution
            process_args = [sys.executable, temp_file]
            process_env = os.environ.copy()
            
            # Set up process inputs if provided
            process_input = None
            if inputs:
                process_input = '\n'.join(inputs) + '\n'
                process_input = process_input.encode('utf-8')
            
            # Execute the code with a timeout
            result = subprocess.run(
                process_args,
                input=process_input,
                capture_output=True,
                text=True,
                timeout=10,  # 10 second timeout
                cwd=temp_dir,
                env=process_env
            )
            
            # Clean up
            import shutil
            shutil.rmtree(temp_dir)
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "status": "success" if result.returncode == 0 else "error"
            }
        except subprocess.TimeoutExpired:
            error_msg = "Execution timed out (10 seconds)"
            logger.error(error_msg)
            return {
                "stdout": "",
                "stderr": error_msg,
                "exit_code": -1,
                "status": "timeout"
            }
        except Exception as e:
            error_msg = f"Failed to execute code: {str(e)}"
            logger.error(error_msg)
            return {
                "stdout": "",
                "stderr": error_msg,
                "exit_code": -1,
                "status": "error"
            }
    
    @tool
    def extract_imports(self, code: str) -> Dict[str, Any]:
        """
        Extract all imports from Python code
        
        Args:
            code: Python code to analyze
            
        Returns:
            List of imports
        """
        imports = []
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        imports.append({
                            "type": "import",
                            "module": name.name,
                            "alias": name.asname,
                            "statement": f"import {name.name}" + (f" as {name.asname}" if name.asname else "")
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for name in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": module,
                            "name": name.name,
                            "alias": name.asname,
                            "statement": f"from {module} import {name.name}" + 
                                        (f" as {name.asname}" if name.asname else "")
                        })
            
            return {
                "imports": imports,
                "count": len(imports),
                "status": "success"
            }
        except SyntaxError as e:
            error_msg = f"Syntax error in code: {str(e)}"
            logger.error(error_msg)
            return {
                "imports": [],
                "count": 0,
                "status": "error",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error extracting imports: {str(e)}"
            logger.error(error_msg)
            return {
                "imports": [],
                "count": 0,
                "status": "error",
                "error": error_msg
            }
    
    @tool
    def generate_requirements(self, imports: Union[List[Dict[str, str]], List[str]]) -> Dict[str, Any]:
        """
        Generate requirements.txt from a list of imports
        
        Args:
            imports: List of imports (either strings or dicts)
            
        Returns:
            Requirements file content
        """
        if not imports:
            return {
                "requirements": "",
                "count": 0,
                "status": "success"
            }
        
        # Standard library modules to exclude
        stdlib_modules = set([
            "abc", "argparse", "asyncio", "collections", "concurrent", "contextlib",
            "copy", "csv", "datetime", "enum", "functools", "glob", "io", "itertools",
            "json", "logging", "math", "multiprocessing", "os", "pathlib", "pickle",
            "random", "re", "shutil", "signal", "socket", "sqlite3", "string",
            "subprocess", "sys", "tempfile", "threading", "time", "typing", "uuid",
            "weakref", "xml", "zipfile"
        ])
        
        # Extract package names from imports
        package_names = set()
        
        for imp in imports:
            if isinstance(imp, dict):
                module = imp.get("module", "")
                if not module:
                    continue
            else:
                module = imp
            
            # Extract the top-level package name
            top_package = module.split('.')[0]
            
            # Skip standard library modules
            if top_package in stdlib_modules:
                continue
            
            package_names.add(top_package)
        
        # Generate requirements.txt content
        requirements = "\n".join(sorted(package_names))
        
        return {
            "requirements": requirements,
            "packages": sorted(list(package_names)),
            "count": len(package_names),
            "status": "success"
        }
    
    @tool
    def extract_docstrings(self, code: str) -> Dict[str, Any]:
        """
        Extract docstrings from Python code
        
        Args:
            code: Python code to analyze
            
        Returns:
            Extracted docstrings for modules, classes, and functions
        """
        result = {
            "module": None,
            "classes": [],
            "functions": [],
            "status": "success"
        }
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Get module docstring
            module_docstring = ast.get_docstring(tree)
            if module_docstring:
                result["module"] = module_docstring
            
            # Extract class and function docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": []
                    }
                    
                    # Extract method docstrings
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "docstring": ast.get_docstring(item)
                            }
                            class_info["methods"].append(method_info)
                    
                    result["classes"].append(class_info)
                
                elif isinstance(node, ast.FunctionDef) and not isinstance(node.parent, ast.ClassDef):
                    function_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node)
                    }
                    result["functions"].append(function_info)
            
            return result
        except SyntaxError as e:
            error_msg = f"Syntax error in code: {str(e)}"
            logger.error(error_msg)
            return {
                "module": None,
                "classes": [],
                "functions": [],
                "status": "error",
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error extracting docstrings: {str(e)}"
            logger.error(error_msg)
            return {
                "module": None,
                "classes": [],
                "functions": [],
                "status": "error",
                "error": error_msg
            }
