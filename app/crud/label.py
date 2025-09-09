from sqlalchemy.orm import Session
from app.schemas import LabelCreate
from app.models import Label

def get_labels(db: Session, skip=0, limit=100):
    return db.query(Label).offset(skip).limit(limit).all()

def get_label(db: Session, label_id: int):
    return db.query(Label).filter(Label.id == label_id).first()

def create_label(db: Session, label: LabelCreate):
    db_label = Label(**label.model_dump())
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label

def delete_label(db: Session, label_id: int):
    label = db.query(Label).filter(Label.id == label_id).first()
    if label:
        db.delete(label)
        db.commit()
        return True
    return False