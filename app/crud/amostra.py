from sqlalchemy.orm import Session
from app.schemas import AmostraCreate
from app.models import Amostra

def get_amostras(db: Session, skip=0, limit=100):
    return db.query(Amostra).offset(skip).limit(limit).all()

def get_amostra(db: Session, amostra_id: int):
    return db.query(Amostra).filter(Amostra.id == amostra_id).first()

def create_amostra(db: Session, amostra: AmostraCreate):
    db_amostra = Amostra(**amostra.model_dump())
    db.add(db_amostra)
    db.commit()
    db.refresh(db_amostra)
    return db_amostra

def delete_amostra(db: Session, amostra_id: int):
    amostra = db.query(Amostra).filter(Amostra.id == amostra_id).first()
    if amostra:
        db.delete(amostra)
        db.commit()
        return True
    return False