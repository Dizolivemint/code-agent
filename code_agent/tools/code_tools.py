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