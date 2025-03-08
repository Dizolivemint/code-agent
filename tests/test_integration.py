
"""
Integration tests for the Code Agent application.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil

from code_agent.config import Config
from code_agent.agents.orchestrator import AgentOrchestrator


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent orchestration"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary config file
        self.config_path = os.path.join(self.temp_dir, "config.json")
        
        # Set test environment variables
        os.environ["GITHUB_TOKEN"] = "test_token"
        os.environ["GITHUB_USERNAME"] = "test_user"
        os.environ["ARCHITECT_MODEL"] = "test_model"
        os.environ["DEVELOPER_MODEL"] = "test_model"
        os.environ["TESTER_MODEL"] = "test_model"
        os.environ["REVIEWER_MODEL"] = "test_model"
        
        # Create config and project directory
        self.config = Config(self.config_path)
        self.project_dir = os.path.join(self.temp_dir, "test_project")
        os.makedirs(self.project_dir, exist_ok=True)
        self.config.set_project("test_project", "Test description", self.project_dir)
        self.config.save()
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Remove environment variables
        for var in ["GITHUB_TOKEN", "GITHUB_USERNAME", "ARCHITECT_MODEL", 
                    "DEVELOPER_MODEL", "TESTER_MODEL", "REVIEWER_MODEL"]:
            if var in os.environ:
                del os.environ[var]
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('smolagents.HfApiModel')
    @patch('smolagents.CodeAgent')
    def test_orchestrator_initialization(self, mock_code_agent, mock_hf_model):
        """Test initialization of the orchestrator with mock agents"""
        # Setup mocks
        mock_hf_model.return_value = MagicMock()
        mock_code_agent.return_value = MagicMock()
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(self.config, self.project_dir)
        
        # Verify agent initialization
        self.assertIn("architect", orchestrator.agents)
        self.assertIn("developer", orchestrator.agents)
        self.assertIn("tester", orchestrator.agents)
        self.assertIn("reviewer", orchestrator.agents)
        self.assertIn("manager", orchestrator.agents)
        
        # Verify tool initialization
        self.assertIn("filesystem", orchestrator.tools)
        self.assertIn("code", orchestrator.tools)
        self.assertIn("test", orchestrator.tools)
        self.assertIn("github", orchestrator.tools)
    
    @patch('smolagents.HfApiModel')
    @patch('smolagents.CodeAgent')
    def test_analyze_requirements(self, mock_code_agent, mock_hf_model):
        """Test requirements analysis workflow"""
        # Setup mocks
        mock_hf_model.return_value = MagicMock()
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            "features": [
                {"name": "User Auth", "description": "User authentication", "priority": "high"},
                {"name": "Task CRUD", "description": "Task management", "priority": "high"}
            ],
            "architecture": {
                "components": ["API", "Database", "Auth Service"]
            }
        }
        mock_code_agent.return_value = mock_agent
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(self.config, self.project_dir)
        
        # Run requirements analysis
        requirements = "Build a task management system with user authentication."
        result = orchestrator.analyze_requirements(requirements)
        
        # Verify agent was called with appropriate prompt
        self.assertTrue(mock_agent.run.called)
        
        # Verify result structure
        self.assertIn("features", result)
        self.assertEqual(len(result["features"]), 2)
        self.assertIn("architecture", result)
    
    @patch('smolagents.HfApiModel')
    @patch('smolagents.CodeAgent')
    def test_implement_feature(self, mock_code_agent, mock_hf_model):
        """Test feature implementation workflow"""
        # Setup mocks
        mock_hf_model.return_value = MagicMock()
        mock_agent = MagicMock()
        mock_agent.run.return_value = {
            "files": [
                {"path": "models/user.py", "content": "# User model implementation"},
                {"path": "routes/auth.py", "content": "# Auth routes implementation"}
            ],
            "status": "success"
        }
        mock_code_agent.return_value = mock_agent
        
        # Initialize orchestrator
        orchestrator = AgentOrchestrator(self.config, self.project_dir)
        
        # Implement feature
        feature_name = "User Authentication"
        feature_description = "Implement user signup, login, and logout functionality."
        architecture_info = "Use JWT for authentication and PostgreSQL for storage."
        
        result = orchestrator.implement_feature(
            feature_name, 
            feature_description, 
            architecture_info
        )
        
        # Verify agent was called with appropriate prompt
        self.assertTrue(mock_agent.run.called)
        
        # Verify result structure
        self.assertIn("files", result)
        self.assertEqual(len(result["files"]), 2)
        self.assertEqual(result["status"], "success")


if __name__ == "__main__":
    unittest.main()