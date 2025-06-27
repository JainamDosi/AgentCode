# 🧠 AgentCode: LLM-Powered Codebase Refactoring Platform

AgentCode is an AI-driven platform for automated, multi-file codebase refactoring and research

---

## 🚀 Features

- **Step-by-step code planning and editing** using LLMs (OpenAI, Groq, Anthropic).
- **Multi-file, multi-step refactoring** with atomic, explicit steps.
- **Automatic codebase modification:** add, move, delete, and update code across files.
- **Frontend code editor** with real-time output and theming.
- **Extensible tool system:** add internal/external search, code mapping, and more.
- **AST-based code understanding** for robust code edits.

---

## 🗂️ Project Structure
```
AgentCode/
├── backend/
│   ├── agents/           # Planner and developer agents
│   ├── codebase/         # Editable codebase (test.py, test2.py, etc.)
│   ├── langgraph_app/    # Main workflow graph
│   ├── models/           # LLM model wrappers
│   ├── utils/            # File operations, AST, etc.
│   └── main.py           # Backend entry point
├── src/                  # React frontend
│   ├── components/       # UI components
│   ├── api.js            # API calls to backend
│   └── App.jsx           # Main app
├── public/               # Static assets
└── README.md
```


---

## ⚡ Quickstart

### **Backend**

1. **Install dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Add your LLM API keys (e.g., `GROQ_API_KEY`, `OPENAI_API_KEY`, etc.) to a `.env` file.

3. **Run the backend:**
   ```bash
   python main.py
   ```

### **Frontend**

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the frontend:**
   ```bash
   npm run dev
   ```

3. **Open [http://localhost:5173](http://localhost:5173) in your browser.**

---

## 🛠️ How It Works

- **Planner Agent:** Breaks down tasks into atomic, explicit steps (per file).
- **Developer Agent:** Applies each step, modifying code using LLMs and AST context.
- **Workflow:** Orchestrated by LangGraph, passing state between planner and developer.
- **Frontend:** Lets you input tasks, view/edit code, and see results in real time.

---

## 🧩 Extending

- **Add new tools:** (e.g., external search, code mapping) in `backend/agents/` and register in the workflow.
- **Customize prompts:** in `backend/agents/planner.py` and `developer.py` for your use case.
- **Plug in new LLMs:** via `backend/models/`.

---

