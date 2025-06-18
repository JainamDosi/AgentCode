from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langgraph_app.graph import setup_graph

app = FastAPI()
workflow = setup_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly allow OPTIONS
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

class TaskRequest(BaseModel):
    task: str

class CodeRequest(BaseModel):
    frontend_language: str
    frontend_code: str
    task: str

@app.post("/generate")
def generate_code(req: TaskRequest):
    result = workflow.invoke({"task": req.task})
    return {
        "steps": result["steps"],
        "code": result["code"]
    }

@app.post("/process-code")
async def process_code(req: CodeRequest):
    try:
        # Process the code and task using the workflow
        result = workflow.invoke({
            "task": req.task,
            "frontend_code": req.frontend_code,
            "frontend_language": req.frontend_language
        })
        
        return {
            "status": "success",
            "steps": result.get("steps", []),
            "modified_code": result.get("code", ""),
            "message": "Code processed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )