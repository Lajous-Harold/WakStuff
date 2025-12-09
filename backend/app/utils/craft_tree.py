"""
Algorithme récursif pour construire l'arbre de craft d'un item.
"""
from typing import Dict, List, Any, Set
from ..models import Item, Recipe, RecipeIngredient, RecipeResult
from ..database import db


def build_craft_tree(item_wakfu_id: int, quantity: int = 1, max_depth: int = 10, _depth: int = 0, _visited: Set[int] = None) -> Dict[str, Any]:
    """
    Construit récursivement l'arbre de craft pour un item.
    Format compatible avec le frontend CraftTreeNode.
    
    Args:
        item_wakfu_id: ID Wakfu de l'item à crafter
        quantity: Quantité souhaitée
        max_depth: Profondeur maximale de récursion
        _depth: Profondeur actuelle (usage interne)
        _visited: Items déjà visités pour éviter les cycles (usage interne)
    
    Returns:
        Dict contenant l'arbre de craft au format CraftTreeNode
    
    Raises:
        ValueError: Si l'item n'existe pas
    """
    if _visited is None:
        _visited = set()
    
    # Récupérer l'item d'abord
    item = Item.query.filter_by(wakfu_id=item_wakfu_id).first()
    if not item:
        raise ValueError(f"Item {item_wakfu_id} not found")
    
    # Extraire le titre en français
    item_dict = item.to_dict(lang='fr')
    item_title = item_dict.get('title', '')
    
    # Vérifier la profondeur maximale
    if _depth >= max_depth:
        return {
            'item_id': item_wakfu_id,
            'item_wakfu_id': item_wakfu_id,
            'item_title': item_title,
            'quantity': quantity,
            'level': item_dict.get('level', 0),
            'is_resource': True,
            'children': [],
            'user_has': False,
            'max_depth_reached': True
        }
    
    # Vérifier si on a déjà visité cet item (cycle détecté)
    if item_wakfu_id in _visited:
        return {
            'item_id': item_wakfu_id,
            'item_wakfu_id': item_wakfu_id,
            'item_title': item_title,
            'quantity': quantity,
            'level': item_dict.get('level', 0),
            'is_resource': True,
            'children': [],
            'user_has': False,
            'cycle_detected': True
        }
    
    # Ajouter à la liste des visités
    _visited.add(item_wakfu_id)
    
    # Trouver les recettes qui produisent cet item
    recipe_results = RecipeResult.query.filter_by(producted_item_id=item_wakfu_id).all()
    
    if not recipe_results:
        # Pas de recette, c'est une ressource de base
        _visited.remove(item_wakfu_id)
        return {
            'item_id': item_wakfu_id,
            'item_wakfu_id': item_wakfu_id,
            'item_title': item_title,
            'quantity': quantity,
            'level': item_dict.get('level', 0),
            'is_resource': True,
            'children': [],
            'user_has': False
        }
    
    # Item craftable - prendre la première recette
    recipe_result = recipe_results[0]
    recipe = Recipe.query.filter_by(wakfu_id=recipe_result.recipe_wakfu_id).first()
    
    if not recipe:
        _visited.remove(item_wakfu_id)
        return {
            'item_id': item_wakfu_id,
            'item_wakfu_id': item_wakfu_id,
            'item_title': item_title,
            'quantity': quantity,
            'level': item_dict.get('level', 0),
            'is_resource': True,
            'children': [],
            'user_has': False
        }
    
    # Calculer combien de crafts sont nécessaires
    produced_qty = recipe_result.producted_item_quantity or 1
    crafts_needed = (quantity + produced_qty - 1) // produced_qty  # Arrondi supérieur
    
    # Construire le nœud craftable
    result = {
        'item_id': item_wakfu_id,
        'item_wakfu_id': item_wakfu_id,
        'item_title': item_title,
        'quantity': quantity,
        'level': item_dict.get('level', 0),
        'is_resource': False,
        'recipe_wakfu_id': recipe.wakfu_id,
        'children': [],
        'user_has': False
    }
    
    # Récupérer les ingrédients de cette recette
    ingredients = RecipeIngredient.query.filter_by(recipe_wakfu_id=recipe.wakfu_id).all()
    
    for ingredient in ingredients:
        ingredient_qty = (ingredient.quantity or 1) * crafts_needed
        
        # Récursion sur l'ingrédient
        ingredient_node = build_craft_tree(
            ingredient.item_id,
            ingredient_qty,
            max_depth,
            _depth + 1,
            _visited.copy()  # Copie pour chaque branche
        )
        
        result['children'].append(ingredient_node)
    
    # Retirer de la liste des visités
    _visited.remove(item_wakfu_id)
    
    return result


def get_shopping_list(craft_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrait une liste d'achat plate depuis un arbre de craft.
    
    Args:
        craft_tree: Arbre de craft généré par build_craft_tree()
    
    Returns:
        Liste des items de base nécessaires avec leurs quantités
    """
    total_ingredients = craft_tree.get('total_ingredients', {})
    
    shopping_list = []
    for item_id, quantity in total_ingredients.items():
        item = Item.query.filter_by(wakfu_id=item_id).first()
        if item:
            shopping_list.append({
                'item_id': item_id,
                'item': item.to_dict(),
                'quantity': quantity
            })
    
    # Trier par niveau puis par nom
    shopping_list.sort(key=lambda x: (x['item'].get('level', 0), x['item_id']))
    
    return shopping_list


def get_craft_steps(craft_tree: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrait les étapes de craft dans l'ordre optimal.
    
    Args:
        craft_tree: Arbre de craft généré par build_craft_tree()
    
    Returns:
        Liste des étapes de craft ordonnées par profondeur
    """
    steps = []
    
    def extract_steps(node: Dict[str, Any], step_list: List[Dict[str, Any]]):
        """Extrait récursivement les étapes."""
        if not node.get('is_craftable'):
            return
        
        # Traiter d'abord les ingrédients (profondeur d'abord)
        for recipe in node.get('recipes', []):
            for ingredient in recipe.get('ingredients', []):
                extract_steps(ingredient, step_list)
        
        # Puis ajouter cette étape
        for recipe in node.get('recipes', []):
            step_list.append({
                'depth': node['depth'],
                'item_id': node['item_id'],
                'item': node.get('item'),
                'recipe_id': recipe['recipe_id'],
                'recipe': recipe.get('recipe'),
                'crafts_needed': recipe['crafts_needed'],
                'produced_quantity': recipe['produced_quantity']
            })
    
    extract_steps(craft_tree, steps)
    
    return steps
