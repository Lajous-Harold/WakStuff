"""
Routes API pour les statistiques et recherche globale.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from ..database import db
from ..models import Item, Resource, Recipe, JobItem, RecipeResult

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
    GET /api/stats/global?query=<text>&limit=<number>&page=<number>
    
    Recherche globale dans items, recettes et ressources avec pagination.
    """
    query_text = request.args.get('query', '').strip()
    limit = request.args.get('limit', 20, type=int)
    page = request.args.get('page', 1, type=int)
    
    if not query_text:
        return jsonify({
            'items': [],
            'recipes': [],
            'resources': [],
            'total': 0,
            'page': page,
            'per_page': limit
        })
    
    try:
        search_pattern = f'%{query_text}%'
        offset = (page - 1) * limit
        
        # Recherche dans items
        items = Item.query.filter(
            or_(
                Item.title.cast(db.String).ilike(search_pattern),
                Item.description.cast(db.String).ilike(search_pattern)
            )
        ).offset(offset).limit(limit).all()
        
        # Recherche dans resources
        resources = Resource.query.filter(
            Resource.title.cast(db.String).ilike(search_pattern)
        ).offset(offset).limit(limit).all()
        
        # Recherche dans recipes - via les items produits
        # D'abord chercher dans JobItem (priorité)
        recipes_query_job = db.session.query(Recipe, JobItem).join(
            RecipeResult, Recipe.wakfu_id == RecipeResult.recipe_wakfu_id
        ).join(
            JobItem, RecipeResult.producted_item_id == JobItem.wakfu_id
        ).filter(
            JobItem.title.cast(db.String).ilike(search_pattern)
        ).offset(offset).limit(limit).all()
        
        # Puis chercher dans Item
        recipes_query_item = db.session.query(Recipe, Item).join(
            RecipeResult, Recipe.wakfu_id == RecipeResult.recipe_wakfu_id
        ).join(
            Item, RecipeResult.producted_item_id == Item.wakfu_id
        ).filter(
            Item.title.cast(db.String).ilike(search_pattern)
        ).offset(offset).limit(limit).all()
        
        recipes_list = []
        # Traiter JobItem results
        for recipe, item in recipes_query_job:
            recipe_dict = recipe.to_dict()
            item_dict = item.to_dict(lang='fr')
            title = item_dict.get('title', '').strip()
            recipe_dict['title'] = title if title else f'Recette #{recipe.wakfu_id}'
            recipe_dict['icon_gfx_id'] = item.icon_gfx_id if item.icon_gfx_id else item.wakfu_id
            recipe_dict['produced_item_wakfu_id'] = item.wakfu_id
            recipes_list.append(recipe_dict)
        
        # Traiter Item results
        for recipe, item in recipes_query_item:
            recipe_dict = recipe.to_dict()
            item_dict = item.to_dict(lang='fr')
            title = item_dict.get('title', '').strip()
            recipe_dict['title'] = title if title else f'Recette #{recipe.wakfu_id}'
            recipe_dict['icon_gfx_id'] = item.icon_gfx_id if item.icon_gfx_id else item.wakfu_id
            recipe_dict['produced_item_wakfu_id'] = item.wakfu_id
            recipes_list.append(recipe_dict)
        
        # Enrichir items et resources avec to_dict(lang='fr')
        items_list = []
        for item in items:
            item_dict = item.to_dict(lang='fr')
            # Assurer que icon_gfx_id est présent
            if 'icon_gfx_id' not in item_dict or not item_dict['icon_gfx_id']:
                item_dict['icon_gfx_id'] = item.wakfu_id
            items_list.append(item_dict)
        
        resources_list = []
        for res in resources:
            res_dict = res.to_dict(lang='fr')
            # Assurer que icon_gfx_id est présent
            if 'icon_gfx_id' not in res_dict or not res_dict['icon_gfx_id']:
                res_dict['icon_gfx_id'] = res.wakfu_id
            resources_list.append(res_dict)
        
        return jsonify({
            'items': items_list,
            'resources': resources_list,
            'recipes': recipes_list,
            'total': len(items) + len(resources) + len(recipes_list),
            'page': page,
            'per_page': limit
        })
    except Exception:
        # Si erreur (tables n'existent pas), retourner des listes vides
        db.session.rollback()
        return jsonify({
            'items': [],
            'recipes': [],
            'resources': [],
            'total': 0,
            'page': page,
            'per_page': limit
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
