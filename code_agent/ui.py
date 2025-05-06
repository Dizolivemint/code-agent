# code_agent/ui.py
import os
import json
import gradio as gr
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .main import CodeAgentApp, create_app
from .utils.logger import logger, setup_logger
from .config import Config


class CodeAgentUI:
    """Gradio UI for the Code Agent application"""

    def __init__(self):
        """Initialize the UI components"""
        self.app = create_app()
        self.config = self.app.config
        self.project_dir = os.path.join(os.getcwd(), "projects")
        
        # Create projects directory if it doesn't exist
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Set up logger
        setup_logger(log_file="code_agent_ui.log", level="INFO")
        logger.info("CodeAgentUI initialized")

    def update_config(self, github_token: str, github_username: str, model_id: str) -> str:
        """
        Update configuration with the provided values
        
        Args:
            github_token: GitHub API token
            github_username: GitHub username
            model_id: Model ID for the agent
            
        Returns:
            Status message
        """
        # Update configuration
        try:
            success = self.app.initialize(
                github_token=github_token,
                github_username=github_username
            )
            
            # Update model ID for all agents
            for agent_name in self.config.agents:
                self.config.agents[agent_name].model_id = model_id
            
            self.config.save()
            
            if success:
                return f"Configuration updated successfully. Model set to: {model_id}"
            else:
                return "Failed to update configuration. Please check the logs for details."
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return f"Error updating configuration: {str(e)}"

    def list_projects(self) -> List[str]:
        """
        List available projects
        
        Returns:
            List of project names
        """
        try:
            projects = []
            for item in os.listdir(self.project_dir):
                if os.path.isdir(os.path.join(self.project_dir, item)):
                    projects.append(item)
            return projects
        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return []

    def create_project(self, 
                     name: str, 
                     description: str, 
                     requirements: str, 
                     create_repo: bool) -> Tuple[str, str]:
        """
        Create a new project
        
        Args:
            name: Project name
            description: Project description
            requirements: Project requirements
            create_repo: Whether to create a GitHub repository
            
        Returns:
            Status message and project path
        """
        try:
            # Build the project
            result = self.app.build_project(
                requirements=requirements,
                project_name=name,
                output_dir=os.path.join(self.project_dir, name.replace(" ", "_").lower())
            )
            
            project_path = result.get("project", {}).get("project_dir", "")
            
            if project_path:
                return f"Project '{name}' created successfully.", project_path
            else:
                return "Failed to create project. Please check the logs for details.", ""
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return f"Error creating project: {str(e)}", ""

    def implement_feature(self, 
                        project_name: str, 
                        feature_name: str, 
                        feature_description: str) -> str:
        """
        Implement a feature for a project
        
        Args:
            project_name: Project name
            feature_name: Feature name
            feature_description: Feature description
            
        Returns:
            Implementation results
        """
        try:
            # Set project
            project_dir = os.path.join(self.project_dir, project_name)
            self.app.set_project(project_name, "", project_dir)
            
            # Implement feature
            result = self.app.implement_feature(
                feature_name=feature_name,
                feature_description=feature_description
            )
            
            return f"Feature '{feature_name}' implemented successfully.\n\n{json.dumps(result, indent=2)}"
        except Exception as e:
            logger.error(f"Error implementing feature: {str(e)}")
            return f"Error implementing feature: {str(e)}"

    def create_ui(self) -> gr.Blocks:
        """
        Create the Gradio UI
        
        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(title="Code Agent UI") as ui:
            gr.Markdown("# Code Agent UI")
            gr.Markdown("AI-powered development team for automating software development workflows")
            
            with gr.Tabs() as tabs:
                # Configuration Tab
                with gr.TabItem("Configuration"):
                    gr.Markdown("## Configuration")
                    gr.Markdown("Set up your GitHub credentials and model settings")
                    
                    with gr.Row():
                        github_token = gr.Textbox(
                            label="GitHub Token",
                            placeholder="Your GitHub personal access token",
                            type="password",
                            value=self.config.github.token
                        )
                        github_username = gr.Textbox(
                            label="GitHub Username",
                            placeholder="Your GitHub username",
                            value=self.config.github.username
                        )
                    
                    with gr.Row():
                        model_id = gr.Textbox(
                            label="Model ID",
                            placeholder="Hugging Face model ID",
                            value=self.config.agents["architect"].model_id or "meta-llama/Meta-Llama-3.1-70B-Instruct"
                        )
                    
                    with gr.Row():
                        update_config_btn = gr.Button("Update Configuration")
                    
                    config_output = gr.Textbox(label="Configuration Status", interactive=False)
                    
                    update_config_btn.click(
                        fn=self.update_config,
                        inputs=[github_token, github_username, model_id],
                        outputs=config_output
                    )
                
                # Create Project Tab
                with gr.TabItem("Create Project"):
                    gr.Markdown("## Create Project")
                    gr.Markdown("Create a new project from requirements")
                    
                    with gr.Row():
                        project_name = gr.Textbox(
                            label="Project Name",
                            placeholder="Enter project name"
                        )
                        project_description = gr.Textbox(
                            label="Project Description",
                            placeholder="Enter project description"
                        )
                    
                    project_requirements = gr.Textbox(
                        label="Project Requirements",
                        placeholder="Enter detailed project requirements",
                        lines=10
                    )
                    
                    with gr.Row():
                        create_repo_checkbox = gr.Checkbox(
                            label="Create GitHub Repository",
                            value=False
                        )
                        create_project_btn = gr.Button("Create Project")
                    
                    with gr.Row():
                        project_output = gr.Textbox(
                            label="Project Creation Status",
                            interactive=False
                        )
                        project_path = gr.Textbox(
                            label="Project Path",
                            interactive=False
                        )
                    
                    create_project_btn.click(
                        fn=self.create_project,
                        inputs=[project_name, project_description, project_requirements, create_repo_checkbox],
                        outputs=[project_output, project_path]
                    )
                
                # Implement Feature Tab
                with gr.TabItem("Implement Feature"):
                    gr.Markdown("## Implement Feature")
                    gr.Markdown("Implement a specific feature for an existing project")
                    
                    with gr.Row():
                        project_selector = gr.Dropdown(
                            label="Select Project",
                            choices=self.list_projects()
                        )
                        refresh_projects_btn = gr.Button("Refresh Projects")
                    
                    with gr.Row():
                        feature_name = gr.Textbox(
                            label="Feature Name",
                            placeholder="Enter feature name"
                        )
                        feature_description = gr.Textbox(
                            label="Feature Description",
                            placeholder="Enter feature description",
                            lines=5
                        )
                    
                    implement_feature_btn = gr.Button("Implement Feature")
                    
                    feature_output = gr.Textbox(
                        label="Implementation Result",
                        interactive=False,
                        lines=10
                    )
                    
                    refresh_projects_btn.click(
                        fn=self.list_projects,
                        inputs=[],
                        outputs=[project_selector]
                    )
                    
                    implement_feature_btn.click(
                        fn=self.implement_feature,
                        inputs=[project_selector, feature_name, feature_description],
                        outputs=feature_output
                    )
                
                # File Browser Tab
                with gr.TabItem("File Browser"):
                    gr.Markdown("## Project Files")
                    gr.Markdown("Browse and view project files")
                    
                    with gr.Row():
                        file_project_selector = gr.Dropdown(
                            label="Select Project",
                            choices=self.list_projects()
                        )
                        file_refresh_btn = gr.Button("Refresh")
                    
                    file_path = gr.Textbox(label="File Path", placeholder="Path to file within the project")
                    view_file_btn = gr.Button("View File")
                    
                    file_content = gr.Code(
                        label="File Content",
                        language="python",
                        interactive=False,
                        lines=20
                    )
                    
                    def view_file(project_name, file_path):
                        """View the content of a file"""
                        try:
                            full_path = os.path.join(self.project_dir, project_name, file_path)
                            with open(full_path, 'r') as f:
                                content = f.read()
                            return content
                        except Exception as e:
                            return f"Error viewing file: {str(e)}"
                    
                    view_file_btn.click(
                        fn=view_file,
                        inputs=[file_project_selector, file_path],
                        outputs=file_content
                    )
                    
                    file_refresh_btn.click(
                        fn=self.list_projects,
                        inputs=[],
                        outputs=[file_project_selector]
                    )
            
            # Footer
            gr.Markdown("---")
            gr.Markdown("Code Agent UI - Automating software development workflows")
        
        return ui

    def launch(self, **kwargs):
        """
        Launch the Gradio UI
        
        Args:
            **kwargs: Additional arguments for gr.launch()
        """
        ui = self.create_ui()
        ui.launch(**kwargs)


def launch_ui(**kwargs):
    """
    Launch the Code Agent UI
    
    Args:
        **kwargs: Additional arguments for gr.launch()
    """
    ui = CodeAgentUI()
    ui.launch(**kwargs)


if __name__ == "__main__":
    launch_ui(share=True)