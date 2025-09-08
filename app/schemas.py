from pydantic import BaseModel
from typing import List, Optional

class ImageBase(BaseModel):
    file_path: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    class Config:
        orm_mode = True


class LabelBase(BaseModel):
    label_type: str
    value: bool

class LabelCreate(LabelBase):
    pass

class Label(LabelBase):
    id: int
    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    text: str

class ItemCreate(ItemBase):
    images: List[str] = [] 
    pass

class Item(ItemBase):
    id: int
    images: List[Image] = []
    labels: List[Label] = []
    class Config:
        orm_mode = True


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    items: List[Item] = []
    class Config:
        orm_mode = True