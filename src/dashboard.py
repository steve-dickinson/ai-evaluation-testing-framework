import sys
from pathlib import Path

# Add project root to sys.path to allow imports from src
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

import streamlit as st
import os
import glob
import yaml
import pandas as pd
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from unittest.mock import MagicMock

from src.framework.chatbot.openai_client import OpenAIChatbot
from src.framework.chatbot.playwright_client import PlaywrightChatbot
from src.framework.evaluators.content_safety import ContentSafetyEvaluator
from src.framework.evaluators.llm_evaluator import LLMEvaluator
from src.framework.runner import TestRunner
from src.framework.models.data_models import TestScenario, TestResult
from src.framework.recommendations.engine import RecommendationEngine
from src.framework.storage.mongo_client import MongoStorage

# Load env vars
load_dotenv()

# --- Page Config ---
st.set_page_config(
    page_title="AI Chatbot Evaluation Framework",
    page_icon="🛡️",
    layout="wide"
)

# --- Helper Functions ---

def load_test_suite(path: str) -> List[TestScenario]:
    """Loads a YAML test suite."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return [TestScenario(**item) for item in data.get("scenarios", [])]

def get_available_suites() -> List[str]:
    """Finds all .yaml files in tests/ directory."""
    return glob.glob("tests/*.yaml")

def setup_sidebar() -> Dict[str, Any]:
    """Renders sidebar and returns user configuration."""
    st.sidebar.header("Configuration")
    
    # API Key
    env_key = os.getenv("OPENAI_API_KEY")
    api_key_input = st.sidebar.text_input(
        "OpenAI API Key", 
        value=env_key if env_key else "",
        type="password",
        help="Leave empty to use OPENAI_API_KEY environment variable."
    )
    
    # Mode
    chatbot_mode = st.sidebar.radio(
        "Chatbot Backend", 
        ["OpenAI (Direct)", "Playwright (UI Testing)"], 
        help="Choose between direct API or UI testing."
    )
    
    config = {
        "api_key": api_key_input or env_key,
        "mode": chatbot_mode,
        "use_mock": st.sidebar.checkbox("Use Mock Client", value=False),
        "target_url": "",
        "selectors": {}
    }

    # Playwright Config
    if chatbot_mode == "Playwright (UI Testing)":
        default_url = os.getenv("TARGET_URL", "http://localhost:8503")
        config["target_url"] = st.sidebar.text_input("Target App URL", default_url)
        
        with st.sidebar.expander("Advanced Configuration"):
            st.caption("CSS Selectors")
            config["selectors"]["input"] = st.text_input("Input Selector", 'textarea[aria-label="Ask me anything..."]')
            config["selectors"]["message"] = st.text_input("Message Container", 'div[data-testid="stChatMessage"]')
            config["selectors"]["response_container"] = st.text_input("Response Text Container", 'div[data-testid="stMarkdownContainer"]')
    
    # Selection
    suites = get_available_suites()
    if not suites:
        st.error("No test suites found in 'tests/' directory.")
        st.stop()
        
    config["suite_path"] = st.sidebar.selectbox("Select Test Suite", suites)
    config["evaluator_type"] = st.sidebar.selectbox("Evaluator Type", ["Keyword (Content Safety)", "LLM-as-a-Judge"])
    
    return config

def initialize_components(config: Dict[str, Any]):
    """Initializes Chatbot, Judge, and Evaluator based on config."""
    chatbot = None
    judge_client = None
    
    # 1. Setup Chatbot
    if config["mode"] == "Playwright (UI Testing)":
        if not config["target_url"]:
            st.error("Please provide a Target URL.")
            st.stop()
        chatbot = PlaywrightChatbot(target_url=config["target_url"], selectors=config["selectors"])
        
        # Judge needs separate client
        judge_key = config["api_key"] or "mock-key" if config["use_mock"] else config["api_key"]
        if not judge_key: # Fallback for pure mock
             judge_key = "mock-key"
        judge_client = OpenAIChatbot(api_key=judge_key)
        
    else:
        # OpenAI Direct
        if config["use_mock"] or not config["api_key"]:
            if not config["use_mock"]:
                st.warning("No API Key provided. Defaulting to MOCK mode.")
            chatbot = OpenAIChatbot(api_key="mock-key")
            # Mock behavior
            chatbot.client.chat.completions.create = MagicMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="[MOCK] Safe response."))]
            ))
            judge_client = chatbot
        else:
            chatbot = OpenAIChatbot(api_key=config["api_key"])
            judge_client = chatbot

    # 2. Setup Evaluator
    if config["evaluator_type"] == "LLM-as-a-Judge":
        if config["use_mock"]:
            # Mock Judge
            judge_client.client.chat.completions.create = MagicMock(return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content='{"passed": true, "score": 0.95, "reason": "Mock judge approves."}'))]
            ))
        evaluator = LLMEvaluator(judge_client)
    else:
        evaluator = ContentSafetyEvaluator()
        
    return chatbot, evaluator, judge_client

def display_metrics(results: List[TestResult]):
    """Displays key metrics in columns."""
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    rate = (passed / total) * 100 if total > 0 else 0
    latency = sum(r.execution_time_ms for r in results) / total if total > 0 else 0
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tests", total)
    m2.metric("Pass Rate", f"{rate:.1f}%")
def load_run_callback(run_id: str):
    """Callback to load a run and switch view."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    storage = MongoStorage(mongo_uri)
    if storage.is_connected():
        details = storage.get_run_details(run_id)
        if details:
            st.session_state["results"] = [TestResult(**r) for r in details["results"]]
            st.session_state["judge_client"] = None
            st.session_state["view_mode"] = "📊 Test Results"
            # Prevent auto-save since this is a loaded run
            st.session_state["last_run_saved"] = True
            st.toast("Run loaded from history.", icon="📂")

