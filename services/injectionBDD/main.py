import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Connexion à Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("numerologie-import-bdd.json", scope)
client = gspread.authorize(creds)

# Ouvrir la feuille
SHEET_ID = "1oIRcJbtxh7g0nkFfjj0MLphDLBNpPOmU0OGnsX1ycbU"
sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Connexion à PostgreSQL via Railway
conn = psycopg2.connect(
    host="postgres.railway.internal",
    dbname="railway",
    user="postgres",
    password="mDSIMZwHiqRIfAooxVfOXUsEFYzPojbj",
    port="5432"
)

cursor = conn.cursor()

# Exemple : création d'une table (à adapter selon ton onglet)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS textes (
        id SERIAL PRIMARY KEY,
        cle VARCHAR,
        contenu TEXT
    );
""")

# Insertion des lignes dans la table
for _, row in df.iterrows():
    cursor.execute("INSERT INTO textes (cle, contenu) VALUES (%s, %s)", (row["Clé"], row["Texte"]))

conn.commit()
cursor.close()
conn.close()

print("✅ Données insérées avec succès.")
