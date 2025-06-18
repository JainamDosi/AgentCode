from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from agents.planner import planner_agent
from agents.developer import developer_agent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OverallState(TypedDict, total=False):
    """Overall state that contains shared information between agents"""
    task: str
    steps: list[str]
    code: str
    frontend_code: str  # Added for existing code
    frontend_language: str  # Added for language
    status: str
    error: str

class PlannerState(TypedDict, total=False):
    """State specific to the planner agent"""
    task: str
    steps: list[str]
    reasoning: str
    frontend_code: str  # Added for code context
    frontend_language: str  # Added for language context

class DeveloperState(TypedDict, total=False):
    """State specific to the developer agent"""
    steps: list[str]
    code: str
    frontend_code: str  # Added for existing code
    frontend_language: str  # Added for language context
    changes: list[dict]
    reasoning: str

def setup_graph():
    # Create the main graph
    graph = StateGraph(OverallState)
    
    def planner_node(state: OverallState) -> dict:
        """Planner node that breaks down tasks into steps"""
        logger.info(f"Planner node received task: {state['task']}")
        
        # Create planner state with code context
        planner_state = PlannerState(
            task=state['task'],
            steps=[],
            reasoning="",
            frontend_code=state['frontend_code'],
            frontend_language=state['frontend_language']
        )
        
        # Execute planner agent with code context
        steps = planner_agent(
            state['task'],
            state['frontend_code'],
            state['frontend_language']
        )
        planner_state['steps'] = steps
        planner_state['reasoning'] = "Task broken down into actionable steps"
        
        logger.info(f"Planner generated steps: {steps}")
        
        return {
            "steps": steps,
            "status": "planning_complete"
        }

    def developer_node(state: OverallState) -> dict:
        """Developer node that implements the planned steps"""
        if 'steps' not in state:
            logger.error("No steps found in state")
            return {
                "error": "No steps found in state",
                "status": "error"
            }
            
        logger.info(f"Developer node received steps: {state['steps']}")
        
        # Create developer state with code context
        dev_state = DeveloperState(
            steps=state['steps'],
            code="",
            changes=[],
            reasoning="",
            frontend_code=state['frontend_code'],
            frontend_language=state['frontend_language']
        )
        
        # Execute developer agent with code context
        code = developer_agent(
            state['steps'],
            state['frontend_code'],
            state['frontend_language']
        )
        dev_state['code'] = code
        dev_state['reasoning'] = "Code modified based on planned steps"
        
        logger.info(f"Developer generated code: {code[:100]}...")
        
        return {
            "code": code,
            "status": "development_complete"
        }

    # Add nodes to the graph
    graph.add_node("planner_node", planner_node)
    graph.add_node("developer_node", developer_node)

    # Add edges
    graph.add_edge("planner_node", "developer_node")
    graph.set_entry_point("planner_node")

    return graph.compile()
