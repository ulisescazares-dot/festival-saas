from flask import Blueprint, render_template, request, jsonify, current_app
from app.models import (
    Festival,
    Exhibitor,
    Event,
    ExhibitorDocument,
    Competition,
    CompetitionParticipant
)
from app.extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import stripe

public_festival_bp = Blueprint(
    "public_festival",
    __name__,
    url_prefix="/public"
)

UPLOAD_FOLDER = "uploads"

# =========================================
# FESTIVAL PAGE
# =========================================
@public_festival_bp.route("/f/<string:slug>", methods=["GET"])
def festival_page(slug):

    festival = Festival.query.filter_by(slug=slug).first()

    if not festival:
        return "Festival no encontrado", 404

    return render_template("public_sign.html", festival=festival)


# =========================================
# REGISTER EXHIBITOR
# =========================================
@public_festival_bp.route("/f/<string:slug>/register", methods=["POST"])
def register_exhibitor(slug):

    festival = Festival.query.filter_by(slug=slug).first()
    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    data = request.get_json()

    event = festival.events[0]

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
        total_amperage=data["electrical"].get("total_amperage"),
        voltage=data["electrical"].get("voltage"),
        needs_220=data["electrical"].get("needs_220"),
        own_generator=data["electrical"].get("own_generator"),
        electrical_notes=data["electrical"].get("notes"),
        accepted_reglamento=data["agreement"].get("accepted_reglamento"),
        accepted_carta_responsiva=data["agreement"].get("accepted_carta_responsiva"),
        signer_name=data["agreement"].get("signer_name"),
        signature_base64=data["agreement"].get("signature_base64")
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


# =========================================
# COMPETITION PAGE
# =========================================
@public_festival_bp.route("/f/<string:festival_slug>/competencia/<string:competition_slug>")
def competition_page(festival_slug, competition_slug):

    festival = Festival.query.filter_by(slug=festival_slug).first()
    if not festival:
        return "Festival no encontrado", 404

    competition = Competition.query.filter_by(
        festival_id=festival.id,
        slug=competition_slug
    ).first()

    if not competition:
        return "Competencia no encontrada", 404

    return render_template(
        "competition_register.html",
        festival=festival,
        competition=competition
    )


# =========================================
# REGISTER COMPETITION + STRIPE
# =========================================
@public_festival_bp.route(
    "/f/<string:festival_slug>/competencia/<string:competition_slug>/register",
    methods=["POST"]
)
def register_competition(festival_slug, competition_slug):

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    festival = Festival.query.filter_by(slug=festival_slug).first()
    if not festival:
        return jsonify({"msg": "Festival not found"}), 404

    competition = Competition.query.filter_by(
        festival_id=festival.id,
        slug=competition_slug
    ).first()

    if not competition:
        return jsonify({"msg": "Competition not found"}), 404

    data = request.get_json()

    participant = CompetitionParticipant(
        competition_id=competition.id,
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        age=data["age"],
        coffee_shop=data["coffee_shop"],
        payment_status="pending"
    )

    db.session.add(participant)
    db.session.commit()

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "mxn",
                "product_data": {
                    "name": f"Registro {competition.name}"
                },
                "unit_amount": 35000
            },
            "quantity": 1
        }],
        success_url=f"https://TU-DOMINIO/payment-success/{participant.id}",
        cancel_url=f"https://TU-DOMINIO/payment-cancel"
    )

    participant.stripe_session_id = session.id
    db.session.commit()

    return jsonify({"checkout_url": session.url})


# =========================================
# STRIPE WEBHOOK
# =========================================
@public_festival_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
    )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        participant = CompetitionParticipant.query.filter_by(
            stripe_session_id=session["id"]
        ).first()

        if participant:
            participant.payment_status = "paid"
            db.session.commit()

    return "", 200