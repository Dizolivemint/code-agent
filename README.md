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
code-agent build --name "TaskManager" --description "A task management system" --requirements-file requirements.txt --create-repo
```

If you don't provide the arguments, the command will prompt you for them.

Requirements can be provided via a file or entered interactively when prompted.

### Implementing a Feature

To implement a specific feature in an existing project:

```bash
code-agent feature --name "User Authentication" --description "Implement user registration, login, and logout" --project-dir ./my_project
```

This will:
1. Create a feature branch (if GitHub integration is set up)
2. Implement the feature code
3. Write tests for the feature
4. Commit the changes and create a pull request (if GitHub integration is set up)

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

## License

MIT