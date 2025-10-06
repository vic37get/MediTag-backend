import mimetypes
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from app import schemas
from app.crud import amostra as amostra_crud
from app.utils import save_upload_file
from app.crud import amostra
from app.database import get_db
from app.utils import save_upload_file, remove_file
from fastapi.responses import FileResponse
import os
from typing import List
from app.schemas import AmostraStatusUpdate, AmostraUpdate, TextReportUpdate
from app.crud.auth import get_current_user
from app.models import User

router = APIRouter(
    prefix="/amostras",
    tags=["Amostras"]
    )


# Endpoint para criação de amostras.
# @router.post("", response_model=schemas.AmostraRead)
# async def create_amostra(
#     id_estudo: int = Form(...),
#     report: str | None = Form(None),
#     images: List[UploadFile] = File(...),
#     db: Session = Depends(get_db),
# ):
#     filepaths = []
#     for image in images:
#         path = await save_upload_file(image, id_estudo)
#         filepaths.append(path)
#     try:
#         amostra_in = schemas.AmostraCreate(id_estudo=id_estudo, report=report)
#         db_amostra = amostra_crud.create_amostra(db, amostra_in, filepaths)
#         return amostra_crud.get_amostra(db, db_amostra.id)
#     except Exception as e:
#         for path in filepaths:
#             remove_file(path)
#         raise HTTPException(status_code=500, detail=str(e))


# Endpoint para listar amostras
@router.get("", response_model=list[schemas.AmostraRead])
def read_amostras(estudo_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return amostra.get_amostras(estudo_id, db, skip, limit)

# Endpoint para obter uma amostra específica pelo ID
@router.get("/{amostra_id}", response_model=schemas.AmostraRead)
def read_amostra(amostra_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_amostra = amostra.get_amostra(db, amostra_id)
    if db_amostra is None:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return db_amostra

# Endpoint para deletar uma amostra
# @router.delete("/{amostra_id}")
# def delete_amostra(amostra_id: int, db: Session = Depends(get_db)):
#     success = amostra.delete_amostra(db, amostra_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")
#     return {"message": "Amostra deletada com sucesso"}

# Endpoint para obter uma imagem de uma amostra
@router.get("/{amostra_id}/images/{image_id}")
def get_amostra_image(amostra_id: int, image_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
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


# Endpoint para definir o relatório de texto de uma amostra
@router.post("/{amostra_id}/set_text_report")
def set_text_report(
    amostra_id: int,
    payload: TextReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_amostra = amostra_crud.set_text_report(db, amostra_id, payload.text_report)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return amostra_crud.get_amostra(db, db_amostra.id)

# Endpoint para resetar uma amostra para o estado inicial
@router.post("/{amostra_id}/reset")
def reset_amostra(amostra_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    success = amostra_crud.reset_amostra(db, amostra_id)
    if not success:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    return {"message": "Amostra resetada com sucesso"}

# Endpoint para listar imagens de uma amostra
@router.get("/{amostra_id}/images")
def list_amostra_images(amostra_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lista todas as imagens de uma amostra e mostra como consultar cada uma.
    """
    db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
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


# Endpoint para apagar uma imagem de uma amostra
# @router.delete("/{amostra_id}/images/{image_id}")
# def delete_amostra_image(amostra_id: int, image_id: int, db: Session = Depends(get_db)):
#     db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
#     if not db_amostra:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")
#     image = next((img for img in db_amostra.images if img.id == image_id), None)
#     if not image:
#         raise HTTPException(status_code=404, detail="Imagem não encontrada")
#     image_path = image.image_path
#     if not os.path.isabs(image_path):
#         image_path = os.path.join(os.path.abspath(os.getcwd()), image_path)
#     if os.path.exists(image_path):
#         remove_file(image_path)
#     db_amostra.images.remove(image)
#     db.delete(image)
#     db.commit()
#     return {"message": "Imagem deletada com sucesso"}


#Endpoint para adicionar imagens a uma amostra
# @router.post("/{amostra_id}/images", response_model=schemas.AmostraRead)
# async def add_images_to_amostra(
#     amostra_id: int,
#     images: List[UploadFile] = File(...),
#     db: Session = Depends(get_db),
# ):
#     db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
#     if not db_amostra:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")
#     filepaths = []
#     for image in images:
#         path = await save_upload_file(image, db_amostra.id_estudo)
#         filepaths.append(path)
#     try:
#         for path in filepaths:
#             img = amostra_crud.ImageAmostra(image_path=path, id_amostra=db_amostra.id)
#             db.add(img)
#         db.commit()
#         db.refresh(db_amostra)
#         return amostra_crud.get_amostra(db, db_amostra.id)
#     except Exception as e:
#         for path in filepaths:
#             remove_file(path)
#         raise HTTPException(status_code=500, detail=str(e))


# Endpoint para substituir uma imagem de uma amostra
# @router.put("/{amostra_id}/images/{image_id}", response_model=schemas.AmostraRead)
# async def replace_amostra_image(
#     amostra_id: int,
#     image_id: int,
#     new_image: UploadFile = File(...),
#     db: Session = Depends(get_db),
# ):
#     db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
#     if not db_amostra:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")
#     image = next((img for img in db_amostra.images if img.id == image_id), None)
#     if not image:
#         raise HTTPException(status_code=404, detail="Imagem não encontrada")
#     old_image_path = image.image_path
#     if not os.path.isabs(old_image_path):
#         old_image_path = os.path.join(os.path.abspath(os.getcwd()), old_image_path)
#     try:
#         new_image_path = await save_upload_file(new_image, db_amostra.id_estudo)
#         image.image_path = new_image_path
#         db.commit()
#         db.refresh(db_amostra)
#         if os.path.exists(old_image_path):
#             remove_file(old_image_path)
#         return amostra_crud.get_amostra(db, db_amostra.id)
#     except Exception as e:
#         if os.path.exists(new_image_path):
#             remove_file(new_image_path)
#         raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint para adicionar labels a uma amostra
@router.post("/{amostra_id}/labels")
def add_labels_to_amostra(
    amostra_id: int, 
    label_ids: list[int], 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):

    db_amostra = amostra.set_labels(db, amostra_id, label_ids)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")

    return amostra_crud.get_amostra(db, db_amostra.id)


@router.patch("/{amostra_id}/status", response_model=schemas.AmostraRead)
def update_amostra_status(
    amostra_id: int, 
    status_update: AmostraStatusUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_amostra = amostra.get_amostra_raw(db, amostra_id)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")

    db_amostra.status = status_update.status
    db.commit()
    db.refresh(db_amostra)

    return amostra.get_amostra(db, amostra_id)

# Endpoint para atualizar campos específicos de uma amostra
@router.patch("/{amostra_id}", response_model=schemas.AmostraRead)
def update_amostra(
    amostra_id: int, 
    field_update: AmostraUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    
    update_data = {k: v for k, v in field_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum campo válido para atualização")
    
    updated_amostra = amostra_crud.update_amostra(db, amostra_id, update_data)
    if not updated_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")
    
    return amostra_crud.get_amostra(db, amostra_id)