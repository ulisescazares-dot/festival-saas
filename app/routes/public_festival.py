from flask import Blueprint, render_template, request, jsonify
from app.models import Festival, FestivalRegistration
from app.extensions import db

public_festival_bp = Blueprint(
    "public_festival",
    __name__,
    url_prefix="/public/festival"
)


# Mostrar página de registro
@public_festival_bp.route("/<string:slug>", methods=["GET"])
def festival_register_page(slug):

    festival = Festival.query.filter_by(slug=slug).first()

    if not festival:
        return "Festival no encontrado", 404

    return render_template("register.html", festival=festival)


# Guardar registro
@public_festival_bp.route("/<string:slug>", methods=["POST"])
def festival_register_submit(slug):

    festival = Festival.query.filter_by(slug=slug).first()

    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    data = request.get_json()

    reg = FestivalRegistration(
        festival_id=festival.id,
        full_name=data.get("full_name"),
        email=data.get("email")
    )

    db.session.add(reg)
    db.session.commit()

    return jsonify({"msg": "Registro exitoso"}), 201