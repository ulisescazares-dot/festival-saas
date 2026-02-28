from datetime import datetime
from app.extensions import db

class Festival(db.Model):
    __tablename__ = "festival"

    id = db.Column(db.Integer, primary_key=True)

    # dueño (multi-tenant)
    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organization.id"),
        nullable=False
    )
    events = db.relationship("Event", backref="festival", lazy=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)