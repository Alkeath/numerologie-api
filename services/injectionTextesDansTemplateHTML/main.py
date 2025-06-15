from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import asyncio
from injection import traiter_injection, supprimer_fichier_apres_delai

app = FastAPI()

# 🔓 Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://test-recup.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST", "OPTIONS"]
    allow_headers=["*"],
)


# 📁 Répertoire temporaire pour les fichiers HTML générés
TEMP_HTML_DIR = "html_genere"
os.makedirs(TEMP_HTML_DIR, exist_ok=True)
app.mount("/html_temp", StaticFiles(directory=TEMP_HTML_DIR, html=True), name="html_temp")


# 🎯 Route principale d'injection
@app.post("/injectionTextesDansTemplateHTML")
async def injecter_textes_depuis_bdd(request: Request):
    try:
        result = await traiter_injection(request)
        return JSONResponse(content=result)  # <- 🔁 on renvoie tel quel le dict {"url_html": ...}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
