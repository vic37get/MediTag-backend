from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import schemas
from app.crud import estudo
from app.database import get_db
from app.crud import tag as tag_crud
from app.models import Estudo, User
from app.crud.auth import get_current_user

router = APIRouter(
    prefix="/estudos",
    tags=["Estudos"]
)

# @router.post("", response_model=schemas.EstudoRead)
# def create_estudo(estudo_in: schemas.EstudoCreate, db: Session = Depends(get_db)):
#     return estudo.create_estudo(db, estudo_in)

@router.get("", response_model=list[schemas.EstudoRead])
# def read_estudos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
def read_estudos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return estudo.get_estudos(db, skip, limit)

@router.get("/{estudo_id}", response_model=schemas.EstudoRead)
# def read_estudo(estudo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@router.get("/{estudo_id}/tags", response_model=list[schemas.TagRead])
# def get_estudo_tags(estudo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
def get_estudo_tags(estudo_id: int, db: Session = Depends(get_db)):
    estudo_obj = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if not estudo_obj:
        raise HTTPException(status_code=404, detail="Estudo não encontrado")
    return tag_crud.get_tags_for_estudo(db, estudo_obj)

# @router.post("/{estudo_id}/tags", response_model=list[schemas.TagRead])
# def add_tags_to_estudo(estudo_id: int, tag_ids: list[int] = Body(..., example=[1,2,3]), db: Session = Depends(get_db)):
#     """
#     Corpo: [1, 2, 3]  -> lista de tag ids a serem adicionados ao estudo
#     """
#     estudo_obj = db.query(Estudo).filter(Estudo.id == estudo_id).first()
#     if not estudo_obj:
#         raise HTTPException(status_code=404, detail="Estudo não encontrado")
#     added = tag_crud.add_tags_to_estudo(db, estudo_obj, tag_ids)
#     if not added:
#         raise HTTPException(status_code=404, detail="Nenhuma tag válida encontrada")
#     return added

# @router.delete("/{estudo_id}/tags/{tag_id}")
# def remove_tag_from_estudo(estudo_id: int, tag_id: int, db: Session = Depends(get_db)):
#     estudo_obj = db.query(Estudo).filter(Estudo.id == estudo_id).first()
#     if not estudo_obj:
#         raise HTTPException(status_code=404, detail="Estudo não encontrado")
#     ok = tag_crud.remove_tag_from_estudo(db, estudo_obj, tag_id)
#     if not ok:
#         raise HTTPException(status_code=404, detail="Tag não encontrada no estudo")
#     return {"message": "Tag removida com sucesso"}


@router.get("/{estudo_id}/export")
def export_estudo(estudo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Exporta um estudo como pandas DataFrame serializado em JSON.
    
    Retorna um JSON com as seguintes colunas:
    - amostra_id: ID da amostra
    - imagem_path: Caminho para a imagem
    - imagem_pil_b64: Imagem em formato base64 (para reconstruir PIL Image)
    - achados: Labels/achados encontrados (separados por vírgula)
    - comentarios: Comentários feitos (text_report)
    - relatorio: Relatório/laudo (report)
    - status: Status da amostra
    """
    df_export = estudo.export_estudo_to_dataframe(db, estudo_id)
    if df_export is None:
        raise HTTPException(status_code=404, detail="Estudo não encontrado")
    df_export = df_export.drop(columns=['imagem_pil'])
    return JSONResponse(content={
        "estudo_id": estudo_id,
        "total_registros": len(df_export),
        "colunas": list(df_export.columns),
        "dados": df_export.to_dict('records')
    })