# filesystem_tools.py
from smolagents import tool
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json

# Module-level variable for base path
_base_path = None

def set_base_path(path: str) -> None:
    """
    Set the base path for filesystem operations
    
    Args:
        path: New base path
    """
    global _base_path
    _base_path = path

def _resolve_path(path: str) -> str:
    """
    Resolve a path relative to the base path
    
    Args:
        path: Relative or absolute path
        
    Returns:
        Absolute path
    """
    # Handle empty path
    if not path:
        return _base_path or os.getcwd()
        
    # Check if it's already absolute
    if os.path.isabs(path):
        return os.path.normpath(path)
        
    # If base path is set, join with it
    if _base_path:
        return os.path.normpath(os.path.join(_base_path, path))
        
    # Otherwise use current directory
    return os.path.normpath(os.path.join(os.getcwd(), path))

def normalize_path(path: str) -> str:
    """
    Normalize a path to be OS-agnostic
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path
    """
    # Handle raw string escaping issues by normalizing all paths
    if path:
        # Convert to Path object and back to string to normalize separators
        return str(Path(path))
    return path

@tool
def get_absolute_path(relative_path: str = "") -> str:
    """
    Convert a relative path to an absolute path based on the base path
    
    Args:
        relative_path: Relative path from the base path
        
    Returns:
        Absolute path
    """
    full_path = _resolve_path(relative_path)
    return str(Path(full_path).resolve())

@tool
def list_directory(path: str = "") -> List[Dict[str, Any]]:
    """
    List contents of a directory
    
    Args:
        path: Directory path (relative to base path)
        
    Returns:
        List of files and directories with metadata
    """
    full_path = _resolve_path(path)
    
    try:
        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            
            items.append({
                "name": item,
                "path": os.path.join(path, item),  # Return relative path
                "type": "directory" if is_dir else "file",
                "size": os.path.getsize(item_path) if not is_dir else None
            })
        
        return sorted(items, key=lambda x: (x["type"] == "file", x["name"]))
    except Exception as e:
        return [{"error": f"Failed to list directory: {str(e)}"}]

@tool
def read_file(path: str) -> Dict[str, Any]:
    """
    Read a file's content
    
    Args:
        path: File path (relative to base path)
        
    Returns:
        Dictionary with file content and metadata
    """
    full_path = _resolve_path(normalize_path(path))
    
    try:
        # Read the file without using "with open" pattern
        file_obj = open(full_path, 'r', encoding='utf-8')
        content = file_obj.read()
        file_obj.close()
        
        return {
            "content": content,
            "path": path,
            "size": os.path.getsize(full_path),
            "type": "file"
        }
    except UnicodeDecodeError:
        return {
            "error": f"Cannot read binary file: {path}",
            "type": "binary_file"
        }
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}

@tool
def create_directory(path: str) -> Dict[str, str]:
    """
    Create a directory
    
    Args:
        path: Directory path (relative to base path)
        
    Returns:
        Status message
    """
    full_path = _resolve_path(path)
    
    try:
        os.makedirs(full_path, exist_ok=True)
        return {
            "status": "success",
            "message": f"Created directory: {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create directory {path}: {str(e)}"
        }

@tool
def write_file(path: str, content: str) -> Dict[str, str]:
    """
    Write content to a file
    
    Args:
        path: File path (relative to base path)
        content: Content to write
        
    Returns:
        Status message
    """
    full_path = _resolve_path(path)
    
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Open, write, and close without using the "with" pattern
        file_obj = open(full_path, 'w', encoding='utf-8')
        file_obj.write(content)
        file_obj.close()
        
        return {
            "status": "success",
            "message": f"Wrote file: {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write file {path}: {str(e)}"
        }
        
@tool
def init_project(project_dir: str, project_name: str) -> Dict[str, Any]:
    """
    Initialize a Python project structure with proper directories and files
    
    Args:
        project_dir: Project root directory
        project_name: Name of the project (should be a valid Python package name)
        
    Returns:
        Dictionary with status information
    """
    from ..utils.project_utils import initialize_project_structure
    return initialize_project_structure(project_dir, project_name)
  
@tool
def init_project(project_dir: str, project_name: str) -> Dict[str, Any]:
    """
    Initialize a Python project structure with proper directories and files.
    Creates a standardized project layout with src, tests, and docs directories,
    along with proper Python packaging and pytest configuration.
    
    Args:
        project_dir: Project root directory (path where the project will be created)
        project_name: Name of the project (should be a valid Python package name)
        
    Returns:
        Dictionary with status information and project path
    """
    from ..utils.project_utils import initialize_project_structure
    
    # Resolve the path relative to the base path
    full_project_dir = _resolve_path(project_dir)
    
    # Initialize the project structure
    result = initialize_project_structure(full_project_dir, project_name)
    
    # If successful, ensure the path in the result is relative to the base path
    if result["status"] == "success" and _base_path:
        try:
            rel_path = os.path.relpath(result["path"], _base_path)
            result["relative_path"] = rel_path
        except ValueError:
            # This can happen if the paths are on different drives
            result["relative_path"] = result["path"]
    
    return result