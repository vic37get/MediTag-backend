import requests

class MediTagClient:
    def __init__(self):
        self.api_url = None
        self.token = None
        self.user = None
        self.role = None

    def is_authenticated(self):
        return self.token is not None

client = MediTagClient()

def get_auth_headers():
    if not client.is_authenticated():
        raise RuntimeError("Você precisa se autenticar primeiro usando mt.init(...)")
    return {"Authorization": f"Bearer {client.token}"}


def init(api_url: str, user: str, password: str = None) -> dict | None:
    url = f"{api_url.rstrip('/')}/sdk/authenticate"
    try:
        response = requests.post(url, data={"username": user, "password": password}, timeout=10)
    except requests.ConnectionError:
        print(f"[ERRO] Não foi possível conectar ao servidor em {url}. Verifique se o backend está rodando e acessível.")
    except requests.Timeout:
        print(f"[ERRO] Timeout ao tentar conectar ao servidor em {url}.")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"[OK] Autenticado como '{user}'.")
            client.api_url = api_url.rstrip("/")
            client.token = data.get("access_token")
            client.user = data.get("user")
            client.role = data.get("role")
        except Exception:
            print("[ERRO] Erro ao decodificar resposta do servidor.")
            return None
    elif response.status_code == 401:
        print("[ERRO] Usuário ou senha inválidos.")
    elif response.status_code == 404:
        print(f"[ERRO] Endpoint '/sdk/authenticate' não encontrado em {api_url}.")
    else:
        print(f"[ERRO] Erro {response.status_code}: {response.text}")

class Settings:
    def __init__(self, label_schema: list[str] = None):
        self.label_schema = label_schema or []
        self.task = None

def configure_dataset(
        name: str,
        settings: Settings,
        workspace: str = None,
        question: str = None,
        description: str = None
        ) -> None:
    
    url = f"{client.api_url}/sdk/configure-dataset"
    headers = get_auth_headers()
    payload = {
        "name": name,
        "settings": settings.__dict__,
        "workspace": workspace,
        "question": question,
        "description": description
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Dataset configurado com sucesso!")
        return response.json()
    else:
        print(f"Erro ao configurar dataset: {response.status_code} - {response.text}")
        return None

def log(records: list, dataset_name: str, workspace: str = None) -> None:
    url = f"{client.api_url}/sdk/log"
    headers = get_auth_headers()
    payload = {
        "records": [record.__dict__ for record in records],
        "dataset_name": dataset_name,
        "workspace": workspace
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Logs registrados com sucesso!")
        return response.json()
    else:
        print(f"Erro ao registrar logs: {response.status_code} - {response.text}")
        return None

class ImageClassificationSettings(Settings):
    def __init__(self, labels: list[str], tags: list[str] = None):
        super().__init__(label_schema=list(set(labels)))
        self.task = "image_classification"
        self.tags = tags or []

class ImageClassificationRecord:
    def __init__(
            self,
            report: str,
            images: list[str],
            status: str = "pending",
            ):
        self.status = status
        self.report = report
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