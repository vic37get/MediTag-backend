from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas
from app.crud import workspace
from app.database import get_db

router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"]
)

@router.post("", response_model=schemas.WorkspaceRead)
def create_workspace(workspace_in: schemas.WorkspaceCreate, db: Session = Depends(get_db)):
    return workspace.create_workspace(db, workspace_in)

@router.get("", response_model=list[schemas.WorkspaceRead])
def read_workspaces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return workspace.get_workspaces(db, skip, limit)

@router.get("/{workspace_id}", response_model=schemas.WorkspaceRead)
def read_workspace(workspace_id: int, db: Session = Depends(get_db)):
    db_workspace = workspace.get_workspace(db, workspace_id)
    if db_workspace is None:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return db_workspace

@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: int, db: Session = Depends(get_db)):
    success = workspace.delete_workspace(db, workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace não encontrado")
    return {"message": "Workspace deletado com sucesso"}