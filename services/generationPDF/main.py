from fastapi import FastAPI
from fastapi.responses import FileResponse
import subprocess

app = FastAPI()

@app.get("/generer-pdf")
async def generer_pdf():
    try:
        subprocess.run(["node", "generate_pdf.js"], check=True)
        return FileResponse("rapport_test.pdf", media_type="application/pdf", filename="rapport_test.pdf")
    except subprocess.CalledProcessError as e:
        return {"error": f"Erreur de génération : {e}"}
