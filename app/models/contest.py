from datetime import datetime
from app.extensions import db


class Contest(db.Model):
    __tablename__ = "contest"

    id = db.Column(db.Integer, primary_key=True)
    festival_id = db.Column(db.Integer, db.ForeignKey("festival.id"))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContestRegistration(db.Model):
    __tablename__ = "contest_registration"

    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey("contest.id"))
    full_name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)