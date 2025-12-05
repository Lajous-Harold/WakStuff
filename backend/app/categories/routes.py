"""
Routes API pour les catégories de métiers.
"""
from flask import Blueprint, jsonify, request
from ..database import db
from ..models import RecipeCategory, Recipe, CollectibleResource

bp = Blueprint('categories', __name__)


@bp.route('', methods=['GET'])
def get_categories():
    """
    GET /api/categories
    
    Liste toutes les catégories de métiers.
    
    Query params:
    - category_type: 'harvest' ou 'craft'
    """
    category_type = request.args.get('category_type')
    
    query = RecipeCategory.query
    
    if category_type:
        query = query.filter(RecipeCategory.category_type == category_type)
    
    query = query.order_by(RecipeCategory.id)
    categories = query.all()
    
    return jsonify({
        'categories': [c.to_dict() for c in categories]
    })


@bp.route('/<int:category_id>', methods=['GET'])
def get_category_detail(category_id):
    """
    GET /api/categories/<category_id>
    
    Détails d'une catégorie avec ses recettes ou ressources.
    """
    category = RecipeCategory.query.get_or_404(category_id)
    
    response = {
        'category': category.to_dict()
    }
    
    # Si c'est un métier de craft, récupérer les recettes
    if category.category_type == 'craft':
        recipes = Recipe.query.filter_by(recipe_category_id=category_id).limit(100).all()
        response['recipes'] = [r.to_dict() for r in recipes]
        response['recipe_count'] = Recipe.query.filter_by(recipe_category_id=category_id).count()
    
    # Si c'est un métier de récolte, récupérer les ressources collectables
    elif category.category_type == 'harvest' and category.skill_id:
        collectables = CollectibleResource.query.filter_by(skill_id=category.skill_id).limit(100).all()
        response['collectables'] = [c.to_dict() for c in collectables]
        response['collectable_count'] = CollectibleResource.query.filter_by(skill_id=category.skill_id).count()
    
    return jsonify(response)


@bp.route('/by-skill/<int:skill_id>', methods=['GET'])
def get_category_by_skill(skill_id):
    """
    GET /api/categories/by-skill/<skill_id>
    
    Trouve la catégorie de métier par son skill_id.
    Utile pour les métiers de récolte (64, 71, 72, 73, 75).
    """
    category = RecipeCategory.query.filter_by(skill_id=skill_id).first_or_404()
    
    return jsonify({
        'category': category.to_dict()
    })
