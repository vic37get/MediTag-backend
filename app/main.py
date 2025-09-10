from fastapi import FastAPI
from app.database import Base, engine
from app.routes import estudo, label, user
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Estudos")
app.include_router(estudo.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(label.router)
app.include_router(user.router)