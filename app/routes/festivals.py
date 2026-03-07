from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Festival, User, Competition
import re
import io
import openpyxl

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

@festivals_bp.route("/<int:festival_id>/competitions", methods=["GET"])
@jwt_required()
def list_competitions(festival_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify([]), 200

    competitions = Competition.query.filter_by(festival_id=festival.id).all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug
        }
        for c in competitions
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

@festivals_bp.route("/<int:festival_id>/exhibitors", methods=["GET"])
@jwt_required()
def list_exhibitors(festival_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify([]), 200

    exhibitors = []

    for event in festival.events:
        for ex in event.exhibitors:
            exhibitors.append({
                "id": ex.id,
                "festival": festival.name,
                "event": event.city,
                "business_name": ex.business_name,
                "email": ex.email,
                "signed": bool(ex.signature_base64),
                "total_amperage": ex.total_amperage or 0
            })

    return jsonify(exhibitors)

@festivals_bp.route("/<int:festival_id>/export", methods=["GET"])
@jwt_required()
def export_exhibitors(festival_id):

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    festival = Festival.query.filter_by(
        id=festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return jsonify({"msg": "Not found"}), 404

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Negocio", "Email", "Evento", "Firmado", "Amperaje"])

    for event in festival.events:
        for ex in event.exhibitors:
            ws.append([
                ex.business_name,
                ex.email,
                event.city,
                "Sí" if ex.signature_base64 else "No",
                ex.total_amperage or 0
            ])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        download_name="expositores.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )