from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Festival, User, Contest
import re

festivals_bp = Blueprint("festivals", __name__, url_prefix="/festivals")

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


@festivals_bp.route("", methods=["POST"])
@jwt_required()
def create_festival():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json()

    # 🔥 Si no tiene organización → crearle una
    if not user.organization_id:
        from app.models import Organization
        org = Organization(name=f"Organization of {user.email}")
        db.session.add(org)
        db.session.commit()
        user.organization_id = org.id
        db.session.commit()

    # 🔥 Generar slug automático
    slug = slugify(data["name"])

    # Crear festival
    f = Festival(
        organization_id=user.organization_id,
        name=data["name"],
        description=data.get("description"),
        slug=slug
    )

    db.session.add(f)
    db.session.commit()

    return jsonify({
        "id": f.id,
        "name": f.name,
        "slug": f.slug
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

@festivals_bp.route("", methods=["GET"])
@jwt_required()
def list_festivals():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user.organization_id:
        return jsonify([])

    festivals = Festival.query.filter_by(
        organization_id=user.organization_id
    ).all()

    return jsonify([
        {
            "id": f.id,
            "name": f.name,
            "description": f.description,
            "slug": f.slug
        }
        for f in festivals
    ])