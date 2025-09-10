from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import amostra, label
from app.database import get_db
from app.models import Amostra, Label
import os
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/amostras",
    tags=["Amostras"]
)

@router.post("", response_model=schemas.AmostraRead)
def create_amostra(amostra_in: schemas.AmostraCreate, db: Session = Depends(get_db)):
    return amostra.create_amostra(db, amostra_in)

@router.get("", response_model=list[schemas.AmostraRead])
def read_amostras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return amostra.get_amostras(db, skip, limit)

@router.get("/{amostra_id}/image")
def get_amostra_image(amostra_id: int, db: Session = Depends(get_db)):
    db_amostra = amostra.get_amostra(db, amostra_id)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    
    image_path = db_amostra.image_path
    
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    return FileResponse(image_path)

@router.post("/amostras/{amostra_id}/labels")
def add_labels_to_amostra(amostra_id: int, label_ids: list[int], db: Session = Depends(get_db)):
    amostra_buscada = amostra.get_amostra(db, amostra_id)
    if not amostra_buscada:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")

    labels = db.query(Label).filter(Label.id.in_(label_ids)).all()
    if not labels:
        raise HTTPException(status_code=404, detail="Nenhum label encontrado")

    amostra.labels.extend(labels)
    db.commit()
    db.refresh(amostra)

    return {"message": "Labels adicionados com sucesso", "labels": [l.name for l in amostra.labels]}

@router.get("/{amostra_id}", response_model=schemas.AmostraRead)
def read_amostra(amostra_id: int, db: Session = Depends(get_db)):
    db_amostra = amostra.get_amostra(db, amostra_id)
    if db_amostra is None:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return db_amostra

@router.delete("/{amostra_id}")
def delete_amostra(amostra_id: int, db: Session = Depends(get_db)):
    success = amostra.delete_amostra(db, amostra_id)
    if not success:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return {"message": "Amostra deletada com sucesso"}