from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import ElectricalRequirement, Exhibitor, Event, Festival

electrical_bp = Blueprint("electrical", __name__, url_prefix="/electrical")

def exhibitor_belongs_to_user(exhibitor_id: int, user_id: int):
    exhibitor = Exhibitor.query.filter_by(id=exhibitor_id).first()
    if not exhibitor:
        return None, ({"msg": "Exhibitor not found"}, 404)

    event = Event.query.filter_by(id=exhibitor.event_id).first()
    if not event:
        return None, ({"msg": "Event not found"}, 404)

    festival = Festival.query.filter_by(id=event.festival_id, owner_user_id=user_id).first()
    if not festival:
        return None, ({"msg": "Not allowed"}, 403)

    return exhibitor, None


@electrical_bp.route("/<int:exhibitor_id>", methods=["PUT"])
@jwt_required()
def upsert_electrical(exhibitor_id):
    user_id = int(get_jwt_identity())
    exhibitor, err = exhibitor_belongs_to_user(exhibitor_id, user_id)
    if err:
        return jsonify(err[0]), err[1]

    data = request.get_json()

    req = ElectricalRequirement.query.filter_by(exhibitor_id=exhibitor.id).first()
    if not req:
        req = ElectricalRequirement(exhibitor_id=exhibitor.id)
        db.session.add(req)

    req.total_amperage = data.get("total_amperage")
    req.voltage = data.get("voltage", req.voltage)
    req.needs_220 = bool(data.get("needs_220", req.needs_220))
    req.own_generator = bool(data.get("own_generator", req.own_generator))
    req.notes = data.get("notes")

    db.session.commit()

    return jsonify({
        "exhibitor_id": exhibitor.id,
        "total_amperage": str(req.total_amperage) if req.total_amperage is not None else None,
        "voltage": req.voltage,
        "needs_220": req.needs_220,
        "own_generator": req.own_generator,
        "notes": req.notes
    }), 200


@electrical_bp.route("/<int:exhibitor_id>", methods=["GET"])
@jwt_required()
def get_electrical(exhibitor_id):
    user_id = int(get_jwt_identity())
    exhibitor, err = exhibitor_belongs_to_user(exhibitor_id, user_id)
    if err:
        return jsonify(err[0]), err[1]

    req = ElectricalRequirement.query.filter_by(exhibitor_id=exhibitor.id).first()
    if not req:
        return jsonify({"msg": "No electrical requirement yet"}), 404

    return jsonify({
        "exhibitor_id": exhibitor.id,
        "total_amperage": str(req.total_amperage) if req.total_amperage is not None else None,
        "voltage": req.voltage,
        "needs_220": req.needs_220,
        "own_generator": req.own_generator,
        "notes": req.notes
    }), 200