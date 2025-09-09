from sqlalchemy.orm import Session
from app.models import Tag
from app.schemas import TagCreate

def get_tags(db: Session, skip=0, limit=100):
    return db.query(Tag).offset(skip).limit(limit).all()

def get_tag(db: Session, tag_id: int):
    return db.query(Tag).filter(Tag.id == tag_id).first()

def create_tag(db: Session, tag: TagCreate):
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def delete_tag(db: Session, estudo_id: int):
    tag = db.query(Tag).filter(Tag.id == estudo_id).first()
    if tag:
        db.delete(tag)
        db.commit()
        return True
    return False