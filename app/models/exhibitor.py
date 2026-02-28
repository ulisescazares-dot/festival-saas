from datetime import datetime
from app.extensions import db

class Exhibitor(db.Model):
    __tablename__ = "exhibitor"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)

    business_name = db.Column(db.String(160), nullable=False)   # nombre comercial
    legal_name = db.Column(db.String(200), nullable=True)       # razón social
    rfc = db.Column(db.String(20), nullable=True)

    contact_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=True)
    email = db.Column(db.String(120), nullable=False)

    payment_status = db.Column(db.String(30), default="pending")  # pending, paid, partial
    created_at = db.Column(db.DateTime, default=datetime.utcnow)