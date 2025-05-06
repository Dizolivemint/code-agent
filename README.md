# Code Agent

A multi-agent system that automates software development workflows using AI agents to write code, tests, and documentation.

## Features

- 🤖 Multi-agent system with specialized roles (architect, developer, tester)
- 🌐 GitHub integration for repository management, branches, and PRs
- 📝 Code generation and management
- 🧪 Automated test generation and execution
- 📚 Documentation generation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/code-agent.git
cd code-agent

# Install the package in development mode
pip install -e .
```

## Environment Setup and Validation

Before using Code Agent, ensure your environment is properly configured:

### Required Environment Variables

Set the following in your `.env` file or environment:

```
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username_here
```

Optional but recommended:
```
HF_TOKEN=your_huggingface_token_here
```

### Required Dependencies

Install all dependencies with:

```bash
pip install -r requirements.txt
```

### Validating Your Environment

Run the environment validator to check if all prerequisites are met:

```bash
python -m code_agent.validate
```

This checks that:
- GitHub credentials are properly configured
- Required packages are installed
- Configuration is valid

If any issues are found, the validator will provide clear instructions to fix them.

## Configuration

Run the initialization command to set up your configuration:

```bash
code-agent init
```

This will prompt you for:
- GitHub token (for GitHub integration)
- GitHub username
- Model ID (defaults to "meta-llama/Meta-Llama-3.1-70B-Instruct")
- Project root directory

Alternatively, you can set these via environment variables:

```bash
export GITHUB_TOKEN=your_token_here
export GITHUB_USERNAME=your_username
export MODEL_ID=your_preferred_model_id
export PROJECT_ROOT=/path/to/projects
```

## Usage

### Building a Project

To build a complete project from requirements:

```bash
code-agent build --name "TaskManager" --description "A task management system" --requirements-file task_app_requirements.txt --create-repo
```

If you don't provide the arguments, the command will prompt you for them.

Requirements can be provided via a file or entered interactively when prompted.

### Implementing a Feature

To implement a specific feature in an existing project:

```bash
code-agent feature --name "User Authentication" --description "Implement user registration, login, and logout" --project-dir my_project
```

This will:
1. Create a feature branch (if GitHub integration is set up)
2. Implement the feature code
3. Write tests for the feature
4. Commit the changes and create a pull request (if GitHub integration is set up)

When specifying a project directory, Code Agent supports:
```bash
# Using a project name in the 'projects' directory
code-agent feature --name "User Authentication" --description "Implement user auth" --project-dir my_project

# Using a relative or absolute path
code-agent feature --name "User Authentication" --description "Implement user auth" --project-dir ./custom/my_project
```

## Architecture

Code Agent uses a multi-agent architecture:

1. **Architect Agent**: Designs the overall system architecture and component relationships
2. **Developer Agent**: Implements code based on requirements and architecture designs
3. **Tester Agent**: Creates and runs tests to validate implemented code

Each agent has access to specialized tools:
- Filesystem tools for directory and file operations
- GitHub tools for repository management
- Code tools for analysis and formatting
- Test tools for test generation and execution

The Development Manager orchestrates the agents and tools, coordinating the development workflow.

## Directory Structure

```
code_agent/
├── __init__.py
├── cli.py                    # Command-line interface
├── development_manager.py    # Main orchestration manager
├── agents/                   # Specialized agents
│   ├── __init__.py
│   └── ...
├── tools/                    # Tools for the agents
│   ├── __init__.py
│   ├── github_tools.py       # GitHub integration
│   ├── filesystem_tools.py   # File operations
│   ├── code_tools.py         # Code analysis
│   └── test_tools.py         # Test generation and execution
└── utils/                    # Utility functions
    ├── __init__.py
    └── ...
```

## Development Workflow

The typical development workflow follows these stages:

1. **Requirements Analysis**:
   - Break down requirements into features
   - Identify components and dependencies

2. **Architecture Design**:
   - Design directory structure
   - Define component interfaces
   - Establish data models

3. **Feature Implementation**:
   - Create feature branch
   - Implement code
   - Add documentation

4. **Testing**:
   - Generate tests
   - Run tests

5. **Code Review**:
   - Create pull request
   - Provide implementation details

# New! Gradio Interface
### Implementation Details

The UI implementation follows these key principles:

1. **Modular Design**: The UI is implemented as a separate module but leverages the existing CodeAgentApp functionality.

2. **Consistent Interface**: The UI provides the same core functionality as the CLI but in a more user-friendly format.

3. **Tabs for Organization**: Different functionalities are organized into tabs:
   - Configuration: For setting up GitHub credentials and model settings
   - Create Project: For building new projects from requirements 
   - Implement Feature: For adding features to existing projects
   - File Browser: For viewing generated files

4. **Reuse of Core Code**: The UI doesn't reimplement any of the core functionality but instead calls the existing methods from CodeAgentApp.

5. **Error Handling**: All UI methods include proper exception handling to ensure a smooth user experience.

6. **Interactive Elements**: The UI provides interactive elements like dropdowns for selecting projects and refresh buttons for updating lists.

### Installation and Usage

After implementing these changes, you can use the UI by:

1. Installing the updated package:
```bash
pip install -e .

Running the UI:

```bash code-agent-ui```
or
```bash python -m code_agent.ui_launcher```

## License

MIT