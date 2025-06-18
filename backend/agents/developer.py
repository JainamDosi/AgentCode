from models.groq_llm import chat
import logging

logger = logging.getLogger(__name__)

def developer_agent(steps: list[str], frontend_code: str, frontend_language: str) -> str:
    """
    Developer agent that implements the planned steps based on existing code.
    """
    logger.info(f"Developing steps: {steps}")
    
    step_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    prompt = f"""Modify the following code according to the development steps.
    Include comments explaining the changes.
    Ensure the code is production-ready and follows best practices.
    
    Language: {frontend_language}
    
    Existing Code:
    {frontend_code}
    
    Steps to implement:
    {step_text}
    
    Modified Code:"""
    
    code = chat(prompt)
    logger.info(f"Generated code: {code}...")
    
    return code
