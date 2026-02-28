from urllib import response

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User
from flask import render_template
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
from app.models import User, Organization

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "User already exists"}), 400

    org = Organization(
        name=data.get("organization_name", "My Organization")
    )
    db.session.add(org)
    db.session.flush()

    user = User(
        email=data["email"],
        organization_id=org.id,
        role="owner"
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User and organization created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "Bad credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    response = jsonify({"msg": "Login successful"})
    set_access_cookies(response, access_token)

    return response, 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    return jsonify({"logged_in_as": user_id}), 200

@auth_bp.route("/login-page", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/register-page", methods=["GET"])
def register_page():
    return render_template("register.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200