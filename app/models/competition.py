from datetime import datetime
from app.extensions import db
import re

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

from app.extensions import db

class Competition(db.Model):
    __tablename__ = "competition"

    id = db.Column(db.Integer, primary_key=True)
    festival_id = db.Column(db.Integer, db.ForeignKey("festival.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(200), unique=True, nullable=False)

    price = db.Column(db.Integer, default=350)  # precio en pesos

    created_at = db.Column(db.DateTime, server_default=db.func.now())