from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)

    items = relationship("Item", back_populates="dataset")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    
    dataset = relationship("Dataset", back_populates="items")
    images = relationship("Image", back_populates="item")
    labels = relationship("Label", back_populates="item")


class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True)
    item_id = Column(Integer, ForeignKey("items.id"))

    item = relationship("Item", back_populates="images")


class Label(Base):
    __tablename__ = "labels"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    label_type = Column(String)  # "correto", "errado"
    value = Column(Boolean, default=True)  # True/False 

    item = relationship("Item", back_populates="labels")