import logging
import re
import ast
import json
from typing import List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from utils.file_ops import (
    write_code_file,
    read_code_file,
    delete_code_file,
    apply_change,
    list_code_files
)
from models.groq_llm import chat  # your LLM wrapper

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ToolStep model ---
class ToolStep(BaseModel):
    file: str = Field(..., description="Filename to operate on")
    tool: str = Field(..., description="One of ['read','write','delete','apply_change','llm_modify']")
    args: dict = Field(default_factory=dict)

# --- Developer state ---
class DevState(TypedDict, total=False):
    steps: List[ToolStep]
    current_step: Optional[ToolStep]
    logs: List[str]

# --- Step: Pick next step ---
def pick_next_step(state: DevState) -> DevState:
    logger.info("[Dev] Picking next step")
    if not state.get("steps"):
        return {"current_step": None}
    step = state["steps"].pop(0)
    logger.info(f"[Dev] Picked step: {step}")
    return {"current_step": step}

# --- Step: Validate/fix step via LLM ---
def validate_step_with_llm(state: DevState) -> DevState:
    step = state["current_step"]
    codebase_files = list_code_files()
    codebase_summary = ""
    for f in codebase_files:
        try:
            code = "".join(read_code_file(f))
            codebase_summary += f"\n---\nFilename: {f}\n{code}"
        except:
            continue

    prompt = f"""
You are a code step validator helping an AI developer execute file operations on a local codebase.

Only use one of these tools:

1. **write**
   - Purpose: Create or overwrite an entire file.
   - Args: {{ "content": "<full file contents>" }}

2. **read**
   - Purpose: Read a file and return its line count.
   - Args: {{}}

3. **delete**
   - Purpose: Remove a file.
   - Args: {{}}

4. **apply_change**
   - Purpose: Insert, modify, or delete a specific line in an existing file.
   - Args:
     - action: one of "insert", "modify", "delete"
     - line: integer (1-based line number)
     - new_code: required if action is "insert" or "modify"

5. **llm_modify**
   - Reserved for LLM-powered auto-edits (not implemented yet).
   - Args: {{}}

Given the codebase context and a proposed ToolStep (file, tool, args), correct and return the step.

Only return the corrected ToolStep as a **pure JSON object** (no comments, no Markdown, no Python dicts):

{{
  "file": "example.py",
  "tool": "apply_change",
  "args": {{
    "action": "modify",
    "line": 4,
    "new_code": "print('Updated')"
  }}
}}

Here is the codebase context:
{codebase_summary}

Planned step:
{step.model_dump()}
"""

    response = chat(prompt)
    logger.info(f"LLM response for steps: {response}")

    clean = re.sub(r"^```[a-zA-Z]*\n?", "", response).replace("```", "").strip()

    try:
        corrected = json.loads(clean)
        return {"current_step": ToolStep(**corrected)}
    except Exception as e:
        logger.warning(f"[Dev] Failed to parse corrected step, using original. Error: {e}")
        return {"current_step": step}  # fallback

# --- Step: Run the tool ---
def run_code_update(state: DevState) -> DevState:
    step = state["current_step"]
    try:
        log = perform_tool_action(step)
    except Exception as e:
        log = f"[ERROR] {step.tool} on {step.file} failed: {e}"
    updated_logs = state.get("logs", []) + [log]
    logger.info(f"[Dev] Log: {log}")
    return {"logs": updated_logs}

# --- Step: Feedback/logging ---
def log_and_feedback(state: DevState) -> DevState:
    step = state["current_step"]
    logger.info(f"[Dev] Step completed: {step.tool} on {step.file}")
    return {}

# --- Tool dispatcher ---
def perform_tool_action(step: ToolStep) -> str:
    tool = step.tool
    file = step.file
    args = step.args

    if tool == "write":
        content = args.get("content", "")
        write_code_file(file, content.splitlines(keepends=True))
        return f"[WRITE] {file} written"

    elif tool == "read":
        lines = read_code_file(file)
        return f"[READ] {file} has {len(lines)} lines"

    elif tool == "delete":
        delete_code_file(file)
        return f"[DELETE] {file} removed"

    elif tool == "apply_change":
        apply_change(
            filename=file,
            action=args["action"],
            line=args["line"],
            new_code=args.get("new_code", "")
        )
        return f"[CHANGE] {args['action']} at line {args['line']} in {file}"

    elif tool == "llm_modify":
        return f"[LLM_MODIFY] Skipped: not implemented yet"

    else:
        raise ValueError(f"Unsupported tool: {tool}")

# --- Loop condition ---
def has_more_steps(state: DevState) -> str:
    return "yes" if state.get("steps") else "no"

# --- LangGraph: Build Developer Subgraph ---
dev_builder = StateGraph(DevState)

dev_builder.add_node("pick_next_step", pick_next_step)
dev_builder.add_node("validate_step_with_llm", validate_step_with_llm)
dev_builder.add_node("run_code_update", run_code_update)
dev_builder.add_node("log_and_feedback", log_and_feedback)

dev_builder.set_entry_point("pick_next_step")
dev_builder.add_edge("pick_next_step", "validate_step_with_llm")
dev_builder.add_edge("validate_step_with_llm", "run_code_update")
dev_builder.add_edge("run_code_update", "log_and_feedback")
dev_builder.add_conditional_edges("log_and_feedback", has_more_steps, {
    "yes": "pick_next_step",
    "no": END
})

developer_graph = dev_builder.compile()

# --- Runner ---
def run_developer_subgraph(steps: List[dict]) -> List[str]:
    parsed = [ToolStep(**step) for step in steps]
    result = developer_graph.invoke({"steps": parsed})
    return result.get("logs", [])

# --- Local Test ---
if __name__ == "__main__":
    test_steps = [
        {
            "file": "hello.py",
            "tool": "write",
            "args": {"content": "print('Hello')\n"}
        },
        {
            "file": "hello.py",
            "tool": "apply_change",
            "args": {"action": "modify", "line": 1, "new_code": "print('Updated')"}
        }
    ]
    logs = run_developer_subgraph(test_steps)
    print("\n--- Logs ---")
    for log in logs:
        print(log)
