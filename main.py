from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import traitement_etape_1


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
    data = await request.json()
    resultats = traitement_etape_1(data)
    return {
        "message": "Étape 1 terminée",
        "donnees": resultats
    }

