from datetime import datetime
from app.extensions import db
import re

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

class Competition(db.Model):
    __tablename__ = "competition"

    id = db.Column(db.Integer, primary_key=True)

    festival_id = db.Column(
        db.Integer,
        db.ForeignKey("festival.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(150), unique=True, nullable=False)

    event_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    festival = db.relationship("Festival", backref="competitions")