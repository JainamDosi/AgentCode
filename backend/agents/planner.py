import re
import ast
import json
import argparse
import requests
import logging
import os
from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field, ValidationError
from models.groq_llm import chat
from utils.file_ops import list_code_files, read_code_file
from langgraph.graph import StateGraph, END
import time
import os
from dotenv import load_dotenv

load_dotenv()


# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Tavily search helper ---
def tavily_search(query: str, max_results: int = 5, retries: int = 3) -> list:
    api_key = os.getenv("TAVILY_API_KEY")
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "include_images": False,
        "max_results": max_results
    }
    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Tavily response: {data}")
            logger.info(f"Tavily returned {len(data.get('results', []))} results.")
            return data.get("results", [])
        except requests.exceptions.Timeout:
            logger.warning(f"Tavily timeout, retrying ({attempt+1}/{retries})...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"Tavily error: {e}")
            break
    return []

# --- ToolStep schema ---
class ToolStep(BaseModel):
    file: str = Field(..., description="Filename to operate on")
    tool: str = Field(..., description="One of ['read','write','delete','apply_change','llm_modify']")
    args: dict = Field(default_factory=dict, description="Arguments for the tool operation")

# --- LangGraph State Definition ---
class PlannerState(TypedDict, total=False):
    task: str
    codebase_summary: str
    enhanced_task: str
    use_external: bool
    search_query: str
    external_results: List[dict]
    steps: List[ToolStep]

# --- Node Functions ---
def summarize_codebase(state: PlannerState) -> PlannerState:
    logger.info("[Node] summarize_codebase")
    try:
        files = list_code_files()
    except Exception:
        files = []
    summary = []
    for f in files:
        try:
            content = ''.join(read_code_file(f))
            summary.append(f"---\nFilename: {f}\n{content}\n")
        except Exception:
            summary.append(f"---\nFilename: {f}\n[Unreadable]\n")
    logger.info(f"Summarized {len(summary)} files.")
    return {"codebase_summary": "".join(summary)}

def enhance_prompt(state: PlannerState) -> PlannerState:
    logger.info("[Node] enhance_prompt")
    prompt = (
        f"You are aware of the following codebase:\n{state['codebase_summary']}\n"
        f"Enhance this task for clarity: {state['task']} Do not give any code just imrpove the task language"
        f"Just give the enhanced task nothing else no additional information"
    )
    enhanced = chat(prompt)
    logger.info(f"Enhanced task: {enhanced.strip()}")
    return {"enhanced_task": enhanced}

def generate_search_query(state: PlannerState) -> PlannerState:
    logger.info("[Node] generate_search_query")
    prompt = (
        f"You are an expert research assistant. Given the following enhanced task, "
        f"generate a single, concise web search query (or a comma-separated list of queries) for any EXTRA information required to complete the task like some information or article or api link etc."
        f"that would help a developer complete the task. "
        f"Do NOT include explanations, just the query or queries. do not mention any year\n\n "
        f"Enhanced Task:\n{state['enhanced_task']}\n"
    )
    query = chat(prompt).strip()
    logger.info(f"Generated search query: {query}")
    return {"search_query": query}

def decide_search_source(state: PlannerState) -> PlannerState:
    logger.info("[Node] decide_search_source")
    prompt = (
        f"Given the task and codebase context, should we fetch external docs?\n"
        f"Task: {state['task']}\nCodebase: {state['codebase_summary']}\n"
        f"Answer with EXTERNAL or INTERNAL."
    )
    result = chat(prompt).strip().upper()
    logger.info(f"Decision from LLM: {result}")
    return {"use_external": result == "EXTERNAL"}

def search_external(state: PlannerState) -> PlannerState:
    logger.info("[Node] search_external")
    logger.info(f"State keys at search_external: {list(state.keys())}")
    query = state.get("search_query", state["task"])
    logger.info(f"Query passed to Tavily: {query}")
    results = tavily_search(query)
    return {"external_results": results}

def generate_steps(state: PlannerState) -> PlannerState:
    logger.info("[Node] generate_steps")
    external_results = state.get('external_results', [])
    external_text = ""
    if external_results:
        external_text = "\n\nExternal Web Search Results:\n"
        for i, res in enumerate(external_results, 1):
            external_text += f"{i}. {res.get('title', '')}\nURL: {res.get('url', '')}\n{res.get('content', '')}\n\n"

    prompt = f"""
You are a software planning agent. Given the following enhanced task, codebase, and web search results, break it down into the smallest possible, atomic steps.
Generate a python list of steps , Each step must mention:
- "file": the filename to operate on (specify the correct extension for the language, e.g., .js, .html, .py, .css, .java, etc.)
- "tool": one of ["read", "write", "delete", "apply_change", "llm_modify"]
- "args": a dict of arguments for the tool (e.g., code, line number, function name, etc.)

Choose the file type and language that best fits the task. If the task involves web, use .html, .js, .css as needed. If the task is for Python, use .py. If the codebase is empty, create all necessary files from scratch.

Be specific: reference real files, functions, and lines. Do not use placeholders like '...' or generic names. If a file does not exist, create it. If you need to add a function or code, specify its full code. If you need to modify a line, specify the line number and the new code.

Output ONLY a valid Python list of steps, no explanations, no markdown, no extra text.

Codebase:
{state['codebase_summary']}

Enhanced Task:
{state['enhanced_task']}
If the required information to complete the task is present in this {external_text} include them in the result.


If you cannot determine the steps, output an empty list: []


"""
    response = chat(prompt)
    clean = re.sub(r"^```[a-zA-Z]*\n?", "", response).replace("```", "").strip()
    try:
        steps_raw = ast.literal_eval(clean)
    except Exception as e:
        logger.error(f"Failed to parse steps: {e}\nRaw string was:\n{clean}")
        steps_raw = []

    steps: List[ToolStep] = []
    for item in steps_raw:
        try:
            steps.append(ToolStep(**item))
        except ValidationError as e:
            raise RuntimeError(f"Step validation failed: {e}")
    logger.info(f"Generated {len(steps)} steps.")
    return {"steps": steps}

# --- Build LangGraph ---
builder = StateGraph(PlannerState)

builder.add_node("summarize_codebase", summarize_codebase)
builder.add_node("enhance_prompt", enhance_prompt)
builder.add_node("generate_search_query", generate_search_query)
builder.add_node("decide_search_source", decide_search_source)
builder.add_node("search_external", search_external)
builder.add_node("generate_steps", generate_steps)

# Edges
builder.set_entry_point("summarize_codebase")
builder.add_edge("summarize_codebase", "enhance_prompt")
builder.add_edge("enhance_prompt", "generate_search_query")
builder.add_edge("generate_search_query", "decide_search_source")

builder.add_conditional_edges(
    "decide_search_source",
    lambda state: "external" if state["use_external"] else "internal",
    {
        "external": "search_external",
        "internal": "generate_steps"
    }
)

builder.add_edge("search_external", "generate_steps")
builder.add_edge("generate_steps", END)

graph = builder.compile()

# --- Public Runner ---
def run_planner_subgraph(task: str) -> List[dict]:
    logger.info(f"Running planner for task: {task}")
    output = graph.invoke({"task": task})
    logger.info("Planner execution completed.")
    return [step.model_dump() for step in output["steps"]]

# --- CLI Testing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--task", type=str, help="Task to plan", required=False)
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        test_tasks = [
            "Add a health-check endpoint to server.py",
            "Refactor the database connector into a new module",
            "Enhance existing authentication flow to use OAuth2"
        ]
        for task in test_tasks:
            print(f"\n=== Task: {task} ===")
            result = run_planner_subgraph(task)
            print(json.dumps(result, indent=2))
    elif args.task:
        result = run_planner_subgraph(args.task)
        print(json.dumps(result, indent=2))
    else:
        parser.error("Provide --task or --test")
