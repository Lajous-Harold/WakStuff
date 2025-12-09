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
