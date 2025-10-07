from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.models import User
from app.crud.auth import get_current_user
from app.routes.auth import create_access_token
from app.crud.sdk import get_user
from app.utils import verify_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/sdk",
    tags=["Sdk"]
)


@router.post("/authenticate")
def authenticate(
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
        "token_type": "bearer", 'user': user.username,
        'role': user.role
    }