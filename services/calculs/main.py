from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from calculs_api import (
    router as calculs_router,
    etape_0_mise_en_forme_prenoms_nom_et_date_de_naissance,
    etape_1_calculs_preliminaires_nombres_principaux,
    etape_3_injection_textes_dans_html
)
import traceback

app = FastAPI()

# ✅ CORS
origines_autorisees = [
    "https://test-recup.vercel.app",
    "https://www.test-recup.vercel.app",
    "http://localhost:3000",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ✅ Inclusion des routes
app.include_router(calculs_router)

# 🧩 ÉTAPE 0 – Mise en forme prénom/nom/date (sans calculs)
@app.post("/mise-en-forme-donnees")
async def mise_en_forme_donnees(request: Request):
    print("✳️ [main.py] Requête reçue pour mise en forme (étape 0)")
    data = await request.json()

    try:
        data = etape_0_mise_en_forme_prenoms_nom_et_date_de_naissance(data)
        print("✅ Étape 0 – Mise en forme terminée")
        return {
            "message": "Mise en forme effectuée",
            "donnees": nettoyer_donnees(data)
        }

    except Exception as e:
        print(f"❌ Erreur dans /mise-en-forme-donnees : {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /mise-en-forme-donnees")


# 🧩 ÉTAPE 1 – Calculs préliminaires
@app.post("/calculs-formulaire")
async def calculs_formulaire(request: Request):
    print("🔢 [main.py] Requête reçue pour calculs initiaux (étape 1)")
    data = await request.json()

    try:
        data = etape_1_calculs_preliminaires_nombres_principaux(data)
        print("✅ Étape 1 – Calculs initiaux terminés")
        return {
            "message": "Calculs préliminaires terminés",
            "donnees": nettoyer_donnees(data)
        }

    except Exception as e:
        print(f"❌ Erreur dans /calculs-formulaire : {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /calculs-formulaire")


# ✅ Étapes 3 + 4 – Injection texte + génération PDF
@app.post("/genererRapport")
async def generer_rapport(request: Request):
    print("🧠 [main.py] Requête reçue pour génération complète du rapport")
    data = await request.json()

    try:
        resultats = etape_3_injection_textes_dans_html(data)
        if "erreur" in resultats or not resultats.get("chemin_pdf"):
            raise ValueError("L'injection ou la génération du PDF a échoué.")
        return resultats

    except Exception as e:
        print("❌ Erreur dans /genererRapport :", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /genererRapport")


# 🧹 Utilitaire de nettoyage JSON
def nettoyer_donnees(data):
    data_saine = {}
    for k, v in data.items():
        try:
            jsonable_encoder(v)
            data_saine[k] = v
        except Exception as e:
            print(f"⚠️ Clé '{k}' ignorée (type {type(v)}): {e}")
    return data_saine
