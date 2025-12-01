"""
Configuration des catégories d'items basée sur les typeIds réels de Wakfu.

Source: itemTypes.json de l'API Wakfu version 1.90.1.47
Dernière mise à jour: Décembre 2025
"""

# Catégories principales et leurs typeIds (basés sur l'API réelle)
WAKFU_ITEM_CATEGORIES = {
    # ========== ÉQUIPEMENTS ==========
    "equipments.helmets": {
        "type_ids": [134],
        "description": "Casques",
        "label_fr": "Casques",
        "label_en": "Helmets",
    },
    "equipments.chest": {
        "type_ids": [118, 136, 575],
        "description": "Plastrons et armures de torse",
        "label_fr": "Plastrons",
        "label_en": "Breastplates",
    },
    "equipments.shoulders": {
        "type_ids": [138],
        "description": "Épaulettes",
        "label_fr": "Épaulettes",
        "label_en": "Epaulettes",
    },
    "equipments.legs": {
        "type_ids": [],  # Pas de typeId spécifique trouvé
        "description": "Pantalons et jambières",
        "label_fr": "Jambes",
        "label_en": "Legs",
    },
    "equipments.back": {
        "type_ids": [132],
        "description": "Capes et manteaux",
        "label_fr": "Capes",
        "label_en": "Cloaks",
    },
    "equipments.belt": {
        "type_ids": [133],
        "description": "Ceintures",
        "label_fr": "Ceintures",
        "label_en": "Belts",
    },
    "equipments.boots": {
        "type_ids": [119],
        "description": "Bottes",
        "label_fr": "Bottes",
        "label_en": "Boots",
    },
    "equipments.amulet": {
        "type_ids": [120],
        "description": "Amulettes",
        "label_fr": "Amulettes",
        "label_en": "Amulets",
    },
    "equipments.ring": {
        "type_ids": [103],
        "description": "Anneaux",
        "label_fr": "Anneaux",
        "label_en": "Rings",
    },
    "equipments.shield": {
        "type_ids": [100, 189],
        "description": "Boucliers",
        "label_fr": "Boucliers",
        "label_en": "Shields",
    },
    "equipments.weapons.one_handed": {
        "type_ids": [108, 110, 112, 113, 115],  # Baguettes, Épées, Dagues, Bâtons, Aiguilles
        "description": "Armes à une main",
        "label_fr": "Armes 1 main",
        "label_en": "One-Handed Weapons",
    },
    "equipments.weapons.two_handed": {
        "type_ids": [101, 111, 114, 117, 223, 253],  # Haches, Pelles, Marteaux, Arcs, Épées 2H, Bâtons 2H
        "description": "Armes à deux mains",
        "label_fr": "Armes 2 mains",
        "label_en": "Two-Handed Weapons",
    },
    "equipments.pet": {
        "type_ids": [582, 827],  # Familiers réels + Apparences
        "description": "Familiers",
        "label_fr": "Familiers",
        "label_en": "Pets",
    },
    "equipments.mount": {
        "type_ids": [480],  # Montures
        "description": "Montures",
        "label_fr": "Montures",
        "label_en": "Mounts",
    },
    "equipments.costume": {
        "type_ids": [525],
        "description": "Cosmétiques",
        "label_fr": "Cosmétiques",
        "label_en": "Cosmetics",
    },
    "equipments.emblem": {
        "type_ids": [646],
        "description": "Emblèmes",
        "label_fr": "Emblèmes",
        "label_en": "Emblems",
    },
    # ========== CONSOMMABLES ==========
    "consumables.food": {
        "type_ids": [745, 757],
        "description": "Nourriture",
        "label_fr": "Nourriture",
        "label_en": "Food",
    },
    "consumables.potions": {
        "type_ids": [106, 746, 747],  # Consommables
        "description": "Potions et consommables",
        "label_fr": "Potions",
        "label_en": "Potions",
    },
    "consumables.buffs": {
        "type_ids": [],
        "description": "Buffs temporaires",
        "label_fr": "Buffs",
        "label_en": "Buffs",
    },
    # ========== AUTRES ==========
    "quest_items": {
        "type_ids": [551],
        "description": "Items de quête",
        "label_fr": "Objets de quête",
        "label_en": "Quest Items",
    },
    "bags": {
        "type_ids": [218, 295, 415, 416, 535, 546, 566, 701, 702],
        "description": "Sacs et décorations de Havre-Sac",
        "label_fr": "Sacs",
        "label_en": "Bags",
    },
    "keys": {
        "type_ids": [317],
        "description": "Clés",
        "label_fr": "Clés",
        "label_en": "Keys",
    },
    "runes": {
        "type_ids": [811],  # Enchantement
        "description": "Runes d'enchantement",
        "label_fr": "Enchantements",
        "label_en": "Enchantments",
    },
    "sublimations": {
        "type_ids": [812],
        "description": "Sublimations",
        "label_fr": "Sublimations",
        "label_en": "Sublimations",
    },
    "tokens": {
        "type_ids": [],
        "description": "Jetons et monnaies spéciales",
        "label_fr": "Jetons",
        "label_en": "Tokens",
    },
    "recipes": {
        "type_ids": [719],
        "description": "Recettes",
        "label_fr": "Recettes",
        "label_en": "Recipes",
    },
    "improvements": {
        "type_ids": [602],
        "description": "Améliorations",
        "label_fr": "Améliorations",
        "label_en": "Improvements",
    },
    "relics": {
        "type_ids": [687],
        "description": "Fragments de relique",
        "label_fr": "Reliques",
        "label_en": "Relics",
    },
    "sets": {
        "type_ids": [604],
        "description": "Panoplies",
        "label_fr": "Panoplies",
        "label_en": "Sets",
    },
    "tools": {
        "type_ids": [537],
        "description": "Outils",
        "label_fr": "Outils",
        "label_en": "Tools",
    },
    "furniture": {
        "type_ids": [296, 297, 447, 449, 515, 534],
        "description": "Mobilier et décoration",
        "label_fr": "Mobilier",
        "label_en": "Furniture",
    },
    "teleportation": {
        "type_ids": [630],
        "description": "Téléportation",
        "label_fr": "Téléportation",
        "label_en": "Teleportation",
    },
    "transformations": {
        "type_ids": [738, 739],
        "description": "Transformations",
        "label_fr": "Transformations",
        "label_en": "Transformations",
    },
    "events": {
        "type_ids": [756],
        "description": "Objets d'événements",
        "label_fr": "Événements",
        "label_en": "Events",
    },
    # Catégories génériques pour fallback
    "equipments": {
        "type_ids": [109, 518, 519, 520, 521],  # Équipements génériques
        "description": "Équipements",
        "label_fr": "Équipements",
        "label_en": "Equipment",
    },
    "misc": {
        "type_ids": [254, 385, 652, 751, 840],  # Divers non catégorisés
        "description": "Divers",
        "label_fr": "Divers",
        "label_en": "Miscellaneous",
    },
}


