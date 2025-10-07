import mimetypes
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import amostra
from app.database import get_db
from fastapi.responses import FileResponse
import os
from app.schemas import AmostraUpdate, TextReportUpdate
from app.crud.auth import get_current_user
from app.models import User

router = APIRouter(
    prefix="/amostras",
    tags=["Amostras"]
    )

@router.get("", response_model=list[schemas.AmostraRead])
def read_amostras(
    estudo_id: int = None, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para listar amostras. Pode ser filtrado por estudo_id.
    """
    return amostra.get_amostras(estudo_id, db, skip, limit)

@router.get("/{amostra_id}", response_model=schemas.AmostraRead)
def read_amostra(
    amostra_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para obter uma amostra específica pelo ID.
    """
    db_amostra = amostra.get_amostra(db, amostra_id)
    if db_amostra is None:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return db_amostra

@router.get("/{amostra_id}/images/{image_id}")
def get_amostra_image(
    amostra_id: int, 
    image_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para obter uma imagem específica de uma amostra.
    """
    db_amostra = amostra.get_amostra_raw(db, amostra_id)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    image = next((img for img in db_amostra.images if img.id == image_id), None)
    if not image:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    image_path = image.image_path
    if not os.path.isabs(image_path):
        image_path = os.path.join(os.path.abspath(os.getcwd()), image_path)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Arquivo de imagem ausente no servidor")
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "application/octet-stream"
    return FileResponse(image_path, media_type=mime_type)

@router.post("/{amostra_id}/set_text_report")
def set_text_report(
    amostra_id: int,
    payload: TextReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para definir ou atualizar o relatório de texto de uma amostra.
    """
    db_amostra = amostra.set_text_report(db, amostra_id, payload.text_report)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return amostra.get_amostra(db, db_amostra.id)

@router.post("/{amostra_id}/reset")
def reset_amostra(amostra_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint para resetar uma amostra para o estado inicial.
    """
    success = amostra.reset_amostra(db, amostra_id)
    if not success:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return {"message": "Amostra resetada com sucesso"}

@router.get("/{amostra_id}/images")
def list_amostra_images(amostra_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lista todas as imagens de uma amostra e mostra como consultar cada uma.
    """
    db_amostra = amostra.get_amostra_raw(db, amostra_id)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    images = [
        {
            "image_id": img.id,
            "url": img.image_path
        }
        for img in db_amostra.images
    ]
    if not images:
        return {"message": "Nenhuma imagem encontrada para esta amostra."}
    return {
        "message": "Para consultar uma imagem específica, acesse o endpoint /amostras/{amostra_id}/images/{image_id}",
        "images": images
    }    

@router.post("/{amostra_id}/labels")
def add_labels_to_amostra(
    amostra_id: int, 
    label_ids: list[int], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    """
    Endpoint para adicionar labels a uma amostra.
    """

    db_amostra = amostra.set_labels(db, amostra_id, label_ids)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return amostra.get_amostra(db, db_amostra.id)

# @router.patch("/{amostra_id}/status", response_model=schemas.AmostraRead)
# def update_amostra_status(
#     amostra_id: int, 
#     status_update: AmostraStatusUpdate, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
#     ):
#     """
#     Endpoint para atualizar o status de uma amostra.
#     """
#     db_amostra = amostra.get_amostra_raw(db, amostra_id)
#     if not db_amostra:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")

#     db_amostra.status = status_update.status
#     db.commit()
#     db.refresh(db_amostra)

#     return amostra.get_amostra(db, amostra_id)

@router.patch("/{amostra_id}", response_model=schemas.AmostraRead)
def update_amostra(
    amostra_id: int, 
    field_update: AmostraUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para atualizar campos específicos de uma amostra.
    """
    update_data = {k: v for k, v in field_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização")

    updated_amostra = amostra.update_amostra(db, amostra_id, update_data, current_user.id)
    if not updated_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    
    return amostra.get_amostra(db, amostra_id)