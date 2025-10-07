from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm
from app.crud.user import get_user_by_username, create_user
from app.utils import verify_password
from app.schemas import UserCreate, UserRead
from app.database import get_db
from dotenv import load_dotenv
import os
load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
    ):
    """
    Endpoint para registrar um novo usuário.
    """
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Usuário já registrado.")
    new_user = create_user(db, user)
    return new_user

def create_access_token(
        data: dict, 
        expires_delta: timedelta | None = None
        ):
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
