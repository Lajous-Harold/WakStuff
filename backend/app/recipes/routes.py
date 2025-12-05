"""
Routes API pour les recettes et le craft.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from ..database import db
from ..models import Recipe, RecipeIngredient, RecipeResult, RecipeCategory
from ..utils.craft_tree import build_craft_tree

bp = Blueprint('recipes', __name__)


@bp.route('', methods=['GET'])
def get_recipes():
    """
    GET /api/recipes
    
    Liste des recettes avec filtrage.
    
    Query params:
    - category_id: Filtrer par catégorie de métier
    - level_min, level_max: Niveau de recette
    - search: Recherche dans le nom
    - page, per_page: Pagination
    """
    category_id = request.args.get('category_id', type=int)
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = Recipe.query
    
    if category_id:
        query = query.filter(Recipe.recipe_category_id == category_id)
    
    if level_min:
        query = query.filter(Recipe.level >= level_min)
    
    if level_max:
        query = query.filter(Recipe.level <= level_max)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(Recipe.title.cast(db.String).ilike(search_pattern))
    
    query = query.order_by(Recipe.level.desc(), Recipe.wakfu_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'recipes': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/<int:wakfu_id>', methods=['GET'])
def get_recipe_detail(wakfu_id):
    """
    GET /api/recipes/<wakfu_id>
    
    Détails d'une recette avec ingrédients et résultats.
    """
    recipe = Recipe.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    
    # Récupérer les ingrédients
    ingredients = RecipeIngredient.query.filter_by(recipe_wakfu_id=wakfu_id).all()
    
    # Récupérer les résultats
    results = RecipeResult.query.filter_by(recipe_wakfu_id=wakfu_id).all()
    
    return jsonify({
        'recipe': recipe.to_dict(),
        'ingredients': [ing.to_dict() for ing in ingredients],
        'results': [res.to_dict() for res in results]
    })


@bp.route('/craft-tree/<int:item_wakfu_id>', methods=['GET'])
def get_craft_tree(item_wakfu_id):
    """
    GET /api/recipes/craft-tree/<item_wakfu_id>
    
    Arbre de craft récursif pour un item.
    Inclut tous les ingrédients et sous-recettes nécessaires.
    
    Query params:
    - quantity: Quantité souhaitée (défaut: 1)
    - max_depth: Profondeur maximale de l'arbre (défaut: 10)
    """
    quantity = request.args.get('quantity', 1, type=int)
    max_depth = request.args.get('max_depth', 10, type=int)
    
    if quantity < 1:
        return jsonify({'error': 'Quantity must be >= 1'}), 400
    
    if max_depth < 1 or max_depth > 20:
        return jsonify({'error': 'Max depth must be between 1 and 20'}), 400
    
    try:
        tree = build_craft_tree(item_wakfu_id, quantity, max_depth)
        return jsonify(tree)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/by-result/<int:item_wakfu_id>', methods=['GET'])
def get_recipes_by_result(item_wakfu_id):
    """
    GET /api/recipes/by-result/<item_wakfu_id>
    
    Trouve toutes les recettes qui produisent cet item.
    """
    results = RecipeResult.query.filter_by(producted_item_id=item_wakfu_id).all()
    
    if not results:
        return jsonify({'recipes': []})
    
    recipe_ids = [r.recipe_wakfu_id for r in results]
    recipes = Recipe.query.filter(Recipe.wakfu_id.in_(recipe_ids)).all()
    
    return jsonify({
        'recipes': [r.to_dict() for r in recipes],
        'results': [res.to_dict() for res in results]
    })


@bp.route('/by-ingredient/<int:item_wakfu_id>', methods=['GET'])
def get_recipes_by_ingredient(item_wakfu_id):
    """
    GET /api/recipes/by-ingredient/<item_wakfu_id>
    
    Trouve toutes les recettes qui utilisent cet item comme ingrédient.
    """
    ingredients = RecipeIngredient.query.filter_by(item_id=item_wakfu_id).all()
    
    if not ingredients:
        return jsonify({'recipes': []})
    
    recipe_ids = [ing.recipe_wakfu_id for ing in ingredients]
    recipes = Recipe.query.filter(Recipe.wakfu_id.in_(recipe_ids)).all()
    
    return jsonify({
        'recipes': [r.to_dict() for r in recipes],
        'ingredients': [ing.to_dict() for ing in ingredients]
    })
