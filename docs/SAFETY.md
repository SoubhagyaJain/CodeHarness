# 🛡️ Safety & Execution Hooks

Letting autonomous agents interact with your filesystem and terminal is inherently risky. CodeHarness is built on the philosophy that **humans must remain in the loop for destructive actions.**

To achieve this, CodeHarness implements two primary safety mechanisms:
1. The Gated Approval Hook
2. The Dual-Execution Sandbox

---

## 1. The Gated Approval Hook

We intercept tool executions *after* the LLM decides to call a tool, but *before* the code actually runs.

```python
from crewai.hooks import before_tool_call, HookAborted

GATED_TOOLS = {"write_file", "execute_command"}

@before_tool_call
def require_approval(context):
    if context.tool_name in GATED_TOOLS:
        if not ui_callback.ask_approval(context.tool_name):
            raise HookAborted(reason="User denied tool execution")
```

### How it Works
1. The Coder Agent decides it needs to write to `src/utils.py`.
2. CrewAI attempts to trigger the `FileWriterTool`.
3. The `@before_tool_call` hook fires, suspending the CrewAI background thread.
4. An event is dispatched to the Streamlit UI, triggering an alert dialog: *"The AI is attempting to modify utils.py. Do you authorize this disk write?"*
5. If the user clicks **Deny**, a `HookAborted` exception is raised. The agent sees this as a standard tool failure and adjusts its strategy.
6. If the user clicks **Approve**, the thread resumes and the file is written.

> [!IMPORTANT]
> Read-only operations (`read_file`, `list_dir`) bypass the approval hook to ensure the agent can explore quickly without exhausting human patience.

---

## 2. The Dual-Execution Sandbox

When the **Tester Agent** attempts to run a test suite, we must ensure it isn't executing malicious or destructive shell commands on your local machine.

CodeHarness conditionally injects execution tools based on your environment:

### Local Mode (Default)
If `USE_LOCAL_TESTING=true` is set, tests are executed using Python's native `subprocess` module within the cloned directory.
> [!CAUTION]
> Local mode should **only** be used if you trust the repository and the agent's behavior. An agent could hallucinate `rm -rf /` or similar commands.

### Cloud Sandbox (E2B)
If `E2B_API_KEY` is provided, CodeHarness imports `crewai_tools.E2BExecTool`.
Instead of running on your machine, a fast, ephemeral micro-VM is spun up in the cloud. The repository is mapped, and commands are executed inside the VM. 
This provides a complete air-gap between the AI's experiments and your local hard drive.
