from sqlalchemy.orm import Session
from app.models import User, RoleEnum

def get_user(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).filter(User.role == RoleEnum.ADMIN).first()