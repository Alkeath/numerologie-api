# 🐍 1. Utilise l’image officielle Python (version légère)
FROM python:3.11-slim

# 🧾 2. Affiche les logs immédiatement (utile pour Railway ou Docker logs)
ENV PYTHONUNBUFFERED=1

# 📂 3. Crée un répertoire /app dans le conteneur et s’y place
WORKDIR /app

# 📦 4. Copie tous les fichiers du dossier courant dans /app du conteneur
COPY . .

# 📚 5. Installe les bibliothèques nécessaires sans conserver les caches
RUN pip install --no-cache-dir pandas gspread oauth2client psycopg2-binary

# 🚀 6. Lance automatiquement le script main.py quand le conteneur démarre
CMD ["python", "main.py"]
