"""
Exemple d'utilisation du calculateur de ressources de craft.

Ce script montre comment utiliser le système pour calculer
les ressources nécessaires pour crafter un item.
"""

import sys
from pathlib import Path

# Ajouter le backend au path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app import create_app
from app.models import Item, Recipe

# Exemple: Calculer les ressources pour un item donné
def example_craft_calculator(item_wakfu_id: int):
    """
    Exemple de calcul de ressources pour un craft.
    
    Args:
        item_wakfu_id: ID Wakfu de l'item à crafter
    """
    app = create_app()
    
    with app.app_context():
        item = Item.query.filter_by(wakfu_id=item_wakfu_id).first()
        
        if not item:
            print(f"Item {item_wakfu_id} non trouvé")
            return
        
        print(f"\nCalculateur de Craft")
        print(f"=" * 60)
        print(f"Item: {item.name}")
        print(f"Niveau: {item.level}")
        print(f"Rareté: {item.rarity}")
        print(f"=" * 60)
        
        recipe = Recipe.query.filter_by(result_item_id=item_wakfu_id).first()
        
        if not recipe:
            print("\nCet item n'a pas de recette de craft (ressource de base)")
            return
        
        print(f"\nRecette:")
        print(f"   Métier requis: ID {recipe.job_id}")
        print(f"   Niveau requis: {recipe.craft_level}")
        print(f"\nIngrédients directs:")
        
        total_resources = {}
        
        for ingredient in recipe.ingredients:
            ing_item_id = ingredient["item_id"]
            ing_quantity = ingredient["quantity"]
            
            ing_item = Item.query.filter_by(wakfu_id=ing_item_id).first()
            ing_name = ing_item.name if ing_item else f"Item #{ing_item_id}"
            
            print(f"   - {ing_quantity}x {ing_name}")
            
            sub_resources = _calculate_recursive(ing_item_id, ing_quantity)
            
            for res_id, res_qty in sub_resources.items():
                total_resources[res_id] = total_resources.get(res_id, 0) + res_qty
        
        print(f"\nRessources totales nécessaires:")
        
        for res_id, res_qty in sorted(total_resources.items(), key=lambda x: -x[1])[:10]:
            res_item = Item.query.filter_by(wakfu_id=res_id).first()
            res_name = res_item.name if res_item else f"Item #{res_id}"
            res_category = res_item.category.name if res_item and res_item.category else "?"
            
            print(f"   - {res_qty:>4}x {res_name:<30} [{res_category}]")
        
        if len(total_resources) > 10:
            print(f"   ... et {len(total_resources) - 10} autres ressources")
        
        print(f"\nTotal: {len(total_resources)} ressources différentes")


def _calculate_recursive(item_id: int, quantity: int = 1, depth: int = 0, max_depth: int = 10) -> dict:
    """Calcule récursivement les ressources."""
    if depth >= max_depth:
        return {item_id: quantity}
    
    resources = {}
    
    # Trouver la recette
    recipe = Recipe.query.filter_by(result_item_id=item_id).first()
    
    if not recipe:
        # Ressource de base
        resources[item_id] = quantity
        return resources
    
    # Pour chaque ingrédient
    for ingredient in recipe.ingredients:
        ing_item_id = ingredient["item_id"]
        ing_quantity = ingredient["quantity"] * quantity
        
        # Récursion
        sub_resources = _calculate_recursive(ing_item_id, ing_quantity, depth + 1, max_depth)
        
        # Fusionner
        for res_id, res_qty in sub_resources.items():
            resources[res_id] = resources.get(res_id, 0) + res_qty
    
    return resources


if __name__ == "__main__":
    # Exemple avec un item ID
    # Remplacez par un vrai ID Wakfu après l'import
    
    if len(sys.argv) > 1:
        item_id = int(sys.argv[1])
    else:
        # ID par défaut (à remplacer)
        item_id = 2021
        print(f"Usage: python craft_calculator_example.py <item_wakfu_id>")
        print(f"Utilisation de l'ID par défaut: {item_id}\n")
    
    example_craft_calculator(item_id)
