from app.extensions import db
from datetime import datetime

class ExhibitorDocument(db.Model):
    __tablename__ = "exhibitor_document"

    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey("exhibitor.id"), nullable=False)

    doc_type = db.Column(db.String(50))  # INE, CONSTANCIA, etc.
    file_path = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)