# --- Main App ---
def main():
    st.title("🛡️ AI Chatbot Evaluation Framework")
    
    # 1. Configuration
    config = setup_sidebar()
    
    # 2. Header
    st.header(f"Test Suite: {os.path.basename(config['suite_path'])}")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"Loaded configuration from `{config['suite_path']}`")
    with col2:
        run_btn = st.button("🚀 Run Evaluation", type="primary", use_container_width=True)

    # 3. Execution Logic
    if run_btn:
        # Reset save flag for new run
        if "last_run_saved" in st.session_state:
            del st.session_state["last_run_saved"]
            
        try:
            scenarios = load_test_suite(config["suite_path"])
            st.toast(f"Loaded {len(scenarios)} scenarios.", icon="✅")
            
            chatbot, evaluator, judge_client = initialize_components(config)
            runner = TestRunner(chatbot, evaluator)
            
            # Run
            results = []
            prog_bar = st.progress(0)
            status = st.empty()
            
            for i, sc in enumerate(scenarios):
                status.text(f"Running scenario {i+1}/{len(scenarios)}: {sc.name}...")
                results.append(runner.run_scenario(sc))
                prog_bar.progress((i + 1) / len(scenarios))
            
            status.text("Execution complete!")
            prog_bar.progress(100)
            
            # Persist
            st.session_state["results"] = results
            st.session_state["judge_client"] = judge_client
            st.session_state["config_snapshot"] = config # Store config used
            
        except Exception as e:
            st.error(f"Execution Error: {e}")
            return

    # 4. Main Display Area (Always Visible)
    st.divider()
    
    # Init view_mode if not present
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "📊 Test Results"

    view = st.radio(
        "Select View", 
        ["📊 Test Results", "🛡️ AI Recommendations", "📜 History"], 
        horizontal=True, 
        label_visibility="collapsed",
        key="view_mode"
    )
    st.markdown("---")
    
    # Retrieve State
    results = st.session_state.get("results")
    judge_client = st.session_state.get("judge_client")
    
    if view == "📊 Test Results":
        # Metrics Header (Only if results exist)
        if results:
            st.subheader("Results Overview")
            display_metrics(results)
            
            # DataFrame
            data = [{
                "ID": r.scenario_id, 
                "Passed": r.passed, 
                "Score": r.score, 
                "Prompt": r.prompt, 
                "Response": r.response, 
                "Reason": r.metrics.get("reason", "N/A")
            } for r in results]
            
            df = pd.DataFrame(data)
            st.dataframe(df.style.map(lambda x: 'background-color: #d4edda' if x else 'background-color: #f8d7da', subset=['Passed']), use_container_width=True)
            
            with st.expander("View Detailed Logs"):
                for r in results:
                    icon = "✅" if r.passed else "❌"
                    st.markdown(f"**{icon} {r.scenario_id}**")
                    st.markdown(f"**Prompt:** `{r.prompt}`")
                    st.markdown(f"**Response:** {r.response}")
                    st.markdown(f"**Reason:** {r.metrics}")
                    st.markdown("---")
        else:
             st.info("No active test results. Run a test suite or load a previous run from History.")

    elif view == "🛡️ AI Recommendations":
        st.subheader("Automated Security Analysis")
        
        if not results:
            st.info("Run a test suite to generate recommendations.")
        else:
            # Recommendation Logic
            failed_count = sum(1 for r in results if not r.passed)
            passed_count = len(results) - failed_count
            
            if "analysis_result" in st.session_state:
                # Render cached result
                analysis = st.session_state["analysis_result"]
                st.success("Analysis Complete (Cached)")
                st.markdown("### 🧐 Analysis")
                st.write(analysis["analysis"])
                st.markdown("### 📝 Revised System Prompt")
                st.code(analysis["revised_system_prompt"])
                if st.button("Clear Analysis"):
                    del st.session_state["analysis_result"]
                    st.rerun()
            elif failed_count > 0:
                st.warning(f"⚠️ {failed_count} tests failed.")
                if st.button("Analyze Failures & Suggest Fixes"):
                    with st.spinner("Analyzing..."):
                        if not judge_client:
                             judge_client = OpenAIChatbot(api_key=config["api_key"] or "mock-key")
                        
                        rec = RecommendationEngine(judge_client)
                        analysis = rec.analyze(results, "You are a helpful assistant.")
                        st.session_state["analysis_result"] = analysis
                        st.rerun()
            else:
                st.success("✅ All tests passed!")

    elif view == "📜 History":
         st.subheader("Execution History (MongoDB)")
         mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
         storage = MongoStorage(mongo_uri)
         
         if not storage.is_connected():
             st.error("MongoDB not connected.")
         else:
             runs = storage.get_recent_runs(10)
             if runs:
                 for run in runs:
                     ts = run["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                     with st.expander(f"{ts} - {run['suite_name']} (Pass: {run['pass_rate']:.1f}%)"):
                         st.button("Load", key=f"load_{run['_id']}", on_click=load_run_callback, args=(str(run['_id']),))
             else:
                 st.info("No history found.")

    # 5. Auto-Save Logic
    # We use a flag to prevent duplicate saves on reruns
    if "results" in st.session_state and "last_run_saved" not in st.session_state:
        # Check if we are in a "fresh run" state (e.g., config_snapshot exists implies a run just happened)
        # To avoid saving "Loaded" results, checking config_snapshot is a decent proxy, 
        # or we just accept that loading results doesn't clear the last_run_saved flag if we manage it right.
        # Simpler: Just check if we are connected and save.
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        storage = MongoStorage(mongo_uri)
        if storage.is_connected():
            # Get suite name from state or default
            config = st.session_state.get("config_snapshot", {})
            suite_name = os.path.basename(config.get("suite_path", "unknown_suite"))
            
            run_id = storage.save_test_run(
                suite_name=suite_name,
                results=st.session_state["results"]
            )
            if run_id:
                st.toast(f"Results saved to History (ID: {run_id})", icon="💾")
                st.session_state["last_run_saved"] = True

if __name__ == "__main__":
    main()
