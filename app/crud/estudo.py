from sqlalchemy.orm import Session
from app.models import Estudo
from app.schemas import EstudoCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_estudos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Estudo).offset(skip).limit(limit).all()

def get_estudo(db: Session, estudo_id: int):
    return db.query(Estudo).filter(Estudo.id == estudo_id).first()

def create_estudo(db: Session, estudo: EstudoCreate):
    try:
        db_estudo = Estudo(**estudo.model_dump())
        db.add(db_estudo)
        db.commit()
        db.refresh(db_estudo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="O estudo já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_estudo

def delete_estudo(db: Session, estudo_id: int):
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if estudo:
        db.delete(estudo)
        db.commit()
        return True
    return False