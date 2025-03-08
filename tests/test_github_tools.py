"""
Tests for GitHub tools module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil

from code_agent.tools.github_tools import GitHubTools
from github import GithubException


class TestGitHubTools(unittest.TestCase):
    """Test cases for the GitHubTools class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.token = "fake_token"
        self.username = "fake_user"
        self.repo_name = "fake_user/fake_repo"
        
        # Create GitHub tools instance
        self.github_tools = GitHubTools(
            token=self.token,
            username=self.username,
            repository=self.repo_name
        )
        
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures"""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
    
    @patch('github.Github')
    def test_set_repository(self, mock_github):
        """Test setting repository"""
        # Setup mock
        mock_repo = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        
        # Set repository
        self.github_tools.set_repository("new_repo")
        
        # Assert repository was set correctly
        self.assertEqual(self.github_tools.repository, "fake_user/new_repo")
        mock_github.return_value.get_repo.assert_called_once_with("fake_user/new_repo")
    
    @patch('github.Github')
    def test_create_issue(self, mock_github):
        """Test creating an issue"""
        # Setup mock
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_issue.number = 1
        mock_issue.html_url = "https://github.com/fake_user/fake_repo/issues/1"
        mock_issue.title = "Test Issue"
        mock_issue.body = "Test body"
        
        mock_repo.create_issue.return_value = mock_issue
        mock_github.return_value.get_repo.return_value = mock_repo
        self.github_tools.repo = mock_repo
        
        # Create issue
        result = self.github_tools.create_issue(
            title="Test Issue",
            body="Test body",
            labels=["bug"]
        )
        
        # Assert issue was created correctly
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Test body",
            labels=["bug"]
        )
        
        self.assertEqual(result["issue_number"], 1)
        self.assertEqual(result["issue_url"], "https://github.com/fake_user/fake_repo/issues/1")
        self.assertEqual(result["title"], "Test Issue")
        self.assertEqual(result["body"], "Test body")
    
    @patch('github.Github')
    def test_create_issue_error(self, mock_github):
        """Test error handling when creating an issue"""
        # Setup mock to raise an exception
        mock_repo = MagicMock()
        mock_repo.create_issue.side_effect = GithubException(
            status=422,
            data={"message": "Validation Failed"},
            headers={}
        )
        
        mock_github.return_value.get_repo.return_value = mock_repo
        self.github_tools.repo = mock_repo
        
        # Create issue (which should fail)
        result = self.github_tools.create_issue(
            title="Test Issue",
            body="Test body"
        )
        
        # Assert error was handled correctly
        self.assertIn("error", result)
        self.assertIn("Failed to create GitHub issue", result["error"])
    
    @patch('code_agent.tools.github_tools.run_command')
    def test_create_branch(self, mock_run_command):
        """Test creating a branch"""
        # Setup mock
        mock_run_command.return_value = ("", "", 0)
        
        # Set local repo path for testing
        self.github_tools.local_repo_path = self.temp_dir
        
        # Create branch
        result = self.github_tools.create_branch(
            branch_name="feature/test",
            base_branch="main"
        )
        
        # Assert git commands were called correctly
        self.assertEqual(mock_run_command.call_count, 5)  # Five git commands
        
        # Assert success
        self.assertEqual(result["status"], "success")
        self.assertIn("Successfully created and pushed branch", result["message"])
    
    @patch('code_agent.tools.github_tools.run_command')
    def test_create_branch_error(self, mock_run_command):
        """Test error handling when creating a branch"""
        # Setup mock to indicate a failure in git checkout
        mock_run_command.side_effect = [
            ("", "", 0),  # fetch
            ("", "", 0),  # checkout base
            ("", "", 0),  # pull
            ("", "Failed to create branch", 1),  # checkout new branch
            ("", "", 0)   # push (should not be called)
        ]
        
        # Set local repo path for testing
        self.github_tools.local_repo_path = self.temp_dir
        
        # Create branch (which should fail)
        result = self.github_tools.create_branch(
            branch_name="feature/test",
            base_branch="main"
        )
        
        # Assert error was handled correctly
        self.assertEqual(result["status"], "error")
        self.assertIn("Failed to create branch", result["message"])
    
    @patch('github.Github')
    def test_create_pull_request(self, mock_github):
        """Test creating a pull request"""
        # Setup mock
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.number = 1
        mock_pr.html_url = "https://github.com/fake_user/fake_repo/pull/1"
        mock_pr.title = "Test PR"
        mock_pr.body = "Test body"
        
        mock_repo.create_pull.return_value = mock_pr
        mock_github.return_value.get_repo.return_value = mock_repo
        self.github_tools.repo = mock_repo
        
        # Create pull request
        result = self.github_tools.create_pull_request(
            title="Test PR",
            body="Test body",
            head_branch="feature/test",
            base_branch="main"
        )
        
        # Assert PR was created correctly
        mock_repo.create_pull.assert_called_once_with(
            title="Test PR",
            body="Test body",
            head="feature/test",
            base="main"
        )
        
        self.assertEqual(result["pr_number"], 1)
        self.assertEqual(result["pr_url"], "https://github.com/fake_user/fake_repo/pull/1")
        self.assertEqual(result["title"], "Test PR")
        self.assertEqual(result["body"], "Test body")


if __name__ == "__main__":
    unittest.main() 
