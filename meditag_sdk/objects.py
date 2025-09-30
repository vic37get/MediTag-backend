class Label:
    def __init__(self, name, color="#2196F3", multi=False):
        self.name = name
        self.color = color
        self.multi = multi

class Tag:
    def __init__(self, name):
        self.name = name

class Amostra:
    def __init__(self, report, imagens=None):
        self.report = report
        self.imagens = imagens or []

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