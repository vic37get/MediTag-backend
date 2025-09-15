import os
import uuid
from fastapi import UploadFile, HTTPException

ROOT_DIR = os.path.abspath(os.getcwd())
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR_PATH = os.path.join(ROOT_DIR, UPLOAD_DIR)
os.makedirs(UPLOAD_DIR_PATH, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

async def save_upload_file(file: UploadFile, estudo_id: int | str) -> str:
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Formato de arquivo não permitido")
    ext = file.filename.rsplit(".", 1)[1].lower()
    estudo_dir = os.path.join(UPLOAD_DIR_PATH, f"estudo_{estudo_id}")
    os.makedirs(estudo_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(estudo_dir, filename)
    try:
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)
    except Exception as e:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")
    return filepath

def remove_file(path: str):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass