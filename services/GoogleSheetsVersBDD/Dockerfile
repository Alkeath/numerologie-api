# Utilise une image Python officielle
FROM python:3.11-slim

# Crée un dossier de travail dans le conteneur
WORKDIR /app

# Copie les fichiers nécessaires
COPY requirements.txt ./
COPY main.py ./

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Commande de démarrage
CMD ["python", "main.py"]
