from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from calculs_api import router as calculs_router
from calculs_api import traitement_etape_1, etape_3_injection_textes_dans_html

app = FastAPI()

# ✅ Liste exacte des origines autorisées
origines_autorisees = [
    "https://test-recup.vercel.app",
    "https://www.test-recup.vercel.app",
    "http://localhost:3000",
    "http://localhost"
]

# ✅ Middleware CORS bien configuré
app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ✅ Inclusion des routes API de calcul
app.include_router(calculs_router)

# ✅ Route POST pour l'étape 1 des calculs
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import traceback

@app.post("/calculs-formulaire")
async def calculs_formulaire(request: Request):
    print("✅ [main.py – service calculs] Requête reçue")
    data = await request.json()

    try:
        # 🔄 Étape 1 : Calculs initiaux (totaux/réduits, avant activation)
        print("🔄 [main.py – service calculs] Appel à traitement_etape_1...")
        data = traitement_etape_1(data)
        print("✅ [main.py – service calculs] traitement_etape_1 terminé")

        # 🧹 Nettoyage des données avant renvoi au frontend
        print("🧹 [main.py – service calculs] Données prêtes à être renvoyées au frontend")
        return {
            "message": "Étape 1 terminée",
            "donnees": data
        }

    except Exception as e:
        print(f"❌ [main.py – service calculs] Exception non capturée : {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /calculs-formulaire")




# ✅ Route POST pour l’enchaînement injection HTML + génération PDF (étapes 3 + 4)
@app.post("/genererRapport")
async def generer_rapport(request: Request):
    print("🧠 [main.py – service calculs] : Requête reçue pour génération complète du rapport")
    data = await request.json()

    try:
        resultats = etape_3_injection_textes_dans_html(data)

        if "erreur" in resultats or not resultats.get("chemin_pdf"):
            raise ValueError("❌ [main.py – service calculs] L'injection ou la génération du PDF a échoué.")

        return resultats

    except Exception as e:
        print("❌ [main.py – service calculs] Erreur dans /genererRapport :", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erreur serveur dans /genererRapport")


from fastapi.encoders import jsonable_encoder

# ✅ Nettoyage des champs non sérialisables
def nettoyer_donnees(data):
    data_saine = {}
    for k, v in data.items():
        try:
            jsonable_encoder(v)
            data_saine[k] = v
        except Exception as e:
            print(f"⚠️ Clé '{k}' supprimée du retour (non sérialisable, type {type(v)}): {e}")
    return data_saine
