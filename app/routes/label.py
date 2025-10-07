from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import label
from app.database import get_db
from app.models import User
from app.crud.auth import get_current_user

router = APIRouter(
    prefix="/labels",
    tags=["Labels"]
)


@router.get("", response_model=list[schemas.LabelRead])
def read_labels(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para listar labels.
    """
    return label.get_labels(db, skip, limit)

@router.get("/{label_id}", response_model=schemas.LabelRead)
def read_label(
    label_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para obter um label específico pelo ID.
    """
    db_label = label.get_label(db, label_id)
    if db_label is None:
        raise HTTPException(status_code=404, detail="Label não encontrado")
    return db_label