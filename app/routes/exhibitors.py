from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Exhibitor, Event, Festival

exhibitors_bp = Blueprint("exhibitors", __name__, url_prefix="/exhibitors")

@exhibitors_bp.route("", methods=["POST"])
@jwt_required()
def create_exhibitor():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    # Validar que el event pertenece a un festival del usuario
    event = Event.query.filter_by(id=data["event_id"]).first()
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    festival = Festival.query.filter_by(id=event.festival_id, owner_user_id=user_id).first()
    if not festival:
        return jsonify({"msg": "Not allowed"}), 403

    exhibitor = Exhibitor(
        event_id=event.id,
        business_name=data["business_name"],
        legal_name=data.get("legal_name"),
        rfc=data.get("rfc"),
        contact_name=data["contact_name"],
        phone=data.get("phone"),
        email=data["email"],
        payment_status=data.get("payment_status", "pending")
    )

    db.session.add(exhibitor)
    db.session.commit()

    return jsonify({"id": exhibitor.id, "business_name": exhibitor.business_name}), 201


@exhibitors_bp.route("/event/<int:event_id>", methods=["GET"])
@jwt_required()
def list_exhibitors(event_id):
    user_id = int(get_jwt_identity())

    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    festival = Festival.query.filter_by(id=event.festival_id, owner_user_id=user_id).first()
    if not festival:
        return jsonify({"msg": "Not allowed"}), 403

    exhibitors = Exhibitor.query.filter_by(event_id=event.id).order_by(Exhibitor.id.desc()).all()

    return jsonify([
        {
            "id": e.id,
            "business_name": e.business_name,
            "contact_name": e.contact_name,
            "email": e.email,
            "phone": e.phone,
            "payment_status": e.payment_status,
            "created_at": e.created_at.isoformat()
        }
        for e in exhibitors
    ]), 200