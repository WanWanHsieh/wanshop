import os

def static_root():
    return os.path.join(os.path.dirname(__file__), "..", "static", "uploads")

def ensure_dir(relpath: str) -> str:
    root = static_root()
    target = os.path.join(root, relpath)
    os.makedirs(target, exist_ok=True)
    return target

def public_url_for(abs_path: str) -> str:
    parts = abs_path.replace("\\", "/").split("/static/")
    if len(parts) >= 2:
        return "/static/" + parts[1]
    return "/static/uploads"
