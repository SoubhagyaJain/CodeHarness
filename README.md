# CodeHarness

CodeHarness is a Python-based orchestration layer for building coding agents that can inspect a repository, plan changes, edit files, and validate results through tests. It combines a Streamlit chat interface with a structured multi-agent workflow so you can interact with the system in a more guided, transparent way.

## Why this project exists

The goal is simple: make it easier to experiment with autonomous coding workflows without surrendering control. The project focuses on:

- clear agent roles for exploration, coding, and QA
- a local execution model for safer testing
- a user-friendly interface for monitoring progress
- a structure that is easy to extend as your agent workflow grows

## Key features

- Streamlit-based chat UI for interactive use
- modular Python package layout under src/codeharness
- local subprocess-based execution for testing and validation
- support for multiple model providers through lightweight integrations
- workspace-aware execution for repository changes

## Quick start

### Prerequisites

- Python 3.11+
- pip or uv
- a valid API key for your chosen provider

### Option 1: using uv

```powershell
uv sync
uv run streamlit run src/codeharness/ui/app.py
```

### Option 2: using pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
streamlit run src/codeharness/ui/app.py
```

### Configure the app

1. Open the Streamlit UI in your browser.
2. Choose your preferred model provider.
3. Enter your API key in the interface.
4. Paste a GitHub issue or task description to start the workflow.

## Project structure

```text
CodeHarness/
├── src/
│   └── codeharness/
│       ├── core/
│       │   ├── code_harness.py
│       │   └── github_harness.py
│       └── ui/
│           ├── app.py
│           └── assets/
├── Workspace/
├── docs/
├── pyproject.toml
├── README.md
└── env.example
```

## Development workflow

- Use the package entry points from src/codeharness for core logic.
- Keep UI changes under src/codeharness/ui.
- Keep agent behavior and orchestration logic in src/codeharness/core.
- Add or update tests in the relevant module area as the project evolves.

For a longer development guide, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Safety notes

This project is designed to keep execution more controlled than a fully unrestricted agent loop. The workflow uses isolated execution paths and human review checkpoints to reduce the risk of unintended actions.

## Contributing

Contributions are welcome. If you want to improve the architecture, documentation, or workflow behavior, open an issue or submit a pull request with a clear explanation of the change.

