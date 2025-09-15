from sqlalchemy.orm import Session
from app.models import Estudo, StatusEnum
from app.schemas import EstudoCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_estudos(db: Session, skip=0, limit=100):
    estudos = db.query(Estudo).offset(skip).limit(limit).all()
    result = []
    for estudo in estudos:
        amostras_validated = len([amostra for amostra in estudo.amostras if amostra.status == StatusEnum.VALIDATED])
        estudo_dict = {
            "id": estudo.id,
            "name": estudo.name,
            "workspace_id": estudo.workspace_id,
            "workspace": estudo.workspace.name,
            "task": estudo.task,
            "question": estudo.question,
            "description": estudo.description,
            "tags": [tag.name for tag in estudo.tags],
            "labels": [label.name for label in estudo.labels],
            "users": [user.username for user in estudo.users],
            "amostras_count": len(estudo.amostras),
            "amostras_validated": amostras_validated
        }
        result.append(estudo_dict)
    return result

def get_estudos_raw(db: Session, skip: int = 0, limit: int = 100):
    """
        Retorna o objeto SQLAlchemy Amostra diretamente, sem processamento.
    """
    return db.query(Estudo).offset(skip).limit(limit).all()

def get_estudo(db: Session, estudo_id: int):
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    amostras_validated = len([amostra for amostra in estudo.amostras if amostra.status == StatusEnum.VALIDATED])

    return {
        "id": estudo.id,
        "name": estudo.name,
        "workspace_id": estudo.workspace_id,
        "workspace": estudo.workspace.name,
        "task": estudo.task,
        "question": estudo.question,
        "description": estudo.description,
        "tags": [tag.name for tag in estudo.tags],
        "labels": [label.name for label in estudo.labels],
        "users": [user.username for user in estudo.users],
        "amostras_count": len(estudo.amostras),
        "amostras_validated": amostras_validated
    }

def create_estudo(db: Session, estudo: EstudoCreate):
    try:
        db_estudo = Estudo(**estudo.model_dump())
        db.add(db_estudo)
        db.commit()
        db.refresh(db_estudo)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="O estudo já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_estudo

def delete_estudo(db: Session, estudo_id: int):
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if estudo:
        db.delete(estudo)
        db.commit()
        return True
    return False