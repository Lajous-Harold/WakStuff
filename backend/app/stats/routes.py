"""
Routes API pour les statistiques et recherche globale.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from ..database import db
from ..models import Item, Resource, Recipe, JobItem

bp = Blueprint('stats', __name__)


@bp.route('/overview', methods=['GET'])
def get_stats_overview():
    """
    GET /api/stats/overview
    
    Statistiques générales de la base de données.
    Retourne toujours 200 avec des stats à 0 si pas de données.
    """
    try:
        total_items = Item.query.count()
        total_resources = Resource.query.count()
        total_recipes = Recipe.query.count()
        total_job_items = JobItem.query.count()
    except Exception:
        # Si les tables n'existent pas, retourner des stats à 0
        db.session.rollback()
        total_items = 0
        total_resources = 0
        total_recipes = 0
        total_job_items = 0
    
    return jsonify({
        'total_items': total_items,
        'total_resources': total_resources,
        'total_recipes': total_recipes,
        'total_job_items': total_job_items,
        'items_by_rarity': {},
        'recipes_by_category': {},
        'level_distribution': {}
    })


@bp.route('/global', methods=['GET'])
def global_search():
    """
    GET /api/stats/global?query=<text>&limit=<number>
    
    Recherche globale dans items, recettes et ressources.
    """
    query_text = request.args.get('query', '').strip()
    limit = request.args.get('limit', 20, type=int)
    
    if not query_text:
        return jsonify({
            'items': [],
            'recipes': [],
            'resources': [],
            'total': 0
        })
    
    try:
        search_pattern = f'%{query_text}%'
        
        # Recherche dans items
        items = Item.query.filter(
            or_(
                Item.title.cast(db.String).ilike(search_pattern),
                Item.description.cast(db.String).ilike(search_pattern)
            )
        ).limit(limit).all()
        
        # Recherche dans resources
        resources = Resource.query.filter(
            Resource.title.cast(db.String).ilike(search_pattern)
        ).limit(limit).all()
        
        # Recherche dans recipes - via les items produits
        recipes = Recipe.query.join(
            Item, Recipe.wakfu_id == Item.wakfu_id
        ).filter(
            Item.title.cast(db.String).ilike(search_pattern)
        ).limit(limit).all()
        
        return jsonify({
            'items': [item.to_dict() for item in items],
            'resources': [res.to_dict() for res in resources],
            'recipes': [recipe.to_dict() for recipe in recipes],
            'total': len(items) + len(resources) + len(recipes)
        })
    except Exception:
        # Si erreur (tables n'existent pas), retourner des listes vides
        db.session.rollback()
        return jsonify({
            'items': [],
            'recipes': [],
            'resources': [],
            'total': 0
        })


@bp.route('/recent', methods=['GET'])
def get_recent_imports():
    """
    GET /api/stats/recent?limit=<number>
    
    Récupère les derniers imports.
    """
    limit = request.args.get('limit', 5, type=int)
    
    # Pour l'instant, retourne des données factices
    # TODO: Implémenter une vraie table d'historique d'imports
    return jsonify({
        'batches': []
    })
