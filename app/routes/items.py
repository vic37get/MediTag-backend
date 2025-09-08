from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil, os

from app import crud, schemas, database

router = APIRouter(prefix="/items", tags=["items"])

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/{dataset_id}/", response_model=schemas.Item)
def create_item(
    dataset_id: int,
    text: str = Form(...),
    files: List[UploadFile] = File([]),
    db: Session = Depends(database.get_db)
):
    item = crud.create_item(db, schemas.ItemCreate(text=text), dataset_id)
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        crud.create_image(db, file_path, item.id)
    return item
