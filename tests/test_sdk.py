from meditag_sdk import MediTagClient, Estudo, Amostra, Label, Tag

client = MediTagClient(database_url="sqlite:///db.sqlite3")

estudo = Estudo(
    name="Raio-X de Tórax Adulto",
    workspace="Radiologia Geral",
    question="O laudo está correto?",
    description="Estudo para classificação de tórax."
)

estudo.add_label(Label(name="Correto", color="#4CAF50"))
estudo.add_label(Label(name="Errado", color="#F44336"))
estudo.add_tag(Tag(name="adulto"))
estudo.add_tag(Tag(name="torax"))

amostra1 = Amostra(report="Laudo exemplo 1", imagens=["img1.jpg", "img2.jpg"])
amostra2 = Amostra(report="Laudo exemplo 2", imagens=["img3.jpg"])
estudo.add_amostra(amostra1)
estudo.add_amostra(amostra2)

client.push_estudo(estudo)