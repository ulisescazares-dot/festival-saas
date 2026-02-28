from datetime import datetime
from app.extensions import db

class ExhibitorAgreement(db.Model):
    __tablename__ = "exhibitor_agreement"

    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey("exhibitor.id"), nullable=False, unique=True)

    # A) Checkboxes
    accepted_reglamento = db.Column(db.Boolean, default=False)
    accepted_carta_responsiva = db.Column(db.Boolean, default=False)

    # B) Firma (imagen)
    signer_name = db.Column(db.String(120), nullable=False)
    signature_image_path = db.Column(db.String(300), nullable=True)  # uploads/signatures/xxx.png

    # C) PDF final
    pdf_path = db.Column(db.String(300), nullable=True)  # uploads/agreements/xxx.pdf

    signed_at = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(60), nullable=True)
    user_agent = db.Column(db.String(250), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)