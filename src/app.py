"""
app.py
------
Streamlit chat UI for the AI Research Agent.
Matches the simplified AgentState (messages-only) used in states.py.
"""

import json
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from graph import graph as agent
from states import AgentState

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Overall app background */
        .stApp {
            background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        }

        /* Main content width */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 900px;
        }

        /* Hero header */
        .hero {
            text-align: center;
            padding: 1.25rem 1rem 1.75rem 1rem;
        }
        .hero h1 {
            font-size: 2.1rem;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
        }
        .hero p {
            color: #9ca3af;
            font-size: 0.95rem;
        }

        /* Chat bubbles */
        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 0.5rem 0.25rem;
            margin-bottom: 0.4rem;
        }

        /* Source card */
        .source-card {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            border-radius: 10px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 6px;
            text-decoration: none !important;
            transition: background 0.15s ease;
        }
        .source-card:hover {
            background: rgba(255,255,255,0.09);
        }
        .source-card img {
            width: 16px;
            height: 16px;
            border-radius: 3px;
            flex-shrink: 0;
        }
        .source-card .src-text {
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .source-card .src-title {
            font-size: 0.85rem;
            color: #e5e7eb;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .source-card .src-domain {
            font-size: 0.72rem;
            color: #9ca3af;
        }
        .src-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 20px;
            height: 20px;
            padding: 0 6px;
            border-radius: 999px;
            background: rgba(96,165,250,0.15);
            color: #60a5fa;
            font-size: 0.72rem;
            font-weight: 700;
            flex-shrink: 0;
        }

        /* Sidebar example question buttons */
        section[data-testid="stSidebar"] button {
            text-align: left !important;
            border-radius: 10px !important;
        }

        .timestamp {
            font-size: 0.7rem;
            color: #6b7280;
            margin-top: -0.4rem;
            margin-bottom: 0.6rem;
        }

        .empty-state {
            text-align: center;
            color: #6b7280;
            padding: 3rem 1rem;
            font-size: 0.95rem;
        }
        .empty-state .emoji {
            font-size: 2.4rem;
            margin-bottom: 0.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = {}  # message_index -> list[dict]
if "timestamps" not in st.session_state:
    st.session_state.timestamps = {}  # message_index -> str

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔎 AI Research Agent")
    st.caption(
        "Ask a research question. The agent decides on its own whether "
        "it needs to search the web, then writes a cited answer."
    )
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.messages))
    with col2:
        total_sources = sum(len(v) for v in st.session_state.sources.values())
        st.metric("Sources used", total_sources)

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources = {}
        st.session_state.timestamps = {}
        st.rerun()

    st.divider()
    st.subheader("💡 Try asking")
    examples = [
        ("⚛️", "What are the latest developments in fusion energy?"),
        ("🤖", "Compare LangGraph and CrewAI for building agents."),
        ("💻", "What's the current state of quantum computing?"),
    ]
    for emoji, q in examples:
        if st.button(f"{emoji}  {q}", use_container_width=True, key=q):
            st.session_state.pending_question = q

    st.divider()
    st.caption("Built with LangGraph + Streamlit")

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>Research Assistant</h1>
        <p>Ask anything — I'll search the web when I need to and cite my sources.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def domain_of(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "")
    except Exception:
        return url


def favicon_url(url: str) -> str:
    domain = domain_of(url)
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=64"


def render_sources(sources: list[dict]) -> None:
    """Render a list of {'url':..., 'title':...} as nice link cards."""
    if not sources:
        return
    with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
        for i, src in enumerate(sources, start=1):
            url = src.get("url", "")
            title = src.get("title") or domain_of(url)
            st.markdown(
                f"""
                <a class="source-card" href="{url}" target="_blank">
                    <span class="src-badge">{i}</span>
                    <img src="{favicon_url(url)}" onerror="this.style.display='none'" />
                    <span class="src-text">
                        <span class="src-title">{title}</span>
                        <span class="src-domain">{domain_of(url)}</span>
                    </span>
                </a>
                """,
                unsafe_allow_html=True,
            )


def extract_sources(messages: list) -> list[dict]:
    """
    Pull source info out of any ToolMessage objects produced by search_tool.
    TavilySearch returns a JSON-ish string with a 'results' list containing
    'url' (and often 'title') keys — parsed defensively since tool output
    format can vary.
    """
    sources: list[dict] = []
    seen_urls: set[str] = set()
    for msg in messages:
        if isinstance(msg, ToolMessage):
            content = msg.content
            try:
                data = json.loads(content) if isinstance(content, str) else content
                results = data.get("results", []) if isinstance(data, dict) else []
                for r in results:
                    url = r.get("url")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({"url": url, "title": r.get("title")})
            except (json.JSONDecodeError, AttributeError, TypeError):
                continue
    return sources


# --------------------------------------------------------------------------
# Render chat history
# --------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown(
        """
        <div class="empty-state">
            <div class="emoji">🧭</div>
            No questions yet — ask one below, or pick an example from the sidebar.
        </div>
        """,
        unsafe_allow_html=True,
    )

for idx, message in enumerate(st.session_state.messages):
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    avatar = "🧑" if role == "user" else "🔎"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message.content)
        ts = st.session_state.timestamps.get(idx)
        if ts:
            st.markdown(f'<div class="timestamp">{ts}</div>', unsafe_allow_html=True)
        if role == "assistant" and st.session_state.sources.get(idx):
            render_sources(st.session_state.sources[idx])


# --------------------------------------------------------------------------
# Agent runner
# --------------------------------------------------------------------------
def run_agent(user_question: str) -> None:
    """Send a question through the graph, showing live status, then render the result."""
    user_idx = len(st.session_state.messages)
    st.session_state.messages.append(HumanMessage(content=user_question))
    st.session_state.timestamps[user_idx] = datetime.now().strftime("%H:%M")

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_question)
        st.markdown(
            f'<div class="timestamp">{st.session_state.timestamps[user_idx]}</div>',
            unsafe_allow_html=True,
        )

    with st.chat_message("assistant", avatar="🔎"):
        status = st.status("🤔 Thinking...", expanded=True)

        graph_input: AgentState = {"messages": st.session_state.messages}

        final_state = None
        try:
            for step_output in agent.stream(graph_input):
                node_name = list(step_output.keys())[0]
                final_state = step_output[node_name]
                if node_name == "chatbot":
                    status.update(label="🧠 Analyzing your question...")
                elif node_name == "tools":
                    status.update(label="🌐 Searching the web...")
            status.update(label="✅ Done", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="❌ Something went wrong", state="error")
            st.error(f"The agent hit an error: {exc}")
            return

        all_messages = final_state["messages"] if final_state else []
        last_ai_message = next(
            (m for m in reversed(all_messages) if isinstance(m, AIMessage) and m.content),
            None,
        )
        answer_text = (
            last_ai_message.content if last_ai_message
            else "I couldn't generate a response — try rephrasing."
        )
        st.markdown(answer_text)

        sources = extract_sources(all_messages)
        render_sources(sources)

        assistant_idx = len(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=answer_text))
        st.session_state.sources[assistant_idx] = sources
        st.session_state.timestamps[assistant_idx] = datetime.now().strftime("%H:%M")
        st.markdown(
            f'<div class="timestamp">{st.session_state.timestamps[assistant_idx]}</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------------------
# Input handling
# --------------------------------------------------------------------------
if "pending_question" in st.session_state:
    run_agent(st.session_state.pop("pending_question"))

user_input = st.chat_input("Ask a research question...")
if user_input:
    run_agent(user_input)