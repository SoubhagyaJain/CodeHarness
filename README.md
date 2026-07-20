# ⚡ CodeHarness

> **The gap between your agent and Claude Code isn't the model — it's the harness.**

CodeHarness is an open-source project that rebuilds the architecture of popular coding agents (like Claude Code) from scratch. It demonstrates a fully autonomous, agent-driven workflow that explores, edits, tests, and reports on a real codebase. 

Instead of a fragile while-loop, CodeHarness implements a robust 6-layer architecture using [CrewAI](https://docs.crewai.com/) for orchestration and [E2B](https://e2b.dev/) for secure, sandboxed execution.

---

## 🏗️ The 6-Layer Architecture

1. **Core Loop**: The basic Task → Tool → Result cycle driven by CrewAI.
2. **Tools**: Native access to read/write files and execute sandboxed shell commands.
3. **Planning**: A roadmap generated before coding to prevent "context rot" (`planning=True`).
4. **Subagents**: A Manager delegates to specialists (Explorer, Coder, Tester) to save context space.
5. **Sandboxing**: Code and tests execute inside an isolated E2B virtual machine.
6. **Memory & Checkpointing**: Persists facts across sessions and survives interruptions.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- API Keys for **OpenRouter** (or any LLM provider), **OpenAI** (for embeddings/memory), and **E2B** (for sandboxing).

### 2. Installation
Clone the repository and set up your environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
*(Alternatively, use `pip install crewai[tools,litellm] crewai-tools[e2b] python-dotenv pytest`)*

### 3. Configuration
Copy the environment template and add your API keys:
```powershell
copy env.example .env
```
Edit `.env` with your keys:
- `MODEL="openrouter/anthropic/claude-sonnet-4-6"` (or your preferred model)
- `OPENROUTER_API_KEY="..."`
- `E2B_API_KEY="..."`
- `OPENAI_API_KEY="..."`

---

## 🛠️ The Demo Task

The `Workspace/` directory contains a minimal banking app (`account.py`) and a test suite (`tests/test_account.py`).

**The Problem:** The code currently has 2 hidden bugs, resulting in 3 failing tests and 2 passing tests.
- Withdrawals can overdraw an account past zero.
- Transfers do not properly credit the recipient's account.

**The Solution:** Run the harness.
```powershell
python code_harness.py
```
Watch as the AI Engineering Lead delegates to the Explorer to read the code, the Coder to implement the fixes, and the Tester to run `pytest` inside the E2B sandbox. The agent will iterate until all 5 tests pass, without hallucinating or modifying the test files.

---

## 📂 Project Structure

- `code_harness.py` — The core 6-layer harness and CrewAI orchestration logic.
- `Workspace/account.py` — The buggy banking implementation.
- `Workspace/tests/test_account.py` — The pytest test suite.
- `env.example` — Configuration template.
- `pyproject.toml` — Package metadata.

## 🛡️ Safety First
If you are building agents, remember: **Prompts are not safeguards. Sandboxes are.** CodeHarness forces all untrusted code execution through E2B, ensuring your host machine remains secure while the agent tests its code.
