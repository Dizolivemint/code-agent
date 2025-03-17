# code_tools.py
from smolagents import tool
import os
import subprocess
import tempfile
from typing import List, Dict, Any, Optional, Union
import ast
import sys
import black
import json

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

@tool
def analyze_code(code: str) -> Dict[str, Any]:
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
        
        # Extract imports, functions, classes, etc.
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
                bases = [_get_name(base) for base in node.bases]
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
                            "type": _infer_type(node.value)
                        })
        
        return result
    except SyntaxError as e:
        result["errors"].append(f"Syntax error in code: {str(e)}")
        return result
    except Exception as e:
        result["errors"].append(f"Error analyzing code: {str(e)}")
        return result

def _get_name(node: ast.AST) -> str:
    """
    Get the name of an AST node
    
    Args:
        node: AST node
        
    Returns:
        Name as string
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_get_name(node.value)}.{node.attr}"
    return "unknown"

def _infer_type(node: ast.AST) -> str:
    """
    Infer the type of an AST node (basic inference)
    
    Args:
        node: AST node
        
    Returns:
        Type as string
    """
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
def format_code(code: str) -> Dict[str, Any]:
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
        return {
            "formatted_code": code,  # Return original code
            "status": "error",
            "error": f"Failed to format code: {str(e)}"
        }
        
@tool
def fix_code(code: str, error_message: str) -> Dict[str, Any]:
    """
    Fix Python code with syntax errors.
    
    Args:
        code: The code with syntax errors
        error_message: The error message
        
    Returns:
        Dictionary with prompt for fixing the code
    """
    # Extract line number and column from error message if available
    line_number = None
    column = None
    import re
    match = re.search(r'line (\d+)', error_message)
    if match:
        line_number = int(match.group(1))
    
    match = re.search(r'column (\d+)', error_message)
    if match:
        column = int(match.group(1))
    
    # Get the problematic line
    error_line = None
    if line_number is not None:
        code_lines = code.split('\n')
        if 0 <= line_number - 1 < len(code_lines):
            error_line = code_lines[line_number - 1]
    
    # Create a prompt for fixing
    prompt = f"""
    The following Python code has a syntax error:
    
    ```python
    {code}
    ```
    
    Error details:
    - Error message: {error_message}
    {f'- Line number: {line_number}' if line_number else ''}
    {f'- Column: {column}' if column else ''}
    {f'- Problematic line: {error_line}' if error_line else ''}
    
    Please fix this code. Common issues include:
    1. Missing colons after if/else/for/while/def statements
    2. Incorrect indentation
    3. Unmatched parentheses, brackets, or braces
    4. Missing commas in lists/dictionaries
    5. Incomplete dictionary entries (key-value pairs)
    
    Return only the corrected code with no additional explanation.
    """
    
    return {
        "prompt_for_fix": prompt,
        "error_details": {
            "message": error_message,
            "line": line_number,
            "column": column
        }
    }

@tool
def fix_directory_structure(code: str, error_message: str) -> Dict[str, Any]:
    """
    Fix Python code that defines a directory structure.
    
    Args:
        code: Python code with directory structure definition
        error_message: The error message
        
    Returns:
        Dictionary with prompt for fixing the directory structure
    """
    prompt = f"""
    The following Python code defining a directory structure has a syntax error:
    
    ```python
    {code}
    ```
    
    Error details: {error_message}
    
    This is likely due to incorrect dictionary syntax. When defining directory structures:
    
    1. Files should be key-value pairs, not standalone items. For example:
    
    INCORRECT:
    ```python
    "dir": {{
        "file1.py",
        "file2.py"
    }}
    ```
    
    CORRECT:
    ```python
    "dir": {{
        "file1.py": None,
        "file2.py": None
    }}
    ```
    
    OR use a list for files:
    ```python
    "dir": ["file1.py", "file2.py"]
    ```
    
    Please fix the code and return only the corrected version.
    """
    
    return {
        "prompt_for_fix": prompt,
        "error_type": "directory_structure"
    }

@tool
def validate_python_code(code: str) -> Dict[str, Any]:
    """
    Validate Python code for syntax errors.
    
    Args:
        code: Python code to validate
        
    Returns:
        Dictionary with validation result
    """
    try:
        ast.parse(code)
        return {
            "valid": True,
            "message": "Code is syntactically valid"
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error_type": "syntax_error",
            "line": e.lineno,
            "column": e.offset,
            "message": str(e)
        }
    except Exception as e:
        return {
            "valid": False,
            "error_type": "unexpected_error",
            "message": str(e)
        }