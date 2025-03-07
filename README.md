# Code Agent

A multi-agent system that automates software development workflows using AI agents to write code, tests, and documentation as a professional scrum team would.

## Features

- 🤖 Multi-agent system with specialized roles (architect, developer, tester, etc.)
- 🌐 GitHub integration for repository management, issues, and PRs
- 📝 Code generation and management
- 🧪 Automated test generation and execution
- 📚 Documentation generation
- 💬 Interactive chat interface

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Set up your GitHub token
export GITHUB_TOKEN=your_token_here
# or create a .env file

# Run the Code Agent
code-agent init
code-agent chat
```

## Configuration

Create a `.env` file in the root directory with the following:

```
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
HF_TOKEN=your_huggingface_token
```

## Building a Project

```bash
code-agent build --project-name "TaskManager" --requirements-file requirements.txt
```

Or interactively:

```bash
code-agent build
```

## Implementing Features

```bash
code-agent feature --name "User Authentication" --description "Implement user signup and login" --test --review
```

## Documentation

For more detailed documentation, see:

- [Usage Guide](./docs/usage.md)
- [Architecture](./docs/architecture.md)
- [API Reference](./docs/api.md)

## License

MIT
