from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Event, Festival
from datetime import datetime

events_bp = Blueprint("events", __name__, url_prefix="/events")


@events_bp.route("", methods=["POST"])
@jwt_required()
def create_event():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Validar que el festival pertenece al usuario
    festival = Festival.query.filter_by(
        id=data["festival_id"],
        owner_user_id=user_id
    ).first()

    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    event = Event(
        festival_id=festival.id,
        city=data["city"],
        venue=data.get("venue"),
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        "id": event.id,
        "city": event.city
    }), 201


@events_bp.route("/<int:festival_id>", methods=["GET"])
@jwt_required()
def list_events(festival_id):
    user_id = int(get_jwt_identity())

    festival = Festival.query.filter_by(
        id=festival_id,
        owner_user_id=user_id
    ).first()

    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    events = Event.query.filter_by(festival_id=festival.id).all()

    return jsonify([
        {
            "id": e.id,
            "city": e.city,
            "venue": e.venue,
            "start_date": e.start_date.isoformat(),
            "end_date": e.end_date.isoformat()
        }
        for e in events
    ]), 200