# 🐍 1. Image de base officielle avec Python
FROM python:3.11-slim

# 📂 2. Crée un répertoire /app dans le conteneur et s’y place
WORKDIR /app

# 📦 3. Copie les fichiers de ce dossier dans le conteneur
COPY . .

# 📚 4. Installe les bibliothèques nécessaires
RUN pip install --no-cache-dir pandas gspread oauth2client psycopg2-binary

# 🚀 5. Commande lancée automatiquement quand le conteneur démarre
CMD ["python", "main.py"]
