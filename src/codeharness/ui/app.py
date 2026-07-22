import streamlit as st
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
import urllib.parse
from PIL import Image

# Add project root to sys.path so we can import codeharness
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
    
# Attempt to add src to sys.path
src_dir = root_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="CodeHarness | Autonomous AI", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()
env_path = root_dir / ".env"
if not env_path.exists():
    env_path.touch()

def save_key(key_name, value):
    if value:
        set_key(str(env_path), key_name, value)

# ==========================================
# PREMIUM CSS INJECTION
# ==========================================
st.markdown("""
<style>
    /* Global Background and Text */
    .stApp {
        background: linear-gradient(135deg, #0f111a 0%, #171a2b 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling (Glassmorphism) */
    [data-testid="stSidebar"] {
        background: rgba(20, 25, 40, 0.45) !important;
        backdrop-filter: blur(12px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chat Inputs */
    .stChatInputContainer>div {
        background-color: rgba(30, 35, 50, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: rgba(30, 35, 50, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Primary Deploy Button */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: transparent !important;
    }
    [data-testid="chatAvatarIcon-user"] {
        background-color: #6366f1 !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #a855f7 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# STATE CLEARING (For seamless LLM switching)
# ==========================================
def clear_env_keys():
    keys_to_clear = ["GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "OPENAI_API_KEY", "OPENAI_API_BASE"]
    for k in keys_to_clear:
        if k in os.environ:
            del os.environ[k]

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Autonomous CodeHarness Swarm. I can clone repositories, fix bugs, run tests, and open Pull Requests.\n\n**To get started, paste a GitHub Issue URL in the chat!**"}
    ]

# ==========================================
# SIDEBAR (Configuration)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9a/Code_Icon.svg", width=50)
    st.markdown("## ⚙️ Swarm Config")
    
    default_gh = os.getenv("GITHUB_TOKEN", "")
    gh_token = st.text_input("GitHub Token (Required)", type="password", value=default_gh)
    if gh_token:
        save_key("GITHUB_TOKEN", gh_token)
        os.environ["GITHUB_TOKEN"] = gh_token

    st.markdown("### 🧠 AI Provider")
    model_choice = st.selectbox(
        "Select your AI brain:",
        [
            "Google Gemini 2.5 Pro",
            "Groq Llama 3.1 70B",
            "OpenRouter (Claude)",
            "Ollama (Local)"
        ]
    )
    
    clear_env_keys()
    if "Gemini" in model_choice:
        default_val = st.session_state.get("gemini_key", os.getenv("GEMINI_API_KEY", ""))
        api_key = st.text_input("Gemini API Key", type="password", value=default_val)
        if api_key:
            st.session_state["gemini_key"] = api_key
            save_key("GEMINI_API_KEY", api_key)
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["MODEL"] = "gemini/gemini-2.5-pro"
    elif "Groq" in model_choice:
        default_val = st.session_state.get("groq_key", os.getenv("GROQ_API_KEY", ""))
        api_key = st.text_input("Groq API Key", type="password", value=default_val)
        if api_key:
            st.session_state["groq_key"] = api_key
            save_key("GROQ_API_KEY", api_key)
            os.environ["GROQ_API_KEY"] = api_key
            os.environ["MODEL"] = "groq/llama-3.3-70b-versatile"
    elif "OpenRouter" in model_choice:
        default_val = st.session_state.get("or_key", os.getenv("OPENROUTER_API_KEY", ""))
        api_key = st.text_input("OpenRouter API Key", type="password", value=default_val)
        if api_key:
            st.session_state["or_key"] = api_key
            save_key("OPENROUTER_API_KEY", api_key)
            os.environ["OPENROUTER_API_KEY"] = api_key
            os.environ["MODEL"] = "openrouter/anthropic/claude-3.5-sonnet"
    elif "Ollama" in model_choice:
        os.environ["MODEL"] = "ollama/llama3"

    st.markdown("### 🧪 Environment")
    use_e2b = st.checkbox("Use E2B Cloud Testing", value=False)
    if use_e2b:
        e2b_key = st.text_input("E2B API Key", type="password", value=st.session_state.get("e2b_key", ""))
        if e2b_key:
            st.session_state["e2b_key"] = e2b_key
            os.environ["E2B_API_KEY"] = e2b_key
            os.environ["USE_LOCAL_TESTING"] = "false"
    else:
        os.environ["USE_LOCAL_TESTING"] = "true"

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Memory wiped. Ready for new instructions."}
        ]
        st.rerun()

# ==========================================
# MAIN INTERFACE (Chat UI)
# ==========================================
st.title("CodeHarness Autonomous Chat")

# Render existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input Box
if prompt := st.chat_input("Paste a GitHub Issue URL or talk to the Swarm..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simple Regex to detect GitHub URL
    url_match = re.search(r"https://github\.com/[^\s]+/issues/\d+", prompt)
    
    if url_match:
        issue_url = url_match.group(0)
        
        # Validation
        if not os.getenv("GITHUB_TOKEN"):
            error_msg = "❌ I cannot start. Please provide your GitHub Token in the sidebar."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        elif "Gemini" in model_choice and not os.getenv("GEMINI_API_KEY"):
            error_msg = "❌ Please enter your Gemini API Key in the sidebar."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        elif "Groq" in model_choice and not os.getenv("GROQ_API_KEY"):
            error_msg = "❌ Please enter your Groq API Key in the sidebar."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        elif "OpenRouter" in model_choice and not os.getenv("OPENROUTER_API_KEY"):
            error_msg = "❌ Please enter your OpenRouter API Key in the sidebar."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        elif use_e2b and not os.getenv("E2B_API_KEY"):
            error_msg = "❌ Please enter your E2B API Key in the sidebar, or uncheck Cloud Testing."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        else:
            with st.chat_message("assistant"):
                st.markdown(f"Deploying Swarm to address: {issue_url}")
                log_placeholder = st.empty()
                live_logs = ["System: Booting neural networks..."]
                log_placeholder.code("\n".join(live_logs), language="bash")
                
                def progress_callback(msg: str):
                    live_logs.append(msg)
                    # Keep only last 20 lines to avoid massive lag
                    log_placeholder.code("\n".join(live_logs[-20:]), language="bash")

                try:
                    from codeharness.core.github_harness import run_pr_agent
                    final_result = run_pr_agent(issue_url, progress_callback=progress_callback)
                    
                    success_msg = f"✅ **Mission Accomplished!**\n\n```text\n{final_result}\n```"
                    st.markdown(success_msg)
                    st.session_state.messages.append({"role": "assistant", "content": success_msg})
                    
                except Exception as e:
                    fail_msg = f"❌ **Critical System Failure:**\n```text\n{str(e)}\n```"
                    st.markdown(fail_msg)
                    st.session_state.messages.append({"role": "assistant", "content": fail_msg})
    else:
        # Generic Chat Response
        with st.chat_message("assistant"):
            reply = "I am a PR engineering swarm. Please provide a valid GitHub issue URL (e.g., `https://github.com/owner/repo/issues/1`) and I will engineer a fix for it!"
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
