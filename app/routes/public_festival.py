from flask import Blueprint, render_template, request, jsonify
from app.models import Festival, Exhibitor, Event, ExhibitorDocument
from app.extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

public_festival_bp = Blueprint("public_festival", __name__)

UPLOAD_FOLDER = "uploads"


# =========================================
# PAGE
# =========================================
@public_festival_bp.route("/f/<string:slug>", methods=["GET"])
def festival_page(slug):

    festival = Festival.query.filter_by(slug=slug).first()

    if not festival:
        return "Festival no encontrado", 404

    return render_template("festival_register.html")


# =========================================
# REGISTER EXHIBITOR
# =========================================
@public_festival_bp.route("/f/<string:slug>/register", methods=["POST"])
def register_exhibitor(slug):

    festival = Festival.query.filter_by(slug=slug).first()
    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    data = request.get_json()

    if not data.get("exhibitor"):
        return jsonify({"msg": "Invalid data"}), 400

    # 🔥 Tomamos el primer evento del festival
    event = festival.events[0] if festival.events else None

    if not event:
        return jsonify({"msg": "No event configured"}), 400

    exhibitor = Exhibitor(
        event_id=event.id,
        business_name=data["exhibitor"]["business_name"],
        legal_name=data["exhibitor"].get("legal_name"),
        rfc=data["exhibitor"].get("rfc"),
        email=data["exhibitor"]["email"],
        contact_name=data["exhibitor"]["contact_name"],
        phone=data["exhibitor"].get("phone"),
        address=data["exhibitor"].get("address"),
        instagram=data["exhibitor"].get("instagram"),
        created_at=datetime.utcnow()
    )

    db.session.add(exhibitor)
    db.session.commit()

    return jsonify({
        "msg": "Registrado correctamente",
        "exhibitor_id": exhibitor.id
    }), 201


# =========================================
# UPLOAD DOCUMENTS
# =========================================
@public_festival_bp.route("/f/<string:slug>/<int:exhibitor_id>/upload", methods=["POST"])
def upload_documents(slug, exhibitor_id):

    festival = Festival.query.filter_by(slug=slug).first()
    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    file = request.files.get("file")
    doc_type = request.form.get("doc_type")

    if not file:
        return jsonify({"msg": "No file"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(path)

    doc = ExhibitorDocument(
        exhibitor_id=exhibitor_id,
        file_path=path,
        doc_type=doc_type
    )

    db.session.add(doc)
    db.session.commit()

    return jsonify({"msg": "Documento subido"}), 201