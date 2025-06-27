from langgraph.graph import StateGraph
from typing import TypedDict
from agents.planner import planner_agent
from agents.developer import developer_agent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- State Classes ---

class OverallState(TypedDict, total=False):
    task: str
    steps: list[dict]
    code: dict
    status: str
    error: str

class PlannerState(TypedDict, total=False):
    task: str
    steps: list[dict]
    reasoning: str

class DeveloperState(TypedDict, total=False):
    steps: list[dict]
    code: dict
    changes: list[dict]
    reasoning: str

# --- Workflow Setup ---

def setup_graph():
    graph = StateGraph(OverallState)

    def planner_node(state: OverallState) -> dict:
        logger.info(f"Planner node received task: {state['task']}")
        planner_state = PlannerState(
            task=state['task'],
            steps=[],
            reasoning=""
        )
        steps = planner_agent(state['task'])
        planner_state['steps'] = steps
        planner_state['reasoning'] = "Task broken down into actionable steps"
        logger.info(f"Planner generated steps: {steps}")
        return {
            "steps": steps,
            "status": "planning_complete"
        }

    def developer_node(state: OverallState) -> dict:
        if 'steps' not in state:
            logger.error("No steps found in state")
            return {
                "error": "No steps found in state",
                "status": "error"
            }
        logger.info(f"Developer node received steps: {state['steps']}")
        developer_state = DeveloperState(
            steps=state['steps'],
            code={},
            changes=[],
            reasoning=""
        )
        all_code = {}
        for step in state['steps']:
            filename = step["file"]
            step_descs = step["steps"]
            code = developer_agent(step_descs, filename)
            all_code[filename] = code
            logger.info(f"Developer updated {filename}")
        developer_state['code'] = all_code
        developer_state['reasoning'] = "Code modified based on planned steps"
        return {
            "code": all_code,
            "status": "development_complete"
        }

    graph.add_node("planner_node", planner_node)
    graph.add_node("developer_node", developer_node)
    graph.add_edge("planner_node", "developer_node")
    graph.set_entry_point("planner_node")

    return graph.compile()
