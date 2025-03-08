# code_agent/tools/filesystem_tools.py
from smolagents import tool
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json

from ..utils.logger import logger

class FilesystemTools:
    """Tools for working with the local filesystem"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize filesystem tools with a base path
        
        Args:
            base_path: Base path for all filesystem operations
        """
        self.base_path = base_path if base_path else os.getcwd()
        
    def set_base_path(self, path: str) -> None:
        """
        Set the base path for filesystem operations
        
        Args:
            path: New base path
        """
        self.base_path = path
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve a path relative to the base path
        
        Args:
            path: Relative or absolute path
            
        Returns:
            Absolute path
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_path, path)
    
    @tool
    def list_directory(self, path: str = "") -> List[Dict[str, Any]]:
        """
        List contents of a directory
        
        Args:
            path: Directory path (relative to base path)
            
        Returns:
            List of files and directories with metadata
        """
        full_path = self._resolve_path(path)
        
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
            logger.error(f"Failed to list directory {path}: {str(e)}")
            return [{"error": f"Failed to list directory: {str(e)}"}]
    
    @tool
    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read a file's content
        
        Args:
            path: File path (relative to base path)
            
        Returns:
            Dictionary with file content and metadata
        """
        full_path = self._resolve_path(path)
        
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
            logger.error(f"Failed to read file {path}: {str(e)}")
            return {"error": f"Failed to read file: {str(e)}"}
    
    @tool
    def create_directory(self, path: str) -> Dict[str, str]:
        """
        Create a directory
        
        Args:
            path: Directory path (relative to base path)
            
        Returns:
            Status message
        """
        full_path = self._resolve_path(path)
        
        try:
            os.makedirs(full_path, exist_ok=True)
            logger.info(f"Created directory: {path}")
            return {
                "status": "success",
                "message": f"Created directory: {path}"
            }
        except Exception as e:
            error_msg = f"Failed to create directory {path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def write_file(self, path: str, content: str) -> Dict[str, str]:
        """
        Write content to a file
        
        Args:
            path: File path (relative to base path)
            content: Content to write
            
        Returns:
            Status message
        """
        full_path = self._resolve_path(path)
        
        try:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote file: {path}")
            return {
                "status": "success",
                "message": f"Wrote file: {path}"
            }
        except Exception as e:
            error_msg = f"Failed to write file {path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def delete_file(self, path: str) -> Dict[str, str]:
        """
        Delete a file
        
        Args:
            path: File path (relative to base path)
            
        Returns:
            Status message
        """
        full_path = self._resolve_path(path)
        
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
                logger.info(f"Deleted file: {path}")
                return {
                    "status": "success",
                    "message": f"Deleted file: {path}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Not a file: {path}"
                }
        except Exception as e:
            error_msg = f"Failed to delete file {path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def delete_directory(self, path: str, recursive: bool = False) -> Dict[str, str]:
        """
        Delete a directory
        
        Args:
            path: Directory path (relative to base path)
            recursive: Whether to recursively delete contents
            
        Returns:
            Status message
        """
        full_path = self._resolve_path(path)
        
        try:
            if os.path.isdir(full_path):
                if recursive:
                    import shutil
                    shutil.rmtree(full_path)
                else:
                    os.rmdir(full_path)
                
                logger.info(f"Deleted directory: {path}")
                return {
                    "status": "success",
                    "message": f"Deleted directory: {path}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Not a directory: {path}"
                }
        except Exception as e:
            error_msg = f"Failed to delete directory {path}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def copy_file(self, source: str, destination: str) -> Dict[str, str]:
        """
        Copy a file
        
        Args:
            source: Source file path (relative to base path)
            destination: Destination file path (relative to base path)
            
        Returns:
            Status message
        """
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)
        
        try:
            import shutil
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            
            logger.info(f"Copied file from {source} to {destination}")
            return {
                "status": "success",
                "message": f"Copied file from {source} to {destination}"
            }
        except Exception as e:
            error_msg = f"Failed to copy file from {source} to {destination}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def move_file(self, source: str, destination: str) -> Dict[str, str]:
        """
        Move a file
        
        Args:
            source: Source file path (relative to base path)
            destination: Destination file path (relative to base path)
            
        Returns:
            Status message
        """
        source_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)
        
        try:
            import shutil
            
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            shutil.move(source_path, dest_path)
            
            logger.info(f"Moved file from {source} to {destination}")
            return {
                "status": "success",
                "message": f"Moved file from {source} to {destination}"
            }
        except Exception as e:
            error_msg = f"Failed to move file from {source} to {destination}: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
    
    @tool
    def file_exists(self, path: str) -> Dict[str, bool]:
        """
        Check if a file exists
        
        Args:
            path: File path (relative to base path)
            
        Returns:
            Whether the file exists
        """
        full_path = self._resolve_path(path)
        exists = os.path.isfile(full_path)
        
        return {
            "exists": exists,
            "is_file": exists
        }
    
    @tool
    def directory_exists(self, path: str) -> Dict[str, bool]:
        """
        Check if a directory exists
        
        Args:
            path: Directory path (relative to base path)
            
        Returns:
            Whether the directory exists
        """
        full_path = self._resolve_path(path)
        exists = os.path.isdir(full_path)
        
        return {
            "exists": exists,
            "is_directory": exists
        } 
