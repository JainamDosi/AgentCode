import os
import ast

CODEBASE_DIR = os.path.join(os.path.dirname(__file__), '../codebase')

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