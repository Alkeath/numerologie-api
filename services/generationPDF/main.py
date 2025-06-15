from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import os
from generate_pdf import convert_html_to_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://test-recup.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PDFRequest(BaseModel):
    html_url: str  # URL complète du fichier HTML injecté (ex: http://.../fichier.html)

@app.post("/generationPDF")
async def generation_pdf_endpoint(payload: PDFRequest):
    html_url = payload.html_url
    print(f"📥 [generationPDF - main.py] URL reçue : {html_url}")
    print("🧾 [generationPDF - main.py] Payload brut reçu :", payload)
    print("🔗 [generationPDF - main.py] URL extraite :", payload.html_url)

    try:
        pdf_path = await convert_html_to_pdf(html_url)
        print("✅ [generationPDF - main.py] Chemin PDF généré :", pdf_path)
        print("📁 [generationPDF - main.py] Le fichier existe-t-il ?", os.path.exists(pdf_path))
        return FileResponse(pdf_path, media_type="application/pdf", filename="rapport.pdf")
    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        return JSONResponse(status_code=500, content={"error": "Erreur lors de la génération du PDF"})
