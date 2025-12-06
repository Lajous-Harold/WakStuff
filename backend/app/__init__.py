from flask import Flask, jsonify
from .config import Config
from .database import db
from flask_cors import CORS


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Tables will be created on first import via API
    # No automatic db.create_all() to avoid duplicate issues

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200

    # Enregistrement des blueprints
    from .items.routes import bp as items_bp
    from .resources.routes import bp as resources_bp
    from .recipes.routes import bp as recipes_bp
    from .categories.routes import bp as categories_bp
    from .harvest.routes import bp as harvest_bp
    from .imports.routes import bp as imports_bp
    from .proxy.routes import proxy_bp
    from .stats.routes import bp as stats_bp

    app.register_blueprint(items_bp, url_prefix="/api/items")
    app.register_blueprint(resources_bp, url_prefix="/api/resources")
    app.register_blueprint(recipes_bp, url_prefix="/api/recipes")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(harvest_bp, url_prefix="/api/harvest")
    app.register_blueprint(imports_bp, url_prefix="/api/imports")
    app.register_blueprint(proxy_bp, url_prefix="/api/proxy")
    app.register_blueprint(stats_bp, url_prefix="/api/stats")
    # Le même blueprint stats contient aussi les routes /search
    # Flask gère automatiquement les routes avec différents prefixes

    return app

