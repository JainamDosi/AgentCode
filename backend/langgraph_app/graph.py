from langgraph.graph import StateGraph
from typing import TypedDict
from agents.planner import run_planner_subgraph as planner_agent
from agents.developer import run_developer_subgraph as developer_agent
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Main state class ---
class OverallState(TypedDict, total=False):
    task: str
    steps: list[dict]
    code: dict
    status: str
    error: str

# --- Build Main LangGraph ---
def setup_graph():
    graph = StateGraph(OverallState)

    # --- Node 1: Planner ---
    def planner_node(state: OverallState) -> dict:
        logger.info(f"[Planner Node] Received task: {state['task']}")
        try:
            steps = planner_agent(state['task'])  # invokes the planner subgraph
            return {
                "steps": steps,
                "status": "planning_complete"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    # --- Node 2: Developer ---
    def developer_node(state: OverallState) -> dict:
        logger.info(f"[Developer Node] Received steps: {state.get('steps')}")
        if not state.get("steps"):
            return {
                "error": "No steps found",
                "status": "error"
            }
        try:
            dev_result = developer_agent(state["steps"])  # invokes the developer subgraph
            return {
                "code": dev_result,
                "status": "development_complete"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    # Add nodes
    graph.add_node("planner_node", planner_node)
    graph.add_node("developer_node", developer_node)

    # Set transitions
    graph.set_entry_point("planner_node")
    graph.add_edge("planner_node", "developer_node")

    return graph.compile()
