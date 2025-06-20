from bs4 import BeautifulSoup, NavigableString
import uuid
import psycopg2
import os
import asyncio
import shutil
import uuid

# 📁 Déclarations des chemins
TEMPLATE_HTML_PATH = "/app/templates/template_temporaire1/index.html"
TEMPLATE_DIR = "/app/templates/template_temporaire1"
TEMP_HTML_DIR = "/app/html_genere"

async def traiter_injection(request):
    try:
        data = await request.json()

        # 🪪 Utilisation de l'UUID fourni (sinon on en génère un)
        uuid_requete = data.get("uuidRequete")
        fichier_id = uuid_requete if uuid_requete else str(uuid.uuid4())

        if uuid_requete:
            print(f"🔗 UUID de requête fourni par le frontend : {uuid_requete}")
        else:
            print(f"🆕 Aucun UUID fourni, généré automatiquement : {fichier_id}")
                
        genre = data.get("Genre_Formulaire", "")
        nb_cdv = str(data.get("NbCdV_Final", "")).zfill(2)
        nb_exp = str(data.get("NbExp_Final", "")).zfill(2)
        nb_rea = str(data.get("NbRea_Final", "")).zfill(2)
        nb_ame = str(data.get("NbAme_Final", "")).zfill(2)
    
        print(f"🔢 [injection.py] Nombres reçus – CdV: {nb_cdv}, Exp: {nb_exp}, Rea: {nb_rea}, Ame: {nb_ame}, Genre: {genre}")
    
        with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
    
        conn = get_db_connection()
        print("🔌 [injection.py] Connexion BDD ouverte", flush=True)
    
        # 🧹 Effacer les contenus existants
        for balise in soup.find_all(lambda tag: tag.has_attr("id")):
            balise.string = ""
            if not balise.string:
                balise.clear()
    
        # 🚀 Injection des textes
        for el in soup.find_all(attrs={"id": True}):
            id_val = el["id"]
            try:
                parts = id_val.split("_", 2)
                if len(parts) != 3:
                    print(f"❌ ID mal formé (pas 3 parties) : {id_val}", flush=True)
                    continue
                table, colonne, ligne_cle = parts
    
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
                    print(f"✅ Injection : table={table}, colonne={colonne}, ligne={ligne_cle} (ID={id_val})", flush=True)
                else:
                    print(f"⚠️ Vide : table={table}, colonne={colonne}, ligne={ligne_cle} (ID={id_val})", flush=True)
            except Exception as e:
                print(f"❌ Erreur d'injection ID={id_val} → {e}", flush=True)
                continue
    
        conn.close()
    
        # 💾 Sauvegarde HTML temporaire
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
    
        print(f"\n📖🔱 Injection terminée — URL finale : {url_html}\n", flush=True)
        print("🎉 Fin complète de l'injection et création du fichier HTML ✅", flush=True)
        
        return {"url_html": url_html}

    except Exception as e:
        print(f"❌ [injection.py] ERREUR GLOBALE DANS traiter_injection : {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise  # pour que FastAPI continue à renvoyer un 500



async def supprimer_fichier_apres_delai(path, delay=300):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 Dossier temporaire supprimé : {path}")


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
            print(f"❌ Erreur SQL : {e} → table={table}, colonne={column}, ligne={row_key}", flush=True)
            return None
