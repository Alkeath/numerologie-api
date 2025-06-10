import os
import json
import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Lecture des credentials JSON depuis la variable d'environnement
google_creds = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
if not google_creds:
    raise ValueError("⛔ La variable d'environnement GOOGLE_SHEETS_CREDENTIALS est introuvable.")

creds_dict = json.loads(google_creds)

# ✅ Connexion à Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ✅ Lecture des données Google Sheets
SHEET_ID = "1oIRcJbtxh7g0nkFfjj0MLphDLBNpPOmU0OGnsX1ycbU"
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ Connexion à PostgreSQL via Railway (les infos peuvent aussi venir de variables d'env si tu préfères)
conn = psycopg2.connect(
    host="postgres.railway.internal",
    dbname="railway",
    user="postgres",
    password=os.getenv("PGPASSWORD"),  # Recommandé
    port="5432"
)

cursor = conn.cursor()

# ✅ Création de la table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS textes (
        id SERIAL PRIMARY KEY,
        cle VARCHAR,
        contenu TEXT
    );
""")

# ✅ Insertion des données
for _, row in df.iterrows():
    cursor.execute("INSERT INTO textes (cle, contenu) VALUES (%s, %s)", (row["Clé"], row["Texte"]))

conn.commit()
cursor.close()
conn.close()

print("✅ Données insérées avec succès.")
