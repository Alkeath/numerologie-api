#il faudra mettre l'URL du site dans allow_origins une fois qu'il sera défini

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

# ✅ Inclusion des routes
app.include_router(calculs_router)

# ✅ Route principale
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
