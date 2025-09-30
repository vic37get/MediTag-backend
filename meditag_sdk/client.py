import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.models import Workspace, Estudo as EstudoDB, Label as LabelDB, Tag as TagDB, Amostra as AmostraDB, ImageAmostra

class MediTagClient:
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def push_estudo(self, estudo):
        session = self.Session()
        # Workspace
        ws = session.query(Workspace).filter_by(name=estudo.workspace).first()
        if not ws:
            ws = Workspace(name=estudo.workspace, description=estudo.workspace)
            session.add(ws)
            session.commit()
            session.refresh(ws)
        # Estudo
        estudo_db = EstudoDB(
            name=estudo.name,
            workspace_id=ws.id,
            task="classificacao",
            question=estudo.question,
            description=estudo.description,
        )
        session.add(estudo_db)
        session.commit()
        session.refresh(estudo_db)
        # Labels
        for label in estudo.labels:
            lbl = LabelDB(
                name=label.name,
                color=label.color,
                multi=label.multi,
                id_estudo=estudo_db.id,
            )
            session.add(lbl)
        session.commit()
        # Tags
        for tag in estudo.tags:
            tg = session.query(TagDB).filter_by(name=tag.name).first()
            if not tg:
                tg = TagDB(name=tag.name)
                session.add(tg)
                session.commit()
                session.refresh(tg)
            estudo_db.tags.append(tg)
        session.commit()
        # Amostras
        for amostra in estudo.amostras:
            amostra_db = AmostraDB(
                id_estudo=estudo_db.id,
                report=amostra.report,
            )
            session.add(amostra_db)
            session.commit()
            session.refresh(amostra_db)
            for img_path in amostra.imagens:
                img = ImageAmostra(image_path=img_path, id_amostra=amostra_db.id)
                session.add(img)
            session.commit()
        print(f"Estudo '{estudo.name}' inserido com sucesso.")
        session.close()