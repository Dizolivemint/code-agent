"""
Tests for configuration module.
"""

import os
import tempfile
import unittest
from pathlib import Path

from code_agent.config import Config, AgentConfig, GitHubConfig, ProjectConfig

class TestConfig(unittest.TestCase):
    """Test cases for the Config class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.json")
        
        # Set test environment variables
        os.environ["GITHUB_TOKEN"] = "test_token"
        os.environ["GITHUB_USERNAME"] = "test_user"
        
        # Create test config
        self.config = Config(self.config_path)
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Remove environment variables
        for var in ["GITHUB_TOKEN", "GITHUB_USERNAME", "GITHUB_REPOSITORY"]:
            if var in os.environ:
                del os.environ[var]
        
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_init_from_env(self):
        """Test initialization from environment variables"""
        self.assertEqual(self.config.github.token, "test_token")
        self.assertEqual(self.config.github.username, "test_user")
    
    def test_save_and_load(self):
        """Test saving and loading configuration"""
        # Modify config
        self.config.github.repository = "test_repo"
        self.config.agents["architect"].model_id = "test_model"
        
        # Save config
        self.config.save()
        
        # Create new config instance to load from file
        new_config = Config(self.config_path)
        
        # Verify loaded config
        self.assertEqual(new_config.github.repository, "test_repo")
        self.assertEqual(new_config.agents["architect"].model_id, "test_model")
    
    def test_set_project(self):
        """Test setting project configuration"""
        # Set project
        self.config.set_project("test_project", "test description", "/tmp/test")
        
        # Verify project settings
        self.assertEqual(self.config.project.name, "test_project")
        self.assertEqual(self.config.project.description, "test description")
        self.assertEqual(str(self.config.project.root_dir), "/tmp/test")
        
        # Save and reload
        self.config.save()
        new_config = Config(self.config_path)
        
        # Verify project settings after reload
        self.assertEqual(new_config.project.name, "test_project")
    
    def test_validate(self):
        """Test configuration validation"""
        # Valid configuration
        self.assertTrue(self.config.validate())
        
        # Invalid configuration
        self.config.github.token = ""
        self.assertFalse(self.config.validate())


if __name__ == "__main__":
    unittest.main()