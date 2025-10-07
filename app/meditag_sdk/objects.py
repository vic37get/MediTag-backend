class Label:
    def __init__(self, name, color="green", multi=False):
        self.name = name
        self.color = color
        self.multi = multi

class Tag:
    def __init__(self, name: str):
        self.name = name

class Amostra:
    def __init__(self, report: str, imagens: list[str] = None):
        self.report = report
        self.imagens = imagens or []

class Workspace:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.estudos = []

class Estudo:
    def __init__(self, name, workspace, question, description=""):
        self.name = name
        self.workspace = workspace
        self.question = question
        self.description = description
        self.labels = []
        self.tags = []
        self.amostras = []

    def add_label(self, label):
        self.labels.append(label)

    def add_tag(self, tag):
        self.tags.append(tag)

    def add_amostra(self, amostra):
        self.amostras.append(amostra)