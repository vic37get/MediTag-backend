from sqlalchemy.orm import Session
from app.models import Tag
from app.schemas import TagCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_tags(db: Session, skip=0, limit=100):
    return db.query(Tag).offset(skip).limit(limit).all()

def get_tag(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id).first()

def create_tag(db: Session, tag: TagCreate):
    try:
        db_tag = Tag(**tag.model_dump())
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A tag já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_tag

def delete_tag(db: Session, estudo_id: int):
    tag = db.query(Tag).filter(Tag.id == estudo_id).first()
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False