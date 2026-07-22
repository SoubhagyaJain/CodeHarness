# ⚡ CodeHarness

CodeHarness is a Python-based project for building and experimenting with coding agents that can inspect a codebase, plan changes, edit files, and validate their work through tests. It brings together a Streamlit interface and a modular Python package so you can interact with an agent workflow in a clear, guided, and transparent way.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-success" alt="Active" />
</p>

---

## 🌟 What this project does

CodeHarness is designed for developers and researchers who want to explore autonomous coding workflows without giving up control. The project focuses on:

- clear agent roles for exploration, coding, and validation
- a safer local testing workflow
- a simple chat-based interface for interacting with the system
- a structure that is easy to extend for experiments and custom agents

---

## ✨ Features

- Streamlit-based chat UI
- modular package layout under src/codeharness
- orchestration logic for agent-based workflows
- workspace-aware execution for repository changes
- environment-based configuration for providers and credentials

---

## ✅ Requirements

Before installing, make sure you have:

- Python 3.11 or newer
- pip or uv
- an API key for your chosen model provider

---

## 🚀 Installation

### Option 1: using uv

```powershell
uv sync
```

### Option 2: using pip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## 🔧 Configuration

1. Copy the example environment file:

```powershell
copy env.example .env
```

2. Open the .env file and fill in the required values.
3. Add your provider credentials and any model settings required by your setup.

---

## ▶️ Running the app

Start the Streamlit interface with:

```powershell
streamlit run src/codeharness/ui/app.py
```

If you are using uv, you can run the same app with:

```powershell
uv run streamlit run src/codeharness/ui/app.py
```

---

## 📁 Project structure

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
├── tests/
├── pyproject.toml
├── README.md
└── env.example
```

---

## 🛠️ Development workflow

- Keep orchestration logic in src/codeharness/core
- Keep the UI layer in src/codeharness/ui
- Add tests for new behavior whenever possible
- Update documentation when setup or behavior changes

For more detailed development notes, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

---

## 🧪 Testing

Run the test suite locally with:

```powershell
pytest tests/test_smoke.py Workspace/tests -q
```

---

## 🛡️ Safety notes

This project is intended to be more controlled than a fully unrestricted agent loop. It uses isolated execution paths and review checkpoints to reduce the risk of unintended actions.

---

## 🤝 Contributing

Contributions are welcome. If you want to improve the workflow, documentation, or architecture, open an issue or submit a pull request with a clear explanation of the change.

