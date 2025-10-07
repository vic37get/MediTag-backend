import requests


import requests

def init(api_url: str, user: str, password: str = None) -> dict | None:
    url = f"{api_url.rstrip('/')}/sdk/authenticate"
    try:
        response = requests.post(url, data={"username": user, "password": password}, timeout=10)
    except requests.ConnectionError:
        print(f"[ERRO] Não foi possível conectar ao servidor em {url}. Verifique se o backend está rodando e acessível.")
        return None
    except requests.Timeout:
        print(f"[ERRO] Timeout ao tentar conectar ao servidor em {url}.")
        return None
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"[OK] Autenticado como '{user}'.")
            return data
        except Exception:
            print("[ERRO] Erro ao decodificar resposta do servidor.")
            return None
    elif response.status_code == 401:
        print("[ERRO] Usuário ou senha inválidos.")
    elif response.status_code == 404:
        print(f"[ERRO] Endpoint '/sdk/authenticate' não encontrado em {api_url}.")
    else:
        print(f"[ERRO] Erro {response.status_code}: {response.text}")
    return None

class Settings:
    def __init__(self, label_schema: list[str] = None):
        self.label_schema = label_schema or []
        self.task = None

def configure_dataset(
        name: str,
        settings: Settings,
        workspace: str = None,
        tags: list[str] = None,
        ) -> None:
    ...

def log(records: list, dataset_name: str, workspace: str = None, tags: list[str] = None) -> None:
    ...

class ImageClassificationSettings(Settings):
    def __init__(self, labels: list[str]):
        super().__init__(label_schema=list(set(labels)))
        self.task = "image_classification"

class ImageClassificationRecord:
    def __init__(
            self,
            text_report: str,
            images: list[str],
            status: str = "pending",
            ):
        self.status = status
        self.text_report = text_report
        self.images = images if images is not None else []


    # def push_estudo(self, estudo):
    #     session = self._get_session()
    #     # Workspace
    #     ws = session.query(Workspace).filter_by(name=estudo.workspace).first()
    #     if not ws:
    #         ws = Workspace(name=estudo.workspace, description=estudo.workspace)
    #         session.add(ws)
    #         session.commit()
    #         session.refresh(ws)
    #     # Estudo
    #     estudo_db = EstudoDB(
    #         name=estudo.name,
    #         workspace_id=ws.id,
    #         task="classificacao",
    #         question=estudo.question,
    #         description=estudo.description,
    #     )
    #     session.add(estudo_db)
    #     session.commit()
    #     session.refresh(estudo_db)
    #     # Labels
    #     for label in estudo.labels:
    #         lbl = LabelDB(
    #             name=label.name,
    #             color=label.color,
    #             multi=label.multi,
    #             id_estudo=estudo_db.id,
    #         )
    #         session.add(lbl)
    #     session.commit()
    #     # Tags
    #     for tag in estudo.tags:
    #         tg = session.query(TagDB).filter_by(name=tag.name).first()
    #         if not tg:
    #             tg = TagDB(name=tag.name)
    #             session.add(tg)
    #             session.commit()
    #             session.refresh(tg)
    #         estudo_db.tags.append(tg)
    #     session.commit()
    #     # Amostras
    #     for amostra in estudo.amostras:
    #         amostra_db = AmostraDB(
    #             id_estudo=estudo_db.id,
    #             report=amostra.report,
    #         )
    #         session.add(amostra_db)
    #         session.commit()
    #         session.refresh(amostra_db)
    #         for img_path in amostra.imagens:
    #             img = ImageAmostra(image_path=img_path, id_amostra=amostra_db.id)
    #             session.add(img)
    #         session.commit()
    #     print(f"Estudo '{estudo.name}' inserido com sucesso.")
    #     session.close()