from datetime import datetime
from app.extensions import db

class Exhibitor(db.Model):
    __tablename__ = "exhibitor"

    id = db.Column(db.Integer, primary_key=True)

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("event.id"),
        nullable=False
    )

    # DATOS
    business_name = db.Column(db.String(150), nullable=False)
    legal_name = db.Column(db.String(150))
    rfc = db.Column(db.String(50))
    email = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.String(250))
    instagram = db.Column(db.String(100))

    # ELÉCTRICO
    total_amperage = db.Column(db.Float)
    voltage = db.Column(db.String(10))
    needs_220 = db.Column(db.Boolean, default=False)
    own_generator = db.Column(db.Boolean, default=False)
    electrical_notes = db.Column(db.Text)

    # ACEPTACIONES
    accepted_reglamento = db.Column(db.Boolean, default=False)
    accepted_carta_responsiva = db.Column(db.Boolean, default=False)
    signer_name = db.Column(db.String(150))

    # FIRMA
    signature_base64 = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELACIONES
    equipment = db.relationship("EquipmentItem", backref="exhibitor", lazy=True)
    documents = db.relationship("ExhibitorDocument", backref="exhibitor", lazy=True)