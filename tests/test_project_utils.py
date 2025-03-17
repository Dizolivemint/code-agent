"""
Tests for project_utils module.
"""

import unittest
from unittest.mock import patch
import tempfile
import shutil
from pathlib import Path

from code_agent.utils.project_utils import initialize_project_structure


class TestProjectUtils(unittest.TestCase):
    """Test cases for the project_utils module functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_initialize_project_structure(self):
        """Test initializing a project structure"""
        # Initialize the project
        project_name = "testproject"
        result = initialize_project_structure(self.temp_dir, project_name)
        
        # Check result status
        self.assertEqual(result["status"], "success")
        
        # Check directories were created
        project_path = Path(self.temp_dir)
        self.assertTrue((project_path / "src").is_dir())
        self.assertTrue((project_path / "tests").is_dir())
        self.assertTrue((project_path / "docs").is_dir())
        self.assertTrue((project_path / "src" / project_name).is_dir())
        
        # Check files were created
        self.assertTrue((project_path / "src" / "__init__.py").is_file())
        self.assertTrue((project_path / "src" / project_name / "__init__.py").is_file())
        self.assertTrue((project_path / "tests" / "__init__.py").is_file())
        self.assertTrue((project_path / "setup.py").is_file())
        self.assertTrue((project_path / "pytest.ini").is_file())
        self.assertTrue((project_path / "tests" / "conftest.py").is_file())
        
        # Check content of setup.py
        with open(project_path / "setup.py", 'r') as f:
            setup_content = f.read()
        self.assertIn(f'name="{project_name}"', setup_content)
    
    def test_initialize_project_structure_error_handling(self):
        """Test error handling when initializing a project structure"""
        # Mock a failure when creating directories
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            result = initialize_project_structure(self.temp_dir, "testproject")
            
            # Check result indicates an error
            self.assertEqual(result["status"], "error")
            self.assertIn("Failed to initialize project structure", result["message"])
            self.assertIn("Permission denied", result["message"])


if __name__ == "__main__":
    unittest.main()