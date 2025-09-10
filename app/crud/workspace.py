from sqlalchemy.orm import Session
from app.models import Workspace
from app.schemas import WorkspaceCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException


def get_workspace(db: Session, workspace_id: int):
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()

def get_workspaces(db: Session, skip=0, limit=100):
    return db.query(Workspace).offset(skip).limit(limit).all()

def create_workspace(db: Session, workspace: WorkspaceCreate):
    try:
        db_workspace = Workspace(
            name=workspace.name,
            description=workspace.description
        )
        db.add(db_workspace)
        db.commit()
        db.refresh(db_workspace)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="O Workspace já existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db_workspace

def delete_workspace(db: Session, workspace_id: int):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if workspace:
        db.delete(workspace)
        db.commit()
        return True
    return False