from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import (
    traitement_etape_1,
    traitement_etape_2,
)

app = FastAPI()

# CORS : autorise les appels du frontend (Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://test-recup.vercel.app"],  # ou ["*"] temporairement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generer-rapport")
async def generer_rapport(request: Request):
    donnees = await request.json()

    # Étape 1 : préparation des variables initiales
    donnees = traitement_etape_1(donnees)

    # Étape 2 : application des réponses aux questions (activation 11/22)
    donnees = traitement_etape_2(donnees)

    return {
        "message": "Étapes 1 et 2 terminées",
        "donnees": donnees
    }
