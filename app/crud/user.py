from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate
from app.utils import hash_password
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip=0, limit=100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    try:
        db_user = User(
            username=user.username,
            email=user.email,
            role=user.role,
            hashed_password=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="O usuário já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False