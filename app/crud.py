from sqlalchemy.orm import Session
from . import models, schemas

def create_dataset(db: Session, dataset: schemas.DatasetCreate):
    db_dataset = models.Dataset(name=dataset.name, description=dataset.description)
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def create_item(db: Session, item: schemas.ItemCreate, dataset_id: int):
    db_item = models.Item(text=item.text, dataset_id=dataset_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_image(db: Session, file_path: str, item_id: int):
    db_image = models.Image(file_path=file_path, item_id=item_id)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def create_label(db: Session, item_id: int, label: schemas.LabelCreate):
    db_label = models.Label(item_id=item_id, label_type=label.label_type, value=label.value)
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label
