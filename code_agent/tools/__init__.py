"""
Tools for the Code Agent application.
"""

# Import tool functions directly
from .filesystem_tools import (
    set_base_path,
    list_directory,
    read_file, 
    create_directory,
    write_file
)

from .code_tools import (
    set_project_path as set_code_project_path,
    analyze_code,
    format_code
)

from .test_tools import (
    set_project_path as set_test_project_path,
    generate_test,
    run_tests,
    run_coverage
)

# Import full modules (alternative approach)
from . import filesystem_tools
from . import code_tools
from . import test_tools
from . import github_tools
from . import development_manager

# Define what's available when importing with *
__all__ = [
    # Modules
    'filesystem_tools',
    'code_tools',
    'test_tools',
    'github_tools',
    'development_manager',
    
    # Functions
    'set_base_path',
    'list_directory',
    'read_file',
    'create_directory',
    'write_file',
    'analyze_code',
    'format_code',
    'generate_test',
    'run_tests',
    'run_coverage'
]