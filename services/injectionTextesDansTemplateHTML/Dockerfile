# Utilise une image Python légère
FROM python:3.11-slim

# Dépendances système pour psycopg2 + BeautifulSoup
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Création du dossier de travail
WORKDIR /app

# Copier les fichiers requis
COPY . /app

# ✅ Copier explicitement le template HTML
COPY app/templates/template_temporaire1/ /app/app/templates/template_temporaire1/

# Installer les dépendances Python
RUN pip install fastapi[all] psycopg2-binary beautifulsoup4 python-multipart

# Port utilisé par Uvicorn
EXPOSE 8000

# Lancement de l’application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
