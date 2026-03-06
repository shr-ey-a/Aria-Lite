
import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ARIA-Lite | Autonomous Software Architect",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.main-title { font-size: 2.5rem; font-weight: bold; color: #6C63FF; }
.agent-card { background: #1e1e2e; border-radius: 10px; padding: 15px; margin: 10px 0; border-left: 4px solid #6C63FF; }
.status-running { color: #FFD700; }
.status-done { color: #00FF88; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 ARIA-Lite</div>', unsafe_allow_html=True)
st.markdown("**Autonomous Resilient Intelligence Architecture** — DevHack 2026 | Team INITIATORS")
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    # api_key = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password")
    # st.markdown("[Get free key →](https://console.groq.com)")
    api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.sidebar.error("⚠️ GROQ_API_KEY missing in .env file")
    st.divider()
    st.markdown("### 🤖 Active Agents")
    st.markdown("1. 🔍 Requirements Agent")
    st.markdown("2. 🏛️ Architect Agent")
    st.markdown("3. 💻 Code Agent")
    st.markdown("4. 🧪 Test Agent")


st.subheader("💬 Describe your software")
example = "Build a task management API where users can create, update, and delete tasks with due dates and priority levels"
user_prompt = st.text_area(
    "Enter a natural language prompt:",
    placeholder=example,
    height=100
)
col1, col2 = st.columns([1, 4])
with col1:
    run_btn = st.button("🚀 Run ARIA-Lite", type="primary", use_container_width=True)
with col2:
    if st.button("📝 Use Example Prompt"):
        st.session_state["prompt"] = example
        st.rerun()

if "prompt" in st.session_state:
    user_prompt = st.session_state["prompt"]

# Run pipeline
if run_btn and user_prompt:
    if not api_key:
        st.error("❌ Please enter your Groq API Key in the sidebar")
    else:
        from core.orchestrator import ARIAOrchestrator

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(msg, pct):
            progress_bar.progress(pct)
            status_text.markdown(f"**{msg}**")

        with st.spinner("ARIA-Lite pipeline running..."):
            try:
                orchestrator = ARIAOrchestrator(api_key)
                results = orchestrator.run_pipeline(user_prompt, update_progress)
                st.session_state["results"] = results
                st.success("🎉 Pipeline completed successfully!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()

# Display results
if "results" in st.session_state:
    results = st.session_state["results"]

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Requirements", "🏛️ Architecture", "💻 Generated Code", "🧪 Tests", "📔 Decision Ledger"
    ])

    with tab1:
        st.subheader("🔍 Requirements Specification")
        spec = results.get("spec", {})
        st.markdown(f"**Project:** `{spec.get('project_name', 'N/A')}`")
        st.markdown(f"**Description:** {spec.get('description', '')}")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📡 API Endpoints**")
            for ep in spec.get("api_endpoints", []):
                st.code(f"{ep['method']} {ep['path']}  →  {ep['description']}", language="text")
        with col2:
            st.markdown("**📦 Data Models**")
            for model in spec.get("data_models", []):
                st.markdown(f"**{model['name']}**")
                for field in model.get("fields", []):
                    req = "✅" if field.get("required") else "○"
                    st.markdown(f"  {req} `{field['name']}`: {field['type']}")

        st.markdown("**Business Logic**")
        for bl in spec.get("business_logic", []):
            st.markdown(f"- {bl}")

        confidence = spec.get("confidence_score", 0)
        st.metric("Confidence Score", f"{float(confidence):.0%}")

    with tab2:
        st.subheader("🏛️ Architecture Design")
        arch = results.get("architecture", {})

        col1, col2, col3 = st.columns(3)
        col1.metric("Database", arch.get("database", "N/A"))
        col2.metric("API Style", arch.get("api_style", "N/A"))
        col3.metric("Pattern", arch.get("architecture_pattern", "N/A"))

        st.markdown(f"**Database Choice:** {arch.get('database_reason', '')}")
        st.markdown(f"**Deployment:** {arch.get('deployment_strategy', '')}")

        st.markdown("**Tech Stack**")
        ts = arch.get("tech_stack", {})
        for k, v in ts.items():
            st.markdown(f"- **{k}:** {v}")

        st.markdown("**Design Decisions**")
        for d in arch.get("design_decisions", []):
            st.markdown(f"- {d}")

    with tab3:
        st.subheader("💻 Generated Code Files")
        code_data = results.get("code", {})
        files = code_data.get("files", {})

        for filename, content in files.items():
            if content:
                with st.expander(f"📄 `{filename}`"):
                    st.code(content, language="python")

        saved = code_data.get("saved_paths", [])
        if saved:
            st.success(f"✅ Saved to `outputs/generated_app/`: {', '.join(saved)}")

    with tab4:
        st.subheader("🧪 Test Suite")
        test_data = results.get("tests", {})
        st.metric("Test Functions Generated", test_data.get("test_count", 0))
        st.code(test_data.get("test_code", ""), language="python")
        st.info(f"📁 Saved to: `{test_data.get('path', '')}`")

        st.markdown("**▶️ To run tests:**")
        st.code("cd outputs/generated_app\npip install fastapi sqlalchemy pytest httpx\npytest test_app.py -v", language="bash")

    with tab5:
        st.subheader("📔 Decision Ledger — Full Audit Trail")
        ledger = results.get("ledger", [])
        st.metric("Total Decisions Logged", len(ledger))

        for entry in ledger:
            with st.expander(f"[{entry['agent']}] {entry['decision'][:60]}..."):
                st.markdown(f"**⏰ Time:** {entry['timestamp']}")
                st.markdown(f"**✅ Decision:** {entry['decision']}")
                st.markdown(f"**💭 Reasoning:** {entry['reasoning']}")
                if entry.get("alternatives_considered"):
                    st.markdown(f"**🔄 Alternatives:** {', '.join(entry['alternatives_considered'])}")
                st.metric("Confidence", f"{entry.get('confidence_score', 0):.0%}")

        if st.button("📥 Download Ledger as JSON"):
            st.download_button(
                label="Download decision_ledger.json",
                data=json.dumps(ledger, indent=2),
                file_name="decision_ledger.json",
                mime="application/json"
            )