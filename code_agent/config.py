import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import dotenv
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for an individual agent"""
    name: str
    model_id: str
    provider: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4000
    
@dataclass
class GitHubConfig:
    """GitHub configuration"""
    token: str
    username: str
    repository: Optional[str] = None

@dataclass
class ProjectConfig:
    """Project configuration"""
    name: str
    description: str
    root_dir: Path
    features: list = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

class Config:
    """Main configuration class for the Code Agent application"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from environment or config file"""
        # Load environment variables
        dotenv.load_dotenv()
        
        # Set default config path
        if config_path is None:
            config_path = os.path.join(str(Path.home()), ".code_agent", "config.json")
        
        self.config_path = config_path
        self._config = {}
        
        # Try to load from config file
        self._load_from_file()
        
        # Set up GitHub config
        self.github = GitHubConfig(
            token=os.getenv("GITHUB_TOKEN") or self._config.get("github", {}).get("token", ""),
            username=os.getenv("GITHUB_USERNAME") or self._config.get("github", {}).get("username", ""),
            repository=os.getenv("GITHUB_REPOSITORY") or self._config.get("github", {}).get("repository", "")
        )
        
        # Set up default agent configs
        self.agents = {
            "architect": AgentConfig(
                name="architect",
                model_id=os.getenv("ARCHITECT_MODEL") or self._config.get("agents", {}).get("architect", {}).get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
            ),
            "developer": AgentConfig(
                name="developer",
                model_id=os.getenv("DEVELOPER_MODEL") or self._config.get("agents", {}).get("developer", {}).get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
            ),
            "tester": AgentConfig(
                name="tester",
                model_id=os.getenv("TESTER_MODEL") or self._config.get("agents", {}).get("tester", {}).get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
            ),
            "reviewer": AgentConfig(
                name="reviewer",
                model_id=os.getenv("REVIEWER_MODEL") or self._config.get("agents", {}).get("reviewer", {}).get("model_id", "meta-llama/Meta-Llama-3.1-70B-Instruct")
            )
        }
        
        # Current project config
        self.project = None
    
    def _load_from_file(self):
        """Load configuration from file if it exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self._config = json.load(f)
            except json.JSONDecodeError:
                self._config = {}
    
    def save(self):
        """Save the current configuration to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Prepare config for saving
        config_dict = {
            "github": {
                "token": self.github.token,
                "username": self.github.username,
                "repository": self.github.repository
            },
            "agents": {
                agent_name: {
                    "model_id": agent_config.model_id,
                    "provider": agent_config.provider,
                    "temperature": agent_config.temperature,
                    "max_tokens": agent_config.max_tokens
                } for agent_name, agent_config in self.agents.items()
            }
        }
        
        if self.project:
            config_dict["project"] = {
                "name": self.project.name,
                "description": self.project.description,
                "root_dir": str(self.project.root_dir),
                "features": self.project.features
            }
        
        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def set_project(self, name: str, description: str, root_dir: str):
        """Set the current project configuration"""
        self.project = ProjectConfig(
            name=name,
            description=description,
            root_dir=Path(root_dir)
        )
        self.save()

    def validate(self) -> bool:
        """Validate that the configuration is complete and usable"""
        if not self.github.token:
            return False
        if not self.github.username:
            return False
        
        # Check that at least one agent has a valid model
        if not any(agent.model_id for agent in self.agents.values()):
            return False
        
        return True