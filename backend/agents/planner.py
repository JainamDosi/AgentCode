from models.groq_llm import chat
import logging
from utils.file_ops import list_code_files, read_code_file
import re

logger = logging.getLogger(__name__)

def extract_python_list(text: str) -> str:
    """
    Extract the first Python list (enclosed in [ ... ]) from the text.
    """
    # Remove code block markers and language specifiers
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = text.replace("```", "")
    # Find the first list in the text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return text  # fallback: return as is

def planner_agent(task: str) -> list[dict]:
    """
    Planner agent that breaks down tasks into actionable steps based on the codebase.
    Each step specifies which file to edit and what to do.
    """
    logger.info(f"Planning task: {task}")

    # List and read codebase files
    files = list_code_files()
    codebase_summary = ""
    for fname in files:
        try:
            code = ''.join(read_code_file(fname))
            codebase_summary += f"\n---\nFilename: {fname}\n{code}\n"
        except Exception as e:
            codebase_summary += f"\n---\nFilename: {fname}\n[Could not read file: {e}]\n"

    prompt = f"""You are a software planner. Analyze the following codebase and the given task.
For each file, provide a list of clear, atomic, and unambiguous steps to implement the task.
Each step should be self-contained and specify exactly what to do in that file (e.g., add, modify, move, or delete a function, class, or line).
If a change involves multiple files (e.g., moving or renaming code), specify the source and destination files and the exact actions for each.
Do not use import statements to move code unless the task explicitly asks for it.
Be precise, avoid repeating steps, and do not assume any context not present in the codebase.

Task: {task}

Codebase files and contents:
{codebase_summary}

Provide steps in the following format (as a Python list of dicts):
[
  {{"file": "filename.py", "steps": ["First step for this file.", "Second step for this file."]}},
  ...
]

Steps:
"""

    response = chat(prompt)
    logger.info(f"Generated steps: {response}")

    # Extract and parse the Python list from the LLM output
    import ast
    try:
        steps_str = extract_python_list(response)
        steps = ast.literal_eval(steps_str)
    except Exception as e:
        logger.error(f"Failed to parse steps: {e}")
        steps = []
    return steps
