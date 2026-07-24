# 🚀 Getting Started & Usage Guide

CodeHarness is designed to be trivial to boot up locally, providing you with an intuitive chat interface to deploy AI agents against a GitHub issue.

## Prerequisites

- **Python 3.11+** installed locally.
- **Git** installed and available in your PATH.
- A **GitHub Personal Access Token** with repository access.
- An **API Key** for your preferred LLM provider (e.g., Anthropic, Groq, OpenAI).

---

## 1. Installation

We recommend using `uv` for lightning-fast environment setup, but `pip` works fine too.

### Option A: Using uv (Recommended)
```powershell
# Syncs the environment automatically based on pyproject.toml
uv sync
```

### Option B: Using pip
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

---

## 2. Configuration

Before starting the harness, you must configure your environment variables. 
CodeHarness comes with an `env.example` file.

1. Copy the example file to `.env`:
```powershell
copy env.example .env
```

2. Open `.env` in your editor and populate the keys:
```env
# Required for cloning repositories and fetching issues
GITHUB_TOKEN=ghp_your_token_here

# The model for CrewAI to use (e.g., gemini/gemini-2.5-pro, openrouter/anthropic/claude-3.5-sonnet, etc.)
MODEL=gemini/gemini-2.5-pro

# Provide the API key for whichever model provider you set above
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Safety configurations
USE_LOCAL_TESTING=true
# E2B_API_KEY=your_e2b_key_here (optional, for cloud sandboxing)
```

---

## 3. Starting the Interface

CodeHarness operates via a Streamlit web interface. 

To launch it, run:
```powershell
streamlit run src/codeharness/ui/app.py
```
*(If using `uv`, prefix with `uv run streamlit run src/codeharness/ui/app.py`)*

This will open a browser tab at `http://localhost:8501`.

---

## 4. Running an Agentic Workflow

1. In the Streamlit UI sidebar, ensure your API keys are loaded. You can override your `.env` variables directly in the UI if needed.
2. In the main chat area, paste a GitHub Issue URL. For example:
   `Solve this https://github.com/owner/repo/issues/123`
3. Hit Enter.

### What Happens Next?
1. The **Orchestrator** parses the URL and clones the repository into the local `./dynamic_workspace` directory.
2. It checks out a new branch (`fix/issue-123`).
3. The **Explorer Agent** begins reading files to understand the repository structure and identify where the bug is located.
4. The **Coder Agent** writes the fix. If it attempts to modify a file, you will receive a pop-up alert in the Streamlit UI asking for approval.
5. The **Tester Agent** runs the local test suite (or remote sandbox) and reports back.
6. Once passing, the Orchestrator opens a Pull Request on GitHub with the fix.

> [!TIP]
> **Monitoring the Agents:**
> You can watch the live terminal logs inside the Streamlit Chat interface. CrewAI's `verbose=True` setting is piped directly into the browser, allowing you to read the AI's internal thoughts and tool calls in real-time.
