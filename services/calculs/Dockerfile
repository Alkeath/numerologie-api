# 🐍 Image officielle Python
FROM python:3.11-slim

# 📂 Créer le dossier de travail
WORKDIR /app
ENV PYTHONPATH=/app

# 📁 Copier tous les fichiers du projet dans l'image Docker
COPY . .

# 📦 Installer les dépendances Python (déclarées dans requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 Commande de démarrage de l'application FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
