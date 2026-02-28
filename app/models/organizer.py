from app.extensions import db

class Organizer(db.Model):
    __tablename__ = "organizer"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)