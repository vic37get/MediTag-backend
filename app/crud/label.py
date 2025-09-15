from sqlalchemy.orm import Session
from app.schemas import LabelCreate
from app.models import Label
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_labels(db: Session, skip=0, limit=100):
    return db.query(Label).offset(skip).limit(limit).all()


def get_label(db: Session, label_id: int):
    return db.query(Label).filter(Label.id == label_id).first()


def get_label_raw(db: Session, label_id: int):
    """Retorna o objeto SQLAlchemy Label diretamente, sem processamento."""
    return db.query(Label).filter(Label.id == label_id).first()


def create_label(db: Session, label: LabelCreate):
    try:
        db_label = Label(**label.model_dump())
        db.add(db_label)
        db.commit()
        db.refresh(db_label)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="O label já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_label


def delete_label(db: Session, label_id: int):
    label = db.query(Label).filter(Label.id == label_id).first()
    if label:
        db.delete(label)
        db.commit()
        return True
    return False
