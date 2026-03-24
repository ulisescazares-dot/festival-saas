from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Competition, Festival, User
from app.extensions import db
import re
from app.models import CompetitionParticipant

admin_competitions_bp = Blueprint(
    "admin_competitions",
    __name__,
    url_prefix="/admin/Competitions"
)

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


# ====================================
# CREAR COMPETENCIA
# ====================================
@admin_competitions_bp.route("", methods=["POST"])
@jwt_required()
def create_competition():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json()
    festival_id = data.get("festival_id")

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
        slug=slug,
        price=data.get("price", 350)
    )

    db.session.add(competition)
    db.session.commit()

    return jsonify({
        "msg": "Competition created",
        "public_url": f"/public/f/{festival.slug}/competencia/{slug}"
    }), 201


# ====================================
# LISTAR COMPETENCIAS POR FESTIVAL
# ====================================
@admin_competitions_bp.route("/festival/<int:festival_id>", methods=["GET"])
@jwt_required()
def list_competitions(festival_id):

    competitions = Competition.query.filter_by(
        festival_id=festival_id
    ).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "price": c.price
        }
        for c in competitions
    ])


# ====================================
# LISTAR PARTICIPANTES PAGADOS POR COMPETENCIA
# ====================================
@admin_competitions_bp.route("/<int:competition_id>/participants", methods=["GET"])
@jwt_required()
def list_participants(competition_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    competition = Competition.query.get_or_404(competition_id)

    # Seguridad: validar que la competencia pertenece a la organización del usuario
    if competition.festival.organization_id != user.organization_id:
        return jsonify({"msg": "Not authorized"}), 403

    participants = CompetitionParticipant.query.filter(
        CompetitionParticipant.competition_id == competition_id,
        CompetitionParticipant.paid.is_(True)
    ).order_by(CompetitionParticipant.created_at.desc()).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "email": p.email,
            "phone": p.phone,
            "coffee_shop": p.coffee_shop,
            "paid": p.paid,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for p in participants
    ])