from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Festival, User, Contest

festivals_bp = Blueprint("festivals", __name__, url_prefix="/festivals")

@festivals_bp.route("", methods=["POST"])
@jwt_required()
def create_festival():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user.organization_id:
        return jsonify({"msg": "User has no organization"}), 400

    data = request.get_json()

    f = Festival(
        organization_id=user.organization_id,
        name=data["name"],
        description=data.get("description")
    )

    db.session.add(f)
    db.session.commit()

    return jsonify({
        "id": f.id,
        "name": f.name,
        "description": f.description
    }), 201

@festivals_bp.route("/<int:festival_id>/contests", methods=["GET"])
@jwt_required()
def list_contests(festival_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify([]), 200

    contests = Contest.query.filter_by(festival_id=festival.id).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug
        }
        for c in contests
    ])