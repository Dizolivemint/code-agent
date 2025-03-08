from smolagents import tool
from github import Github, GithubException
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import tempfile
import shutil

from ..utils.logger import logger
from ..utils.helpers import run_command, sanitize_branch_name

class GitHubTools:
    """Tools for interacting with GitHub repositories"""
    
    def __init__(self, token: str, username: str, repository: Optional[str] = None):
        """
        Initialize GitHub tools with authentication
        
        Args:
            token: GitHub API token
            username: GitHub username
            repository: GitHub repository name (optional)
        """
        self.token = token
        self.username = username
        self.repository = repository
        self.github = Github(token)
        self.repo = None
        
        self.local_repo_path = None
        
        if repository:
            self.set_repository(repository)
    
    def set_repository(self, repository: str) -> None:
        """
        Set the GitHub repository to work with
        
        Args:
            repository: GitHub repository name (username/repo or just repo)
        """
        # If repository doesn't include username, add it
        if '/' not in repository:
            repository = f"{self.username}/{repository}"
        
        self.repository = repository
        try:
            self.repo = self.github.get_repo(repository)
            logger.info(f"Successfully connected to GitHub repository: {repository}")
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub repository: {e}")
            raise
    
    def clone_repository(self, path: Optional[str] = None) -> str:
        """
        Clone the repository to a local directory
        
        Args:
            path: Path where to clone the repository (optional)
            
        Returns:
            Path to the cloned repository
        """
        if not self.repository:
            raise ValueError("Repository not set. Call set_repository first.")
        
        if path is None:
            path = tempfile.mkdtemp(prefix="code_agent_repo_")
        
        # Clone the repository
        clone_url = f"https://{self.token}@github.com/{self.repository}.git"
        
        try:
            logger.info(f"Cloning repository to {path}")
            stdout, stderr, return_code = run_command(
                ["git", "clone", clone_url, path]
            )
            
            if return_code != 0:
                logger.error(f"Failed to clone repository: {stderr}")
                raise Exception(f"Failed to clone repository: {stderr}")
            
            self.local_repo_path = path
            return path
            
        except Exception as e:
            logger.error(f"Error during repository cloning: {str(e)}")
            raise
    
    @tool
    def create_issue(self, title: str, body: str, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a GitHub issue
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of labels to apply to the issue
            
        Returns:
            Dictionary with issue details including URL and number
        """
        if not self.repo:
            return {"error": "Repository not set. Call set_repository first."}
        
        try:
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            logger.info(f"Created issue #{issue.number}: {title}")
            
            return {
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "title": issue.title,
                "body": issue.body
            }
        except GithubException as e:
            error_msg = f"Failed to create GitHub issue: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    @tool
    def get_issues(self, state: str = "open") -> List[Dict[str, Any]]:
        """
        Get GitHub issues for the repository
        
        Args:
            state: Issue state ('open', 'closed', or 'all')
            
        Returns:
            List of issues with their details
        """
        if not self.repo:
            return [{"error": "Repository not set. Call set_repository first."}]
        
        try:
            issues = self.repo.get_issues(state=state)
            return [
                {
                    "issue_number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "url": issue.html_url,
                    "labels": [label.name for label in issue.labels]
                }
                for issue in issues
            ]
        except GithubException as e:
            error_msg = f"Failed to get GitHub issues: {str(e)}"
            logger.error(error_msg)
            return [{"error": error_msg}]
    
    @tool
    def create_branch(self, branch_name: str, base_branch: str = "main") -> Dict[str, str]:
        """
        Create a new branch in the GitHub repository
        
        Args:
            branch_name: Name for the new branch
            base_branch: The branch to base the new branch on
            
        Returns:
            Dictionary with status and message
        """
        if not self.local_repo_path:
            # Clone repository if not already cloned
            self.clone_repository()
        
        # Sanitize branch name
        branch_name = sanitize_branch_name(branch_name)
        
        try:
            # Update the local repo
            run_command(["git", "fetch", "origin"], cwd=self.local_repo_path)
            run_command(["git", "checkout", base_branch], cwd=self.local_repo_path)
            run_command(["git", "pull", "origin", base_branch], cwd=self.local_repo_path)
            
            # Create and push the new branch
            _, stderr, return_code = run_command(
                ["git", "checkout", "-b", branch_name],
                cwd=self.local_repo_path
            )
            
            if return_code != 0:
                logger.error(f"Failed to create branch: {stderr}")
                return {"status": "error", "message": f"Failed to create branch: {stderr}"}
            
            _, stderr, return_code = run_command(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.local_repo_path
            )
            
            if return_code != 0:
                logger.error(f"Failed to push branch: {stderr}")
                return {"status": "error", "message": f"Failed to push branch: {stderr}"}
            
            logger.info(f"Successfully created and pushed branch: {branch_name}")
            return {
                "status": "success", 
                "message": f"Successfully created and pushed branch: {branch_name}"
            }
            
        except Exception as e:
            error_msg = f"Error creating branch: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    @tool
    def commit_changes(
        self, 
        message: str, 
        files: Optional[List[str]] = None, 
        branch: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Commit changes to the repository
        
        Args:
            message: Commit message
            files: List of files to commit (commits all changes if None)
            branch: Branch to commit to (uses current branch if None)
            
        Returns:
            Dictionary with status and message
        """
        if not self.local_repo_path:
            return {
                "status": "error", 
                "message": "Local repository not available. Clone repository first."
            }
        
        try:
            # Switch to the specified branch if provided
            if branch:
                _, stderr, return_code = run_command(
                    ["git", "checkout", branch],
                    cwd=self.local_repo_path
                )
                
                if return_code != 0:
                    logger.error(f"Failed to switch to branch {branch}: {stderr}")
                    return {
                        "status": "error", 
                        "message": f"Failed to switch to branch {branch}: {stderr}"
                    }
            
            # Add files
            if files:
                for file in files:
                    run_command(["git", "add", file], cwd=self.local_repo_path)
            else:
                run_command(["git", "add", "."], cwd=self.local_repo_path)
            
            # Commit
            _, stderr, return_code = run_command(
                ["git", "commit", "-m", message],
                cwd=self.local_repo_path
            )
            
            if return_code != 0:
                # If nothing to commit, that's okay
                if "nothing to commit" in stderr:
                    return {
                        "status": "warning",
                        "message": "Nothing to commit, working tree clean"
                    }
                else:
                    logger.error(f"Failed to commit: {stderr}")
                    return {"status": "error", "message": f"Failed to commit: {stderr}"}
            
            # Push
            _, stderr, return_code = run_command(
                ["git", "push"],
                cwd=self.local_repo_path
            )
            
            if return_code != 0:
                logger.error(f"Failed to push: {stderr}")
                return {"status": "error", "message": f"Failed to push: {stderr}"}
            
            logger.info(f"Successfully committed and pushed changes with message: {message}")
            return {
                "status": "success",
                "message": f"Successfully committed and pushed changes with message: {message}"
            }
            
        except Exception as e:
            error_msg = f"Error committing changes: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    @tool
    def create_pull_request(
        self, 
        title: str, 
        body: str, 
        head_branch: str, 
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create a pull request on GitHub
        
        Args:
            title: PR title
            body: PR description
            head_branch: The branch containing changes
            base_branch: The branch to merge changes into
            
        Returns:
            Dictionary with PR details including URL and number
        """
        if not self.repo:
            return {"error": "Repository not set. Call set_repository first."}
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            logger.info(f"Created PR #{pr.number}: {title}")
            
            return {
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "title": pr.title,
                "body": pr.body
            }
        except GithubException as e:
            error_msg = f"Failed to create GitHub pull request: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    @tool
    def get_content(self, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the content of a file from the GitHub repository
        
        Args:
            path: Path to the file
            ref: The branch, tag or commit to get the content from
            
        Returns:
            Dictionary with file content and metadata
        """
        if not self.repo:
            return {"error": "Repository not set. Call set_repository first."}
        
        try:
            content = self.repo.get_contents(path, ref=ref)
            
            if isinstance(content, list):
                # Directory listing
                return {
                    "type": "directory",
                    "path": path,
                    "items": [
                        {"name": item.name, "path": item.path, "type": item.type}
                        for item in content
                    ]
                }
            else:
                # File content
                return {
                    "type": "file",
                    "path": content.path,
                    "content": content.decoded_content.decode('utf-8'),
                    "sha": content.sha
                }
        except GithubException as e:
            if e.status == 404:
                return {
                    "type": "missing",
                    "path": path,
                    "error": f"File not found: {path}"
                }
            error_msg = f"Failed to get content: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def cleanup(self):
        """Clean up temporary directories and resources"""
        if self.local_repo_path and os.path.exists(self.local_repo_path):
            try:
                shutil.rmtree(self.local_repo_path)
                logger.info(f"Cleaned up local repository at {self.local_repo_path}")
            except Exception as e:
                logger.error(f"Failed to clean up local repository: {str(e)}")
