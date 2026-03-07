from app.extensions import db
from datetime import datetime

class CompetitionParticipant(db.Model):
    __tablename__ = "competition_participant"

    id = db.Column(db.Integer, primary_key=True)

    competition_id = db.Column(
        db.Integer,
        db.ForeignKey("competition.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    coffee_shop = db.Column(db.String(150), nullable=False)

    payment_status = db.Column(db.String(50), default="pending")
    stripe_session_id = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)