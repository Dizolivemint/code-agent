# Using Code Agent

Code Agent is an AI-powered development system that helps automate software development workflows using specialized AI agents.

## Installation

### Prerequisites

- Python 3.9 or higher
- GitHub account and personal access token (for GitHub integration)
- Hugging Face API token (for accessing AI models)

### Install from source

```bash
# Clone the repository
git clone https://github.com/username/code-agent.git
cd code-agent

# Install the package
pip install -e .
```

## Configuration

Before using Code Agent, you need to set up your configuration:

```bash
# Interactive setup
code-agent init

# Or with command-line arguments
code-agent init --github-token YOUR_TOKEN --github-username YOUR_USERNAME --github-repo YOUR_REPO
```

Alternatively, you can create a `.env` file in the root of your project:

```
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
HF_TOKEN=your_huggingface_token
```

## Basic Usage

### Building a Project from Requirements

To build a complete project from requirements:

```bash
# Interactive mode
code-agent build --project-name "My Project"

# Or specifying a requirements file
code-agent build --requirements-file requirements.txt --project-name "My Project" --output-dir ./my_project
```

### Implementing a Feature

To implement a specific feature:

```bash
code-agent feature --name "User Authentication" --description "Implement user signup and login" --project-dir ./my_project --test --review
```

### Interactive Mode

For a more interactive experience, use the chat interface:

```bash
code-agent chat --project-dir ./my_project
```

In chat mode, you can:

- Analyze requirements
- Implement features
- Create tests
- Review code
- Ask general development questions

## Example Workflow

Here's a typical workflow:

1. Initialize Code Agent configuration:
   ```bash
   code-agent init
   ```

2. Build a new project from requirements:
   ```bash
   code-agent build --project-name "TaskManager" --requirements-file requirements.txt
   ```

3. Enter interactive mode to work with the project:
   ```bash
   code-agent chat --project-dir ./TaskManager
   ```

4. In interactive mode, implement specific features:
   ```
   > implement
   Enter feature name: User Authentication
   Enter feature description: Implement user registration, login, and logout
   ```

5. Create tests for the feature:
   ```
   > test
   Enter feature name to test: User Authentication
   ```

6. Review the implementation:
   ```
   > review
   Enter feature name to review: User Authentication
   ```

## Advanced Usage

### Using as a Library

You can also use Code Agent as a library in your own Python code:

```python
from code_agent import create_app

# Create app instance
app = create_app()

# Initialize configuration
app.initialize(
    github_token="your_token",
    github_username="your_username",
    github_repository="your_repo"
)

# Set up a project
app.set 
