import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional

def sanitize_filename(name: str) -> str:
    """Convert a string to a valid filename"""
    # Replace spaces with underscores and remove invalid characters
    name = re.sub(r'[^\w\-\.]', '_', name)
    return name

def sanitize_branch_name(name: str) -> str:
    """Convert a string to a valid git branch name"""
    # Replace spaces and special characters with dashes
    name = re.sub(r'[^\w\-]', '-', name)
    name = re.sub(r'-+', '-', name)  # Replace multiple dashes with single dash
    name = name.lower().strip('-')  # Lowercase and trim dashes from start/end
    return name

def create_directory_if_not_exists(path: str) -> None:
    """Create a directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)

def is_git_repo(path: str) -> bool:
    """Check if the given path is a git repository"""
    return os.path.isdir(os.path.join(path, '.git'))

def run_command(cmd: List[str], cwd: Optional[str] = None) -> tuple:
    """Run a shell command and return stdout, stderr, and return code"""
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def get_current_branch(repo_path: str) -> str:
    """Get the current git branch"""
    stdout, _, _ = run_command(['git', 'branch', '--show-current'], cwd=repo_path)
    return stdout.strip()

def extract_features_from_requirements(requirements: str) -> List[dict]:
    """
    Extract features from requirements text using a simple heuristic.
    In a real implementation, we would use an LLM for this.
    """
    features = []
    lines = requirements.strip().split('\n')
    
    current_feature = None
    description = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a number (likely a feature)
        if re.match(r'^\d+\.', line):
            # Save previous feature if exists
            if current_feature:
                features.append({
                    'name': current_feature,
                    'description': ' '.join(description)
                })
            
            # Extract new feature
            current_feature = line.split('.', 1)[1].strip()
            description = []
        else:
            # Add to current feature description
            description.append(line)
    
    # Add the last feature
    if current_feature:
        features.append({
            'name': current_feature,
            'description': ' '.join(description)
        })
    
    return features
