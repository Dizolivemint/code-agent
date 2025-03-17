from pathlib import Path
from typing import Dict, Any

def initialize_project_structure(project_dir: str, project_name: str) -> Dict[str, Any]:
    """
    Initialize a proper project structure with necessary files
    
    Args:
        project_dir: Project root directory
        project_name: Name of the project
        
    Returns:
        Status message with path and success indicators
    """
    project_path = Path(project_dir)
    
    try:
        # Create directory if it doesn't exist
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic structure
        dirs_to_create = [
            "tests",
            "docs",
            "src",
            f"src/{project_name}",
        ]
        
        for dir_path in dirs_to_create:
            (project_path / dir_path).mkdir(exist_ok=True)
        
        # Create __init__.py files to make proper Python packages
        init_files = [
            "src/__init__.py",
            f"src/{project_name}/__init__.py",
            "tests/__init__.py",
        ]
        
        for init_file in init_files:
            init_path = project_path / init_file
            if not init_path.exists():
                init_path.write_text(f'"""\n{project_name} package\n"""\n')
        
        # Create setup.py file
        setup_py = project_path / "setup.py"
        if not setup_py.exists():
            setup_content = f'''
from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
)
'''
            setup_py.write_text(setup_content)
        
        # Create pytest.ini file for proper test configuration
        pytest_ini = project_path / "pytest.ini"
        if not pytest_ini.exists():
            pytest_content = '''
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
'''
            pytest_ini.write_text(pytest_content)
        
        # Create conftest.py for pytest configuration
        conftest_py = project_path / "tests/conftest.py"
        if not conftest_py.exists():
            conftest_content = '''
import sys
import os
import pytest
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.fixture
def project_root():
    """Return the project root directory as a Path object"""
    return Path(__file__).parent.parent

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
'''
            conftest_py.write_text(conftest_content)
        
        return {
            "status": "success",
            "message": f"Project structure initialized at {project_path}",
            "path": str(project_path)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to initialize project structure: {str(e)}",
            "path": str(project_path)
        }