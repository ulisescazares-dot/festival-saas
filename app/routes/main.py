from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return "<h1>Festival SaaS está en producción 🚀</h1>"