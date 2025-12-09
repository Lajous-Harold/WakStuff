"""
Routes API pour les recettes et le craft.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from ..database import db
from ..models import Recipe, RecipeIngredient, RecipeResult, RecipeCategory, Item
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
    
    # Enrichir chaque recette avec le nom de l'item produit
    recipes_with_names = []
    for recipe in pagination.items:
        recipe_dict = recipe.to_dict()
        
        # Trouver l'item produit par cette recette
        result = RecipeResult.query.filter_by(recipe_wakfu_id=recipe.wakfu_id).first()
        if result:
            item = Item.query.filter_by(wakfu_id=result.producted_item_id).first()
            if item:
                item_dict = item.to_dict(lang='fr')
                recipe_dict['name'] = item_dict.get('title', f'Recette #{recipe.wakfu_id}')
                recipe_dict['item_wakfu_id'] = result.producted_item_id
            else:
                recipe_dict['name'] = f'Recette #{recipe.wakfu_id}'
        else:
            recipe_dict['name'] = f'Recette #{recipe.wakfu_id}'
        
        recipes_with_names.append(recipe_dict)
    
    return jsonify({
        'recipes': recipes_with_names,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/<int:wakfu_id>', methods=['GET'])
def get_recipe_detail(wakfu_id):
    """
    GET /api/recipes/<wakfu_id>
    
    Détails d'une recette avec ingrédients et résultats enrichis.
    """
    recipe = Recipe.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    
    # Récupérer les ingrédients et enrichir avec les noms
    ingredients = RecipeIngredient.query.filter_by(recipe_wakfu_id=wakfu_id).all()
    ingredients_list = []
    for ing in ingredients:
        ing_dict = ing.to_dict()
        # Enrichir avec le nom de l'item
        item = Item.query.filter_by(wakfu_id=ing.item_id).first()
        if item:
            item_dict = item.to_dict(lang='fr')
            ing_dict['item_title'] = item_dict.get('title', f'Item #{ing.item_id}')
            ing_dict['item_wakfu_id'] = ing.item_id
        else:
            ing_dict['item_title'] = f'Item #{ing.item_id}'
            ing_dict['item_wakfu_id'] = ing.item_id
        ingredients_list.append(ing_dict)
    
    # Récupérer les résultats et enrichir avec les noms
    results = RecipeResult.query.filter_by(recipe_wakfu_id=wakfu_id).all()
    results_list = []
    for res in results:
        res_dict = res.to_dict()
        # Enrichir avec le nom de l'item produit
        item = Item.query.filter_by(wakfu_id=res.producted_item_id).first()
        if item:
            item_dict = item.to_dict(lang='fr')
            res_dict['produced_item_title'] = item_dict.get('title', f'Item #{res.producted_item_id}')
            res_dict['produced_item_wakfu_id'] = res.producted_item_id
            res_dict['quantity'] = res.producted_item_quantity
        else:
            res_dict['produced_item_title'] = f'Item #{res.producted_item_id}'
            res_dict['produced_item_wakfu_id'] = res.producted_item_id
            res_dict['quantity'] = res.producted_item_quantity
        results_list.append(res_dict)
    
    return jsonify({
        'recipe': recipe.to_dict(),
        'ingredients': ingredients_list,
        'results': results_list
    })


@bp.route('/craft-tree/<int:item_wakfu_id>', methods=['GET'])
def get_craft_tree(item_wakfu_id):
    """
    GET /api/recipes/craft-tree/<item_wakfu_id>
    
    Arbre de craft récursif pour un item.
    Retourne le format CraftTreeResponse attendu par le frontend.
    
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
        craft_tree = build_craft_tree(item_wakfu_id, quantity, max_depth)
        
        # Récupérer la recette si l'item est craftable
        recipe_info = None
        if not craft_tree.get('is_resource') and craft_tree.get('recipe_wakfu_id'):
            recipe = Recipe.query.filter_by(wakfu_id=craft_tree['recipe_wakfu_id']).first()
            if recipe:
                recipe_dict = recipe.to_dict(lang='fr')
                recipe_info = {
                    'id': recipe_dict.get('id'),
                    'wakfu_id': recipe_dict.get('wakfu_id'),
                    'level': recipe_dict.get('level'),
                    'recipe_category_id': recipe_dict.get('recipe_category_id')
                }
        
        return jsonify({
            'recipe': recipe_info,
            'craft_tree': craft_tree
        })
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
