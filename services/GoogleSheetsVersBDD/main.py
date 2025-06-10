import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# 🔐 Lecture de la clé JSON depuis une variable d'environnement
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not creds_json:
    raise Exception("❌ Variable GOOGLE_APPLICATION_CREDENTIALS_JSON non définie.")

creds_dict = json.loads(creds_json)

# 🔗 Authentification Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Accès à la feuille
SHEET_ID = "1oIRcJbtxh7g0nkFfjj0MLphDLBNpPOmU0OGnsX1ycbU"
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 🗃️ Connexion à PostgreSQL (valeurs Railway)
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    port=os.getenv("PGPORT")
)
cursor = conn.cursor()

# 🧱 Création de la table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS textes (
        id SERIAL PRIMARY KEY,
        cle VARCHAR,
        contenu TEXT
    );
""")

# 💾 Insertion des données
for _, row in df.iterrows():
    cursor.execute("INSERT INTO textes (cle, contenu) VALUES (%s, %s)", (row["Clé"], row["Texte"]))

conn.commit()
cursor.close()
conn.close()

print("✅ Données insérées avec succès.")
