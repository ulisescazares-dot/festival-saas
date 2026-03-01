from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Contest, Festival, User
from app.extensions import db
import re

admin_contests_bp = Blueprint("admin_contests", __name__, url_prefix="/admin/contests")


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


@admin_contests_bp.route("", methods=["POST"])
@jwt_required()
def create_contest():

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    data = request.get_json()
    festival_id = data.get("festival_id")

    # 🔒 Validar que el festival pertenece a su organización
    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify({"msg": "Festival not found or not allowed"}), 404

    slug = slugify(data["name"])

    contest = Contest(
        festival_id=festival.id,
        name=data["name"],
        description=data.get("description"),
        slug=slug
    )

    db.session.add(contest)
    db.session.commit()

    return jsonify({
        "msg": "Contest created",
        "public_url": f"/public/contest/{slug}"
    }), 201