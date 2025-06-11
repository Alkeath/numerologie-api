import pandas as pd
import psycopg2
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

# 🔐 Authentification avec les credentials Google via variable Railway
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not creds_json:
    raise Exception("❌ Variable GOOGLE_APPLICATION_CREDENTIALS_JSON non définie.")
creds_dict = json.loads(creds_json)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📄 Connexion à Google Sheet
SHEET_ID = "1oIRcJbtxh7g0nkFfjj0MLphDLBNpPOmU0OGnsX1ycbU"
spreadsheet = client.open_by_key(SHEET_ID)

# 🗃️ Connexion à PostgreSQL (valeurs Railway)
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    dbname=os.getenv("PGDATABASE"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    port=os.getenv("PGPORT")
)
cursor = conn.cursor()

# 📥 Traitement de chaque onglet du Google Sheet
for worksheet in spreadsheet.worksheets():
    table_name = worksheet.title  # Garde les majuscules/minuscules
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        print(f"⚠️ Onglet « {table_name} » vide, ignoré.")
        continue

    # ❌ Supprime toutes les tables existantes dans la base PostgreSQL
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema='public' AND table_type='BASE TABLE';
    """)
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
        print(f'🗑️ Table "{table_name}" supprimée')


    # ✅ Crée la table avec les noms de colonnes dynamiques
    column_defs = ", ".join([f'"{col}" TEXT' for col in df.columns])
    cursor.execute(f'CREATE TABLE "{table_name}" ({column_defs});')

    # ➕ Insert ligne par ligne
    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(df.columns))
        column_names = ", ".join([f'"{col}"' for col in df.columns])
        values = [row[col] for col in df.columns]
        cursor.execute(f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})', values)

    print(f"✅ Table « {table_name} » importée avec succès ({len(df)} lignes).")

# 🔚 Finalisation
conn.commit()
cursor.close()
conn.close()
print("🎉 Tous les onglets ont été importés correctement.")
