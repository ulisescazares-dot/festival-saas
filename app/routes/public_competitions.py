from flask import Blueprint, request, jsonify, current_app
from app.models import Competition, CompetitionParticipant
from app.extensions import db
import stripe

public_competitions_bp = Blueprint(
    "public_competitions",
    __name__,
    url_prefix="/public"
)

# ====================================
# CREATE CHECKOUT SESSION
# ====================================
@public_competitions_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    data = request.json

    competition_id = data.get("competition_id")
    full_name = data.get("full_name")
    phone = data.get("phone")
    age = data.get("age")
    cafe = data.get("cafe")

    competition = Competition.query.get_or_404(competition_id)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[{
            "price_data":{
                "currency":"mxn",
                "product_data":{
                    "name": competition.name
                },
                "unit_amount": int(competition.price) * 100
            },
            "quantity":1
        }],
        success_url=f"{request.host_url}public/success",
        cancel_url=f"{request.host_url}public/cancel",
        metadata={
            "competition_id": str(competition_id),
            "full_name": full_name,
            "phone": phone,
            "age": str(age),
            "cafe": cafe
        }
    )

    return jsonify({"url": session.url})


# ====================================
# STRIPE WEBHOOK
# ====================================
@public_competitions_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():

    stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = current_app.config["STRIPE_WEBHOOK_SECRET"]

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        participant_id = session["metadata"].get("participant_id")

        participant = CompetitionParticipant.query.get(participant_id)

        if participant:
            participant.payment_status = "paid"
            participant.paid = True
            db.session.commit()

    return "", 200