from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import estudo
from app.database import get_db

router = APIRouter(
    prefix="/estudos",
    tags=["Estudos"]
)

@router.post("", response_model=schemas.EstudoRead)
def create_estudo(estudo_in: schemas.EstudoCreate, db: Session = Depends(get_db)):
    return estudo.create_estudo(db, estudo_in)

@router.get("", response_model=list[schemas.EstudoRead])
def read_estudos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return estudo.get_estudos(db, skip, limit)

@router.get("/{estudo_id}", response_model=schemas.EstudoRead)
def read_estudo(estudo_id: int, db: Session = Depends(get_db)):
    db_estudo = estudo.get_estudo(db, estudo_id)
    if db_estudo is None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado")
    return db_estudo

@router.delete("/{estudo_id}")
def delete_estudo(estudo_id: int, db: Session = Depends(get_db)):
    success = estudo.delete_estudo(db, estudo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Estudo não encontrado")
    return {"message": "Estudo deletado com sucesso"}