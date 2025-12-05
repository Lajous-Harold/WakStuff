"""
Routes API pour les ressources récoltables et le système de récolte.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import and_, or_
from ..database import db
from ..models import (
    Resource, CollectibleResource, HarvestLoot, HarvestResource,
    ResourceType, RecipeCategory, Item
)

bp = Blueprint('resources', __name__)


@bp.route('', methods=['GET'])
def get_resources():
    """
    GET /api/resources
    
    Récupère la liste des ressources récoltables.
    
    Query params:
    - resource_type_id: Filtrer par type (1=Arbres, 2=Cultures, 7=Minerais, 10=Plantes, 20=Poissons)
    - level_min, level_max: Niveau de récolte
    - page, per_page: Pagination
    """
    resource_type_id = request.args.get('resource_type_id', type=int)
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = Resource.query
    
    if resource_type_id:
        query = query.filter(Resource.resource_type_id == resource_type_id)
    
    if level_min:
        query = query.filter(Resource.level >= level_min)
    
    if level_max:
        query = query.filter(Resource.level <= level_max)
    
    query = query.order_by(Resource.level, Resource.wakfu_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'resources': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/<int:wakfu_id>', methods=['GET'])
def get_resource_detail(wakfu_id):
    """
    GET /api/resources/<wakfu_id>
    
    Détails complets d'une ressource avec ses actions de collecte et loots.
    """
    resource = Resource.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    
    # Récupérer les actions de collecte liées
    collectibles = CollectibleResource.query.filter_by(resource_id=wakfu_id).all()
    
    return jsonify({
        'resource': resource.to_dict(),
        'collectibles': [c.to_dict() for c in collectibles]
    })


@bp.route('/harvest-resources', methods=['GET'])
def get_harvest_resources():
    """
    GET /api/resources/harvest-resources
    
    Items récoltables avec filtrage par métier.
    
    Query params:
    - skill_id: 64=Paysan, 71=Forestier, 72=Herboriste, 73=Mineur, 75=Pêcheur
    - resource_type_id: Type de ressource
    - level_min, level_max: Niveau
    - page, per_page: Pagination
    """
    skill_id = request.args.get('skill_id', type=int)
    resource_type_id = request.args.get('resource_type_id', type=int)
    level_min = request.args.get('level_min', type=int)
    level_max = request.args.get('level_max', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    query = HarvestResource.query
    
    if skill_id:
        query = query.filter(HarvestResource.skill_id == skill_id)
    
    if resource_type_id:
        query = query.filter(HarvestResource.resource_type_id == resource_type_id)
    
    if level_min:
        query = query.filter(HarvestResource.level >= level_min)
    
    if level_max:
        query = query.filter(HarvestResource.level <= level_max)
    
    query = query.order_by(HarvestResource.level, HarvestResource.item_wakfu_id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'harvest_resources': [hr.to_dict() for hr in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@bp.route('/collectable/<int:wakfu_id>', methods=['GET'])
def get_collectable_detail(wakfu_id):
    """
    GET /api/resources/collectable/<wakfu_id>
    
    Détails d'une action de collecte avec ses loots.
    """
    collectable = CollectibleResource.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    
    # Récupérer les loots
    loots = HarvestLoot.query.filter_by(collect_loot_list_id=collectable.collect_loot_list_id).all()
    
    return jsonify({
        'collectable': collectable.to_dict(),
        'loots': [l.to_dict() for l in loots]
    })


@bp.route('/types', methods=['GET'])
def get_resource_types():
    """
    GET /api/resources/types
    
    Liste tous les types de ressources (Arbres, Cultures, Minerais, etc.)
    """
    types = ResourceType.query.order_by(ResourceType.type_id).all()
    
    return jsonify({
        'resource_types': [rt.to_dict() for rt in types]
    })
