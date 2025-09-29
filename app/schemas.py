from pydantic import BaseModel
from typing import Optional, List
from app.models import StatusEnum, RoleEnum


# Estudo
class EstudoBase(BaseModel):
    name: str
    task: str
    question: str
    description: Optional[str] = None
    
class EstudoCreate(EstudoBase):
    workspace_id: int

class EstudoRead(EstudoBase):
    id: int
    workspace: str
    tags: List[str] = []
    labels: List[str] = []
    users: List[str] = []
    amostras_count: Optional[int] = 0
    amostras_validated: Optional[int] = 0

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
    report: str | None = None

class AmostraCreate(AmostraBase):
    id_estudo: int
    image_path: str | None = None

class AmostraRead(AmostraBase):
    id: int
    id_estudo: int
    images: List[int] = []
    status: str
    report: Optional[str]
    labels: List[str] = []
    labels_ids: List[int] = []
    text_report: Optional[str] = None

    class Config:
        from_attributes = True

class AmostraUpdate(BaseModel):
    report: Optional[str] = None
    text_report: Optional[str] = None
    status: Optional[StatusEnum] = None
    
    class Config:
        from_attributes = True

class AmostraStatusUpdate(AmostraBase):
    status: StatusEnum

class TextReportUpdate(AmostraBase):
    text_report: str


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