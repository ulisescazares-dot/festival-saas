from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Festival, Event, Exhibitor, ElectricalRequirement
from app.extensions import db
from sqlalchemy import func

summary_bp = Blueprint("summary", __name__, url_prefix="/summary")


@summary_bp.route("/event/<int:event_id>", methods=["GET"])
@jwt_required()
def electrical_summary(event_id):
    user_id = int(get_jwt_identity())

    event = Event.query.filter_by(id=event_id).first()
    if not event:
        return jsonify({"msg": "Event not found"}), 404

    festival = Festival.query.filter_by(
        id=event.festival_id,
        owner_user_id=user_id
    ).first()

    if not festival:
        return jsonify({"msg": "Not allowed"}), 403

    # Total amperaje
    total_amperage = db.session.query(
        func.coalesce(func.sum(ElectricalRequirement.total_amperage), 0)
    ).join(
        Exhibitor, Exhibitor.id == ElectricalRequirement.exhibitor_id
    ).filter(
        Exhibitor.event_id == event_id
    ).scalar()

    # Conteo 220V
    count_220 = db.session.query(ElectricalRequirement).join(
        Exhibitor
    ).filter(
        Exhibitor.event_id == event_id,
        ElectricalRequirement.needs_220 == True
    ).count()

    # Generadores
    count_generators = db.session.query(ElectricalRequirement).join(
        Exhibitor
    ).filter(
        Exhibitor.event_id == event_id,
        ElectricalRequirement.own_generator == True
    ).count()

    return jsonify({
        "event_id": event_id,
        "total_amperage": float(total_amperage),
        "needs_220_count": count_220,
        "own_generator_count": count_generators
    }), 200