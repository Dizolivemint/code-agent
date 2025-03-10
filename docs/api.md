# Code Agent API Reference

This document provides a reference for the Code Agent API. It covers the main classes and functions that can be used to integrate Code Agent into your applications.

## Main Application

### `CodeAgentApp`

The main application class that provides access to all Code Agent functionality.

```python
from code_agent import CodeAgentApp, create_app

# Create app instance
app = create_app()
```

#### Methods

##### `initialize(github_token=None, github_username=None, github_repository=None)`

Initialize the application configuration.

```python
app.initialize(
    github_token="your_github_token",
    github_username="your_github_username",
    github_repository="your_repository"
)
```

##### `set_project(name, description, root_dir)`

Set the current project to work with.

```python
app.set_project(
    name="TaskManager",
    description="Task management system with user authentication",
    root_dir="./TaskManager"
)
```

##### `build_project(requirements, project_name, output_dir=None)`

Build a complete project from requirements.

```python
requirements = """
Build a task management API with:
1. User authentication (signup, login, logout)
2. Task creation, updating, and deletion
"""

result = app.build_project(requirements, "TaskManager")
```

##### `implement_feature(feature_name, feature_description)`

Implement a specific feature in the current project.

```python
result = app.implement_feature(
    "User Authentication",
    "Implement user signup, login, and logout functionality."
)
```

##### `create_tests(feature_name, implementation_info)`

Create tests for an implemented feature.

```python
result = app.create_tests(
    "User Authentication",
    implementation_info
)
```

##### `review_code(feature_name, implementation_info, test_results)`

Review code for an implemented feature.

```python
result = app.review_code(
    "User Authentication",
    implementation_info,
    test_results
)
```

##### `process_request(request)`

Process a general request using the manager agent.

```python
result = app.process_request(
    "Refactor the authentication module to use JWT tokens."
)
```

## Configuration

### `Config`

Manages the application configuration.

```python
from code_agent.config import Config

# Create config instance
config = Config()
```

#### Methods

##### `save()`

Save the current configuration to a file.

```python
config.save()
```

##### `set_project(name, description, root_dir)`

Set the current project configuration.

```python
config.set_project(
    name="TaskManager",
    description="Task management system",
    root_dir="./TaskManager"
)
```

##### `validate()`

Validate that the configuration is complete and usable.

```python
if config.validate():
    print("Configuration is valid")
else:
    print("Configuration is incomplete")
```

## Agent Orchestrator

### `AgentOrchestrator`

Coordinates the specialized agents.

```python
from code_agent.agents.orchestrator import AgentOrchestrator

# Create orchestrator instance
orchestrator = AgentOrchestrator(config, project_path)
```

#### Methods

##### `analyze_requirements(requirements)`

Analyze project requirements using the architect agent.

```python
result = orchestrator.analyze_requirements(
    "Build a task management system with user authentication."
)
```

##### `design_architecture(requirements, project_name)`

Design the project architecture using the architect agent.

```python
result = orchestrator.design_architecture(
    "Build a task management system with user authentication.",
    "TaskManager"
)
```

##### `implement_feature(feature_name, feature_description, architecture_info)`

Implement a specific feature using the developer agent.

```python
result = orchestrator.implement_feature(
    "User Authentication",
    "Implement user signup, login, and logout functionality.",
    architecture_info
)
```

##### `create_tests(feature_name, implementation_info)`

Create tests for an implemented feature using the tester agent.

```python
result = orchestrator.create_tests(
    "User Authentication",
    implementation_info
)
```

##### `review_code(feature_name, implementation_info, test_results)`

Review code for an implemented feature using the reviewer agent.

```python
result = orchestrator.review_code(
    "User Authentication",
    implementation_info,
    test_results
)
```

## Tools

### `GitHubTools`

Tools for interacting with GitHub repositories.

