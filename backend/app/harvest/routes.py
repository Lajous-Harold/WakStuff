"""
Routes API pour le système de récolte (harvest).
Alias et endpoints spécialisés pour les ressources de récolte.
"""
from flask import Blueprint, jsonify, request
from ..database import db
from ..models import HarvestResource, HarvestLoot, CollectibleResource, Resource, RecipeCategory

bp = Blueprint('harvest', __name__)


@bp.route('/resources', methods=['GET'])
def get_harvest_resources():
    """
    GET /api/harvest/resources
    
    Items récoltables avec information complète.
    
    Query params:
    - job_name: 'Paysan', 'Forestier', 'Herboriste', 'Mineur', 'Pêcheur'
    - skill_id: 64, 71, 72, 73, 75
    - level_min, level_max: Niveau
    - page, per_page: Pagination
    """
    job_name = request.args.get('job_name')
    skill_id = request.args.get('skill_id', type=int)
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = HarvestResource.query
    
    # Conversion job_name -> skill_id
    if job_name:
        job_mapping = {
            'Paysan': 64,
            'Forestier': 71,
            'Herboriste': 72,
            'Mineur': 73,
            'Pêcheur': 75
        }
        skill_id = job_mapping.get(job_name, skill_id)
    
    if skill_id:
        query = query.filter(HarvestResource.skill_id == skill_id)
    
    if level_min:
        query = query.filter(HarvestResource.level >= level_min)
    
    if level_max:
        query = query.filter(HarvestResource.level <= level_max)
    
    query = query.order_by(HarvestResource.level, HarvestResource.item_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'harvest_resources': [hr.to_dict() for hr in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/loots', methods=['GET'])
def get_harvest_loots():
    """
    GET /api/harvest/loots
    
    Liste des loots de récolte.
    
    Query params:
    - list_id: ID de la liste de loots
    - item_id: ID de l'item dropé
    - page, per_page: Pagination
    """
    list_id = request.args.get('list_id', type=int)
    item_id = request.args.get('item_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    query = HarvestLoot.query
    
    if list_id:
        query = query.filter(HarvestLoot.list_id == list_id)
    
    if item_id:
        query = query.filter(HarvestLoot.item_id == item_id)
    
    query = query.order_by(HarvestLoot.quantity.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'harvest_loots': [loot.to_dict() for loot in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/jobs', methods=['GET'])
def get_harvest_jobs():
    """
    GET /api/harvest/jobs
    
    Liste des métiers de récolte uniquement.
    """
    jobs = RecipeCategory.query.filter_by(category_type='harvest').all()
    
    return jsonify({
        'jobs': [j.to_dict() for j in jobs]
    })


@bp.route('/by-resource/<int:resource_id>', methods=['GET'])
def get_harvest_by_resource(resource_id):
    """
    GET /api/harvest/by-resource/<resource_id>
    
    Toutes les actions de collecte disponibles pour une ressource donnée.
    """
    collectables = CollectibleResource.query.filter_by(resource_id=resource_id).all()
    
    if not collectables:
        return jsonify({'collectables': []})
    
    # Récupérer la ressource
    resource = Resource.query.filter_by(wakfu_id=resource_id).first()
    
    return jsonify({
        'resource': resource.to_dict() if resource else None,
        'collectables': [c.to_dict() for c in collectables]
    })


@bp.route('/zones', methods=['GET'])
def get_harvest_zones():
    """
    GET /api/harvest/zones
    
    Liste des zones de récolte avec les ressources disponibles.
    Retourne des zones fictives pour démarrer (pourra être enrichi avec vraies données).
    
    Query params:
    - level_min: Niveau minimum requis
    - level_max: Niveau maximum
    - skill_id: Filtrer par métier (64, 71, 72, 73, 75)
    - resource_ids: Liste d'IDs de ressources séparés par virgule
    """
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    skill_id = request.args.get('skill_id', type=int)
    resource_ids = request.args.get('resource_ids', '')
    
    # Parse resource_ids
    resource_id_list = []
    if resource_ids:
        resource_id_list = [int(x) for x in resource_ids.split(',') if x.strip()]
    
    # Zones de récolte fictives avec coordonnées approximatives
    zones = [
        {
            'id': 1,
            'name': 'Astrub - Forêt',
            'level_range': [1, 20],
            'coordinates': {'x': 0, 'y': 0},
            'skill_ids': [71, 72],  # Forestier, Herboriste
            'resource_ids': [5, 10, 15],
            'description': 'Zone de démarrage avec arbres et plantes'
        },
        {
            'id': 2,
            'name': 'Astrub - Champs',
            'level_range': [1, 15],
            'coordinates': {'x': 5, 'y': -3},
            'skill_ids': [64],  # Paysan
            'resource_ids': [1, 2, 3],
            'description': 'Cultures de base'
        },
        {
            'id': 3,
            'name': 'Mines d\'Astrub',
            'level_range': [5, 25],
            'coordinates': {'x': -8, 'y': 2},
            'skill_ids': [73],  # Mineur
            'resource_ids': [50, 51, 52],
            'description': 'Minerais de fer et cuivre'
        },
        {
            'id': 4,
            'name': 'Lac Cania',
            'level_range': [10, 30],
            'coordinates': {'x': 10, 'y': 5},
            'skill_ids': [75],  # Pêcheur
            'resource_ids': [100, 101],
            'description': 'Poissons d\'eau douce'
        },
        {
            'id': 5,
            'name': 'Bonta - Forêt Nord',
            'level_range': [30, 60],
            'coordinates': {'x': -15, 'y': 10},
            'skill_ids': [71, 72],
            'resource_ids': [20, 25, 30],
            'description': 'Forêt dense avec plantes rares'
        },
        {
            'id': 6,
            'name': 'Sufokia - Mines',
            'level_range': [40, 80],
            'coordinates': {'x': 20, 'y': -15},
            'skill_ids': [73],
            'resource_ids': [55, 60, 65],
            'description': 'Minerais précieux'
        },
        {
            'id': 7,
            'name': 'Brâkmar - Champs Obscurs',
            'level_range': [50, 100],
            'coordinates': {'x': -20, 'y': -10},
            'skill_ids': [64, 72],
            'resource_ids': [40, 45],
            'description': 'Cultures et herbes sombres'
        },
        {
            'id': 8,
            'name': 'Océan Crocuzko',
            'level_range': [60, 120],
            'coordinates': {'x': 25, 'y': 20},
            'skill_ids': [75],
            'resource_ids': [110, 115],
            'description': 'Poissons exotiques'
        }
    ]
    
    # Filtrage
    filtered_zones = []
    for zone in zones:
        # Filtrer par niveau
        if level_min and zone['level_range'][1] < level_min:
            continue
        if level_max and zone['level_range'][0] > level_max:
            continue
            
        # Filtrer par skill_id
        if skill_id and skill_id not in zone['skill_ids']:
            continue
            
        # Filtrer par resource_ids
        if resource_id_list:
            if not any(rid in zone['resource_ids'] for rid in resource_id_list):
                continue
        
        filtered_zones.append(zone)
    
    return jsonify({
        'zones': filtered_zones,
        'total': len(filtered_zones)
    })


@bp.route('/optimize', methods=['POST'])
def optimize_harvest_route():
    """
    POST /api/harvest/optimize
    
    Calcule l'itinéraire optimal pour récolter une liste de ressources.
    
    Body JSON:
    {
        "resource_ids": [5, 10, 15, 50],
        "player_level": 50,
        "max_zones": 5
    }
    
    Returns:
    {
        "recommended_zones": [
            {
                "zone": {...},
                "efficiency": 0.85,
                "matched_resources": [5, 10],
                "distance": 12.3
            }
        ],
        "total_distance": 45.2,
        "itinerary": "Zone 1 -> Zone 3 -> Zone 5"
    }
    """
    data = request.get_json()
    
    if not data or 'resource_ids' not in data:
        return jsonify({'error': 'resource_ids required'}), 400
    
    resource_ids = data.get('resource_ids', [])
    player_level = data.get('player_level', 1)
    max_zones = data.get('max_zones', 5)
    
    # Zones fictives (mêmes que l'endpoint /zones)
    all_zones = [
        {'id': 1, 'name': 'Astrub - Forêt', 'level_range': [1, 20], 'coordinates': {'x': 0, 'y': 0}, 'skill_ids': [71, 72], 'resource_ids': [5, 10, 15]},
        {'id': 2, 'name': 'Astrub - Champs', 'level_range': [1, 15], 'coordinates': {'x': 5, 'y': -3}, 'skill_ids': [64], 'resource_ids': [1, 2, 3]},
        {'id': 3, 'name': 'Mines d\'Astrub', 'level_range': [5, 25], 'coordinates': {'x': -8, 'y': 2}, 'skill_ids': [73], 'resource_ids': [50, 51, 52]},
        {'id': 4, 'name': 'Lac Cania', 'level_range': [10, 30], 'coordinates': {'x': 10, 'y': 5}, 'skill_ids': [75], 'resource_ids': [100, 101]},
        {'id': 5, 'name': 'Bonta - Forêt Nord', 'level_range': [30, 60], 'coordinates': {'x': -15, 'y': 10}, 'skill_ids': [71, 72], 'resource_ids': [20, 25, 30]},
        {'id': 6, 'name': 'Sufokia - Mines', 'level_range': [40, 80], 'coordinates': {'x': 20, 'y': -15}, 'skill_ids': [73], 'resource_ids': [55, 60, 65]},
        {'id': 7, 'name': 'Brâkmar - Champs Obscurs', 'level_range': [50, 100], 'coordinates': {'x': -20, 'y': -10}, 'skill_ids': [64, 72], 'resource_ids': [40, 45]},
        {'id': 8, 'name': 'Océan Crocuzko', 'level_range': [60, 120], 'coordinates': {'x': 25, 'y': 20}, 'skill_ids': [75], 'resource_ids': [110, 115]}
    ]
    
    # Filtrer zones accessibles par niveau
    accessible_zones = [z for z in all_zones if z['level_range'][0] <= player_level]
    
    # Calculer efficacité pour chaque zone
    zone_scores = []
    for zone in accessible_zones:
        matched_resources = [rid for rid in resource_ids if rid in zone['resource_ids']]
        if matched_resources:
            efficiency = len(matched_resources) / len(resource_ids)
            zone_scores.append({
                'zone': zone,
                'efficiency': efficiency,
                'matched_resources': matched_resources,
                'match_count': len(matched_resources)
            })
    
    # Trier par efficacité
    zone_scores.sort(key=lambda x: x['match_count'], reverse=True)
    
    # Limiter au nombre max de zones
    recommended_zones = zone_scores[:max_zones]
    
    # Calculer distances entre zones (distance euclidienne)
    def calculate_distance(zone1, zone2):
        import math
        x1, y1 = zone1['coordinates']['x'], zone1['coordinates']['y']
        x2, y2 = zone2['coordinates']['x'], zone2['coordinates']['y']
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Calculer distance totale (parcours séquentiel)
    total_distance = 0
    if len(recommended_zones) > 1:
        for i in range(len(recommended_zones) - 1):
            z1 = recommended_zones[i]['zone']
            z2 = recommended_zones[i + 1]['zone']
            dist = calculate_distance(z1, z2)
            recommended_zones[i]['distance_to_next'] = round(dist, 2)
            total_distance += dist
    
    # Générer itinéraire textuel
    itinerary = ' -> '.join([rz['zone']['name'] for rz in recommended_zones])
    
    return jsonify({
        'recommended_zones': [
            {
                'zone': rz['zone'],
                'efficiency': round(rz['efficiency'], 2),
                'matched_resources': rz['matched_resources'],
                'distance_to_next': rz.get('distance_to_next', 0)
            }
            for rz in recommended_zones
        ],
        'total_distance': round(total_distance, 2),
        'itinerary': itinerary,
        'resources_covered': sum(len(rz['matched_resources']) for rz in recommended_zones),
        'resources_requested': len(resource_ids)
    })
