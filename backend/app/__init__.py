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

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    from .items.routes import items_bp
    from .imports.routes import imports_bp
    from .proxy.routes import proxy_bp

    app.register_blueprint(items_bp, url_prefix="/api/items")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")
    app.register_blueprint(proxy_bp, url_prefix="/api/proxy")

    return app
