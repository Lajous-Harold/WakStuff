from flask import Blueprint, jsonify, current_app

from ..pipeline.full_import import run_full_wakfu_import
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
    Utilise maintenant le système complet avec classification et parsing d'effets.
    """
    try:
        batch = run_full_wakfu_import()
        
        payload = serialize_batch(batch)
        payload["batch_id"] = batch.id
        
        return jsonify(payload), 201
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'import: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Erreur lors de l'import des données Wakfu"
        }), 500


@imports_bp.get("/")
def list_imports():
    """
    Retourne les derniers imports, le plus récent en premier.
    """
    batches = ImportBatch.query.order_by(ImportBatch.started_at.desc()).limit(20).all()

    return jsonify([serialize_batch(b) for b in batches]), 200


@imports_bp.delete("/")
def delete_all_imports():
    """
    Supprime toutes les données de la base mais conserve la structure des tables.
    Cela inclut :
    - Import batches
    - Items bruts (item_raw)
    - Items parsés
    - Catégories d'items
    - Recettes
    - Actions
    - États
    - Métiers
    - Ressources de récolte
    """
    try:
        from ..database import db
        from ..models import (
            Item, ItemRaw, ItemCategory, Recipe, 
            Action, State, Job, HarvestResource
        )
        
        # Compter avant suppression
        import_count = ImportBatch.query.count()
        item_count = Item.query.count()
        recipe_count = Recipe.query.count()
        action_count = Action.query.count()
        state_count = State.query.count()
        job_count = Job.query.count()
        
        # Supprimer toutes les données dans l'ordre (respecter les FK)
        HarvestResource.query.delete()
        Recipe.query.delete()
        Item.query.delete()
        ItemRaw.query.delete()  # Dépend de ImportBatch
        ItemCategory.query.delete()
        Action.query.delete()
        State.query.delete()
        Job.query.delete()
        ImportBatch.query.delete()
        
        db.session.commit()
        
        message = (
            f"Base de données nettoyée : "
            f"{import_count} import(s), "
            f"{item_count} item(s), "
            f"{recipe_count} recette(s), "
            f"{action_count} action(s), "
            f"{state_count} état(s), "
            f"{job_count} métier(s) supprimé(s)"
        )
        
        current_app.logger.info(message)
        
        return jsonify({
            "message": message,
            "deleted": {
                "imports": import_count,
                "items": item_count,
                "recipes": recipe_count,
                "actions": action_count,
                "states": state_count,
                "jobs": job_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur lors du nettoyage de la base: {e}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Erreur lors du nettoyage de la base de données"
        }), 500
