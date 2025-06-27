from models.groq_llm import chat
import logging
from utils.file_ops import read_code_file, write_code_file, code_to_ast_string, delete_code_file
import re
import os

logger = logging.getLogger(__name__)

def clean_code_block(text: str) -> str:
    # Remove triple backticks and any language specifier
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = text.replace("```", "")
    return text.strip()

def developer_agent(steps: list[str], filename: str) -> str:
    """
    Developer agent that implements the planned steps based on existing code.
    Handles new files gracefully and can delete files.
    """
    logger.info(f"Developing steps: {steps} for file: {filename}")

    # Check for a delete instruction
    delete_instructions = [s for s in steps if "delete this file" in s.lower() or "remove this file" in s.lower()]
    if delete_instructions:
        delete_code_file(filename)
        logger.info(f"Deleted file: {filename}")
        return ""  # No code to return

    # Try to read the code from file, or use empty string if file does not exist
    try:
        code_lines = read_code_file(filename)
        code_str = ''.join(code_lines)
    except FileNotFoundError:
        code_str = ""
    ast_str = code_to_ast_string(code_str) if code_str else "No code (new file)."

    step_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

    prompt = f"""
You are a codebase refactoring agent.

Modify the following code according to the development steps. For each step:
- Only make the exact change described in the step.
- For "delete" steps, remove the entire function or class definition as specified.
- For "add" steps, insert the provided code exactly as given.
- For import changes, insert the import line at the top of the file.
- Do NOT add, remove, or modify any code that is not explicitly mentioned in the steps.
- Do NOT add extra functions, comments, or explanations.
- Add comments to explain only where necessary , keep the comments short 
- Do NOT use markdown or code blocks—return only the full, final code for the file.

Existing Code:
{code_str}

AST of Existing Code:
{ast_str}

Steps to implement:
{step_text}

Return ONLY the full, modified code for the file, with all steps applied in order.
"""

    modified_code = chat(prompt)
    cleaned_code = clean_code_block(modified_code)
    logger.info(f"Modified code: {cleaned_code[:200]}...")

    # Overwrite the file with the new code
    write_code_file(filename, [line + "\n" for line in cleaned_code.splitlines()])
    return cleaned_code
