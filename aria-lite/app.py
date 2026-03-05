import streamlit as st
import json
from agents.requirements_agent import run_requirements_agent
from agents.code_agent import run_code_agent
from utils.decision_ledger import DecisionLedger

st.set_page_config(page_title="ARIA-Lite", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
    color: #e2e8f0;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}

.hero-subtitle {
    text-align: center;
    color: #64748b;
    font-size: 1rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.badge-row {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
}

.badge {
    background: rgba(96,165,250,0.1);
    border: 1px solid rgba(96,165,250,0.25);
    color: #60a5fa;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.05em;
}

.agent-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.3s;
}

.agent-card:hover { border-color: rgba(96,165,250,0.3); }

.agent-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #60a5fa;
    font-weight: 600;
    margin-bottom: 0.3rem;
}

.agent-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 0.4rem;
}

.agent-desc { color: #64748b; font-size: 0.85rem; line-height: 1.5; }

.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #475569;
    font-weight: 600;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.ledger-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 3px solid #60a5fa;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.ledger-agent { color: #60a5fa; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; }
.ledger-decision { color: #f1f5f9; font-size: 0.95rem; margin: 0.3rem 0; }
.ledger-reasoning { color: #64748b; font-size: 0.82rem; }

.confidence-bar-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 4px;
    margin-top: 0.6rem;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #34d399;
    display: inline-block;
    margin-right: 6px;
    box-shadow: 0 0 8px #34d399;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.success-banner {
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    color: #34d399;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 1rem;
    text-align: center;
}

div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(96,165,250,0.5) !important;
    box-shadow: 0 0 0 3px rgba(96,165,250,0.1) !important;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.8rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: 0.02em !important;
    transition: opacity 0.2s !important;
}

div[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

.stCodeBlock, pre {
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

div[data-testid="stJson"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}

.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# Hero
st.markdown('<div class="hero-title">ARIA-Lite</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Autonomous Resilient Intelligence Architecture</div>', unsafe_allow_html=True)
st.markdown('''
<div class="badge-row">
    <span class="badge">DevHack 2026</span>
    <span class="badge">Team INITIATORS</span>
    <span class="badge">TID060</span>
    <span class="badge">AIPS02</span>
    <span class="badge"><span class="status-dot"></span>2 Agents Active</span>
</div>
''', unsafe_allow_html=True)

# Layout
left_col, right_col = st.columns([1, 2])

with left_col:
    st.markdown('<div class="section-header">Active Agents</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="agent-card">
        <div class="agent-label">Agent 01</div>
        <div class="agent-name">Requirements Agent</div>
        <div class="agent-desc">Converts vague prompts into structured JSON specifications with confidence scoring.</div>
    </div>
    <div class="agent-card">
        <div class="agent-label">Agent 03</div>
        <div class="agent-name">Code Agent</div>
        <div class="agent-desc">Generates production-grade FastAPI code with SQLAlchemy, Pydantic, and full error handling.</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="section-header" style="margin-top:1.5rem">Roadmap</div>', unsafe_allow_html=True)
    for agent, status, color in [
        ("Architect Agent", "Planned", "#f59e0b"),
        ("Test Agent", "Planned", "#f59e0b"),
        ("Sentinel Agent", "Future", "#64748b"),
        ("Retrospective Agent", "Future", "#64748b"),
    ]:
        st.markdown(f'''
        <div style="display:flex; justify-content:space-between; padding:0.5rem 0; border-bottom:1px solid rgba(255,255,255,0.04); font-size:0.82rem;">
            <span style="color:#94a3b8">{agent}</span>
            <span style="color:{color}; font-size:0.72rem; font-weight:600">{status}</span>
        </div>''', unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header">Describe Your App Idea</div>', unsafe_allow_html=True)
    user_prompt = st.text_area("", placeholder="e.g. I want a task manager API where users can create, update, and delete tasks", height=110, label_visibility="collapsed")

    if st.button("🚀  Generate Application", use_container_width=True):
        if not user_prompt.strip():
            st.warning("Please enter an idea first!")
        else:
            ledger = DecisionLedger()

            with st.spinner("Requirements Agent analyzing your idea..."):
                spec = run_requirements_agent(user_prompt, ledger)
            st.markdown('<div class="success-banner">✅ Requirements Agent — Specification generated</div>', unsafe_allow_html=True)

            with st.spinner("Code Agent generating production code..."):
                code = run_code_agent(spec, ledger)
            st.markdown('<div class="success-banner">✅ Code Agent — FastAPI application ready</div>', unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📋 Requirements Spec", "💻 Generated Code", "📒 Decision Ledger"])

            with tab1:
                st.json(spec)

            with tab2:
                st.code(code, language="python")

            with tab3:
                for entry in ledger.get_all():
                    conf = int(entry['confidence'] * 100)
                    st.markdown(f'''
                    <div class="ledger-card">
                        <div class="ledger-agent">🕐 {entry["timestamp"]}  ·  {entry["agent"]}</div>
                        <div class="ledger-decision">{entry["decision"]}</div>
                        <div class="ledger-reasoning">{entry["reasoning"]}</div>
                        <div class="confidence-bar-bg">
                            <div style="width:{conf}%; height:4px; background:linear-gradient(90deg,#60a5fa,#a78bfa); border-radius:999px;"></div>
                        </div>
                        <div style="text-align:right; font-size:0.72rem; color:#475569; margin-top:0.3rem">Confidence: {conf}%</div>
                    </div>
                    ''', unsafe_allow_html=True)