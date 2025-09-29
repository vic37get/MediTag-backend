from sqlalchemy.orm import Session
from app.models import Estudo, StatusEnum
from app.schemas import EstudoCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
import os


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
        "amostras": [amostra.id for amostra in estudo.amostras],
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

import shutil
import pandas as pd
from PIL import Image
import io
import base64
from typing import Optional

def export_estudo_to_dataframe(db: Session, estudo_id: int) -> Optional[pd.DataFrame]:
    """
    Exporta um estudo para um pandas DataFrame com as colunas:
    - amostra_id: ID da amostra
    - imagem_path: Caminho para a imagem
    - imagem_pil: Imagem em formato PIL (serializada como base64)
    - achados: Labels/achados encontrados (separados por vírgula)
    - comentarios: Comentários feitos (text_report)
    - relatorio: Relatório/laudo (report)
    """
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if not estudo:
        return None
    
    data = []
    
    for amostra in estudo.amostras:
        # Para cada imagem da amostra, criar uma linha no DataFrame
        if amostra.images:
            for image_obj in amostra.images:
                # Carregar imagem com PIL
                pil_image = None
                pil_image_b64 = None
                try:
                    if os.path.exists(image_obj.image_path):
                        with Image.open(image_obj.image_path) as img:
                            # Converter para RGB se necessário
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Serializar imagem como base64 para armazenar no DataFrame
                            buffered = io.BytesIO()
                            img.save(buffered, format="JPEG")
                            pil_image_b64 = base64.b64encode(buffered.getvalue()).decode()
                            pil_image = img.copy()  # Fazer uma cópia para não perder a referência
                except Exception as e:
                    print(f"Erro ao carregar imagem {image_obj.image_path}: {e}")
                
                # Preparar achados (labels)
                achados = ", ".join([label.name for label in amostra.labels]) if amostra.labels else ""
                
                # Adicionar linha ao DataFrame
                data.append({
                    'amostra_id': amostra.id,
                    'imagem_path': image_obj.image_path,
                    'imagem_pil_b64': pil_image_b64,  # Imagem serializada
                    'imagem_pil': pil_image,  # Objeto PIL original (pode ser None se erro)
                    'achados': achados,
                    'comentarios': amostra.text_report or "",
                    'relatorio': amostra.report or "",
                    'status': amostra.status.value if hasattr(amostra.status, 'value') else str(amostra.status)
                })
        else:
            # Se não há imagens, ainda criar uma linha com os dados da amostra
            achados = ", ".join([label.name for label in amostra.labels]) if amostra.labels else ""
            data.append({
                'amostra_id': amostra.id,
                'imagem_path': "",
                'imagem_pil_b64': None,
                'imagem_pil': None,
                'achados': achados,
                'comentarios': amostra.text_report or "",
                'relatorio': amostra.report or "",
                'status': amostra.status.value if hasattr(amostra.status, 'value') else str(amostra.status)
            })
    
    if not data:
        # Retornar DataFrame vazio com as colunas corretas
        return pd.DataFrame(columns=[
            'amostra_id', 'imagem_path', 'imagem_pil_b64', 'imagem_pil', 
            'achados', 'comentarios', 'relatorio', 'status'
        ])
    
    return pd.DataFrame(data)

def delete_estudo(db: Session, estudo_id: int):
    estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
    if not estudo:
        return False

    estudo_dir = None
    for amostra in estudo.amostras:
        for image in amostra.images:
            if image.image_path:
                estudo_dir = os.path.dirname(image.image_path)
                break
        if estudo_dir:
            break

    if estudo_dir and os.path.exists(estudo_dir) and os.path.isdir(estudo_dir):
        shutil.rmtree(estudo_dir)

    db.delete(estudo)
    db.commit()
    return True