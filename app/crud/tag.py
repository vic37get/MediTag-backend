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

def add_tags_to_estudo(db: Session, estudo, tag_ids: list[int]) -> list[Tag]:
    """
    Recebe um objeto Estudo (ORM) e uma lista de tag_ids.
    Adiciona as tags ao estudo (ignorando duplicatas) e retorna a lista atualizada de Tag.
    """
    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    if not tags:
        return []
    
    for t in tags:
        if t not in estudo.tags:
            estudo.tags.append(t)
    db.commit()
    db.refresh(estudo)
    return estudo.tags

def remove_tag_from_estudo(db: Session, estudo, tag_id: int) -> bool:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False
    if tag in estudo.tags:
        estudo.tags.remove(tag)
        db.commit()
        db.refresh(estudo)
        return True
    return False

def get_tags_for_estudo(db: Session, estudo):
    return estudo.tags