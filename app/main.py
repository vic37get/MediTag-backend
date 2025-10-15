# no app.py (logo no início)
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import (
    estudo,
    label,
    amostra,
    workspace,
    tag,
    auth,
    sdk
)
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

app.include_router(estudo.router)
app.include_router(auth.router)
app.include_router(workspace.router)
app.include_router(label.router)
app.include_router(amostra.router)
app.include_router(tag.router)
app.include_router(sdk.router)