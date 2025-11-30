from flask import Blueprint, send_file, abort, current_app
import requests
from io import BytesIO

proxy_bp = Blueprint("proxy", __name__)


@proxy_bp.get("/icon/<int:icon_gfx_id>")
def proxy_icon(icon_gfx_id: int):
    """
    Proxy pour les icônes Wakfu.
    Télécharge l'icône depuis le CDN Ankama et la retourne.
    Cela permet de contourner les problèmes CORS.
    """
    base_url = current_app.config.get("ICON_BASE_URL", "").rstrip("/")
    if not base_url:
        abort(404)

    icon_url = f"{base_url}/{icon_gfx_id}.png"

    try:
        response = requests.get(icon_url, timeout=10)
        response.raise_for_status()

        return send_file(
            BytesIO(response.content),
            mimetype="image/png",
            download_name=f"{icon_gfx_id}.png",
        )
    except requests.RequestException:
        abort(404)
