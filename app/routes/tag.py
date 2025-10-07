from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import tag
from app.database import get_db
from app.models import User
from app.crud.auth import get_current_user

router = APIRouter(
    prefix="/tags",
    tags=["Tags"]
)


@router.get("", response_model=list[schemas.TagRead])
def read_tags(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para listar tags.
    """
    return tag.get_tags(db, skip, limit)

@router.get("/{tag_id}", response_model=schemas.TagRead)
def read_tag(
    tag_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para obter uma tag específica pelo ID.
    """
    db_tag = tag.get_tag(db, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag não encontrada")
    return db_tag