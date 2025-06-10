import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# 🔐 Authentification via variable d'environnement
json_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not json_creds:
    raise Exception("❌ Variable GOOGLE_APPLICATION_CREDENTIALS_JSON non définie.")

creds_dict = json.loads(json_creds)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Lecture du Google Sheet
SHEET_ID = "1oIRcJbtxh7g0nkFfjj0MLphDLBNpPOmU0OGnsX1ycbU"
sheet = client.open_by_key(SHEET_ID).sheet1
rows = sheet.get_all_values()

# ⚙️ Construction du DataFrame
df = pd.DataFrame(rows[1:], columns=rows[0])  # Ignore la 1ère ligne et utilise-la comme en-tête

# 🔃 Renommer la première colonne si elle n’a pas de nom explicite
if df.columns[0] == "":
    df.rename(columns={df.columns[0]: "Cle"}, inplace=True)
else:
    df.rename(columns={df.columns[0]: "Cle"}, inplace=True)

# 🗃️ Connexion à PostgreSQL (Railway)
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    port=os.getenv("PGPORT")
)
cursor = conn.cursor()

# ✅ Création de la table avec toutes les colonnes
cursor.execute("""
    CREATE TABLE IF NOT EXISTS textes (
        id SERIAL PRIMARY KEY,
        cle VARCHAR,
        identite_generique TEXT,
        identite_chemin_de_vie_titre TEXT,
        identite_chemin_de_vie_nom_graph TEXT,
        identite_chemin_de_vie_global_homme_texte TEXT,
        identite_chemin_de_vie_global_femme_texte TEXT,
        identite_chemin_de_vie_partie1_homme_texte TEXT
    );
""")

# Insertion ligne par ligne
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO textes (
            cle, identite_generique, identite_chemin_de_vie_titre,
            identite_chemin_de_vie_nom_graph,
            identite_chemin_de_vie_global_homme_texte,
            identite_chemin_de_vie_global_femme_texte,
            identite_chemin_de_vie_partie1_homme_texte
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        row["Cle"],
        row.get("IdentiteGenerique", ""),
        row.get("IdentiteCheminDeVieTitre", ""),
        row.get("IdentiteCheminDeVieNomGraph", ""),
        row.get("IdentiteCheminDeVieGlobalHommeTexte", ""),
        row.get("IdentiteCheminDeVieGlobalFemmeTexte", ""),
        row.get("IdentiteCheminDeViePartie1HommeTexte", "")
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Données insérées avec succès.")
