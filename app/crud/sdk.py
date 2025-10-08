from sqlalchemy.orm import Session
from app.crud import estudo
from app import schemas
from app.models import Estudo, User, RoleEnum, Workspace, Label, Tag, Amostra, ImageAmostra
from sqlalchemy.exc import IntegrityError

def get_user(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).filter(User.role == RoleEnum.ADMIN).first()

def create_dataset(db: Session, dataset: schemas.DatasetCreate):
    try:
        workspace_id = db.query(Workspace.id).filter(Workspace.name == dataset.workspace).first()
        if not workspace_id:
            new_workspace = Workspace(name=dataset.workspace, description=dataset.workspace)
            db.add(new_workspace)
            db.commit()
            db.refresh(new_workspace)
            workspace_id = new_workspace.id
        else:
            workspace_id = workspace_id[0]
        
        db_estudo = Estudo(
            name = dataset.name,
            task = dataset.settings.get("task", ""),
            workspace_id = workspace_id,
            question = dataset.question,
            description = dataset.description
        )
        db.add(db_estudo)
        db.commit()
        db.refresh(db_estudo)

        for label in dataset.settings.get("label_schema", []):
            existing_label = db.query(Label).filter(Label.name == label).first()
            if existing_label:
                db_estudo.labels.append(existing_label)
            else:
                new_label = Label(id_estudo=db_estudo.id, name=label, color="#008EED", multi=False)
                db.add(new_label)
                db_estudo.labels.append(new_label)

        for tag in dataset.settings.get("tags", []):
            existing_tag = db.query(Tag).filter(Tag.name == tag).first()
            if not existing_tag:
                db_tag = Tag(name=tag)  
                db.add(db_tag)
            else:
                db_tag = existing_tag
            db_estudo.tags.append(db_tag)
        db.commit()
    except IntegrityError:
        db.rollback()
        print("Dataset já existe.")
        return None
    except Exception as e:
        db.rollback()
        print("Erro ao criar dataset:", e)
        return None
    return db_estudo

def create_amostras(db: Session, dataset_info: schemas.DatasetLog) -> bool:
    try:
        estudo_instance = db.query(Estudo).filter(Estudo.name == dataset_info.dataset_name).first()
        if not estudo_instance:
            print("Estudo não encontrado.")
            return False

        for record in dataset_info.records:
            new_amostra = Amostra(
                id_estudo=estudo_instance.id,
                report=record.get("report", "")
            )
            db.add(new_amostra)
            db.flush()

            for img_path in record.get("images", []):
                new_image = ImageAmostra(image_path=img_path, id_amostra=new_amostra.id)
                db.add(new_image)
        db.commit()
    except Exception as e:
        db.rollback()
        print("Erro ao criar amostras:", e)
        return False
    return True