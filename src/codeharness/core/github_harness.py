import os
import re
import shutil
from pathlib import Path
from dotenv import load_dotenv

from github import Github
from git import Repo
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool
from crewai.tools import tool
from crewai.hooks import before_tool_call, HookAborted

load_dotenv()

# ==========================================
# 1) CONFIGURATION & GITHUB SETUP
# ==========================================
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN must be set in .env to use the PR Agent.")

gh = Github(GITHUB_TOKEN)
gh = Github(GITHUB_TOKEN)

def parse_github_issue_url(url: str):
    """Parses a GitHub issue URL into owner, repo, and issue number."""
    match = re.search(r"github\.com/([^/]+)/([^/]+)/issues/(\d+)", url)
    if not match:
        raise ValueError("Invalid GitHub issue URL. Expected format: https://github.com/owner/repo/issues/123")
    return match.groups()

# ==========================================
# 2) DYNAMIC WORKSPACE PREPARATION
# ==========================================
WORKSPACE_DIR = os.path.abspath("./dynamic_workspace")

def prepare_workspace(owner: str, repo_name: str, issue_number: str) -> Repo:
    """Clones the repository and checks out a new feature branch."""
    if os.path.exists(WORKSPACE_DIR):
        print(f"Cleaning up existing workspace at {WORKSPACE_DIR}...")
        import stat
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(WORKSPACE_DIR, onerror=remove_readonly)
    
    clone_url = f"https://{GITHUB_TOKEN}@github.com/{owner}/{repo_name}.git"
    print(f"Cloning {owner}/{repo_name} into {WORKSPACE_DIR}...")
    repo = Repo.clone_from(clone_url, WORKSPACE_DIR)
    
    branch_name = f"fix/issue-{issue_number}"
    print(f"Checking out new branch: {branch_name}")
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()
    
    return repo

# ==========================================
# 3) CUSTOM TOOLS (Local & Sandbox Testing)
# ==========================================
from crewai.tools import tool
import subprocess

read_file = FileReadTool()
write_file = FileWriterTool()
list_dir = DirectoryReadTool()
filesystem_tools = [read_file, write_file, list_dir]

USE_LOCAL = os.getenv("USE_LOCAL_TESTING", "true").lower() == "true"

if not USE_LOCAL:
    try:
        from crewai_tools import E2BExecTool, E2BPythonTool
        exec_tool = E2BExecTool()
        sandbox_tools = [exec_tool, E2BPythonTool()]
    except ImportError:
        exec_tool = None
        sandbox_tools = []
else:
    exec_tool = None
    sandbox_tools = []

@tool("run_tests")
def run_tests(path: str = ".") -> str:
    """Run tests. It will automatically attempt to install requirements first."""
    setup_cmd = "echo 'No requirements.txt found'"
    if os.path.exists(os.path.join(WORKSPACE_DIR, "requirements.txt")):
        setup_cmd = "pip install -r requirements.txt"
    elif os.path.exists(os.path.join(WORKSPACE_DIR, "pyproject.toml")):
        setup_cmd = "pip install ."
        
    test_cmd = f"pytest {path} -q"
    full_cmd = f"{setup_cmd} && {test_cmd}"

    if USE_LOCAL:
        try:
            # Run locally using subprocess
            result = subprocess.run(
                full_cmd, 
                shell=True, 
                cwd=WORKSPACE_DIR, 
                capture_output=True, 
                text=True
            )
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        except Exception as e:
            return f"Local Execution Failed: {str(e)}"
    else:
        # Run in E2B cloud sandbox
        if exec_tool:
            return exec_tool.run(command=f"cd {WORKSPACE_DIR} && {full_cmd}")
        return "E2B tool not configured."

custom_tools = [run_tests]

@tool("submit_pull_request")
def submit_pull_request(commit_message: str, pr_title: str, pr_body: str, issue_url: str) -> str:
    """Commits all changes, pushes the branch, and opens a Pull Request on GitHub."""
    try:
        owner, repo_name, issue_num = parse_github_issue_url(issue_url)
        repo = Repo(WORKSPACE_DIR)
        
        # Commit and push
        repo.git.add(A=True)
        repo.index.commit(commit_message)
        branch_name = repo.active_branch.name
        origin = repo.remote(name='origin')
        origin.push(branch_name)
        
        # Open PR via API
        gh_repo = gh.get_repo(f"{owner}/{repo_name}")
        pr = gh_repo.create_pull(
            title=pr_title,
            body=f"{pr_body}\n\nFixes #{issue_num}",
            head=branch_name,
            base=gh_repo.default_branch
        )
        return f"Successfully opened PR: {pr.html_url}"
    except Exception as e:
        return f"Failed to submit PR: {str(e)}"

# ==========================================
# 4) AGENTS & EXECUTION API
# ==========================================
HEADLESS_MODE = False

GATED_TOOLS = {write_file.name, "run_tests", "submit_pull_request", *(t.name for t in sandbox_tools)}

