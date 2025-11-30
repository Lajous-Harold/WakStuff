from flask import Flask, jsonify
from .config import Config
from .database import db
from .models import Item, ItemRaw, ImportBatch 
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    # Healthcheck simple
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # Blueprints
    from .items.routes import items_bp
    from .imports.routes import imports_bp

    app.register_blueprint(items_bp, url_prefix="/api/items")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")

    return app
