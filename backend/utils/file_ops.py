import os
import ast
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import shutil
from fastapi.responses import PlainTextResponse

router = APIRouter()

class PathRequest(BaseModel):
    path: str

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../codebase'))


def safe_join(base, *paths):
    # Prevent path traversal attacks
    final_path = os.path.abspath(os.path.join(base, *paths))
    if not final_path.startswith(base):
        raise HTTPException(status_code=403, detail="Access denied")
    return final_path

@router.get("/fs/list")
def list_dir(path: str = ""):
    try:
        abs_path = safe_join(BASE_DIR, path)
        items = []
        for name in os.listdir(abs_path):
            full_path = os.path.join(abs_path, name)
            items.append({
                "name": name,
                "type": "folder" if os.path.isdir(full_path) else "file"
            })
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/fs/create_folder")
def create_folder(req: PathRequest):
    try:
        abs_path = safe_join(BASE_DIR, req.path)
        os.makedirs(abs_path, exist_ok=True)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/fs/create_file")
def create_file(req: PathRequest):
    try:
        abs_path = safe_join(BASE_DIR, req.path)
        open(abs_path, "w").close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/fs/delete")
def delete_path(req: PathRequest):
    try:
        abs_path = safe_join(BASE_DIR, req.path)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



CODEBASE_DIR = os.path.join(os.path.dirname(__file__), '../../codebase')

def list_code_files():
    return [f for f in os.listdir(CODEBASE_DIR) if os.path.isfile(os.path.join(CODEBASE_DIR, f))]

def read_code_file(filename: str) -> list[str]:
    path = os.path.join(CODEBASE_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_code_file(filename: str, lines: list[str]):
    path = os.path.join(CODEBASE_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def apply_change(filename: str, action: str, line: int, new_code: str = None):
    lines = read_code_file(filename)
    if action == "modify":
        lines[line-1] = new_code + "\n"
    elif action == "insert":
        lines.insert(line, new_code + "\n")
    elif action == "delete":
        lines.pop(line-1)
    write_code_file(filename, lines)

def code_to_ast_string(code: str) -> str:
    try:
        tree = ast.parse(code)
        return ast.dump(tree, indent=4)
    except Exception as e:
        return f"Could not parse AST: {e}"

def delete_code_file(filename: str):
    path = os.path.join(CODEBASE_DIR, filename)
    if os.path.exists(path):
        os.remove(path)

class RenameRequest(BaseModel):
    old_path: str
    new_path: str

@router.post("/fs/rename")
def rename_path(req: RenameRequest):
    try:
        abs_old = safe_join(BASE_DIR, req.old_path)
        abs_new = safe_join(BASE_DIR, req.new_path)
        os.rename(abs_old, abs_new)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/fs/read")
def read_file(path: str):
    try:
        abs_path = safe_join(BASE_DIR, path)
        if not os.path.isfile(abs_path):
            raise HTTPException(status_code=404, detail="File not found")
        with open(abs_path, "r", encoding="utf-8") as f:
            return PlainTextResponse(f.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class SaveFileRequest(BaseModel):
    path: str
    content: str

@router.post("/fs/save")
def save_file(req: SaveFileRequest):
    try:
        abs_path = safe_join(BASE_DIR, req.path)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))