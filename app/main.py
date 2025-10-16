from fastapi import FastAPI
from app.database import Base, engine
from app.routes import estudo, label, amostra, workspace, tag, auth, sdk
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Estudos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os, logging
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Request

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app.include_router(prefix="/api/v1", router=estudo.router)
app.include_router(prefix="/api/v1", router=auth.router)
app.include_router(prefix="/api/v1", router=workspace.router)
app.include_router(prefix="/api/v1", router=label.router)
app.include_router(prefix="/api/v1", router=amostra.router)
app.include_router(prefix="/api/v1", router=tag.router)
app.include_router(prefix="/api/v1", router=sdk.router)

# --- Static Files Setup ---
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/browser")
os.makedirs(static_dir, exist_ok=True)

# app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


# --- Catch-all for React Routes ---
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    # Tenta servir arquivo estático primeiro (JS, CSS, etc)
    file_path = os.path.join(static_dir, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # Fallback para index.html (rotas do SPA)
    index_html = os.path.join(static_dir, "index.html")
    if os.path.exists(index_html):
        logger.info(f"Serving Angular frontend for path: /{full_path}")
        return FileResponse(index_html)

    logger.error("Frontend not built. index.html missing.")
    raise HTTPException(
        status_code=404, detail="Frontend not built. Please run 'npm run build' first."
    )
