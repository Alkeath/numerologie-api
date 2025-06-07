# 🐍 Image officielle Python
FROM python:3.11

# 🧰 Installation des dépendances système nécessaires à WeasyPrint
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# 📂 Créer le dossier de travail
WORKDIR /app

# 📁 Copier tous les fichiers du projet dans l'image Docker
COPY . .

# 📦 Installer les dépendances Python (déclarées dans requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 Commande de démarrage de l'application FastAPI via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80000"]
