from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import traitement_numerologie_depuis_json  # ✅ importe ta fonction depuis ton fichier

app = FastAPI()

# Pour autoriser les appels du frontend (ex : vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://test-recup.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from calculs_api import traitement_numerologie_depuis_json  # ✅ importe ta fonction depuis ton fichier

app = FastAPI()

# Pour autoriser les appels du frontend (ex : vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tu pourras restreindre à ton domaine plus tard
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/generer-rapport")
async def generer_rapport(request: Request):
    data = await request.json()
    resultats = traitement_numerologie_depuis_json(data)
    return resultats
