from datetime import datetime
from app.extensions import db

class ElectricalRequirement(db.Model):
    __tablename__ = "electrical_requirement"

    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey("exhibitor.id"), nullable=False, unique=True)

    total_amperage = db.Column(db.Numeric(6, 2), nullable=True)  # ej 12.50
    voltage = db.Column(db.String(10), default="110")            # "110" / "220"
    needs_220 = db.Column(db.Boolean, default=False)
    own_generator = db.Column(db.Boolean, default=False)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)