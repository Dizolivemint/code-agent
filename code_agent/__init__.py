"""
Code Agent - A multi-agent system that automates software development workflows.
"""

__version__ = '0.1.0'

from .main import CodeAgentApp, create_app

# Add UI-related imports and functions
def launch_ui_app(**kwargs):
    """Launch the Code Agent UI application"""
    from .ui import launch_ui
    launch_ui(**kwargs)

__all__ = ['CodeAgentApp', 'create_app', 'launch_ui_app']