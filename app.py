import streamlit as st
from streamlit_chat import message
from datetime import datetime

from agent.graph import graph
from agent.memory_store import store_memory
from agent.HTML_todo_dashboard import render_html_dashboard
from agent.HTML_patch_viewer import render_patch_html
from langchain_core.messages import HumanMessage, AIMessage


st.set_page_config(page_title="My Task Manager — Gemini LangGraph Agent", layout="wide")

# -------------------------------
# LOGIN SCREEN (Centered & Professional)
# -------------------------------
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

if st.session_state.user_id == "":
    # Create 3 columns to center the login box
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center;'>👋 Welcome to Your AI Task Manager</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size:19px;'>Please enter your name to begin.</p>", unsafe_allow_html=True)

       # Larger text input label
        st.markdown(
            "<label style='font-size: 18px; font-weight: 600;'>Your Name:</label>",
            unsafe_allow_html=True
        )

        name = st.text_input(
            "",
            key="login_name",
            placeholder="Type your name here...",
        )
        # Add spacing
        st.write("")
        st.write("")

        if st.button("Start", use_container_width=True):
            if name.strip():
                st.session_state.user_id = name.strip()
                st.rerun()

    st.stop()



# -------------------------------
# After Login Greeting
# -------------------------------

# -------------------------------
# Sidebar Navigation
# -------------------------------
with st.sidebar:
    st.header("📌 Navigation")
    page = st.radio("Go to:", ["Chat", "Task Dashboard", "Memory Store", "Patch Viewer"])

user_id = str(st.session_state.user_id)
config = {"configurable": {"thread_id": user_id, "user_id": user_id}}
user_name = f"My name is {user_id}. "

# -------------------------------
# Chat Page
# -------------------------------

if page == "Chat":
    

    st.title(f"Hi {user_id}! 👋")
    st.subheader("I'm your AI Task Manager.")

    st.markdown("""
    I can help you:
    - Log tasks and update your to‑do list  
    - Remember your preferences and profile  
    - Learn about how you like your tasks to be managed  
    - Show you exactly how I think using Patch Viewer  
    """)

    # Bigger, centered highlight line
    st.markdown(
        "<p style='font-size:20px; color:#00FF00; font-weight:700; text-align:center; color:#2A4D69;'>"
        "Go ahead and start chatting with me in the <b>Chat</b> tab."
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown("""
    And don’t forget to check your **Task Dashboard** & **Memory Store** to see what I’ve learned about you!
    """)

# -------------------------------
# Wrapper for Streamlit
# -------------------------------
def run_agent_streamlit(user_message):
    result = graph.invoke({"messages": [HumanMessage(content=user_name + user_message)]}, config)
    return result["messages"], result.get("patches", None)



# -------------------------------
# Chat Page
# -------------------------------
if page == "Chat":
    # Professional header styling
    st.markdown(
        "<h2 style='text-align:center; color:#808080; font-weight:700;'>💬 Chat with Your AI Agent</h2>",
        unsafe_allow_html=True
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    # Center the input field using columns
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.markdown(
            "<p style='font-size:18px; font-weight:600; text-align:left; margin-bottom:6px;'>How can I help you today?</p>",
            unsafe_allow_html=True
        )
        # Initialize session state keys safely
        if "chat_input_buffer" not in st.session_state:
            st.session_state.chat_input_buffer = ""

        if "chat_input" not in st.session_state:
            st.session_state.chat_input = ""

        if "send" not in st.session_state:
            st.session_state.send = False

        if "history" not in st.session_state:
            st.session_state.history = []

            
        # Create a placeholder for the input
        def submit_message():
            st.session_state.send = True
            st.session_state.chat_input = st.session_state.chat_input_buffer
            st.session_state.chat_input_buffer = ""   # clear input safely


        # Visible, centered input box
        user_input = st.text_input(
            "",
            placeholder="Type your message here...",
            key="chat_input",
            on_change=submit_message
        )

        send_clicked = st.session_state.get("send", False)
        #st.session_state["send"] = False


    # Handle sending

    #if send_clicked and user_input:
    if send_clicked and st.session_state.chat_input:
        user_message = st.session_state.chat_input
        st.session_state.send = False
        
        # -------------------------------
        # Thinking.......
        # -------------------------------
        # Create a placeholder for typing indicator

        thinking_placeholder = st.empty()

        # Show typing indicator
        thinking_placeholder.markdown(
            "<p style='font-size:16px; color:gray;'>🤖 Thinking…</p>",
            unsafe_allow_html=True
        )

        # 2. Run agent
        response, patches = run_agent_streamlit(user_input)       
        #print(f"Response: {response}")
        
        # 3. Remove typing indicator
        thinking_placeholder.empty()

        # Extract ONLY final AI_response
        final_msg = ""
        for msg in response:
            if isinstance(msg, AIMessage):
                content = msg.content
                if isinstance(content, list):
                    content = content[0].get("text", "")
                if isinstance(content, str):
                    final_msg = content
                    break

        st.session_state.history.append(("user", user_input))
        st.session_state.history.append(("ai", final_msg))


        if patches:
            st.session_state.patches = patches

    # Display chat history
    for i, (role, msg) in enumerate(st.session_state.history):
        message(msg, is_user=(role == "user"), key=f"msg_{i}")


# -------------------------------
# Task Dashboard Page
# -------------------------------
elif page == "Task Dashboard":
    st.subheader("📋 Task Dashboard")
    html = render_html_dashboard(user_id, store_memory)
    st.components.v1.html(html, height=600, scrolling=True)



# -------------------------------
# Memory Store Page
# -------------------------------
elif page == "Memory Store":
    st.subheader("🧠 Long‑Term Memory Store")

    namespaces = [
        ("UserProfile", user_id),
        ("ToDo", user_id),
        ("Instructions", user_id)
    ]

    for ns in namespaces:
        st.markdown(f"### 📌 Namespace: `{ns[0]}` — User: `{ns[1]}`")
        items = store_memory.search(ns)

        if not items:
            st.info("No memory found.")
            continue

        for m in items:
            st.json(m.value)


# -------------------------------
# Patch Viewer Page
# -------------------------------
elif page == "Patch Viewer":
    st.subheader("🔍 Patch Viewer (Tool Call Visibility)")
    if "patches" in st.session_state:
        html = render_patch_html(st.session_state.patches)
        st.components.v1.html(html, height=600, scrolling=True)
    else:
        st.info("No patches yet. Chat with the agent first.")





















