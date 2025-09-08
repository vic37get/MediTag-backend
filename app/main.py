from fastapi import FastAPI
from app.database import Base, engine
from app.routes import items

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Labeling Tool")

app.include_router(items.router)