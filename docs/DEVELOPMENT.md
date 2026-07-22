# Development Guide

## Overview

This project is organized around a small Python package in src/codeharness with a UI layer and a core orchestration layer.

## Suggested layout

- src/codeharness/core: orchestration, agent loops, and repository interaction logic
- src/codeharness/ui: Streamlit UI and supporting assets
- Workspace: local working area used during agent-driven tasks

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Running the app

```powershell
streamlit run src/codeharness/ui/app.py
```

## Recommended workflow

1. Keep changes focused and modular.
2. Update docs when behavior or setup changes.
3. Test changes locally before sharing them.
4. Prefer small, understandable components over tightly coupled logic.
