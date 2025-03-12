from typing import Dict, Any, Optional, List
from github import Github, GithubException
import os
import subprocess
from pathlib import Path

class GitHubTools:
    """Enhanced GitHub tools with repository creation capabilities"""
    
    def __init__(self, token: str, username: str, repository: Optional[str] = None):
        """
        Initialize GitHub tools
        
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
        
        # Connect to repository if provided
        if repository:
            self.set_repository(repository)
    
    def set_repository(self, repository: str) -> Dict[str, str]:
        """
        Set the GitHub repository to work with
        
        Args:
            repository: GitHub repository name (username/repo or just repo)
            
        Returns:
            Status message
        """
        # If repository doesn't include username, add it
        if '/' not in repository:
            repository = f"{self.username}/{repository}"
        
        self.repository = repository
        try:
            self.repo = self.github.get_repo(repository)
            return {"status": "success", "message": f"Connected to repository: {repository}"}
        except GithubException as e:
            return {"status": "error", "message": f"Failed to connect to GitHub repository: {str(e)}"}
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        Create a new GitHub repository
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Repository details if successful
        """
        try:
            # Create repository
            user = self.github.get_user()
            repo = user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=True  # Initialize with README
            )
            
            # Set as current repository
            self.repository = repo.full_name
            self.repo = repo
            
            # Save repository to config
            try:
                config_path = os.path.join(str(Path.home()), ".code_agent", "config.json")
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                else:
                    config = {}
                
                if "github" not in config:
                    config["github"] = {}
                
                config["github"]["repository"] = repo.full_name
                
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            except Exception as e:
                print(f"Warning: Could not save repository to config: {str(e)}")
            
            return {
                "status": "success",
                "message": f"Created repository: {repo.full_name}",
                "repo_name": repo.full_name,
                "repo_url": repo.html_url
            }
        except GithubException as e:
            return {"status": "error", "message": f"Failed to create repository: {str(e)}"}
    
    def clone_repository(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Clone the repository to a local directory
        
        Args:
            path: Path where to clone the repository (optional)
            
        Returns:
            Path to the cloned repository
        """
        if not self.repository:
            return {"status": "error", "message": "Repository not set. Call set_repository first."}
        
        if path is None:
            # If no path provided, create a temporary directory
            path = os.path.join(os.getcwd(), self.repository.split('/')[-1])
        
        # Clone the repository
        clone_url = f"https://{self.token}@github.com/{self.repository}.git"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Check if directory already contains a git repository
            if os.path.exists(os.path.join(path, '.git')):
                # Repository already cloned, just pull latest changes
                subprocess.run(["git", "-C", path, "pull"], check=True)
            else:
                # Clone the repository
                subprocess.run(["git", "clone", clone_url, path], check=True)
            
            self.local_repo_path = path
            return {"status": "success", "message": f"Repository cloned to {path}", "path": path}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error during repository cloning: {str(e)}"}
    
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
            result = self.clone_repository()
            if result["status"] == "error":
                return result
        
        try:
            # Update the local repo
            subprocess.run(["git", "-C", self.local_repo_path, "fetch", "origin"], check=True)
            subprocess.run(["git", "-C", self.local_repo_path, "checkout", base_branch], check=True)
            subprocess.run(["git", "-C", self.local_repo_path, "pull", "origin", base_branch], check=True)
            
            # Create and push the new branch
            subprocess.run(["git", "-C", self.local_repo_path, "checkout", "-b", branch_name], check=True)
            subprocess.run(["git", "-C", self.local_repo_path, "push", "-u", "origin", branch_name], check=True)
            
            return {
                "status": "success", 
                "message": f"Successfully created and pushed branch: {branch_name}"
            }
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error creating branch: {str(e)}"}
    
    def commit_changes(self, message: str, files: Optional[List[str]] = None, branch: Optional[str] = None) -> Dict[str, str]:
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
                subprocess.run(["git", "-C", self.local_repo_path, "checkout", branch], check=True)
            
            # Add files
            if files:
                for file in files:
                    file_path = os.path.join(self.local_repo_path, file)
                    subprocess.run(["git", "-C", self.local_repo_path, "add", file], check=True)
            else:
                subprocess.run(["git", "-C", self.local_repo_path, "add", "."], check=True)
            
            # Commit
            subprocess.run(["git", "-C", self.local_repo_path, "commit", "-m", message], check=True)
            
            # Push
            subprocess.run(["git", "-C", self.local_repo_path, "push"], check=True)
            
            return {
                "status": "success",
                "message": f"Successfully committed and pushed changes with message: {message}"
            }
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Git error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error committing changes: {str(e)}"}
    
    def create_pull_request(self, title: str, body: str, head_branch: str, base_branch: str = "main") -> Dict[str, Any]:
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
            return {"status": "error", "message": "Repository not set. Call set_repository first."}
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            return {
                "status": "success",
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "title": pr.title,
                "body": pr.body
            }
        except GithubException as e:
            return {"status": "error", "message": f"Failed to create GitHub pull request: {str(e)}"}

# Function to create a GitHub tools instance with proper error handling
def create_github_tools(token: str, username: str, repository: Optional[str] = None) -> GitHubTools:
    """
    Create and return a GitHubTools instance
    
    Args:
        token: GitHub API token
        username: GitHub username
        repository: GitHub repository name (optional)
        
    Returns:
        GitHubTools instance
    """
    return GitHubTools(token, username, repository)