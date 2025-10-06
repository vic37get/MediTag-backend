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

# @router.post("", response_model=schemas.LabelRead)
# def create_label(label_in: schemas.LabelCreate, db: Session = Depends(get_db)):
#     return label.create_label(db, label_in)

@router.get("", response_model=list[schemas.LabelRead])
def read_labels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return label.get_labels(db, skip, limit)

@router.get("/{label_id}", response_model=schemas.LabelRead)
def read_label(label_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_label = label.get_label(db, label_id)
    if db_label is None:
        raise HTTPException(status_code=404, detail="Label não encontrado")
    return db_label

# @router.delete("/{label_id}")
# def delete_label(label_id: int, db: Session = Depends(get_db)):
#     success = label.delete_label(db, label_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Label não encontrado")
#     return {"message": "Label deletado com sucesso"}