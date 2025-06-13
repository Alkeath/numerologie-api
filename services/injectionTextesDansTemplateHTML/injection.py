from bs4 import BeautifulSoup, NavigableString
import os
import psycopg2
import uuid
import shutil
import asyncio
import traceback

TEMPLATE_HTML_PATH = "templates/template_temporaire1/index.html"
TEMPLATE_DIR = "templates/template_temporaire1"
TEMP_HTML_DIR = "html_genere"

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
        dbname=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD")
    )

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

async def traiter_injection(request):
    data = await request.json()

    genre = data.get("Genre_Formulaire", "")
    nb_cdv = str(data.get("NbCdV_Final", "")).zfill(2)
    nb_exp = str(data.get("NbExp_Final", "")).zfill(2)
    nb_rea = str(data.get("NbRea_Final", "")).zfill(2)
    nb_ame = str(data.get("NbAme_Final", "")).zfill(2)

    print(f"🔢 Nombres reçus – CdV: {nb_cdv}, Exp: {nb_exp}, Rea: {nb_rea}, Ame: {nb_ame}, Genre: {genre}")

    with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    conn = get_db_connection()

    for balise in soup.find_all(lambda tag: tag.has_attr("id")):
        balise.string = ""
        if not balise.string:
            balise.clear()

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
                el.clear()
                lignes = texte.split("\n")
                for i, ligne in enumerate(lignes):
                    if i > 0:
                        el.append(soup.new_tag("br"))
                    el.append(NavigableString(ligne))
                print(f"✅ Injection réussie pour ID={id_val} → {table}.{colonne} [{ligne_cle}]", flush=True)
            else:
                print(f"⚠️ Aucun contenu trouvé pour ID={id_val} → {table}.{colonne} [{ligne_cle}]", flush=True)
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

    # 🔊 Afficher  l'URL à fin
     print(f"\n✅ Injection terminée — URL finale : {url_html}\n", flush=True)
    
    return {"url_html": url_html}

async def supprimer_fichier_apres_delai(path, delay=300):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 Dossier temporaire supprimé : {path}")
