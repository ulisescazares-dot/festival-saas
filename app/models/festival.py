from datetime import datetime
from app.extensions import db
import re

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


class Festival(db.Model):
    __tablename__ = "festival"

    id = db.Column(db.Integer, primary_key=True)

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organization.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    slug = db.Column(db.String(150), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship("Event", backref="festival", lazy=True)
    registrations = db.relationship("FestivalRegistration", backref="festival", lazy=True)


# 🔥 ESTA CLASE VA FUERA
class FestivalRegistration(db.Model):
    __tablename__ = "festival_registration"

    id = db.Column(db.Integer, primary_key=True)

    festival_id = db.Column(
        db.Integer,
        db.ForeignKey("festival.id"),
        nullable=False
    )

    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)