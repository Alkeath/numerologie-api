@app.post("/injectionTextesDansTemplateHTML")
async def injection_textes(request: Request, data: dict):
    from bs4 import BeautifulSoup
    import uuid
    import os

    TEMPLATE_HTML_PATH = "app/templates/template_temporaire1/index.html"
    DOSSIER_HTML_TEMP = "app/templates/html_temp"
    
    # Chargement du template HTML
    try:
        with open(TEMPLATE_HTML_PATH, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Template HTML non trouvé.")

    # Suppression du contenu dans les zones identifiées par un ID
    for el in soup.find_all(attrs={"id": True}):
        el.clear()

    # Création du dossier temporaire
    fichier_id = str(uuid.uuid4())
    dossier_temp = os.path.join(DOSSIER_HTML_TEMP, fichier_id)
    os.makedirs(dossier_temp, exist_ok=True)

    chemin_fichier = os.path.join(dossier_temp, "index.html")
    with open(chemin_fichier, "w", encoding="utf-8") as f:
        f.write(str(soup))

    # Construction de l'URL temporaire
    base_url = str(request.base_url).rstrip("/")
    url_html = f"{base_url}/html_temp/{fichier_id}/index.html"

    print(f"🧹 HTML vidé généré : {url_html}", flush=True)

    return {"url_html": url_html}
