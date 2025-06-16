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

@app.post("/calculs-formulaire")
async def calculs_formulaire(request: Request):
    print("✅ [main.py – service calculs] Requête reçue")
    data = await request.json()

    try:
        print("🔄 [main.py – service calculs] Appel à traitement_etape_1...")
        data = traitement_etape_1(data)
        print("✅ [main.py – service calculs] traitement_etape_1 terminé")

        # 🚫 Si aucun maître ni deuxième prénom → génération directe
        if data.get("Presence11") != "oui" and data.get("Presence22") != "oui" and not data.get("PrenomsSecondaires"):
            print("🚫 [main.py – service calculs] Aucun maître et aucun 2e prénom : génération directe du rapport")
            try:
                resultats = etape_3_injection_textes_dans_html(data)
        
                if "erreur" in resultats or not resultats.get("chemin_pdf"):
                    raise ValueError("❌ [main.py – service calculs - cas sans nb maître ni 2ème prenom] L'injection ou la génération du PDF a échoué.")
                return resultats
            except Exception as e:
                print("❌ [main.py – service calculs - cas sans nb maître ni 2ème prenom] Erreur dans /genererRapport :", str(e))
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail="Erreur serveur dans /genererRapport")
        
        else:
            print("🕓 [main.py – service calculs] Modales attendues : pas de génération directe")

        print("🧹 [main.py – service calculs] Nettoyage des données avant envoi au frontend")
        return {
            "message": "Étape 1 terminée",
            "donnees": data
        }

    except Exception as e:
        print(f"❌ [main.py – service calculs] Exception non capturée : {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
