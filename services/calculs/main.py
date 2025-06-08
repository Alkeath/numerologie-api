from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import router as calculs_router
from calculs_api import traitement_etape_1

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

# ✅ Lancement du serveur si exécuté directement (utile pour Docker/Cloud Run)
if __name__ == "__main__":
    import os
    import uvicorn

    # 🔁 Récupération du port depuis les variables d'environnement (Cloud Run impose PORT)
    port = int(os.environ.get("PORT", 8080))

    # 🚀 Démarrage de l’application FastAPI avec Uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
