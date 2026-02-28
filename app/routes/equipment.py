from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import EquipmentItem, Exhibitor, Event, Festival

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")

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


@equipment_bp.route("/<int:exhibitor_id>", methods=["POST"])
@jwt_required()
def add_equipment(exhibitor_id):
    user_id = int(get_jwt_identity())
    exhibitor, err = exhibitor_belongs_to_user(exhibitor_id, user_id)
    if err:
        return jsonify(err[0]), err[1]

    data = request.get_json()

    item = EquipmentItem(
        exhibitor_id=exhibitor.id,
        name=data["name"],
        quantity=int(data.get("quantity", 1)),
        watts=data.get("watts"),
        notes=data.get("notes")
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({"id": item.id, "name": item.name}), 201


@equipment_bp.route("/<int:exhibitor_id>", methods=["GET"])
@jwt_required()
def list_equipment(exhibitor_id):
    user_id = int(get_jwt_identity())
    exhibitor, err = exhibitor_belongs_to_user(exhibitor_id, user_id)
    if err:
        return jsonify(err[0]), err[1]

    items = EquipmentItem.query.filter_by(exhibitor_id=exhibitor.id).order_by(EquipmentItem.id.desc()).all()

    return jsonify([
        {
            "id": i.id,
            "name": i.name,
            "quantity": i.quantity,
            "watts": i.watts,
            "notes": i.notes
        } for i in items
    ]), 200


@equipment_bp.route("/item/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_equipment(item_id):
    user_id = int(get_jwt_identity())

    item = EquipmentItem.query.filter_by(id=item_id).first()
    if not item:
        return jsonify({"msg": "Item not found"}), 404

    exhibitor, err = exhibitor_belongs_to_user(item.exhibitor_id, user_id)
    if err:
        return jsonify(err[0]), err[1]

    db.session.delete(item)
    db.session.commit()
    return jsonify({"msg": "Deleted"}), 200