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
    allow_origins=["*"],  # ou une liste précise de domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PDFRequest(BaseModel):
    html_url: str  # URL complète du fichier HTML injecté (ex: http://.../fichier.html)

@app.post("/generationPDF")
async def generation_pdf(req: PDFRequest):
    try:
        pdf_path = await convert_html_to_pdf(req.html_url)
        return FileResponse(pdf_path, media_type='application/pdf', filename=os.path.basename(pdf_path))
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
