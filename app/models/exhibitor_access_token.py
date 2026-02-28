import uuid
from datetime import datetime, timedelta
from app.extensions import db

class ExhibitorAccessToken(db.Model):
    __tablename__ = "exhibitor_access_token"

    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey("exhibitor.id"), nullable=False)

    token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    purpose = db.Column(db.String(30), default="agreement")  # futuro: "payment", "profile", etc.
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=14))
    is_revoked = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)