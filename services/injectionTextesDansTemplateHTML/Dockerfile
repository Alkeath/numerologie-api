# Utilise une image Python légère
FROM python:3.11-slim

# Étape 1 : mise à jour du cache
RUN apt-get update

# Étape 2 : installation plus légère
RUN apt-get install -y gcc libpq-dev

# Étape 3 : nettoyage
RUN rm -rf /var/lib/apt/lists/*

# Création du dossier de travail
WORKDIR /app

# Copier les fichiers requis
COPY . /app

# Installer les dépendances Python
RUN pip install fastapi[all] psycopg2-binary beautifulsoup4 python-multipart

# Port utilisé par Uvicorn
EXPOSE 8000

# Lancement de l’application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
