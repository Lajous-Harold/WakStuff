"""
Routes API pour gérer les imports de données Wakfu.
Permet de lancer l'import complet manuellement via POST /api/imports/full
"""

from flask import Blueprint, jsonify, request
from ..database import db
from ..models import ImportBatch
from ..pipeline.full_import import (
    run_full_wakfu_import,
    get_import_stats,
    clear_all_data
)
import logging

bp = Blueprint('imports', __name__, url_prefix='/api/imports')
logger = logging.getLogger(__name__)


@bp.route('/full', methods=['POST'])
def launch_full_import():
    """
    Lance l'import complet de toutes les données Wakfu.
    
    POST /api/imports/full
    
    Body (optionnel):
    {
        "clear_before": true  // Supprimer les données avant l'import
    }
    
    Retourne:
    {
        "status": "success",
        "batch_id": 1,
        "stats": {...},
        "message": "Import terminé avec succès"
    }
    """
    try:
        data = request.get_json() or {}
        clear_before = data.get('clear_before', False)
        
        # Nettoyer si demandé
        if clear_before:
            logger.info("Suppression des données existantes...")
            clear_all_data()
        
        # Lancer l'import
        logger.info("Lancement de l'import complet...")
        batch = run_full_wakfu_import()
        
        # Récupérer les stats
        stats = get_import_stats()
        
        return jsonify({
            "status": "success",
            "batch_id": batch.id,
            "stats": stats,
            "metadata": batch.import_metadata,
            "message": f"Import terminé avec succès! {batch.items_imported} entrées importées.",
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Récupère les statistiques de la base de données.
    
    GET /api/imports/stats
    
    Retourne le nombre d'entrées pour chaque table.
    """
    try:
        stats = get_import_stats()
        
        # Calculer les totaux par phase
        phase_1_total = (
            stats['recipe_categories'] + 
            stats['item_types'] + 
            stats['equipment_item_types'] + 
            stats['resource_types']
        )
        phase_2_total = (
            stats['resources'] + 
            stats['collectable_resources'] + 
            stats['harvest_loots'] + 
            stats['harvest_resources']
        )
        phase_3_total = stats['job_items'] + stats['items']
        phase_4_total = (
            stats['recipes'] + 
            stats['recipe_ingredients'] + 
            stats['recipe_results']
        )
        grand_total = phase_1_total + phase_2_total + phase_3_total + phase_4_total
        
        return jsonify({
            "stats": stats,
            "summary": {
                "phase_1_total": phase_1_total,
                "phase_2_total": phase_2_total,
                "phase_3_total": phase_3_total,
                "phase_4_total": phase_4_total,
                "grand_total": grand_total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route('/batches', methods=['GET'])
def get_batches():
    """
    Liste tous les batches d'import.
    
    GET /api/imports/batches?limit=10
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        batches = ImportBatch.query.order_by(
            ImportBatch.started_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            "batches": [b.to_dict() for b in batches]
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des batches: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@bp.route('/clear', methods=['POST'])
def clear_data():
    """
    Supprime toutes les données importées.
    
    POST /api/imports/clear
    
    Body:
    {
        "confirm": true  // Obligatoire pour confirmer
    }
    """
    try:
        data = request.get_json() or {}
        
        if not data.get('confirm'):
            return jsonify({
                "status": "error",
                "message": "Confirmation requise (confirm: true)"
            }), 400
        
        clear_all_data()
        
        return jsonify({
            "status": "success",
            "message": "Toutes les données ont été supprimées"
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
