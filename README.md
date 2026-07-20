# CodeHarness

## Overview

`CodeHarness` is a small Python repository built around a CrewAI-style code harness. It demonstrates a simple bank account implementation with a test suite and a harness script that can run, inspect, and repair the repository using an agent-driven workflow.

The repository includes:

- `code_harness.py` — a CrewAI-based harness that configures model, tools, and sandboxed testing.
- `Workspace/account.py` — a minimal `BankAccount` class with deposit, withdraw, and transfer operations.
- `Workspace/tests/test_account.py` — a pytest suite targeting the bank account behavior.
- `pyproject.toml` — project metadata and dependencies.
- `env.example` — environment variable templates used by the harness.

## Purpose

This repo is designed as a code-debugging and test-driven exercise. The core task is to fix bugs in `Workspace/account.py` so that the test suite in `Workspace/tests/` passes.

## Requirements

- Python 3.11 or newer
- `pip` for installing dependencies
- Optional: CrewAI and E2B sandbox access for running the harness as intended

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install project dependencies:

```powershell
pip install -r requirements.txt
```

or, if using Poetry / PEP 621 / `pyproject.toml`:

```powershell
pip install crewai[tools,litellm] crewai-tools[e2b] python-dotenv pytest
```

3. Copy the environment template and provide API keys as needed:

```powershell
copy env.example .env
```

4. Edit `.env` and set values for:

- `MODEL` — the model string used by CrewAI
- `OPENROUTER_API_KEY` — required for model access if using OpenRouter
- `E2B_API_KEY` — required to enable sandbox tools and tests inside the harness
- `OPENAI_API_KEY` — required by CrewAI memory if memory is enabled

## Running Tests

From the repository root, run:

```powershell
pytest Workspace/tests/ -q
```

This will execute the bank account unit tests and report pass/fail status.

## Running the Harness

The harness is intended to coordinate agents and sandboxed tools. Run it from the repository root:

```powershell
python code_harness.py
```

The harness reads the object code from `Workspace/`, applies the configured model and tools, and can run the test suite inside an isolated environment.

## Project Structure

- `code_harness.py` — harness entrypoint and CrewAI orchestration logic
- `Workspace/account.py` — bank account implementation
- `Workspace/tests/test_account.py` — pytest tests covering deposit, withdrawal, overdraft protection, and transfers
- `pyproject.toml` — package metadata and dependencies
- `env.example` — sample environment variables for model and sandbox configuration

## Notes

- The current test suite identifies two important banking behaviors:
  - Withdrawals should raise `InsufficientFunds` when the requested amount exceeds the balance.
  - Transfers should move money from one account into the recipient account.
- The harness is designed to avoid editing tests: only implementation code should be changed to fix failing behavior.

## License

This repository does not include a license file. Add one if you want to make the project open source.
