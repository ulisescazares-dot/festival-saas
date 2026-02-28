from datetime import datetime
import os

from flask import Blueprint, request, jsonify, send_file, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import (
    Exhibitor, Event, Festival,
    ExhibitorAccessToken, ExhibitorAgreement,
    ElectricalRequirement, EquipmentItem,
    ExhibitorDocument, User
)
from app.utils.agreement_pdf import save_signature_png, generate_agreement_pdf


agreements_bp = Blueprint("agreements", __name__, url_prefix="/agreements")
public_agreements_bp = Blueprint("public_agreements", __name__, url_prefix="/public/agreements")


# =========================================================
# HELPERS
# =========================================================

def get_current_user():
    user_id = int(get_jwt_identity())
    return User.query.get(user_id)


def exhibitor_belongs_to_user(exhibitor_id: int, user: User):
    exhibitor = Exhibitor.query.get(exhibitor_id)
    if not exhibitor:
        return None, ({"msg": "Exhibitor not found"}, 404)

    event = Event.query.get(exhibitor.event_id)
    if not event:
        return None, ({"msg": "Event not found"}, 404)

    if user.role == "admin":
        return exhibitor, None

    festival = Festival.query.filter_by(
        id=event.festival_id,
        organization_id=user.organization_id
    ).first()

    if not festival:
        return None, ({"msg": "Not allowed"}, 403)

    return exhibitor, None


def token_record_or_error(token: str):
    t = ExhibitorAccessToken.query.filter_by(
        token=token,
        purpose="agreement",
        is_revoked=False
    ).first()

    if not t:
        return None, ({"msg": "Invalid token"}, 404)

    if t.expires_at < datetime.utcnow():
        return None, ({"msg": "Token expired"}, 401)

    return t, None


# =========================================================
# ORGANIZER
# =========================================================

@agreements_bp.route("/invite/<int:exhibitor_id>", methods=["POST"])
@jwt_required()
def create_agreement_invite(exhibitor_id):

    user = get_current_user()

    exhibitor, err = exhibitor_belongs_to_user(exhibitor_id, user)
    if err:
        return jsonify(err[0]), err[1]

    t = ExhibitorAccessToken(
        exhibitor_id=exhibitor.id,
        purpose="agreement"
    )

    db.session.add(t)
    db.session.commit()

    public_url = f"http://127.0.0.1:5000/public/agreements/{t.token}/page"

    return jsonify({
        "token": t.token,
        "public_url": public_url,
        "expires_at": t.expires_at.isoformat()
    }), 201


# =========================================================
# PUBLIC
# =========================================================

@public_agreements_bp.route("/<string:token>/page", methods=["GET"])
def sign_page(token):
    t, err = token_record_or_error(token)
    if err:
        return jsonify(err[0]), err[1]

    return render_template("public_sign.html")


@public_agreements_bp.route("/<string:token>/prefill", methods=["GET"])
def prefill(token):

    t, err = token_record_or_error(token)
    if err:
        return jsonify(err[0]), err[1]

    exhibitor = Exhibitor.query.get(t.exhibitor_id)
    electrical = ElectricalRequirement.query.filter_by(
        exhibitor_id=exhibitor.id
    ).first()

    equipment = EquipmentItem.query.filter_by(
        exhibitor_id=exhibitor.id
    ).all()

    return jsonify({
        "exhibitor": {
            "business_name": exhibitor.business_name,
            "legal_name": exhibitor.legal_name,
            "rfc": exhibitor.rfc,
            "email": exhibitor.email,
            "contact_name": exhibitor.contact_name,
            "phone": exhibitor.phone,
            "address": exhibitor.address,
            "instagram": exhibitor.instagram,
        },
        "electrical": None if not electrical else {
            "total_amperage": float(electrical.total_amperage) if electrical.total_amperage else None,
            "voltage": electrical.voltage,
            "needs_220": electrical.needs_220,
            "own_generator": electrical.own_generator,
            "notes": electrical.notes
        },
        "equipment": [
            {
                "name": i.name,
                "quantity": i.quantity,
                "watts": i.watts
            } for i in equipment
        ]
    }), 200


