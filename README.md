# 📌 My Task Manager — Gemini‑Powered LangGraph ReAct Agent
**A powerful, intelligent task‑management AI assistant that can reason, use tools, update long‑term memory, manage tasks, and even generate customized To‑Do cards — all inside a ReAct‑style workflow.**

`Agent is built using Gemini, LangGraph, TrustCall, and a custom SPY listener for full visibility into tool calls and JSON Patch updates.`

🧠 How It Works
**Below is a clean workflow diagram**

              ┌──────────────────────────┐
                │        User Input         │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │     Gemini LLM (ReAct)    │
                │  Thought → Tool → Answer  │
                └─────────────┬────────────┘
                              │
                ┌─────────────┼──────────────┐
                ▼             ▼               ▼
      ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
      │ UserProfile     │  │ ToDoItem       │  │ InstructionMemory  │
      │ TrustCall Tool  │  │ TrustCall Tool │  │ TrustCall Tool     │
      └────────────────┘  └────────────────┘  └────────────────────┘
                │             │               │
                └─────────────┼──────────────┘
                              ▼
                ┌──────────────────────────┐
                │     Memory Store          │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │     SPY Listener          │
                │  (Tool Call Visibility)   │
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   HTML Patch Viewer       │
                └──────────────────────────┘

