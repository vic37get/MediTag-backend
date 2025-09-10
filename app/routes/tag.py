from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import tag
from app.models import Estudo, Tag
from app.database import get_db

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)

@router.post("", response_model=schemas.TagRead)
def create_tag(tag_in: schemas.TagCreate, db: Session = Depends(get_db)):
    return tag.create_tag(db, tag_in)

@router.get("", response_model=list[schemas.TagRead])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return tag.get_tags(db, skip, limit)

@router.get("/{tag_id}", response_model=schemas.TagRead)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = tag.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag não encontrada")
    return db_tag

@router.post("/estudos/{estudo_id}/tags")
def add_tags_to_estudo(estudo_id: int, tag_ids: list[int], db: Session = Depends(get_db)):
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if not estudo:
        raise HTTPException(status_code=404, detail="Estudo não encontrado")

    tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    if not tags:
        raise HTTPException(status_code=404, detail="Nenhuma tag encontrada")

    estudo.tags.extend(tags)
    db.commit()
    db.refresh(estudo)

    return {"message": "Tags adicionadas com sucesso", "tags": [t.name for t in estudo.tags]}

@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    success = tag.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag não encontrada")
    return {"message": "Tag deletada com sucesso"}