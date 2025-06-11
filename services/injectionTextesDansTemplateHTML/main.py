from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from bs4 import BeautifulSoup
import psycopg2
import os
import uuid
import shutil
import asyncio
import traceback

app = FastAPI()

# 📁 Chemins
TEMPLATE_HTML_PATH = "templates/template_temporaire1/index.html"
TEMPLATE_DIR = "templates/template_temporaire1"
TEMP_HTML_DIR = "html_genere"

# 📦 Crée le dossier temporaire s’il n’existe pas
os.makedirs(TEMP_HTML_DIR, exist_ok=True)

# 📦 Sert les fichiers temporaires
app.mount("/html_temp", StaticFiles(directory=TEMP_HTML_DIR), name="html_temp")

# 🔐 Connexion PostgreSQL via variables d’environnement
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

# 🔍 Fonction de récupération de texte
def get_cell_value(conn, table, column, row_key):
    with conn.cursor() as cur:
        try:
            query = f"SELECT {column} FROM {table} WHERE cle = %s"
            cur.execute(query, (row_key,))
            result = cur.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"❌ Erreur SQL : {e}")
            return None

# 🧠 Route principale d’injection
@app.post("/injectionTextesDansTemplateHTML")
async def injecter_textes_depuis_bdd(request: Request):
    try:
        data = await request.json()

        genre = data.get("Genre", "")
        nb_cdv = str(data.get("NbCdV_Final", "")).zfill(2)
        nb_exp = str(data.get("NbExp_Final", "")).zfill(2)
        nb_rea = str(data.get("NbRea_Final", "")).zfill(2)
        nb_ame = str(data.get("NbAme_Final", "")).zfill(2)

        try:
            with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Template HTML non trouvé.")

        conn = get_db_connection()

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
            except Exception as e:
                print(f"⚠️ Problème avec l’ID {id_val} : {e}")
                continue

        conn.close()

        # 💾 Création fichier temporaire
        fichier_id = str(uuid.uuid4())
        fichier_nom = f"{fichier_id}.html"
        chemin_complet = os.path.join(TEMP_HTML_DIR, fichier_nom)

        with open(chemin_complet, "w", encoding="utf-8") as f:
            f.write(str(soup))

        # ⏳ Suppression planifiée
        asyncio.create_task(supprimer_fichier_apres_delai(chemin_complet, delay=60))

        base_url = str(request.base_url).rstrip("/")
        return JSONResponse(content={"url_html": f"{base_url}/html_temp/{fichier_nom}"})
    
    except Exception as e:
        print("❌ Erreur dans injecter_textes_depuis_bdd()")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})


# 🧹 Suppression automatique
async def supprimer_fichier_apres_delai(path, delay=60):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)
        print(f"🧹 Fichier temporaire supprimé : {path}")

