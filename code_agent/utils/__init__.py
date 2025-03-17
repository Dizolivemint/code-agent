"""
Utility functions for the Code Agent application.
"""

from .logger import logger, setup_logger
from .helpers import (
    sanitize_filename, 
    sanitize_branch_name, 
    create_directory_if_not_exists,
    is_git_repo,
    run_command,
    get_current_branch,
    extract_features_from_requirements
)
from .project_utils import initialize_project_structure

__all__ = [
    'logger',
    'setup_logger',
    'sanitize_filename',
    'sanitize_branch_name',
    'create_directory_if_not_exists',
    'is_git_repo',
    'run_command',
    'get_current_branch',
    'extract_features_from_requirements',
    'initialize_project_structure'
] 
