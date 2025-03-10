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
    if os.path.isabs(path):
        return path
    return os.path.join(_base_path or os.getcwd(), path)

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
    full_path = _resolve_path(path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
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
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": f"Wrote file: {path}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to write file {path}: {str(e)}"
        }