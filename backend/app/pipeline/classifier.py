"""
Système de classification des items Wakfu.

Basé sur les typeId et les propriétés des items pour les classer en catégories:
- Équipements (armes, armures, accessoires)
- Ressources (minerais, plantes, ingrédients)
- Consommables (potions, nourriture)
- Quête
- Cosmétiques
- etc.
"""

from typing import Any, Dict, List, Optional
from .wakfu_config import (
    WAKFU_ITEM_CATEGORIES,
    WAKFU_RARITIES,
    WAKFU_ELEMENTS,
    get_category_for_type_id as _get_category_for_type_id,
)


def get_category_from_type_id(type_id: int) -> Optional[str]:
    """
    Retourne la catégorie d'un item basé sur son typeId.

    Args:
        type_id: Le typeId de l'item

    Returns:
        Le nom de la catégorie ou None
    """
    if not type_id:
        return None

    # Utiliser la configuration centralisée
    return _get_category_for_type_id(type_id)


def classify_item(item_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Classifie un item en déterminant sa catégorie et sous-catégorie.

    Args:
        item_data: Données brutes de l'item

    Returns:
        Dict avec 'category' et 'subcategory'
    """
    definition = item_data.get("definition", {})
    item_def = definition.get("item", {})
    base_params = item_def.get("baseParameters", {})

    # Récupérer le typeId
    type_id = base_params.get("itemTypeId")
    if not type_id:
        type_id = item_def.get("itemTypeId") or item_def.get("typeId")

    # Déterminer la catégorie
    category_path = get_category_from_type_id(type_id)

    if category_path and "." in category_path:
        category, subcategory = category_path.split(".", 1)
    else:
        category = category_path or "misc"
        subcategory = None

    # Heuristiques supplémentaires
    if not subcategory:
        # Vérifier si c'est une ressource craftable
        if _is_craftable_resource(item_data):
            category = "resources"
            subcategory = "crafting_ingredients"

        # Vérifier si c'est un consommable
        elif _is_consumable(item_data):
            category = "consumables"
            subcategory = "food" if _is_food(item_data) else "potions"

    return {"category": category, "subcategory": subcategory or "general"}


def _is_craftable_resource(item_data: Dict[str, Any]) -> bool:
    """Vérifie si un item est une ressource utilisée pour le craft."""
    definition = item_data.get("definition", {})
    item_def = definition.get("item", {})

    # Si l'item a useParameters.useCostAp, ce n'est probablement pas une ressource
    use_params = item_def.get("useParameters", {})
    if use_params.get("useCostAp"):
        return False

    # Si l'item n'a pas d'équipEffects mais a des useEffects, c'est peut-être une ressource
    equip_effects = definition.get("equipEffects", [])
    use_effects = definition.get("useEffects", [])

    # Les ressources n'ont généralement pas d'effets
    if not equip_effects and not use_effects:
        return True

    return False


def _is_consumable(item_data: Dict[str, Any]) -> bool:
    """Vérifie si un item est consommable."""
    definition = item_data.get("definition", {})
    item_def = definition.get("item", {})

    use_params = item_def.get("useParameters", {})

    # Un consommable a généralement un useCostAp et des useEffects
    if use_params.get("useCostAp") and definition.get("useEffects"):
        return True

    return False


def _is_food(item_data: Dict[str, Any]) -> bool:
    """Vérifie si un consommable est de la nourriture."""
    definition = item_data.get("definition", {})

    # Vérifier les useEffects pour des effets typiques de la nourriture
    use_effects = definition.get("useEffects", [])

    for effect_wrapper in use_effects:
        effect = effect_wrapper.get("effect", {})
        action_id = effect.get("definition", {}).get("actionId")

        # ActionIds typiques pour la nourriture (heal, regen, etc.)
        food_action_ids = [1084, 1068, 20]  # À affiner
        if action_id in food_action_ids:
            return True

    return False


def get_item_rarity_label(rarity_id: int) -> str:
    """
    Convertit un rarity ID en label lisible.

    Source: Configuration Wakfu
    """
    rarity_info = WAKFU_RARITIES.get(rarity_id)
    if rarity_info:
        return rarity_info["name"]
    return f"rarity_{rarity_id}"


def enrich_item_types_from_api(
    item_types_data: List[Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    """
    Crée un mapping enrichi des typeId depuis itemTypes.json.

    Args:
        item_types_data: Données brutes de itemTypes.json

    Returns:
        Dict {typeId: {name, category, ...}}
    """
    type_mapping = {}

    for item_type in item_types_data:
        definition = item_type.get("definition", {})
        type_id = definition.get("id")

        if not type_id:
            continue

        title = item_type.get("title", {})
        name_fr = title.get("fr", "")
        name_en = title.get("en", "")

        # Déterminer la catégorie approximative depuis le nom
        category = _guess_category_from_name(name_en or name_fr)

        type_mapping[type_id] = {
            "id": type_id,
            "name": {"fr": name_fr, "en": name_en},
            "category": category,
            "raw": definition,
        }

    return type_mapping


def _guess_category_from_name(name: str) -> str:
    """Devine la catégorie à partir du nom du type (heuristique)."""
    name_lower = name.lower()

    if any(word in name_lower for word in ["weapon", "arme", "sword", "épée", "staff", "bâton"]):
        return "equipments.weapons"
    if any(word in name_lower for word in ["armor", "armure", "helmet", "casque"]):
        return "equipments.armor"
    if any(word in name_lower for word in ["ring", "anneau", "amulet", "amulette"]):
        return "equipments.accessories"
    if any(word in name_lower for word in ["resource", "ressource", "ore", "minerai"]):
        return "resources"
    if any(word in name_lower for word in ["food", "nourriture", "potion"]):
        return "consumables"
    if any(word in name_lower for word in ["quest", "quête"]):
        return "quest_items"
    if any(word in name_lower for word in ["cosmetic", "costume", "costume"]):
        return "cosmetics"

    return "misc"