@public_agreements_bp.route("/<string:token>/submit", methods=["POST"])
def submit_all(token):

    t, err = token_record_or_error(token)
    if err:
        return jsonify(err[0]), err[1]

    payload = request.get_json() or {}

    exhibitor = Exhibitor.query.get(t.exhibitor_id)

    # ================= EXHIBITOR =================
    for k, v in (payload.get("exhibitor") or {}).items():
        setattr(exhibitor, k, v or None)

    # ================= ELECTRICAL =================
    electrical_data = payload.get("electrical") or {}
    req = ElectricalRequirement.query.filter_by(
        exhibitor_id=exhibitor.id
    ).first() or ElectricalRequirement(exhibitor_id=exhibitor.id)

    req.total_amperage = electrical_data.get("total_amperage")
    req.voltage = electrical_data.get("voltage")
    req.needs_220 = bool(electrical_data.get("needs_220"))
    req.own_generator = bool(electrical_data.get("own_generator"))
    req.notes = electrical_data.get("notes")

    db.session.add(req)

    # ================= EQUIPMENT =================
    EquipmentItem.query.filter_by(exhibitor_id=exhibitor.id).delete()

    for item in payload.get("equipment") or []:
        if not item.get("name"):
            continue

        db.session.add(EquipmentItem(
            exhibitor_id=exhibitor.id,
            name=item["name"],
            quantity=int(item.get("quantity") or 1),
            watts=item.get("watts")
        ))

    db.session.commit()

    # ================= AGREEMENT =================
    agreement_data = payload.get("agreement") or {}
    signer_name = agreement_data.get("signer_name")

    if not signer_name:
        return jsonify({"msg": "signer_name required"}), 400

    agreement = ExhibitorAgreement.query.filter_by(
        exhibitor_id=exhibitor.id
    ).first() or ExhibitorAgreement(exhibitor_id=exhibitor.id)

    agreement.accepted_reglamento = True
    agreement.accepted_carta_responsiva = True
    agreement.signer_name = signer_name
    agreement.signed_at = datetime.utcnow()
    agreement.ip_address = request.remote_addr
    agreement.user_agent = request.headers.get("User-Agent", "")[:250]

    sig_path = None
    if agreement_data.get("signature_base64"):
        sig_filename = f"exhibitor_{exhibitor.id}_sig.png"
        sig_path = save_signature_png(
            agreement_data["signature_base64"],
            sig_filename
        )
        agreement.signature_image_path = sig_path

    pdf_path = generate_agreement_pdf(
        pdf_filename=f"exhibitor_{exhibitor.id}_agreement.pdf",
        exhibitor_name=exhibitor.business_name,
        signer_name=signer_name,
        accepted_reglamento=True,
        accepted_carta=True,
        signed_at=agreement.signed_at,
        signature_png_path=sig_path,
        notes=None
    )

    agreement.pdf_path = pdf_path
    db.session.add(agreement)
    db.session.commit()

    return jsonify({
        "msg": "Signed successfully",
        "pdf_download_url": f"/public/agreements/{t.token}/pdf"
    }), 200


# =========================================================
# DASHBOARD
# =========================================================

@agreements_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    user = get_current_user()

    if user.role == "admin":
        festivals = Festival.query.all()
    else:
        festivals = Festival.query.filter_by(
            organization_id=user.organization_id
        ).all()

    data = []

    for festival in festivals:
        for event in festival.events:
            for exhibitor in event.exhibitors:

                agreement = ExhibitorAgreement.query.filter_by(
                    exhibitor_id=exhibitor.id
                ).first()

                electrical = ElectricalRequirement.query.filter_by(
                    exhibitor_id=exhibitor.id
                ).first()

                documents = ExhibitorDocument.query.filter_by(
                    exhibitor_id=exhibitor.id
                ).count()

                token_record = ExhibitorAccessToken.query.filter_by(
                    exhibitor_id=exhibitor.id,
                    purpose="agreement",
                    is_revoked=False
                ).first()

                pdf_url = None
                if agreement and token_record:
                    pdf_url = f"/public/agreements/{token_record.token}/pdf"

                data.append({
                    "festival": festival.name,
                    "event": f"{event.city} - {event.venue}" if event.venue else event.city,
                    "business_name": exhibitor.business_name,
                    "email": exhibitor.email,
                    "signed": bool(agreement and agreement.signed_at),
                    "pdf_url": pdf_url,
                    "total_amperage": float(electrical.total_amperage) if electrical and electrical.total_amperage else 0,
                    "documents": documents
                })

    return jsonify({
        "metrics": {
            "total_exhibitors": len(data),
            "signed": len([x for x in data if x["signed"]]),
            "pending": len([x for x in data if not x["signed"]]),
            "total_amperage": sum([x["total_amperage"] for x in data])
        },
        "rows": data
    }), 200


@agreements_bp.route("/panel", methods=["GET"])
def panel_page():
    return render_template("panel.html")