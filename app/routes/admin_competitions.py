from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Competition, Festival, User
from app.extensions import db
import re

admin_competitions_bp = Blueprint(
    "admin_competitions",
    __name__,
    url_prefix="/admin/competitions"
)

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


@admin_competitions_bp.route("", methods=["POST"])
@jwt_required()
def create_competition():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json()
    festival_id = data.get("festival_id")

    # Validar festival
    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify({"msg": "Festival not found or not allowed"}), 404

    slug = slugify(data["name"])

    competition = Competition(
        festival_id=festival.id,
        name=data["name"],
        description=data.get("description"),
        slug=slug
    )

    db.session.add(competition)
    db.session.commit()

    return jsonify({
        "msg": "Competition created",
        "public_url": f"/f/{festival.slug}/competencia/{slug}"
    }), 201

@admin_competitions_bp.route("/<int:competition_id>/participants", methods=["GET"])
@jwt_required()
def list_participants(competition_id):

    participants = CompetitionParticipant.query.filter_by(
        competition_id=competition_id
    ).all()

    return jsonify([
        {
            "name": p.name,
            "email": p.email,
            "phone": p.phone,
            "age": p.age,
            "coffee_shop": p.coffee_shop,
            "payment_status": p.payment_status
        }
        for p in participants
    ])