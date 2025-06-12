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
    allow_origins=["*"],  # à restreindre si besoin
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

# 🔐 Connexion PostgreSQL via variables d’environnement
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

# 🔍 Récupération du contenu à injecter
def get_cell_value(conn, table, column, row_key):
    with conn.cursor() as cur:
        try:
            query = f'SELECT "{column}" FROM "{table}" WHERE cle = %s'
            cur.execute(query, (row_key,))
            result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Erreur SQL : {e}")
            return None

# 🧠 Route principale
@app.post("/injectionTextesDansTemplateHTML")
async def injecter_textes_depuis_bdd(request: Request):
    try:
        data = await request.json()

        genre = data.get("Genre", "")
        nb_cdv = str(data.get("NbCdV_Final", "")).zfill(2)
        nb_exp = str(data.get("NbExp_Final", "")).zfill(2)
        nb_rea = str(data.get("NbRea_Final", "")).zfill(2)
        nb_ame = str(data.get("NbAme_Final", "")).zfill(2)

        # 📋 Affiche les nombres dans les logs
        print(f"🔢 Nombres reçus – CdV: {nb_cdv}, Exp: {nb_exp}, Rea: {nb_rea}, Ame: {nb_ame}")

        # Lecture du template HTML
        try:
            with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Template HTML non trouvé.")

        conn = get_db_connection()

        # Injection des textes dans les éléments par ID
        for el in soup.find_all(attrs={"id": True}):
            id_val = el["id"]
            try:
                table, colonne, ligne = id_val.split("_", 2)

                colonne = colonne.replace("Genre", genre)
                ligne = (ligne
                         .replace("CdVX", f"CdV{nb_cdv}")
                         .replace("ExpY", f"Exp{nb_exp}")
                         .replace("ReaZ", f"Rea{nb_rea}")
                         .replace("AmeQ", f"Ame{nb_ame}"))

                texte = get_cell_value(conn, table, colonne, ligne)
                if texte:
                    el.clear()
                    el.append(texte)
                    print(f"✅ Injection réussie pour ID={id_val} → table={table}, colonne={colonne}, ligne={ligne}")
                else:
                    print(f"⚠️ Aucun contenu trouvé pour ID={id_val} → table={table}, colonne={colonne}, ligne={ligne}")

            except Exception as e:
                print(f"⚠️ Problème avec l’ID {id_val} : {e}")
                continue

        conn.close()

        # 💾 Crée un dossier temporaire unique pour cette version HTML
        fichier_id = str(uuid.uuid4())
        dossier_temporaire = os.path.join(TEMP_HTML_DIR, fichier_id)
        os.makedirs(dossier_temporaire, exist_ok=True)

        # Copie tous les fichiers et sous-dossiers du template original
        shutil.copytree(TEMPLATE_DIR, dossier_temporaire, dirs_exist_ok=True)

        # Remplace le contenu du index.html par la version injectée
        chemin_index = os.path.join(dossier_temporaire, "index.html")
        with open(chemin_index, "w", encoding="utf-8") as f:
            f.write(str(soup))

        # ⏳ Suppression planifiée
        asyncio.create_task(supprimer_fichier_apres_delai(dossier_temporaire, delay=60))

        base_url = str(request.base_url).rstrip("/")
        url_html = f"{base_url}/html_temp/{fichier_id}/index.html"

        print(f"✅ HTML généré : {url_html}")  # 👈 Pour affichage console Railway

        return JSONResponse(content={"url_html": url_html})

    except Exception as e:
        print("❌ Erreur dans injecter_textes_depuis_bdd()")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

# 🧹 Supprime le dossier temporaire après un délai
async def supprimer_fichier_apres_delai(path, delay=60):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 Dossier temporaire supprimé : {path}")
