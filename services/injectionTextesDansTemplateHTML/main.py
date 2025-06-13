from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import psycopg2
import os
import uuid
import shutil
import asyncio
import traceback

app = FastAPI()

# 🔓 Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Chemins
TEMPLATE_HTML_PATH = "templates/template_temporaire1/index.html"
TEMPLATE_DIR = "templates/template_temporaire1"
TEMP_HTML_DIR = "html_genere"

# 📦 Crée le dossier temporaire s’il n’existe pas
os.makedirs(TEMP_HTML_DIR, exist_ok=True)

# 📦 Sert les fichiers HTML temporaires avec assets
app.mount("/html_temp", StaticFiles(directory=TEMP_HTML_DIR, html=True), name="html_temp")

# 🔐 Connexion PostgreSQL (conservée au cas où tu la réutilises plus tard)
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

# 🧠 Route principale
@app.post("/injectionTextesDansTemplateHTML")
async def injecter_textes_depuis_bdd(request: Request):
    try:
        data = await request.json()

        genre = data.get("Genre_Formulaire", "")
        nb_cdv = str(data.get("NbCdV_Final", "")).zfill(2)
        nb_exp = str(data.get("NbExp_Final", "")).zfill(2)
        nb_rea = str(data.get("NbRea_Final", "")).zfill(2)
        nb_ame = str(data.get("NbAme_Final", "")).zfill(2)

        print(f"🔢 Nombres reçus – CdV: {nb_cdv}, Exp: {nb_exp}, Rea: {nb_rea}, Ame: {nb_ame}, Genre: {genre}")

        try:
            with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Template HTML non trouvé.")

        # 🧹 Effacer uniquement les contenus des éléments ayant un ID
        for el in soup.find_all(attrs={"id": True}):
            try:
                el.clear()
            except Exception as e:
                print(f"⚠️ Problème en effaçant le contenu de {el.get('id', '[aucun ID]')} : {e}", flush=True)
                continue

        fichier_id = str(uuid.uuid4())
        base_url = str(request.base_url).rstrip("/")
        url_html = f"{base_url}/html_temp/{fichier_id}/index.html"

        print(f"➡️ URL du fichier temporaire : {url_html}", flush=True)

        dossier_temporaire = os.path.join(TEMP_HTML_DIR, fichier_id)
        os.makedirs(dossier_temporaire, exist_ok=True)
        shutil.copytree(TEMPLATE_DIR, dossier_temporaire, dirs_exist_ok=True)

        chemin_index = os.path.join(dossier_temporaire, "index.html")
        with open(chemin_index, "w", encoding="utf-8") as f:
            f.write(str(soup))

        asyncio.create_task(supprimer_fichier_apres_delai(dossier_temporaire, delay=300))

        print("➡️ HTML vidé généré :", url_html, flush=True)
        return JSONResponse(content={"url_html": url_html})

    except Exception as e:
        print("❌ Erreur dans injecter_textes_depuis_bdd()")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

# 🧹 Supprime le dossier temporaire après un délai
async def supprimer_fichier_apres_delai(path, delay=300):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 Dossier temporaire supprimé : {path}")
