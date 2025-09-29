from sqlalchemy.orm import Session
from app.schemas import AmostraCreate, AmostraRead
from app.models import Amostra, ImageAmostra
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.crud import label as label_crud


def get_amostras(estudo_id, db: Session, skip=0, limit=100):
    if estudo_id:
        amostras = db.query(Amostra).filter(Amostra.id_estudo == estudo_id).offset(skip).limit(limit).all()
    else:
        amostras = db.query(Amostra).offset(skip).limit(limit).all()
    result = []
    for amostra in amostras:
        amostra_dict = {
            "id": amostra.id,
            "id_estudo": amostra.id_estudo,
            "images": [img.id for img in amostra.images],
            "report": amostra.report,
            "text_report": amostra.text_report,
            "status": amostra.status,
            "labels": [label.name for label in amostra.labels],
            "labels_ids": [label.id for label in amostra.labels],
        }
        result.append(amostra_dict)
    return result

def set_text_report(db: Session, amostra_id: int, text_report: str):
    amostra = get_amostra_raw(db, amostra_id)
    if not amostra:
        return None
    amostra.text_report = text_report
    db.commit()
    db.refresh(amostra)
    return amostra


def set_labels(db: Session, amostra_id: int, label_ids: list[int]):
    """Adiciona labels a uma amostra usando o ID da amostra.

    Args:
        db: Sessão do banco de dados
        amostra_id: ID da amostra
        label_ids: Lista de IDs de labels para adicionar

    Returns:
        O objeto SQLAlchemy da amostra atualizado
    """

    amostra = get_amostra_raw(db, amostra_id)
    amostra.labels.clear() 
    if not amostra:
        return None

    for label_id in label_ids:
        db_label = label_crud.get_label_raw(db, label_id)
        if db_label and db_label not in amostra.labels:
            amostra.labels.append(db_label)

    db.commit()
    db.refresh(amostra)
    return amostra

def create_amostra(db: Session, amostra: AmostraCreate, image_paths: list[str]):
    try:
        db_amostra = Amostra(
            id_estudo=amostra.id_estudo,
            report=amostra.report,
        )
        db.add(db_amostra)
        db.commit()
        db.refresh(db_amostra)
        for path in image_paths:
            img = ImageAmostra(image_path=path, id_amostra=db_amostra.id)
            db.add(img)
        db.commit()
        db.refresh(db_amostra)
        return db_amostra
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Amostra já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def update_amostra(db: Session, amostra_id: int, update_data: dict):
    """Atualiza os campos de uma amostra.
    
    Args:
        db: Sessão do banco de dados
        amostra_id: ID da amostra a ser atualizada
        update_data: Dicionário com os campos a serem atualizados
        
    Returns:
        O objeto amostra atualizado, ou None se não encontrar
    """
    amostra = get_amostra_raw(db, amostra_id)
    if not amostra:
        return None
    
    for field, value in update_data.items():
        if hasattr(amostra, field):
            setattr(amostra, field, value)
    
    db.commit()
    db.refresh(amostra)
    return amostra

def get_amostra(db: Session, amostra_id: int):
    amostra = db.query(Amostra).filter(Amostra.id == amostra_id).first()
    if amostra:
        return {
            "id": amostra.id,
            "id_estudo": amostra.id_estudo,
            "report": amostra.report,
            "status": amostra.status.value if hasattr(amostra.status, "value") else amostra.status,
            "images": [img.id for img in amostra.images],
        }
    return None


def reset_amostra(db: Session, amostra_id: int):
    amostra = db.query(Amostra).filter(Amostra.id == amostra_id).first()
    if amostra:
        amostra.status = "PENDING"
        amostra.labels.clear()
        amostra.label_ids = []
        amostra.text_report = None
        db.commit()
        db.refresh(amostra)
        return True
    return False


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