from fastapi import FastAPI
from app.database import Base, engine
from app.routes import estudo, label, user

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Estudos")
app.include_router(estudo.router)
app.include_router(label.router)
app.include_router(user.router)