def get_all_type_ids():
    """Retourne tous les typeIds mappés."""
    all_ids = []
    for category_data in WAKFU_ITEM_CATEGORIES.values():
        all_ids.extend(category_data["type_ids"])
    return set(all_ids)


def get_category_for_type_id(type_id: int) -> str:
    """
    Retourne la catégorie pour un typeId donné.
    
    Args:
        type_id: Le typeId à rechercher
        
    Returns:
        Le nom de la catégorie ou "misc" si non trouvé
    """
    for category_name, category_data in WAKFU_ITEM_CATEGORIES.items():
        if type_id in category_data["type_ids"]:
            return category_name
    return "misc"


def get_category_description(category_name: str) -> str:
    """Retourne la description d'une catégorie."""
    category_data = WAKFU_ITEM_CATEGORIES.get(category_name)
    if category_data:
        return category_data.get("description", "")
    return ""


# Mapping de raretés (observé de l'API)
WAKFU_RARITIES = {
    0: {"name": "common", "label_fr": "Commun", "color": "#FFFFFF"},
    1: {"name": "unusual", "label_fr": "Inhabituel", "color": "#00FF00"},
    2: {"name": "rare", "label_fr": "Rare", "color": "#0088FF"},
    3: {"name": "mythical", "label_fr": "Mythique", "color": "#FF00FF"},
    4: {"name": "legendary", "label_fr": "Légendaire", "color": "#FF8800"},
    5: {"name": "relic", "label_fr": "Relique", "color": "#FF0000"},
    6: {"name": "souvenir", "label_fr": "Souvenir", "color": "#FFFF00"},
    7: {"name": "epic", "label_fr": "Épique", "color": "#8800FF"},
}


# Mapping des éléments
WAKFU_ELEMENTS = {
    0: {"name": "neutral", "label_fr": "Neutre", "label_en": "Neutral"},
    1: {"name": "fire", "label_fr": "Feu", "label_en": "Fire"},
    2: {"name": "water", "label_fr": "Eau", "label_en": "Water"},
    3: {"name": "earth", "label_fr": "Terre", "label_en": "Earth"},
    4: {"name": "air", "label_fr": "Air", "label_en": "Air"},
    5: {"name": "light", "label_fr": "Lumière", "label_en": "Light"},
    6: {"name": "shadow", "label_fr": "Ténèbres", "label_en": "Shadow"},
}
