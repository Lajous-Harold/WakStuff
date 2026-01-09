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
import logging

bp = Blueprint('items', __name__)
logger = logging.getLogger(__name__)


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
        sort_by = request.args.get('sort_by', 'level')  # name, level, rarity, created_at
        sort_order = request.args.get('sort_order', 'asc')  # asc, desc
        
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
        
        # Tri
        sort_column = Item.level  # default
        if sort_by == 'name':
            sort_column = Item.title
        elif sort_by == 'rarity':
            sort_column = Item.rarity
        elif sort_by == 'created_at':
            sort_column = Item.created_at
        
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc(), Item.wakfu_id)
        else:
            query = query.order_by(sort_column.asc(), Item.wakfu_id)
        
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
    def parse_action_description(action, params):
        """
        Parse la description Wakfu avec placeholders et retourne le label final.
        Exemples de placeholders:
        - [#1] = params[0] (première valeur)
        - [#2] = params[1] (deuxième valeur)
        - [#charac XXX] = ignoré (métadonnée UI)
        - {[~3]?texte1:texte2} = condition ternaire
        Le signe (+/-) est déjà défini dans la description selon l'actionId.
        """
        if not action or not action.description:
            return None
            
        desc = action.description.get('fr', '')
        if not desc:
            return None
        
        import re
        
        # Supprimer les tags [#charac XXX]
        desc = re.sub(r'\[#charac [^\]]+\]\s*', '', desc)
        
        # Remplacer [#1], [#2], etc. par les valeurs des params
        for i, param_value in enumerate(params, start=1):
            placeholder = f'[#{i}]'
            # Formater la valeur (entier si possible, sinon float)
            int_value = int(param_value) if param_value == int(param_value) else param_value
            desc = desc.replace(placeholder, str(int_value))
        
        # Gérer les conditions ternaires complexes {[condition]?vrai:faux}
        # Simplification: on prend la partie principale
        desc = re.sub(r'\{[^\}]*\?([^:]+):[^\}]*\}', r'\1', desc)
        desc = re.sub(r'\{[^\}]*\}', '', desc)
        
        # Nettoyer les espaces multiples
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        return desc if desc else None
    
    stats = {}
    if item.equip_effects:
        for effect in item.equip_effects:
            if isinstance(effect, dict):
                # Les effets sont dans effect.effect
                effect_data = effect.get('effect', {})
                effect_def = effect_data.get('definition', {})
                action_id = effect_def.get('actionId')
                params_str = effect_def.get('params', '')
                
                # Parser les params (format: "177.0 0.0 1.0 0.0 0.0 0.0" ou liste)
                params = []
                if isinstance(params_str, str):
                    params = [float(x) for x in params_str.split() if x]
                elif isinstance(params_str, list):
                    params = params_str
                
                # Utiliser la description enrichie depuis effect.description si disponible
                effect_description = effect_data.get('description', {})
                
                if not action_id:
                    continue
                
                # Priorité 1: Utiliser directement la description enrichie depuis l'effet (source Wakfu officielle)
                # Cette description contient des placeholders [#1], [#2], etc. qu'il faut remplacer
                # Le signe (+/-) est déjà défini dans la description selon l'actionId
                label = None
                if effect_description and 'fr' in effect_description:
                    import re
                    desc = effect_description['fr']
                    
                    # Supprimer les tags [#charac XXX] (métadonnées UI)
                    desc = re.sub(r'\[#charac [^\]]+\]\s*', '', desc)
                    
                    # Remplacer les placeholders [#1], [#2], etc. par les valeurs des params SANS ajouter de signe
                    for i, param_value in enumerate(params, start=1):
                        placeholder = f'[#{i}]'
                        # Formater la valeur (entier si possible, sinon float) - le signe est déjà dans la description
                        int_value = int(param_value) if param_value == int(param_value) else param_value
                        formatted_value = str(int_value)
                        desc = desc.replace(placeholder, formatted_value)
                    
                    # Gérer les conditions ternaires simples {[~2]?%:} -> afficher % si params[1] est vrai
                    desc = re.sub(r'\{[^\}]*\?([^:]*):([^\}]*)\}', r'\1', desc)
                    
                    label = desc
                
                # Priorité 2: Fallback sur la table Action en BDD
                if not label:
                    action = Action.query.filter_by(wakfu_id=action_id).first()
                    if action:
                        label = parse_action_description(action, params)
                        
                        # Si toujours pas de label, utiliser l'effet
                        if not label or len(label) < 3:
                            effect_text = action.effect or f"Action {action_id}"
                            if ':' in effect_text:
                                label = effect_text.split(':', 1)[1].strip()
                            else:
                                label = effect_text
                    else:
                        # Action inconnue
                        label = f"Action {action_id}"
                
                # Générer un nom unique basé sur le label
                import re
                name = re.sub(r'[^a-zA-Z0-9]', '', label.replace(' ', '').replace(':', ''))
                if not name:
                    name = f"Action{action_id}"
                
                # Valeur de la stat (généralement le premier paramètre)
                value = params[0] if params else 0
                
                # Cas spécial pour actionId 1068 (Maîtrise multi-éléments)
                # Intégrer la valeur directement dans le label
                if action_id == 1068 and len(params) >= 3:
                    num_elements = int(params[2]) if params[2] else 3
                    stat_value = int(params[0]) if params[0] == int(params[0]) else params[0]
                    label = f"{stat_value} Maîtrise sur {num_elements} élément{'s' if num_elements > 1 else ''}"
                    value = params[0]
                
                # Cas spécial pour actionId 1069 (Résistance multi-éléments)
                # Intégrer la valeur directement dans le label
                if action_id == 1069 and len(params) >= 3:
                    num_elements = int(params[2]) if params[2] else 3
                    stat_value = int(params[0]) if params[0] == int(params[0]) else params[0]
                    label = f"{stat_value} Résistance sur {num_elements} élément{'s' if num_elements > 1 else ''}"
                    value = params[0]
                
                # Gérer les doublons de nom
                key = name
                counter = 2
                while key in stats and stats[key]['action_id'] != action_id:
                    key = f"{name}_{counter}"
                    counter += 1
                
                stats[key] = {
                    'label': label,
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


@bp.route('/compare', methods=['POST'])
def compare_items():
    """
    POST /api/items/compare
    
    Compare 2 items en extrayant leurs stats depuis equip_effects.
    Utilise la même logique que get_item_detail pour le parsing.
    """
    data = request.get_json()
    
    if not data or 'item_ids' not in data:
        return jsonify({'error': 'item_ids required'}), 400
    
    item_ids = data['item_ids']
    
    if not isinstance(item_ids, list) or len(item_ids) != 2:
        return jsonify({'error': 'item_ids must be an array of exactly 2 items'}), 400
    
    # Récupérer les items dans l'ordre demandé
    items = []
    for item_id in item_ids:
        item = Item.query.filter_by(wakfu_id=item_id).first()
        if not item:
            return jsonify({'error': f'Item {item_id} not found'}), 404
        items.append(item)
    
    # Préparer les données items avec leurs stats
    items_data = []
    all_stats = {}
    
    for idx, item in enumerate(items):
        # Utiliser to_dict() comme dans get_item_detail pour avoir toutes les données
        item_dict = item.to_dict()
        
        # Essayer JobItem pour icon_gfx_id si manquant
        if not item_dict.get('icon_gfx_id'):
            job_item = JobItem.query.filter_by(wakfu_id=item.wakfu_id).first()
            if job_item and job_item.icon_gfx_id:
                item_dict['icon_gfx_id'] = job_item.icon_gfx_id
        
        # Ajouter type d'équipement
        if item.equipment_type_id:
            equipment_type = EquipmentItemType.query.filter_by(
                wakfu_id=item.equipment_type_id
            ).first()
            if equipment_type:
                # Extraire la version française du titre
                title = equipment_type.title
                if isinstance(title, dict):
                    item_dict['equipment_type'] = title.get('fr', title.get('en', str(title)))
                else:
                    item_dict['equipment_type'] = title
        
        items_data.append(item_dict)
        
        # Parser les stats de cet item (même logique que get_item_detail)
        equip_effects = item_dict.get('equip_effects')
        if equip_effects:
            for effect in equip_effects:
                if isinstance(effect, dict):
                    # Structure: effect['effect']['definition']
                    effect_data = effect.get('effect', {})
                    effect_def = effect_data.get('definition', {})
                    action_id = effect_def.get('actionId')
                    params_raw = effect_def.get('params', [])
                    
                    # Parser les params (string ou liste)
                    params = []
                    if isinstance(params_raw, str):
                        params = [float(x) for x in params_raw.split() if x]
                    elif isinstance(params_raw, list):
                        params = params_raw
                    
                    if not action_id or not params:
                        continue
                    
                    # Valeur principale (premier paramètre)
                    value = params[0] if params else 0
                    
                    # Récupérer le nom de la stat
                    stat_name = f"Action_{action_id}"
                    action = Action.query.filter_by(wakfu_id=action_id).first()
                    if action:
                        desc = action.description
                        if isinstance(desc, dict) and 'fr' in desc:
                            stat_name = desc['fr']
                            # Nettoyer les placeholders [#1], [#2], etc.
                            import re
                            # Enlever les métadonnées [#charac XXX]
                            stat_name = re.sub(r'\[#charac [^\]]+\]\s*', '', stat_name)
                            # Enlever les conditions Wakfu complexes {[...]}
                            stat_name = re.sub(r'\{[^\}]*\}', '', stat_name)
                            # Enlever les placeholders [#1], [#2], etc.
                            stat_name = re.sub(r'\[#\d+\]', '', stat_name)
                            # Enlever les accolades et crochets orphelins
                            stat_name = re.sub(r'[{}\[\]]', '', stat_name)
                            # Nettoyer les espaces multiples et trim
                            stat_name = re.sub(r'\s+', ' ', stat_name).strip()
                        elif isinstance(desc, str) and desc.strip():
                            stat_name = desc
                        elif action.effect:
                            stat_name = action.effect
                    
                    # Si le nom est vide après nettoyage, utiliser l'effet comme fallback
                    if not stat_name or len(stat_name) < 2:
                        if action and action.effect:
                            # Utiliser l'effet comme nom de stat
                            stat_name = action.effect
                            # Nettoyer le nom de l'effet (enlever les préfixes techniques)
                            stat_name = re.sub(r'^(Gain|Perte|Boost|Deboost)\s*:\s*', '', stat_name)
                        else:
                            # Dernier recours: ignorer cette stat
                            continue
                    
                    # Initialiser si nouveau
                    if stat_name not in all_stats:
                        all_stats[stat_name] = {
                            'action_id': action_id,
                            'values': [None] * len(items)
                        }
                    
                    # Stocker la valeur pour cet item
                    all_stats[stat_name]['values'][idx] = value
        
    return jsonify({
        'items': items_data,
        'stats': all_stats
    })

