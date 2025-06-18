from models.groq_llm import chat
import logging

logger = logging.getLogger(__name__)

def planner_agent(task: str, frontend_code: str, frontend_language: str) -> list[str]:
    """
    Planner agent that breaks down tasks into actionable steps based on existing code.
    """
    logger.info(f"Planning task: {task}")
    
    prompt = f"""Analyze the following code and task, then break down what changes are needed into 2-3 clear, actionable steps.
    Consider the existing codebase and what modifications are required.
    
    Task: {task}
    Language: {frontend_language}
    
    Existing Code:
    {frontend_code}
    
    Provide steps in the following format:
    1. [Step description]
    2. [Step description]
    3. [Step description] (if needed)
    
    Steps:"""
    
    response = chat(prompt)
    steps = [line.strip("-• \n") for line in response.split("\n") if line.strip()]
    logger.info(f"Generated steps: {steps}")
    
    return steps
