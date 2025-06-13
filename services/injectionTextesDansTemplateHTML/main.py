from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
import uuid

app = FastAPI()

TEMPLATE_HTML_PATH = "app/templates/template_temporaire1/index.html"
DOSSIER_HTML_TEMP = "app/templates/html_temp"

@app.post("/vider_zones_id")
async def vider_zones_id(request: Request):
    # Lecture du template
    with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Vide chaque zone avec un ID
    for el in soup.find_all(attrs={"id": True}):
        el.clear()

    # Création fichier temporaire
    fichier_id = str(uuid.uuid4())
    dossier_temp = os.path.join(DOSSIER_HTML_TEMP, fichier_id)
    os.makedirs(dossier_temp, exist_ok=True)

    chemin_fichier = os.path.join(dossier_temp, "index.html")
    with open(chemin_fichier, "w", encoding="utf-8") as f:
        f.write(str(soup))

    base_url = str(request.base_url).rstrip("/")
    url_html = f"{base_url}/html_temp/{fichier_id}/index.html"

    return {"url_html": url_html}
