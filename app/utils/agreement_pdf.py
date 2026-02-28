import os
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

UPLOAD_SIG_DIR = os.path.join(PROJECT_ROOT, "uploads", "signatures")
UPLOAD_PDF_DIR = os.path.join(PROJECT_ROOT, "uploads", "agreements")

def save_signature_png(signature_base64: str, filename: str) -> str:
    # signature_base64 puede venir como "data:image/png;base64,AAAA..."
    if signature_base64.startswith("data:image"):
        signature_base64 = signature_base64.split(",", 1)[1]

    raw = base64.b64decode(signature_base64)
    img = Image.open(BytesIO(raw)).convert("RGBA")

    os.makedirs(UPLOAD_SIG_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_SIG_DIR, filename)
    img.save(path, "PNG")
    return path

def generate_agreement_pdf(
    pdf_filename: str,
    exhibitor_name: str,
    signer_name: str,
    accepted_reglamento: bool,
    accepted_carta: bool,
    signed_at: datetime,
    signature_png_path: str | None,
    notes: str | None = None
) -> str:
    os.makedirs(UPLOAD_PDF_DIR, exist_ok=True)
    pdf_path = os.path.join(UPLOAD_PDF_DIR, pdf_filename)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Acuerdo del Expositor (Reglamento + Carta Responsiva)")

    y -= 40
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Expositor: {exhibitor_name}")
    y -= 18
    c.drawString(50, y, f"Firmante: {signer_name}")
    y -= 18
    c.drawString(50, y, f"Fecha/Hora: {signed_at.isoformat(sep=' ', timespec='seconds')}")

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Aceptaciones:")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(70, y, f"- Reglamento interno: {'SI' if accepted_reglamento else 'NO'}")
    y -= 16
    c.drawString(70, y, f"- Carta responsiva: {'SI' if accepted_carta else 'NO'}")

    if notes:
        y -= 24
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Notas:")
        y -= 16
        c.setFont("Helvetica", 11)
        c.drawString(70, y, notes[:1200])

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Firma:")
    y -= 10

    if signature_png_path and os.path.exists(signature_png_path):
        # Insertar imagen firma
        c.drawImage(signature_png_path, 50, y-120, width=250, height=120, mask='auto')
        c.rect(50, y-120, 250, 120)
    else:
        c.setFont("Helvetica", 11)
        c.drawString(70, y-40, "(Sin imagen de firma)")

    c.showPage()
    c.save()
    return pdf_path