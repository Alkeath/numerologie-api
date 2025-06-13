from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup, NavigableString
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
os.makedirs(TEMP_HTML_DIR, exist_ok=True)

app.mount("/html_temp", StaticFiles(directory=TEMP_HTML_DIR, html=True), name="html_temp")

# 🔐 Connexion PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

# 🔍 Récupération du texte depuis la BDD
def get_cell_value(conn, table, column, row_key):
    with conn.cursor() as cur:
        try:
            query = f'SELECT "{column}" FROM "{table}" WHERE cle = %s'
            cur.execute(query, (row_key,))
            result = cur.fetchone()
            return str(result[0]) if result and result[0] is not None else None
        except Exception as e:
            print(f"❌ Erreur SQL : {e} → table={table}, colonne={column}, ligne={row_key}")
            return None

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

        with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

        conn = get_db_connection()

        # 🧹 Efface les contenus entre chaque paire de balises avec id+class
        balises_cibles = soup.find_all(lambda tag: tag.has_attr("id"))
        
        for i in range(len(balises_cibles) - 1):
            debut = balises_cibles[i]
            fin = balises_cibles[i + 1]
        
            current = debut.next_sibling
            while current and current != fin:
                next_node = current.next_sibling
                if getattr(current, "name", None) in ["span", "br"] or isinstance(current, NavigableString):
                    current.extract()
                current = next_node
        
            while debut.contents:
                debut.contents[0].extract()
        
            print(f"🧹 Zone vidée entre ID={debut['id']} et ID={fin['id']}", flush=True)
        
        # ✅ Ne pas oublier la dernière balise
        if balises_cibles:
            dernier = balises_cibles[-1]
            while dernier.contents:
                dernier.contents[0].extract()
            print(f"🧹 Zone vidée pour la dernière balise ID={dernier['id']}", flush=True)



        # 📥 injection des textes
        for el in soup.find_all(attrs={"id": True}):
            id_val = el["id"]
            try:
                table, colonne, ligne_cle = id_val.split("_", 2)
        
                colonne = colonne.replace("Genre", genre)
                ligne_cle = (ligne_cle
                                .replace("CdVX", f"CdV{nb_cdv}")
                                .replace("ExpY", f"Exp{nb_exp}")
                                .replace("ReaZ", f"Rea{nb_rea}")
                                .replace("AmeQ", f"Ame{nb_ame}"))
        
                texte = get_cell_value(conn, table, colonne, ligne_cle)
                if texte is not None:
                    # Nettoyer l'élément (supprime tout contenu)
                    el.clear()
                
                    # Gérer les multiples sauts de ligne consécutifs
                    lignes = texte.split("\n")
                    for i, ligne in enumerate(lignes):
                        if i > 0:
                            el.append(soup.new_tag("br"))
                        if ligne.strip() == "":
                            # Saut vide : ajouter un <br> supplémentaire
                            el.append(soup.new_tag("br"))
                        else:
                            el.append(NavigableString(ligne))
                
                    print(f"✅ Injection réussie pour ID={id_val} → table={table}, colonne={colonne}, ligne={ligne_cle}", flush=True)
                else:
                    print(f"⚠️ Aucun contenu trouvé pour ID={id_val} → table={table}, colonne={colonne}, ligne={ligne_cle}", flush=True)

            
            except Exception as e:
                print(f"⚠️ Problème avec l’ID {id_val} : {e}")
                continue

        conn.close()


        fichier_id = str(uuid.uuid4())
        base_url = str(request.base_url).rstrip("/")
        url_html = f"{base_url}/html_temp/{fichier_id}/index.html"

        dossier_temporaire = os.path.join(TEMP_HTML_DIR, fichier_id)
        os.makedirs(dossier_temporaire, exist_ok=True)
        shutil.copytree(TEMPLATE_DIR, dossier_temporaire, dirs_exist_ok=True)

        chemin_index = os.path.join(dossier_temporaire, "index.html")
        with open(chemin_index, "w", encoding="utf-8") as f:
            f.write(str(soup))

        asyncio.create_task(supprimer_fichier_apres_delai(dossier_temporaire, delay=300))

        print("➡️ HTML généré :", url_html, flush=True)
        return JSONResponse(content={"url_html": url_html})

    except Exception as e:
        print("❌ Erreur dans injecter_textes_depuis_bdd()")
        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})

# ⏳ Nettoyage automatique
async def supprimer_fichier_apres_delai(path, delay=300):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 Dossier temporaire supprimé : {path}")