@before_tool_call
def require_approval(context):
    if HEADLESS_MODE:
        return None # Auto-approve for Streamlit UI for now
    if context.tool_name in GATED_TOOLS:
        response = input(f"\n[INTERCEPTOR] Approve '{context.tool_name}' tool execution? [yes/no]: ")
        if response.strip().lower() != "yes":
            raise HookAborted(reason="User denied tool execution via Interceptor.", source="require_approval")
    return None

def run_pr_agent(issue_url: str, progress_callback=None):
    """API entry point for the Streamlit UI."""
    global HEADLESS_MODE
    HEADLESS_MODE = True
    
    # Read the model dynamically so UI changes take effect
    model_name = os.getenv("MODEL", "openrouter/anthropic/claude-3.5-sonnet")
    
    llm_kwargs = {"model": model_name}
    if os.getenv("OPENAI_API_BASE"):
        llm_kwargs["base_url"] = os.getenv("OPENAI_API_BASE")
        llm_kwargs["api_key"] = os.getenv("OPENAI_API_KEY")
        
    llm = LLM(**llm_kwargs)
    
    if progress_callback:
        progress_callback(f"Initializing Autonomous PR Swarm with model: {model_name}...")

    explorer = Agent(
        role="Codebase Explorer",
        goal="Map the cloned repository and surface the files relevant to the GitHub issue.",
        backstory="You navigate massive repositories quickly. You read files to build context before anyone mutates them.",
        tools=[read_file, list_dir],
        llm=llm,
        verbose=True,
        step_callback=lambda step: progress_callback(f"[Explorer] {step.thought}") if progress_callback and hasattr(step, 'thought') else None
    )

    coder = Agent(
        role="Software Engineer",
        goal="Implement the fix for the GitHub issue by editing files in the workspace.",
        backstory="You write clean, correct code. You draft a reasoning plan before writing files.",
        tools=filesystem_tools + sandbox_tools,
        reasoning=True,
        llm=llm,
        verbose=True,
        step_callback=lambda step: progress_callback(f"[Coder] {step.thought}") if progress_callback and hasattr(step, 'thought') else None
    )

    tester = Agent(
        role="QA Engineer",
        goal="Run the repository tests in the E2B sandbox and verify the fix works.",
        backstory="You ensure that tests pass before the Manager approves a Pull Request. You never lie about test results.",
        tools=sandbox_tools + [read_file] + custom_tools,
        llm=llm,
        verbose=True,
        step_callback=lambda step: progress_callback(f"[Tester] {step.thought}") if progress_callback and hasattr(step, 'thought') else None
    )

    manager = Agent(
        role="Engineering Lead",
        goal="Orchestrate the swarm to fix the issue, and ultimately submit the Pull Request.",
        backstory="You own the outcome. You assign the Explorer to find the bug, the Coder to fix it, and the Tester to verify. Once tests pass, YOU use the `submit_pull_request` tool to ship it.",
        tools=[submit_pull_request],
        llm=llm,
        allow_delegation=True,
        verbose=True,
        step_callback=lambda step: progress_callback(f"[Manager] {step.thought}") if progress_callback and hasattr(step, 'thought') else None
    )

    owner, repo_name, issue_num = parse_github_issue_url(issue_url)
    if progress_callback: progress_callback(f"Fetching Issue #{issue_num} from {owner}/{repo_name}...")
    
    gh_repo = gh.get_repo(f"{owner}/{repo_name}")
    issue = gh_repo.get_issue(number=int(issue_num))
    issue_context = f"TITLE: {issue.title}\n\nBODY: {issue.body}"
    
    if progress_callback: progress_callback(f"Preparing Workspace (Cloning repo & branching)...")
    prepare_workspace(owner, repo_name, issue_num)
    
    task = Task(
        description=(
            f"Fix the following GitHub Issue in the cloned repository at {WORKSPACE_DIR}:\n\n"
            f"{issue_context}\n\n"
            "Steps:\n"
            "1. Delegate the Explorer to find the relevant code.\n"
            "2. Delegate the Coder to implement the fix.\n"
            "3. Delegate the Tester to run tests using the `run_tests` tool and confirm success.\n"
            f"4. Finally, you (the Manager) MUST use the `submit_pull_request` tool to open the PR. Pass the issue_url: {issue_url}"
        ),
        expected_output="A successful Pull Request URL.",
        human_input=False, # Disable human input for headless UI
    )

    crew = Crew(
        agents=[explorer, coder, tester],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
        planning=True,
        planning_llm=llm,
        verbose=True,
    )

    if progress_callback: progress_callback("Swarm execution started. Agents are now thinking...")
    result = crew.kickoff()
    return str(result)

if __name__ == "__main__":
    print("🚀 CodeHarness Autonomous PR Agent (CLI Mode)")
    issue_url = input("Enter a GitHub Issue URL: ").strip()
    result = run_pr_agent(issue_url, progress_callback=lambda msg: print(f"-> {msg}"))
    print("\n✅ Final Result:")
    print(result)
