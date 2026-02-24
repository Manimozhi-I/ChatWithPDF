import streamlit as st
import requests
import datetime

BACKEND_URL = "http://127.0.0.1:8001"

st.set_page_config(page_title="Document AI Assistant", page_icon="🤖", layout="wide")

# Session State

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

# Navbar

st.markdown("""
<div style="background:#2F4156; padding:18px 40px; color:white;
font-size:26px; font-weight:700; border-radius:0 0 15px 15px;">
Document Q&A AI Assistant
</div>
""", unsafe_allow_html=True)

st.write("")

# Upload Document

def upload_document(file):
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        res = requests.post(f"{BACKEND_URL}/upload-doc", files=files)
        if res.status_code == 200:
            st.session_state.file_uploaded = True
            st.success("📄 Document uploaded successfully!")
        else:
            st.error("Upload failed.")
    except:
        st.error("❌ Cannot reach backend.")


with st.sidebar:
    st.header("📄 Upload Document")
    uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])

    if uploaded:
        upload_document(uploaded)

    st.markdown("---")
    if st.button("🆕 New Chat"):
        st.session_state.messages = []

# Ask Backend

def ask_backend(query):
    try:
        response = requests.post(
            f"{BACKEND_URL}/query",
            json={"query": query}
        )
        if response.status_code == 200:
            return response.json().get("answer", "")
        return "⚠ Backend error."
    except:
        return "❌ Backend unreachable."


# Chat UI

st.markdown("""
<h1 style="text-align:center;color:#2F4156;">AI Document Assistant</h1>
<p style="text-align:center;color:#BBC6CB;">Ask anything based on the uploaded document.</p>
""", unsafe_allow_html=True)

chat_area = st.container()

with chat_area:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:#2F4156;color:white;padding:15px;border-radius:12px;
            margin-bottom:10px;width:70%;margin-left:auto;">
                {msg['content']}
                <div style="font-size:12px;opacity:0.7;text-align:right;">{msg['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#F5EFEB;color:#2F4156;padding:15px;border-radius:12px;
            border:1px solid #C8D9E6;margin-bottom:10px;width:70%;">
                {msg['content']}
                <div style="font-size:12px;opacity:0.7;text-align:right;">{msg['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)

# Input Box

def handle_message():
    query = st.session_state.user_query
    if not query:
        return

    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    # Get bot response
    answer = ask_backend(query)

    st.session_state.messages.append({
        "role": "bot",
        "content": answer,
        "timestamp": datetime.datetime.now().strftime("%H:%M")
    })

    st.session_state.user_query = ""


st.text_input(
    "Ask a question...",
    key="user_query",
    placeholder="Ask based on the uploaded document...",
    on_change=handle_message
)
