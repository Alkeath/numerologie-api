import asyncio
import os
import uuid
from pyppeteer import launch

OUTPUT_FOLDER = "pdf_outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

async def convert_html_to_pdf(url: str) -> str:
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'networkidle2'})

    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)
    
    await page.pdf({
        'path': pdf_path,
        'format': 'A4',
        'margin': {
            'top': '30px',
            'bottom': '30px',
            'left': '30px',
            'right': '30px'
        },
        'printBackground': True
    })

    await browser.close()
    asyncio.create_task(supprimer_fichier_pdf_apres_delai(pdf_path))
    return pdf_path


async def supprimer_fichier_pdf_apres_delai(path, delay=300):
    await asyncio.sleep(delay)
    if os.path.exists(path):
        os.remove(path)
        print(f"🧹 PDF temporaire supprimé : {path}")

