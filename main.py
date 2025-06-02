#il faudra mettre l'URL du site dans allow_origins une fois qu'il sera défini

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import router as calculs_router
from calculs_api import traitement_etape_1 

app = FastAPI()
app.include_router(calculs_router)

# CORS : autorise les appels du frontend (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://test-recup.vercel.app"],  # Modifier avec l'URL définitive de production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generer-rapport")
async def generer_rapport(request: Request):
    donnees = await request.json()

    # Étape 1 : préparation des variables initiales et calculs bruts
    donnees = traitement_etape_1(donnees)

    return {
        "message": "Étape 1 terminée",
        "donnees": donnees
    }
