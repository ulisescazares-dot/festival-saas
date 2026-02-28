from flask import Flask
from app.extensions import db, migrate, jwt
from dotenv import load_dotenv

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Importar modelos ANTES de usarlos
    from app.models import User

    # Crear tablas y usuario admin automáticamente
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="admin@festival.com").first():
            u = User(email="admin@festival.com", role="admin")
            u.set_password("123456")
            db.session.add(u)
            db.session.commit()

    # Importar blueprints
    from app.routes.auth import auth_bp
    from app.routes.festivals import festivals_bp
    from app.routes.events import events_bp
    from app.routes.exhibitors import exhibitors_bp
    from app.routes.electrical import electrical_bp
    from app.routes.equipment import equipment_bp
    from app.routes.electrical_summary import summary_bp
    from app.routes.agreements import agreements_bp, public_agreements_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(festivals_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(exhibitors_bp)
    app.register_blueprint(electrical_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(summary_bp)
    app.register_blueprint(agreements_bp)
    app.register_blueprint(public_agreements_bp)
    app.register_blueprint(main_bp)

    return app