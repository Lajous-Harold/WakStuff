from flask import Flask, jsonify
from .config import Config
from .database import db
from .models import Item, ItemRaw, ImportBatch, HarvestResource
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
    from .wakfu_data.routes import bp as wakfu_data_bp
    from .test_views.routes import test_views_bp

    app.register_blueprint(items_bp, url_prefix="/api/items")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")
    app.register_blueprint(proxy_bp, url_prefix="/api/proxy")
    app.register_blueprint(wakfu_data_bp, url_prefix="/api/wakfu")
    app.register_blueprint(test_views_bp)

    return app
