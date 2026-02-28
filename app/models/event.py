from datetime import datetime
from app.extensions import db

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)

    festival_id = db.Column(
        db.Integer,
        db.ForeignKey("festival.id"),
        nullable=False
    )

    city = db.Column(db.String(120), nullable=False)
    venue = db.Column(db.String(150), nullable=True)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    exhibitors = db.relationship("Exhibitor", backref="event", lazy=True)