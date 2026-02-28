from datetime import datetime
from app.extensions import db

class EquipmentItem(db.Model):
    __tablename__ = "equipment_item"

    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey("exhibitor.id"), nullable=False)

    name = db.Column(db.String(120), nullable=False)     # "Máquina espresso"
    quantity = db.Column(db.Integer, default=1)
    watts = db.Column(db.Integer, nullable=True)         # opcional
    notes = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)