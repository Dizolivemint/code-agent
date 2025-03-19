# code_agent/tools/environment_tools.py
from smolagents import tool
import os
import subprocess
import venv
from typing import List, Dict, Any, Optional

@tool
def setup_virtual_environment(project_dir: str, env_name: str = ".venv") -> Dict[str, str]:
    """
    Create a Python virtual environment for the project
    
    Args:
        project_dir: Path to the project directory
        env_name: Name of the virtual environment directory
        
    Returns:
        Status and environment path
    """
    try:
        env_path = os.path.join(project_dir, env_name)
        
        # Create the virtual environment
        venv.create(env_path, with_pip=True)
        
        return {
            "status": "success",
            "message": f"Created virtual environment at: {env_path}",
            "env_path": env_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create virtual environment: {str(e)}"
        }

@tool
def install_dependencies(project_dir: str, requirements_path: Optional[str] = None, env_name: str = ".venv") -> Dict[str, Any]:
    """
    Install dependencies from requirements.txt
    
    Args:
        project_dir: Path to the project directory
        requirements_path: Path to requirements.txt (default: project_dir/requirements.txt)
        env_name: Name of the virtual environment directory
        
    Returns:
        Installation status and details
    """
    try:
        # Determine requirements path
        if requirements_path is None:
            requirements_path = os.path.join(project_dir, "requirements.txt")
        
        # Get path to pip in the virtual environment
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(project_dir, env_name, "Scripts", "pip")
        else:  # Unix/Linux/Mac
            pip_path = os.path.join(project_dir, env_name, "bin", "pip")
        
        # Install dependencies
        result = subprocess.run(
            [pip_path, "install", "-r", requirements_path],
            capture_output=True,
            text=True
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "message": "Dependencies installed successfully" if result.returncode == 0 else "Failed to install dependencies",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to install dependencies: {str(e)}"
        }

@tool
def extract_dependencies_from_code(project_dir: str) -> Dict[str, Any]:
    """
    Extract dependencies by analyzing imports in Python files
    
    Args:
        project_dir: Path to the project directory
        
    Returns:
        List of identified dependencies
    """
    import ast
    
    dependencies = set()
    standard_libs = set([
        "os", "sys", "re", "math", "json", "time", "datetime", "random",
        "collections", "itertools", "functools", "pathlib", "typing",
        "unittest", "logging", "argparse", "subprocess", "tempfile", "shutil"
    ])
    
    # Walk through the directory and check Python files
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    # Direct open without context manager
                    f = open(file_path, 'r', encoding='utf-8')
                    code_content = f.read()
                    f.close()
                    
                    tree = ast.parse(code_content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                if name.name.split('.')[0] not in standard_libs:
                                    dependencies.add(name.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and node.module.split('.')[0] not in standard_libs:
                                dependencies.add(node.module.split('.')[0])
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    # Common package name mappings (import name -> package name)
    package_mappings = {
        "bs4": "beautifulsoup4",
        "PIL": "pillow",
        "yaml": "pyyaml",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "dotenv": "python-dotenv",
        "mx": "mxnet",
        "plt": "matplotlib",
        "yaml": "pyyaml"
    }
    
    # Map import names to package names
    requirements = []
    for dep in dependencies:
        if dep in package_mappings:
            requirements.append(package_mappings[dep])
        else:
            requirements.append(dep)
    
    return {
        "status": "success",
        "dependencies": list(sorted(requirements))
    }

@tool
def create_requirements_file(project_dir: str, dependencies: List[str]) -> Dict[str, str]:
    """
    Create a requirements.txt file
    
    Args:
        project_dir: Path to the project directory
        dependencies: List of dependencies to include
        
    Returns:
        Status and file path
    """
    try:
        requirements_path = os.path.join(project_dir, "requirements.txt")
        content = "\n".join(dependencies)
        
        # Direct file operations without context manager
        f = open(requirements_path, 'w', encoding='utf-8')
        f.write(content)
        f.close()
        
        return {
            "status": "success",
            "message": f"Created requirements.txt at: {requirements_path}",
            "path": requirements_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create requirements.txt: {str(e)}"
        }