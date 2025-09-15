from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from app import schemas
from app.crud import amostra as amostra_crud
from app.utils import save_upload_file
from app.crud import amostra, label
from app.database import get_db
from app.models import Amostra, Label, StatusEnum
from app.utils import save_upload_file, remove_file
from fastapi.responses import FileResponse, Response, RedirectResponse
import os
import base64
import re
from app.schemas import AmostraStatusUpdate

router = APIRouter(prefix="/amostras", tags=["Amostras"])


@router.post("", response_model=schemas.AmostraRead)
async def create_amostra(
    id_estudo: int = Form(...),
    report: str | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filepath = await save_upload_file(image, id_estudo)
    try:
        amostra_in = schemas.AmostraCreate(id_estudo=id_estudo, report=report, image_path=filepath)
        db_amostra = amostra_crud.create_amostra(db, amostra_in)
        return db_amostra
    except Exception as e:
        remove_file(filepath)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{amostra_id}/image")
def get_amostra_image(amostra_id: int, db: Session = Depends(get_db)):
    db_amostra = amostra_crud.get_amostra_raw(db, amostra_id)
    if not db_amostra or not getattr(db_amostra, "image_path", None):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    image_path = db_amostra.image_path
    if not os.path.isabs(image_path):
        # se armazenou path relativo, torne absoluto baseado no cwd
        image_path = os.path.join(os.path.abspath(os.getcwd()), image_path)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Arquivo de imagem ausente no servidor")
    return FileResponse(image_path, media_type="application/octet-stream")


# @router.post("", response_model=schemas.AmostraRead)
# def create_amostra(amostra_in: schemas.AmostraCreate, db: Session = Depends(get_db)):
#     return amostra.create_amostra(db, amostra_in)


@router.get("", response_model=list[schemas.AmostraRead])
def read_amostras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return amostra.get_amostras(db, skip, limit)


# @router.get("/{amostra_id}/image")
# def get_amostra_image(amostra_id: int, db: Session = Depends(get_db)):
#     db_amostra = amostra.get_amostra_raw(db, amostra_id)
#     if not db_amostra:
#         raise HTTPException(status_code=404, detail="Amostra não encontrada")

#     image_path = db_amostra.image_path

#     # Caso 1: Verificar se é um caminho base64 inline
#     if image_path.startswith("data:"):
#         try:
#             # Extrair formato e dados da string base64
#             pattern = r"data:image/([a-zA-Z]+);base64,(.+)"
#             match = re.match(pattern, image_path)

#             if match:
#                 image_format, image_data = match.groups()
#                 decoded_image = base64.b64decode(image_data)
#                 return Response(
#                     content=decoded_image, media_type=f"image/{image_format}"
#                 )
#             else:
#                 raise HTTPException(
#                     status_code=400, detail="Formato de dados base64 inválido"
#                 )
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, detail=f"Erro ao processar imagem base64: {str(e)}"
#             )

#     # Caso 2: Verificar se é uma URL web
#     elif image_path.startswith(("http://", "https://")):
#         try:
#             # Opção 1: Redirecionar para a URL
#             return RedirectResponse(url=image_path)

#             # Opção 2 (alternativa): Buscar a imagem e servir do backend
#             # response = requests.get(image_path)
#             # if response.status_code == 200:
#             #     content_type = response.headers.get('content-type', 'image/jpeg')
#             #     return Response(content=response.content, media_type=content_type)
#             # else:
#             #     raise HTTPException(status_code=response.status_code, detail="Não foi possível acessar a imagem remota")
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, detail=f"Erro ao acessar imagem remota: {str(e)}"
#             )

#     # Caso 3: Caminho do sistema de arquivos local
#     elif os.path.exists(image_path):
#         return FileResponse(image_path)

#     # Nenhum dos casos acima
#     else:
#         raise HTTPException(
#             status_code=404, detail="Imagem não encontrada ou formato não suportado"
#         )


@router.post("/{amostra_id}/labels")
def add_labels_to_amostra(
    amostra_id: int, label_ids: list[int], db: Session = Depends(get_db)
):
    # Obter amostra bruta, adicionar labels e obter resultado
    db_amostra = amostra.set_labels(db, amostra_id, label_ids)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")

    # Formatar resposta
    return {
        "message": "Labels adicionados com sucesso",
        "amostra": {
            "id": db_amostra.id,
            "id_estudo": db_amostra.id_estudo,
            "status": db_amostra.status,
            "labels": [label.name for label in db_amostra.labels],
            "labels_ids": [label.id for label in db_amostra.labels],
        },
    }


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


@router.patch("/{amostra_id}/status", response_model=schemas.AmostraRead)
def update_amostra_status(
    amostra_id: int, status_update: AmostraStatusUpdate, db: Session = Depends(get_db)
):
    db_amostra = amostra.get_amostra_raw(db, amostra_id)
    if not db_amostra:
        raise HTTPException(status_code=404, detail="Amostra não encontrada")

    db_amostra.status = status_update.status
    db.commit()
    db.refresh(db_amostra)

    return amostra.get_amostra(db, amostra_id)