"""
Routes API pour les analytics et statistiques avancées.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc
from ..database import db
from ..models import (
    Item, Recipe, Resource, RecipeIngredient, RecipeResult,
    HarvestResource, RecipeCategory, JobItem
)

bp = Blueprint('analytics', __name__)


@bp.route('/top-resources', methods=['GET'])
def get_top_resources():
    """
    GET /api/analytics/top-resources
    
    Ressources les plus demandées dans les recettes.
    
    Query params:
    - limit: Nombre de ressources à retourner (défaut: 10)
    """
    limit = request.args.get('limit', 10, type=int)
    
    # Compter les occurrences de chaque item_id dans RecipeIngredient
    top_ingredients = db.session.query(
        RecipeIngredient.item_id,
        func.count(RecipeIngredient.item_id).label('usage_count')
    ).group_by(
        RecipeIngredient.item_id
    ).order_by(
        desc('usage_count')
    ).limit(limit).all()
    
    results = []
    for item_id, count in top_ingredients:
        # Chercher dans JobItem d'abord
        job_item = JobItem.query.filter_by(wakfu_id=item_id).first()
        if job_item:
            item_data = job_item.to_dict()
        else:
            # Fallback sur Item
            item = Item.query.filter_by(wakfu_id=item_id).first()
            item_data = item.to_dict() if item else {'wakfu_id': item_id, 'title': {'fr': f'Item #{item_id}'}}
        
        results.append({
            'item': item_data,
            'usage_count': count
        })
    
    return jsonify({
        'top_resources': results,
        'total': len(results)
    })


@bp.route('/top-crafts', methods=['GET'])
def get_top_crafts():
    """
    GET /api/analytics/top-crafts
    
    Items les plus craftés (apparaissent le plus dans RecipeResult).
    
    Query params:
    - limit: Nombre d'items (défaut: 10)
    """
    limit = request.args.get('limit', 10, type=int)
    
    # Compter les recettes qui produisent chaque item
    top_results = db.session.query(
        RecipeResult.producted_item_id,
        func.count(RecipeResult.producted_item_id).label('recipe_count')
    ).group_by(
        RecipeResult.producted_item_id
    ).order_by(
        desc('recipe_count')
    ).limit(limit).all()
    
    results = []
    for item_id, count in top_results:
        # Chercher dans JobItem d'abord
        job_item = JobItem.query.filter_by(wakfu_id=item_id).first()
        if job_item:
            item_data = job_item.to_dict()
        else:
            item = Item.query.filter_by(wakfu_id=item_id).first()
            item_data = item.to_dict() if item else {'wakfu_id': item_id, 'title': {'fr': f'Item #{item_id}'}}
        
        results.append({
            'item': item_data,
            'recipe_count': count
        })
    
    return jsonify({
        'top_crafts': results,
        'total': len(results)
    })


@bp.route('/by-job', methods=['GET'])
def get_analytics_by_job():
    """
    GET /api/analytics/by-job
    
    Statistiques par métier (nombre de recettes, items, etc.).
    """
    # Compter les recettes par catégorie
    recipe_counts = db.session.query(
        RecipeCategory.wakfu_id,
        RecipeCategory.category_type,
        func.count(Recipe.id).label('recipe_count')
    ).outerjoin(
        Recipe, Recipe.recipe_category_id == RecipeCategory.id
    ).group_by(
        RecipeCategory.id
    ).all()
    
    results = []
    for cat_id, cat_type, count in recipe_counts:
        category = RecipeCategory.query.filter_by(wakfu_id=cat_id).first()
        if category:
            results.append({
                'category': category.to_dict(),
                'recipe_count': count
            })
    
    return jsonify({
        'jobs': results,
        'total': len(results)
    })


@bp.route('/level-distribution', methods=['GET'])
def get_level_distribution():
    """
    GET /api/analytics/level-distribution
    
    Distribution des items et recettes par tranche de niveau.
    """
    # Distribution items par tranche de 10 niveaux
    item_distribution = db.session.query(
        (Item.level / 10).cast(db.Integer).label('level_bracket'),
        func.count(Item.id).label('count')
    ).filter(
        Item.level.isnot(None)
    ).group_by(
        'level_bracket'
    ).order_by(
        'level_bracket'
    ).all()
    
    # Distribution recettes
    recipe_distribution = db.session.query(
        (Recipe.level / 10).cast(db.Integer).label('level_bracket'),
        func.count(Recipe.id).label('count')
    ).filter(
        Recipe.level.isnot(None)
    ).group_by(
        'level_bracket'
    ).order_by(
        'level_bracket'
    ).all()
    
    return jsonify({
        'items': [
            {'level_range': f'{int(bracket * 10)}-{int(bracket * 10 + 9)}', 'count': count}
            for bracket, count in item_distribution
        ],
        'recipes': [
            {'level_range': f'{int(bracket * 10)}-{int(bracket * 10 + 9)}', 'count': count}
            for bracket, count in recipe_distribution
        ]
    })


@bp.route('/rarity-distribution', methods=['GET'])
def get_rarity_distribution():
    """
    GET /api/analytics/rarity-distribution
    
    Répartition des items par rareté.
    """
    rarity_counts = db.session.query(
        Item.rarity,
        func.count(Item.id).label('count')
    ).filter(
        Item.rarity.isnot(None)
    ).group_by(
        Item.rarity
    ).order_by(
        Item.rarity
    ).all()
    
    rarity_names = {
        0: 'Commun',
        1: 'Rare',
        2: 'Mythique',
        3: 'Légendaire',
        4: 'Relique',
        5: 'Souvenir',
        7: 'Épique'
    }
    
    return jsonify({
        'distribution': [
            {
                'rarity': rarity,
                'name': rarity_names.get(rarity, f'Rareté {rarity}'),
                'count': count
            }
            for rarity, count in rarity_counts
        ]
    })


@bp.route('/complex-crafts', methods=['GET'])
def get_complex_crafts():
    """
    GET /api/analytics/complex-crafts
    
    Crafts les plus complexes (plus d'ingrédients).
    
    Query params:
    - limit: Nombre de crafts (défaut: 10)
    """
    limit = request.args.get('limit', 10, type=int)
    
    # Compter les ingrédients par recette
    complex_recipes = db.session.query(
        Recipe.wakfu_id,
        Recipe.level,
        func.count(RecipeIngredient.id).label('ingredient_count')
    ).join(
        RecipeIngredient, Recipe.wakfu_id == RecipeIngredient.recipe_wakfu_id
    ).group_by(
        Recipe.id
    ).order_by(
        desc('ingredient_count')
    ).limit(limit).all()
    
    results = []
    for recipe_wakfu_id, level, ing_count in complex_recipes:
        recipe = Recipe.query.filter_by(wakfu_id=recipe_wakfu_id).first()
        if recipe:
            # Obtenir le nom du résultat
            recipe_result = RecipeResult.query.filter_by(recipe_wakfu_id=recipe_wakfu_id).first()
            result_name = None
            if recipe_result:
                job_item = JobItem.query.filter_by(wakfu_id=recipe_result.producted_item_id).first()
                if job_item:
                    result_name = job_item.title.get('fr') if isinstance(job_item.title, dict) else job_item.title
                else:
                    item = Item.query.filter_by(wakfu_id=recipe_result.producted_item_id).first()
                    if item:
                        result_name = item.title.get('fr') if isinstance(item.title, dict) else item.title
            
            results.append({
                'recipe': recipe.to_dict(),
                'result_name': result_name,
                'ingredient_count': ing_count
            })
    
    return jsonify({
        'complex_crafts': results,
        'total': len(results)
    })
