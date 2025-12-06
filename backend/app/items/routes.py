"""
Routes API pour les items.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from ..database import db
from ..models import (
    Item, ItemType, ItemCategory, JobItem, EquipmentItemType,
    ItemProperty, Action, State, Recipe, RecipeIngredient, RecipeResult,
    RecipeCategory
)

bp = Blueprint('items', __name__)


@bp.route('', methods=['GET'])
def get_items():
    """
    GET /api/items
    
    Liste des items avec filtrage et pagination.
    
    Query params:
    - search: Recherche dans le titre
    - item_type_id: Filtrer par type d'item
    - equipment_type_id: Filtrer par type d'équipement
    - level_min, level_max: Niveau
    - rarity: Rareté (0-7)
    - page, per_page: Pagination
    """
    try:
        search = request.args.get('search', '').strip()
        item_type_id = request.args.get('item_type_id', type=int)
        equipment_type_id = request.args.get('equipment_type_id')  # Peut être un ID ou une catégorie groupée
        level_min = request.args.get('level_min', type=int)
        level_max = request.args.get('level_max', type=int)
        rarity = request.args.get('rarity', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        query = Item.query
        
        if search:
            # Recherche dans le JSON title
            search_pattern = f'%{search}%'
            query = query.filter(
                or_(
                    Item.title.cast(db.String).ilike(search_pattern),
                    Item.description.cast(db.String).ilike(search_pattern)
                )
            )
        
        if item_type_id:
            query = query.filter(Item.item_type_id == item_type_id)
        
        if equipment_type_id:
            # Mapper les catégories groupées vers les IDs réels
            category_mappings = {
                'weapon_1h': [108, 110, 113, 115, 254, 518],  # Armes 1 main
                'weapon_2h': [101, 111, 114, 117, 223, 253, 519],  # Armes 2 mains
                'second_hand': [112, 189, 520]  # Seconde main
            }
            
            if equipment_type_id in category_mappings:
                # C'est une catégorie groupée
                type_ids = category_mappings[equipment_type_id]
                query = query.filter(Item.equipment_type_id.in_(type_ids))
            else:
                # C'est un ID simple
                try:
                    type_id = int(equipment_type_id)
                    query = query.filter(Item.equipment_type_id == type_id)
                except ValueError:
                    pass  # Ignorer les valeurs invalides
        
        if level_min:
            query = query.filter(Item.level >= level_min)
        
        if level_max:
            query = query.filter(Item.level <= level_max)
        
        if rarity is not None:
            query = query.filter(Item.rarity == rarity)
        
        query = query.order_by(Item.level.asc(), Item.wakfu_id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Enrichir les items avec les titres des types
        items_data = []
        for item in pagination.items:
            item_dict = item.to_dict()
            
            # Ajouter le titre du type d'item si disponible
            if item.item_type_id:
                item_type = ItemType.query.filter_by(wakfu_id=item.item_type_id).first()
                if item_type:
                    item_dict['item_type_title'] = item_type.to_dict().get('title', '')
            
            # Ajouter le titre du type d'équipement si disponible
            if item.equipment_type_id:
                equipment_type = EquipmentItemType.query.filter_by(wakfu_id=item.equipment_type_id).first()
                if equipment_type:
                    item_dict['equipment_type_title'] = equipment_type.to_dict().get('title', '')
            
            items_data.append(item_dict)
        
        return jsonify({
            'items': items_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception:
        # Si les tables n'existent pas, retourner des données vides
        db.session.rollback()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        return jsonify({
            'items': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'pages': 0
        })


@bp.route('/<int:wakfu_id>', methods=['GET'])
def get_item_detail(wakfu_id):
    """
    GET /api/items/<wakfu_id>
    
    Détails complets d'un item avec toutes les données enrichies :
    - Informations de base (titre, description, niveau, rareté)
    - Type d'item et type d'équipement
    - Propriétés spéciales (Relique, Épique, etc.)
    - Effets (use_effects, equip_effects avec descriptions lisibles)
    - États appliqués
    - Statistiques de l'item
    - Recettes où l'item est utilisé (comme ingrédient)
    - Recettes qui produisent cet item (comme résultat)
    """
    item = Item.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    item_dict = item.to_dict()
    
    # 1. ENRICHIR AVEC LE TYPE D'ITEM
    if item.item_type_id:
        item_type = ItemType.query.filter_by(wakfu_id=item.item_type_id).first()
        if item_type:
            item_dict['item_type'] = item_type.to_dict()
    
    # 2. ENRICHIR AVEC LE TYPE D'ÉQUIPEMENT
    if item.equipment_type_id:
        equipment_type = EquipmentItemType.query.filter_by(wakfu_id=item.equipment_type_id).first()
        if equipment_type:
            item_dict['equipment_type'] = equipment_type.to_dict()
    
    # 3. ENRICHIR AVEC LES PROPRIÉTÉS SPÉCIALES
    if item.item_properties:
        properties = []
        for prop_id in item.item_properties:
            item_property = ItemProperty.query.filter_by(wakfu_id=prop_id).first()
            if item_property:
                properties.append(item_property.to_dict())
        item_dict['properties'] = properties
    
    # 4. ENRICHIR LES EFFETS AVEC LES DESCRIPTIONS D'ACTIONS
    def enrich_effects(effects_list):
        """Enrichit une liste d'effets avec les descriptions des actions"""
        if not effects_list:
            return []
        
        enriched = []
        for effect in effects_list:
            enriched_effect = effect.copy() if isinstance(effect, dict) else {}
            
            # Si l'effet a un actionId, récupérer la description
            if isinstance(effect, dict) and 'actionId' in effect:
                action = Action.query.filter_by(wakfu_id=effect['actionId']).first()
                if action:
                    enriched_effect['action'] = action.to_dict()
            
            enriched.append(enriched_effect)
        
        return enriched
    
    if item.use_effects:
        item_dict['use_effects_enriched'] = enrich_effects(item.use_effects)
    
    if item.use_critical_effects:
        item_dict['use_critical_effects_enriched'] = enrich_effects(item.use_critical_effects)
    
    if item.equip_effects:
        item_dict['equip_effects_enriched'] = enrich_effects(item.equip_effects)
    
    # 5. EXTRAIRE ET ENRICHIR LES STATISTIQUES DE L'ÉQUIPEMENT
    stats = {}
    if item.equip_effects:
        for effect in item.equip_effects:
            if isinstance(effect, dict):
                # Les effets sont dans effect.effect.definition
                effect_def = effect.get('effect', {}).get('definition', {})
                action_id = effect_def.get('actionId')
                params = effect_def.get('params', [])
                
                # Mapper les actions vers les statistiques
                stat_mapping = {
                    # Stats de base
                    20: {'name': 'HP', 'label': 'Point de vie (PV)'},
                    21: {'name': 'HP', 'label': 'Point de vie (PV)'},  # Debuff
                    26: {'name': 'HealMastery', 'label': 'Maîtrise Soin'},
                    31: {'name': 'AP', 'label': 'PA'},
                    39: {'name': 'CharacGain', 'label': 'Gain paramétré'},
                    40: {'name': 'CharacLoss', 'label': 'Perte paramétrée'},
                    41: {'name': 'MP', 'label': 'PM'},
                    56: {'name': 'Initiative', 'label': 'Initiative'},
                    57: {'name': 'MPMaxDebuff', 'label': 'PM max'},
                    66: {'name': 'Range', 'label': 'Portée'},
                    71: {'name': 'RearResBase2', 'label': 'Résistance Dos'},
                    80: {'name': 'WP', 'label': 'PW'},
                    82: {'name': 'FireResPercent', 'label': 'Résistance Feu'},
                    83: {'name': 'ElementalResBase', 'label': 'Résistance'},
                    84: {'name': 'EarthResBase', 'label': 'Résistance Terre'},
                    85: {'name': 'WaterResBase', 'label': 'Résistance Eau'},
                    90: {'name': 'ElementalResDebuff', 'label': 'Résistance Élémentaire'},
                    96: {'name': 'Dodge', 'label': 'Esquive'},
                    97: {'name': 'Lock', 'label': 'Tacle'},
                    98: {'name': 'WaterResDebuffNoCap', 'label': 'Résistance Eau'},
                    100: {'name': 'ElementalResDebuffNoCap', 'label': 'Résistance Élémentaire'},
                    120: {'name': 'ElementalMasteryBase', 'label': 'Maîtrise Élémentaire'},
                    122: {'name': 'Wisdom', 'label': 'Sagesse'},
                    123: {'name': 'EarthMasteryBase', 'label': 'Maîtrise Terre'},
                    124: {'name': 'Prospecting', 'label': 'Prospection'},
                    125: {'name': 'AirMasteryBase', 'label': 'Maîtrise Air'},
                    130: {'name': 'Control', 'label': 'Contrôle'},
                    132: {'name': 'FireMasteryDebuff', 'label': 'Maîtrise Feu'},
                    149: {'name': 'CritChance', 'label': '% Coup critique'},
                    150: {'name': 'Block', 'label': 'Parade'},
                    160: {'name': 'CritMastery', 'label': 'Maîtrise Critique'},
                    161: {'name': 'RangeDebuff', 'label': 'Portée'},
                    162: {'name': 'RearMastery', 'label': 'Maîtrise Dos'},
                    166: {'name': 'Heals', 'label': 'Soins'},
                    168: {'name': 'CritChanceDebuff', 'label': '% Coup Critique'},
                    171: {'name': 'RearRes', 'label': 'Résistance Dos'},
                    172: {'name': 'InitiativeDebuff', 'label': 'Initiative'},
                    173: {'name': 'CritRes', 'label': 'Résistance Critique'},
                    174: {'name': 'LockDebuff', 'label': 'Tacle'},
                    175: {'name': 'RearRes', 'label': 'Résistance Dos'},  # Alias
                    176: {'name': 'DodgeDebuff', 'label': 'Esquive'},
                    177: {'name': 'Willpower', 'label': 'Volonté'},
                    180: {'name': 'APRes', 'label': 'Résistance PA'},
                    181: {'name': 'RearMasteryDebuff', 'label': 'Maîtrise Dos'},
                    184: {'name': 'MPRes', 'label': 'Résistance PM'},
                    191: {'name': 'WPRes', 'label': 'Résistance PW'},
                    192: {'name': 'WPMaxDebuff', 'label': 'PW max'},
                    304: {'name': 'ApplyState', 'label': 'Applique état'},
                    400: {'name': 'NullEffect', 'label': 'Effet vide'},
                    875: {'name': 'BlockPercent', 'label': 'Parade'},
                    876: {'name': 'BlockPercentDebuff', 'label': 'Parade'},
                    988: {'name': 'CritResAlt', 'label': 'Résistance Critique'},
                    2001: {'name': 'Unknown2001', 'label': 'Effet inconnu'},
                }
                
                # Éléments (maîtrises et résistances)
                element_mastery = {
                    1020: {'name': 'FireMastery', 'label': 'Maîtrise Feu'},
                    1021: {'name': 'FireRes', 'label': 'Résistance Feu'},
                    1040: {'name': 'WaterMastery', 'label': 'Maîtrise Eau'},
                    1041: {'name': 'WaterRes', 'label': 'Résistance Eau'},
                    1052: {'name': 'MeleeMastery', 'label': 'Maîtrise Mêlée'},
                    1053: {'name': 'RangedMastery', 'label': 'Maîtrise Distance'},
                    1055: {'name': 'BerserkMastery', 'label': 'Maîtrise Berserk'},
                    1056: {'name': 'CritMasteryDebuff', 'label': 'Maîtrise Critique'},
                    1059: {'name': 'MeleeMasteryDebuff', 'label': 'Maîtrise Mêlée'},
                    1060: {'name': 'EarthMastery', 'label': 'Maîtrise Terre'},
                    1061: {'name': 'EarthRes', 'label': 'Résistance Terre'},
                    1062: {'name': 'CritResDebuff', 'label': 'Résistance Critique'},
                    1063: {'name': 'RearResDebuff', 'label': 'Résistance Dos'},
                    1068: {'name': 'ElementMastery', 'label': 'Maîtrise sur 3 éléments'},
                    1069: {'name': 'ElementalResVariable', 'label': 'Résistance Élémentaire variable'},
                    1080: {'name': 'AirMastery', 'label': 'Maîtrise Air'},
                    1081: {'name': 'AirRes', 'label': 'Résistance Air'},
                }
                
                stat_info = stat_mapping.get(action_id) or element_mastery.get(action_id)
                
                if stat_info and params:
                    # Valeur de la stat (généralement le premier paramètre)
                    value = params[0] if isinstance(params, list) and len(params) > 0 else params
                    
                    # Pour les stats élémentaires multi-éléments (actionId 1068)
                    if action_id == 1068 and isinstance(params, list) and len(params) >= 3:
                        # params[2] indique le nombre d'éléments (3 dans l'exemple)
                        num_elements = int(params[2]) if params[2] else 3
                        stat_info = {
                            'name': 'ElementMastery',
                            'label': f'Maîtrise sur {num_elements} éléments'
                        }
                    
                    stats[stat_info['name']] = {
                        'label': stat_info['label'],
                        'value': int(value) if isinstance(value, (int, float)) else value,
                        'action_id': action_id
                    }
                    
                    # Si le nom existe déjà, ajouter l'action_id pour le rendre unique
                    key = stat_info['name']
                    counter = 2
                    while key in stats and stats[key]['action_id'] != action_id:
                        key = f"{stat_info['name']}_{counter}"
                        counter += 1
                    
                    stats[key] = {
                        'label': stat_info['label'],
                        'value': int(value) if isinstance(value, (int, float)) else value,
                        'action_id': action_id
                    }
    
    item_dict['statistics'] = stats
    
    # 6. TROUVER LES RECETTES OÙ CET ITEM EST UN INGRÉDIENT
    recipes_using_item = []
    ingredients = RecipeIngredient.query.filter_by(item_id=wakfu_id).all()
    
    for ingredient in ingredients:
        recipe = Recipe.query.filter_by(wakfu_id=ingredient.recipe_wakfu_id).first()
        if recipe:
            recipe_dict = recipe.to_dict()
            recipe_dict['quantity_needed'] = ingredient.quantity
            
            # Enrichir avec la catégorie
            if recipe.recipe_category_id:
                category = RecipeCategory.query.get(recipe.recipe_category_id)
                if category:
                    recipe_dict['category'] = category.to_dict()
            
            recipes_using_item.append(recipe_dict)
    
    item_dict['used_in_recipes'] = recipes_using_item
    
    # 7. TROUVER LES RECETTES QUI PRODUISENT CET ITEM
    recipes_producing_item = []
    results = RecipeResult.query.filter_by(producted_item_id=wakfu_id).all()
    
    for result in results:
        recipe = Recipe.query.filter_by(wakfu_id=result.recipe_wakfu_id).first()
        if recipe:
            recipe_dict = recipe.to_dict()
            recipe_dict['quantity_produced'] = result.producted_item_quantity
            
            # Enrichir avec la catégorie
            if recipe.recipe_category_id:
                category = RecipeCategory.query.get(recipe.recipe_category_id)
                if category:
                    recipe_dict['category'] = category.to_dict()
            
            recipes_producing_item.append(recipe_dict)
    
    item_dict['produced_by_recipes'] = recipes_producing_item
    
    # 8. VÉRIFIER SI L'ITEM EST UN JOB ITEM
    if item.job_item_id:
        job_item = JobItem.query.filter_by(wakfu_id=wakfu_id).first()
        if job_item:
            item_dict['job_item'] = job_item.to_dict()
    
    return jsonify({
        'item': item_dict
    })


