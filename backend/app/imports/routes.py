from flask import Blueprint, jsonify, current_app

from ..pipeline.import_items import run_full_import
from ..models import ImportBatch

imports_bp = Blueprint("imports", __name__)


def serialize_batch(batch: ImportBatch) -> dict:
    """
    Sérialise un ImportBatch pour l'API.
    """
    return {
        "id": batch.id,
        "game_version": batch.game_version,
        "started_at": batch.started_at.isoformat() if batch.started_at else None,
        "ended_at": batch.ended_at.isoformat() if batch.ended_at else None,
        "status": batch.status,
        "total_items": batch.total_items,
        "error_count": batch.error_count,
    }


def build_icon_url(icon_gfx_id: int | None) -> str | None:
    """
    Génère l'URL de l'icône d'un item à partir de son icon_gfx_id.
    Utilise un proxy local pour contourner les problèmes CORS.
    """
    if not icon_gfx_id:
        return None

    # Utilise le proxy local avec l'URL complète
    return f"http://localhost:5000/api/proxy/icon/{icon_gfx_id}"


@imports_bp.post("/run")
def run_import():
    """
    Lance un import complet depuis l'API Wakfu via WakStuff.
    """
    batch = run_full_import()

    payload = serialize_batch(batch)
    payload["batch_id"] = batch.id

    return jsonify(payload), 201


@imports_bp.get("/")
def list_imports():
    """
    Retourne les derniers imports, le plus récent en premier.
    """
    batches = ImportBatch.query.order_by(ImportBatch.started_at.desc()).limit(20).all()

    return jsonify([serialize_batch(b) for b in batches]), 200
