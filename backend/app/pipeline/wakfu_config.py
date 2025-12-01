"""
Configuration des catégories d'items basée sur les typeIds réels de Wakfu.

Source: itemTypes.json de l'API Wakfu
Ces valeurs peuvent être mises à jour après analyse de itemTypes.json
"""

# Catégories principales et leurs typeIds
WAKFU_ITEM_CATEGORIES = {
    # ========== ÉQUIPEMENTS ==========
    "equipments.helmets": {
        "type_ids": [119],
        "description": "Casques et coiffes",
    },
    "equipments.chest": {
        "type_ids": [136],
        "description": "Plastrons et armures de torse",
    },
    "equipments.shoulders": {
        "type_ids": [133],
        "description": "Épaulettes",
    },
    "equipments.legs": {
        "type_ids": [138],
        "description": "Pantalons et jambières",
    },
    "equipments.back": {
        "type_ids": [132],
        "description": "Capes et manteaux",
    },
    "equipments.belt": {
        "type_ids": [134],
        "description": "Ceintures",
    },
    "equipments.boots": {
        "type_ids": [139],
        "description": "Bottes",
    },
    "equipments.amulet": {
        "type_ids": [120],
        "description": "Amulettes",
    },
    "equipments.ring": {
        "type_ids": [103],
        "description": "Anneaux",
    },
    "equipments.shield": {
        "type_ids": [189],
        "description": "Boucliers",
    },
    "equipments.weapons.one_handed": {
        "type_ids": [108, 110, 111, 113, 114, 115, 117],
        "description": "Armes à une main (épées, dagues, baguettes, etc.)",
    },
    "equipments.weapons.two_handed": {
        "type_ids": [223, 253, 254, 480, 518, 520],
        "description": "Armes à deux mains (épées, haches, bâtons, etc.)",
    },
    "equipments.pet": {
        "type_ids": [582],
        "description": "Familiers",
    },
    "equipments.mount": {
        "type_ids": [611],
        "description": "Montures",
    },
    "equipments.costume": {
        "type_ids": [647],
        "description": "Costumes et cosmétiques",
    },
    "equipments.emblem": {
        "type_ids": [646],
        "description": "Emblèmes",
    },
    # ========== RESSOURCES ==========
    "resources.ore": {
        "type_ids": [475],
        "description": "Minerais",
    },
    "resources.plants": {
        "type_ids": [476],
        "description": "Plantes et herbes",
    },
    "resources.wood": {
        "type_ids": [477],
        "description": "Bois",
    },
    "resources.fish": {
        "type_ids": [478],
        "description": "Poissons",
    },
    "resources.meat": {
        "type_ids": [479],
        "description": "Viandes",
    },
    "resources.cereals": {
        "type_ids": [480],
        "description": "Céréales",
    },
    "resources.vegetables": {
        "type_ids": [481],
        "description": "Légumes",
    },
    "resources.leather": {
        "type_ids": [515],
        "description": "Cuirs et peaux",
    },
    "resources.gems": {
        "type_ids": [516],
        "description": "Gemmes et pierres précieuses",
    },
    "resources.cloth": {
        "type_ids": [517],
        "description": "Tissus et étoffes",
    },
    "resources.crafting_materials": {
        "type_ids": [482, 483, 484, 485, 486, 487],
        "description": "Matériaux de craft divers",
    },
    # ========== CONSOMMABLES ==========
    "consumables.food": {
        "type_ids": [520, 521, 522, 523],
        "description": "Nourriture",
    },
    "consumables.potions": {
        "type_ids": [100],
        "description": "Potions",
    },
    "consumables.buffs": {
        "type_ids": [528, 529],
        "description": "Objets de buff temporaire",
    },
    # ========== AUTRES ==========
    "quest_items": {
        "type_ids": [518, 519],
        "description": "Items de quête",
    },
    "bags": {
        "type_ids": [519],
        "description": "Sacs et conteneurs",
    },
    "keys": {
        "type_ids": [530],
        "description": "Clés",
    },
    "runes": {
        "type_ids": [812],
        "description": "Runes d'enchantement",
    },
    "sublimations": {
        "type_ids": [808],
        "description": "Sublimations",
    },
    "tokens": {
        "type_ids": [650],
        "description": "Jetons et monnaies spéciales",
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
