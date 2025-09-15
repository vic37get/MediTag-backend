from pydantic import BaseModel
from typing import Optional, List
from app.models import StatusEnum, RoleEnum


# Estudo
class EstudoBase(BaseModel):
    name: str
    workspace_id: int
    task: str
    question: str
    description: Optional[str] = None


class EstudoCreate(EstudoBase):
    pass


class EstudoRead(EstudoBase):
    id: int

    class Config:
        from_attributes = True


# Workspace
class WorkspaceBase(BaseModel):
    name: str
    description: str


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceRead(WorkspaceBase):
    id: int

    class Config:
        from_attributes = True


# Tag
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int

    class Config:
        from_attributes = True


# Label
class LabelBase(BaseModel):
    name: str
    color: str
    multi: bool = False
    id_estudo: int


class LabelCreate(LabelBase):
    pass


class LabelRead(LabelBase):
    id: int

    class Config:
        from_attributes = True


# Amostra
class AmostraBase(BaseModel):
    id_estudo: int
    image_path: str
    report: Optional[str] = None
    status: StatusEnum = StatusEnum.PENDING


class AmostraCreate(AmostraBase):
    pass


class AmostraRead(AmostraBase):
    id: int
    labels: List[str] = []  # Nomes das labels
    labels_ids: List[int] = []  # IDs das labels

    class Config:
        from_attributes = True


# User
class UserBase(BaseModel):
    username: str
    email: str
    role: RoleEnum


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


# AuditLog
class AuditLogBase(BaseModel):
    user_id: int


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    id: int

    class Config:
        from_attributes = True
