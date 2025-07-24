from fastapi import FastAPI, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.chat_agent import chat_with_memory, memory ,chat_with_memory_with_confirmation # Import your chat agent
from langgraph_app.graph import setup_graph
from utils.file_ops import router as file_ops_router
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


app = FastAPI()

# Allow CORS for your frontend (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(file_ops_router)

class ChatRequest(BaseModel): 
    message: str
    custom_instructions: str = "Behave like a helpful assitant please"  # Default instructions

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    reply = chat_with_memory_with_confirmation(req.message, req.custom_instructions)
    return reply

@app.post("/reset")
async def reset_endpoint():
    memory.clear()
    return {"status": "memory reset"}




@app.post("/run-task")
async def run_task_endpoint(data: dict = Body(...)):
    print("run-task called with:", data)
    task = data.get("task")
    if not task:
        return {"error": "No task provided"}
    workflow = setup_graph()
    result = workflow.invoke({"task": task})
    return {
        "status": "success",
    }