@bp.route('/types', methods=['GET'])
def get_item_types():
    """
    GET /api/items/types
    
    Liste tous les types d'items.
    """
    types = ItemType.query.order_by(ItemType.wakfu_id).all()
    
    return jsonify({
        'item_types': [t.to_dict() for t in types]
    })


@bp.route('/equipment-types', methods=['GET'])
def get_equipment_types():
    """
    GET /api/items/equipment-types
    
    Liste tous les types d'équipements avec catégories groupées.
    
    Query params:
    - grouped: Si true, retourne les catégories groupées (armes 1 main, 2 mains, etc.)
    """
    grouped = request.args.get('grouped', 'true').lower() == 'true'
    
    if not grouped:
        # Mode classique : tous les types individuels
        types = EquipmentItemType.query.order_by(EquipmentItemType.wakfu_id).all()
        return jsonify({
            'equipment_types': [t.to_dict() for t in types]
        })
    
    # Mode groupé : catégories simplifiées pour l'UX
    # Définir les groupes d'armes
    one_hand_weapons = [108, 110, 113, 115, 254, 518]  # Baguette, Épée, Bâton, Aiguille, Carte, Arme 1M
    two_hand_weapons = [101, 111, 114, 117, 223, 253, 519]  # Hache, Pelle, Marteau, Arc, Épée 2M, Bâton 2M, Arme 2M
    second_hand = [112, 189, 520]  # Dague, Bouclier, Seconde Main
    
    # Créer les catégories groupées
    grouped_categories = [
        {
            'wakfu_id': 'weapon_1h',
            'title': 'Arme 1 main',
            'equipment_type_ids': one_hand_weapons,
            'equipment_positions': ['FIRST_WEAPON']
        },
        {
            'wakfu_id': 'weapon_2h',
            'title': 'Arme 2 mains',
            'equipment_type_ids': two_hand_weapons,
            'equipment_positions': ['FIRST_WEAPON']
        },
        {
            'wakfu_id': 'second_hand',
            'title': 'Seconde main',
            'equipment_type_ids': second_hand,
            'equipment_positions': ['SECOND_WEAPON']
        }
    ]
    
    # Ajouter les autres catégories non groupées
    other_types = EquipmentItemType.query.filter(
        ~EquipmentItemType.wakfu_id.in_(one_hand_weapons + two_hand_weapons + second_hand)
    ).order_by(EquipmentItemType.wakfu_id).all()
    
    for equipment_type in other_types:
        type_dict = equipment_type.to_dict()
        grouped_categories.append({
            'wakfu_id': type_dict['wakfu_id'],
            'title': type_dict['title'],
            'equipment_type_ids': [type_dict['wakfu_id']],
            'equipment_positions': type_dict.get('equipment_positions', [])
        })
    
    return jsonify({
        'equipment_types': grouped_categories
    })


@bp.route('/job-items', methods=['GET'])
def get_job_items():
    """
    GET /api/items/job-items
    
    Items de métiers avec filtrage par catégorie.
    
    Query params:
    - category_id: ID de la catégorie de métier
    - level_min, level_max: Niveau
    - page, per_page: Pagination
    """
    category_id = request.args.get('category_id', type=int)
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = JobItem.query
    
    if category_id:
        query = query.filter(JobItem.category_id == category_id)
    
    if level_min:
        query = query.filter(JobItem.level >= level_min)
    
    if level_max:
        query = query.filter(JobItem.level <= level_max)
    
    query = query.order_by(JobItem.level.desc(), JobItem.item_wakfu_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'job_items': [ji.to_dict() for ji in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