```python
from code_agent.tools.github_tools import GitHubTools

# Create GitHub tools instance
github_tools = GitHubTools(
    token="your_github_token",
    username="your_github_username",
    repository="your_repository"
)
```

#### Methods

##### `set_repository(repository)`

Set the GitHub repository to work with.

```python
github_tools.set_repository("username/repository")
```

##### `create_issue(title, body, labels=None)`

Create a GitHub issue.

```python
result = github_tools.create_issue(
    title="Implement user authentication",
    body="Create signup, login, and logout functionality.",
    labels=["feature"]
)
```

##### `create_branch(branch_name, base_branch="main")`

Create a new branch in the GitHub repository.

```python
result = github_tools.create_branch(
    branch_name="feature/user-auth",
    base_branch="main"
)
```

##### `commit_changes(message, files=None, branch=None)`

Commit changes to the repository.

```python
result = github_tools.commit_changes(
    message="Implement user authentication",
    files=["auth.py", "models/user.py"],
    branch="feature/user-auth"
)
```

##### `create_pull_request(title, body, head_branch, base_branch="main")`

Create a pull request on GitHub.

```python
result = github_tools.create_pull_request(
    title="Implement user authentication",
    body="This PR adds user authentication functionality.",
    head_branch="feature/user-auth",
    base_branch="main"
)
```

### `FilesystemTools`

Tools for working with the local filesystem.

```python
from code_agent.tools import filesystem_tools

# Create filesystem tools instance
filesystem_tools = FilesystemTools(base_path="./project")
```

#### Methods

##### `set_base_path(path)`

Set the base path for filesystem operations.

```python
filesystem_tools.set_base_path("./new_project")
```

##### `list_directory(path="")`

List contents of a directory.

```python
result = filesystem_tools.list_directory("src")
```

##### `read_file(path)`

Read a file's content.

```python
result = filesystem_tools.read_file("src/main.py")
```

##### `create_directory(path)`

Create a directory.

```python
result = filesystem_tools.create_directory("src/models")
```

##### `write_file(path, content)`

Write content to a file.

```python
result = filesystem_tools.write_file(
    "src/models/user.py",
    "class User:\n    pass"
)
```

### `CodeTools`

Tools for code generation, analysis, and validation.

```python
from code_agent.tools.code_tools import CodeTools

# Create code tools instance
code_tools = CodeTools(project_path="./project")
```

#### Methods

##### `set_project_path(path)`

Set the project path.

```python
code_tools.set_project_path("./new_project")
```

##### `analyze_code(code)`

Analyze Python code for structure and quality.

```python
result = code_tools.analyze_code(
    "def hello():\n    print('Hello, world!')"
)
```

##### `format_code(code)`

Format Python code using Black.

```python
result = code_tools.format_code(
    "def hello():\n  print('Hello, world!')"
)
```

##### `lint_code(code, path=None)`

Lint Python code using flake8.

```python
result = code_tools.lint_code(
    "def hello():\n    print('Hello, world!')",
    path="hello.py"
)
```

### `TestTools`

Tools for test generation, execution, and coverage analysis.

```python
from code_agent.tools.test_tools import TestTools

# Create test tools instance
test_tools = TestTools(project_path="./project")
```

#### Methods

##### `set_project_path(path)`

Set the project path.

```python
test_tools.set_project_path("./new_project")
```

##### `generate_test(code_path, test_path=None)`

Generate a pytest test file for a given Python file.

```python
result = test_tools.generate_test(
    code_path="src/models/user.py",
    test_path="tests/test_user.py"
)
```

##### `run_tests(test_path, verbose=True)`

Run pytest tests on a file or directory.

```python
result = test_tools.run_tests(
    test_path="tests/test_user.py",
    verbose=True
)
```

##### `run_coverage(test_path, source_path=None)`

Run tests with coverage analysis.

```python
result = test_tools.run_coverage(
    test_path="tests/test_user.py",
    source_path="src/models"
)
``` 
