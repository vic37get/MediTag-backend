from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.models import User
from app.crud.auth import get_current_user
from app.routes.auth import create_access_token
from app.crud.sdk import create_amostras, create_dataset, get_user
from app.utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/sdk",
    tags=["Sdk"]
)


@router.post("/authenticate")
def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    """
    Endpoint de teste para verificar autenticação via SDK.
    """
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    token_data = create_access_token(data={"sub": user.username})

    return {
        "access_token": token_data["access_token"],
        "expires_in": token_data["expires_in"],
        "token_type": "bearer", "user": user.username,
        "role": user.role
    }

@router.post("/configure-dataset")
def configure_dataset(
    dataset_info: schemas.DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo dataset.
    """
    db_estudo = create_dataset(db, dataset_info)  
    if not db_estudo:
        raise HTTPException(status_code=400, detail="Dataset já existe.")
    else:
        return {"message": "Dataset criado com sucesso.", "estudo_id": db_estudo.id}


@router.post("/log")
def log_dataset(
    dataset_info: schemas.DatasetLog,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra um novo log para um dataset existente.
    """
    success = create_amostras(db, dataset_info)

    if not success:
        raise HTTPException(status_code=400, detail="Erro ao registrar log.")
    else:
        return {"message": "Log registrado com sucesso."}