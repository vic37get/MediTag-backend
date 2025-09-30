from sqlalchemy import text
import os
import shutil
import requests
from sqlalchemy.orm import Session
from app.models import Workspace, Estudo, Amostra, StatusEnum, Label, Tag, Base
from sqlalchemy import create_engine
from app.database import SessionLocal, Base, engine

# URLs de imagens de raio-x (livres para uso educacional)
XRAY_IMAGES = [
    # Tórax adulto
    "https://s1.static.brasilescola.uol.com.br/be/conteudo/images/o-choque-dos-raios-x-com-corpo-gera-imagens-que-auxiliam-no-diagnostico-problemas-saude-59a6de7dc3eb0.jpg",
    "https://www.pneumoimagem.com.br/admin/exames/RX-NORMAL-3(1).jpg",
    # Mão adulto
    "https://www.radiografiacuritiba.com.br/wp-content/uploads/2025/06/Unimagem-RADIOGRAFIAS-DE-IDADE-OSSEA-1.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT4UCXnFgVPMUSSUGaAwMKpLFxJou68YkwfJA&s",
    # Tórax infantil
    "https://www.residenciapediatrica.com.br/Content//images/v7s1a06-fig02.jpg",
    "https://www.residenciapediatrica.com.br/Content//images/v7s1a06-fig04.jpg",
]


def baixar_imagem(url, save_path):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(resp.content)


def popular_mock():
    db: Session = SessionLocal()

    try:
        # Limpa banco e uploads (apenas para dev!)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        upload_dir = os.getenv("UPLOAD_DIR", "uploads")
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)

        # Workspaces
        ws1 = Workspace(
            name="Radiologia Geral",
            description="Workspace para exames gerais de raio-x",
        )
        ws2 = Workspace(
            name="Radiologia Pediátrica",
            description="Workspace para exames pediátricos",
        )
        db.add_all([ws1, ws2])
        db.commit()
        db.refresh(ws1)
        db.refresh(ws2)

        # Estudos
        estudo1 = Estudo(
            name="Raio-X de Tórax Adulto",
            workspace_id=ws1.id,
            task="classificacao",
            question="Considerando as imagens de raio-X de tórax (projeções frontal e lateral) apresentadas, você concorda que o laudo fornecido descreve corretamente os achados?",
            description="Estudo para classificação de achados em raio-x do tórax de adultos.",
        )
        estudo2 = Estudo(
            name="Raio-X de Mão Adulto",
            workspace_id=ws1.id,
            task="classificacao",
            question="Há fratura visível na mão?",
            description="Estudo para detecção de fraturas em mãos adultas.",
        )
        estudo3 = Estudo(
            name="Raio-X de Tórax Infantil",
            workspace_id=ws2.id,
            task="classificacao",
            question="Há sinais de bronquiolite?",
            description="Estudo para análise de bronquiolite em crianças.",
        )

        db.add_all([estudo1, estudo2, estudo3])
        db.commit()
        db.refresh(estudo1)
        db.refresh(estudo2)
        db.refresh(estudo3)

        # Tags para cada estudo

        tags_estudo = {
            estudo1.id: ["adulto", "torax"],
            estudo2.id: ["adulto", "mao"],
            estudo3.id: ["infantil", "torax"],
        }

        for estudo_id, tag_names in tags_estudo.items():
            for name in tag_names:
                tag = db.query(Tag).filter(Tag.name == name).first()
                if not tag:
                    tag = Tag(name=name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                estudo = db.query(Estudo).filter(Estudo.id == estudo_id).first()
                if tag not in estudo.tags:
                    estudo.tags.append(tag)
            db.commit()

        # Labels para cada estudo
        labels_estudo = {
            estudo1.id: [
                ("Correto", "#4CAF50"),
                ("Errado", "#F44336"),
                ("Neutro", "#9E9E9E"),
            ],
            estudo2.id: [
                ("Sem fratura", "#2196F3"),
                ("Fratura distal", "#E91E63"),
                ("Fratura proximal", "#9C27B0"),
                ("Deslocamento", "#FF9800"),
                ("Artefato", "#607D8B"),
            ],
            estudo3.id: [
                ("Normal", "#8BC34A"),
                ("Bronquiolite", "#FF5722"),
            ],
        }
        for estudo_id, labels in labels_estudo.items():
            for name, color in labels:
                label = Label(name=name, color=color, multi=False, id_estudo=estudo_id)
                db.add(label)
        db.commit()

        # Amostras e imagens
        estudo_imgs = {
            estudo1.id: XRAY_IMAGES[:2],  # Tórax adulto
            estudo2.id: XRAY_IMAGES[2:4],  # Mão adulto
            estudo3.id: XRAY_IMAGES[4:],  # Tórax infantil
        }
        for estudo in [estudo1, estudo2, estudo3]:
            estudo_dir = os.path.join(upload_dir, f"estudo_{estudo.id}")
            os.makedirs(estudo_dir, exist_ok=True)
            for i in range(1, 6):
                import random as rd, json

                laudos = json.load(open("laudos_mock.json", "r"))
                laudo = rd.choice(laudos)
                amostra = Amostra(
                    id_estudo=estudo.id,
                    report=laudo["report"],
                )
                db.add(amostra)
                db.commit()
                db.refresh(amostra)
                # Baixa e associa 2 imagens por amostra
                for idx, img_url in enumerate(estudo_imgs[estudo.id]):
                    img_path = os.path.join(
                        estudo_dir, f"amostra_{amostra.id}_img{idx+1}.jpg"
                    )
                    try:
                        baixar_imagem(img_url, img_path)
                    except Exception as e:
                        print(f"Erro ao baixar imagem: {img_url} -> {e}")
                        continue
                    # Cria registro da imagem
                    from app.models import ImageAmostra

                    db.add(ImageAmostra(image_path=img_path, id_amostra=amostra.id))
                db.commit()

        print("Mock inserido com sucesso!")
        print(f"Workspaces: {[ws1.name, ws2.name]}")
        print(f"Estudos: {[estudo1.name, estudo2.name, estudo3.name]}")
        print("Cada estudo possui 5 amostras, cada amostra possui 2 imagens reais.")
        print("Labels criadas com nomes e cores realistas para cada estudo.")

    finally:
        db.close()


if __name__ == "__main__":
    popular_mock()
