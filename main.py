from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from calculs_api import router as calculs_router
from calculs_api import traitement_etape_1
from pathlib import Path
from weasyprint import HTML
import uuid

app = FastAPI()

# ✅ Liste exacte des origines autorisées
allow_origins = [
    "https://test-recup.vercel.app",
    "https://www.test-recup.vercel.app",
    "http://localhost:3000",
    "http://localhost"
]

# ✅ Middleware CORS bien configuré
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Inclusion des routes API de calcul
app.include_router(calculs_router)

# ✅ Route POST pour l'étape 1 des calculs
@app.post("/generer-rapport")
async def generer_rapport(request: Request):
    print("✅ Requête reçue")
    donnees = await request.json()
    print("📥 Données :", donnees)
    donnees = traitement_etape_1(donnees)
    return {
        "message": "Étape 1 terminée",
        "donnees": donnees
    }

# ✅ Route GET pour générer le PDF depuis le template HTML
@app.get("/generer-pdf")
def generer_pdf():
    # 📄 Lire le HTML de base
    chemin_html = Path("app/templates/template_temporaire1/index.html")
    contenu_html = chemin_html.read_text(encoding="utf-8")

    # 📂 Créer un fichier temporaire
    nom_temporaire = f"rapport_{uuid.uuid4().hex[:8]}.pdf"
    chemin_pdf = Path(f"/tmp/{nom_temporaire}")  # Compatible Render

    # 🖨️ Générer le PDF
    HTML(string=contenu_html).write_pdf(target=str(chemin_pdf))

    # 📤 Envoyer le fichier PDF comme réponse
    return FileResponse(
        path=chemin_pdf,
        media_type="application/pdf",
        filename="rapport.pdf"
    )
