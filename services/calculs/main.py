from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from calculs_api import router as calculs_router
from calculs_api import traitement_etape_1, generer_rapport_depuis_donnees

app = FastAPI()

# ✅ Liste exacte des origines autorisées
origines_autorisees = [
    "https://test-recup.vercel.app",
    "https://www.test-recup.vercel.app",
    "http://localhost:3000",
    "http://localhost"
]

print("🌐 Origines CORS autorisées dans ce service :", origines_autorisees, flush=True)

# ✅ Middleware CORS bien configuré
app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

print("🌐 Origines CORS autorisées :", origines_autorisees)

# ✅ Inclusion des routes API de calcul
app.include_router(calculs_router)

# ✅ Route POST pour l'étape 1 des calculs
@app.post("/calculs-formulaire")
async def calculs_formulaire(request: Request):
    print("✅ Calculs/main : étape 1, Requête reçue")
    donnees = await request.json()
    print("📥 Données :", donnees)
    donnees = traitement_etape_1(donnees)
    return {
        "message": "Étape 1 terminée",
        "donnees": donnees
    }

# ✅ Route POST pour l’enchaînement injection HTML + génération PDF (étapes 3 + 4)
@app.post("/genererRapport")
async def generer_rapport(request: Request):
    print("🧠 Calculs/main : Requête reçue pour génération complète du rapport")
    data = await request.json()
    return generer_rapport_depuis_donnees(data)

# ✅ Lancement du serveur si exécuté directement (utile pour Docker/Cloud Run)
if __name__ == "__main__":
    import os
    import uvicorn

    # 🔁 Récupération du port depuis les variables d'environnement (Cloud Run impose PORT)
    port = int(os.environ.get("PORT", 8080))

    # 🚀 Démarrage de l’application FastAPI avec Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
