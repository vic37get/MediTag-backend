from sqlalchemy.orm import Session
from app.schemas import AmostraCreate, AmostraRead
from app.models import Amostra
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from pydantic import parse_obj_as


def get_amostras(db: Session, skip=0, limit=100):
    amostras = db.query(Amostra).offset(skip).limit(limit).all()
    # Adicionar labels e labels_ids para cada amostra
    result = []
    for amostra in amostras:
        amostra_dict = {
            "id": amostra.id,
            "id_estudo": amostra.id_estudo,
            "image_path": amostra.image_path,
            "report": amostra.report,
            "status": amostra.status,
            "labels": [label.name for label in amostra.labels],
            "labels_ids": [label.id for label in amostra.labels],
        }
        result.append(amostra_dict)
    return result


def set_labels(db: Session, amostra_id: int, label_ids: list[int]):
    """Adiciona labels a uma amostra usando o ID da amostra.

    Args:
        db: Sessão do banco de dados
        amostra_id: ID da amostra
        label_ids: Lista de IDs de labels para adicionar

    Returns:
        O objeto SQLAlchemy da amostra atualizado
    """
    from app.crud import label as label_crud

    # Obter o objeto SQLAlchemy diretamente
    amostra = get_amostra_raw(db, amostra_id)
    amostra.labels.clear()  # Limpar labels existentes
    if not amostra:
        return None

    for label_id in label_ids:
        db_label = label_crud.get_label_raw(db, label_id)
        if db_label and db_label not in amostra.labels:
            amostra.labels.append(db_label)

    db.commit()
    db.refresh(amostra)
    return amostra


def get_amostra(db: Session, amostra_id: int):
    amostra = db.query(Amostra).filter(Amostra.id == amostra_id).first()
    if amostra:
        # Criar um dicionário com os dados da amostra
        amostra_dict = {
            "id": amostra.id,
            "id_estudo": amostra.id_estudo,
            "image_path": amostra.image_path,
            "report": amostra.report,
            "status": amostra.status,
            "labels": [label.name for label in amostra.labels],
            "labels_ids": [label.id for label in amostra.labels],
        }
        return amostra_dict
    return None


def create_amostra(db: Session, amostra: AmostraCreate):
    try:
        db_amostra = Amostra(**amostra.model_dump())
        db.add(db_amostra)
        db.commit()
        db.refresh(db_amostra)
    except IntegrityError as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=400, detail="A amostra já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_amostra


def delete_amostra(db: Session, amostra_id: int):
    amostra = db.query(Amostra).filter(Amostra.id == amostra_id).first()
    if amostra:
        db.delete(amostra)
        db.commit()
        return True
    return False


def get_amostra_raw(db: Session, amostra_id: int):
    """Retorna o objeto SQLAlchemy Amostra diretamente, sem processamento."""
    return db.query(Amostra).filter(Amostra.id == amostra_id).first()
