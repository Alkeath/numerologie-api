from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from bs4 import NavigableString
import psycopg2
import os
import uuid
import shutil
import asyncio
import traceback

app = FastAPI()


@app.post("/injectionTextesDansTemplateHTML")
async def injection_textes(request: Request, data: dict):

    # 📁 Chemins
    TEMPLATE_HTML_PATH = "templates/template_temporaire1/index.html"
    TEMPLATE_DIR = "templates/template_temporaire1"
    TEMP_HTML_DIR = "html_genere"

    # 🧾 Lecture du template
    try:
        with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Template HTML non trouvé.")

    # 🧹 Suppression du contenu des balises avec un ID
    for el in soup.find_all(attrs={"id": True}):
        el.clear()

    # 🆔 Création d’un identifiant unique
    fichier_id = str(uuid.uuid4())
    temp_dir_path = os.path.join(TEMP_HTML_DIR, fichier_id)
    os.makedirs(temp_dir_path, exist_ok=True)

    # 📄 Copie des fichiers nécessaires (CSS, fonts, etc.)
    for item in os.listdir(TEMPLATE_DIR):
        s = os.path.join(TEMPLATE_DIR, item)
        d = os.path.join(temp_dir_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        elif item != "index.html":  # le HTML sera réécrit après
            shutil.copy2(s, d)

    # 💾 Sauvegarde du fichier HTML modifié
    chemin_fichier_html = os.path.join(temp_dir_path, "index.html")
    with open(chemin_fichier_html, "w", encoding="utf-8") as f:
        f.write(str(soup))

    # 🌐 Génération de l’URL du fichier temporaire
    base_url = str(request.base_url).rstrip("/")
    url_html = f"{base_url}/html_temp/{fichier_id}/index.html"
    print(f"🧹 HTML vidé généré : {url_html}", flush=True)

    # ⏳ Suppression automatique après 300 secondes
    async def supprimer_dossier():
        await asyncio.sleep(300)
        try:
            shutil.rmtree(temp_dir_path)
            print(f"🗑️ Dossier temporaire supprimé : {temp_dir_path}", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur lors de la suppression du dossier temporaire : {e}", flush=True)

    asyncio.create_task(supprimer_dossier())

    return {"url_html": url_html}
