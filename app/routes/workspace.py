from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import workspace
from app.crud.auth import get_current_user
from app.models import User
from app.database import get_db

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)


@router.get("", response_model=list[schemas.WorkspaceRead])
def read_workspaces(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para listar workspaces.
    """
    return workspace.get_workspaces(db, skip, limit)

@router.get("/{workspace_id}", response_model=schemas.WorkspaceRead)
def read_workspace(
    workspace_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint para obter um workspace específico pelo ID.
    """
    db_workspace = workspace.get_workspace(db, workspace_id)
    if db_workspace is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return db_workspace