"""
Routes API pour les items.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from ..database import db
from ..models import Item, ItemType, ItemCategory, JobItem

bp = Blueprint('items', __name__)


@bp.route('', methods=['GET'])
def get_items():
    """
    GET /api/items
    
    Liste des items avec filtrage et pagination.
    
    Query params:
    - search: Recherche dans le titre
    - item_type_id: Filtrer par type d'item
    - level_min, level_max: Niveau
    - rarity: Rareté (0-7)
    - page, per_page: Pagination
    """
    try:
        search = request.args.get('search', '').strip()
        item_type_id = request.args.get('item_type_id', type=int)
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
        
        if level_min:
            query = query.filter(Item.level >= level_min)
        
        if level_max:
            query = query.filter(Item.level <= level_max)
        
        if rarity is not None:
            query = query.filter(Item.rarity == rarity)
        
        query = query.order_by(Item.level.desc(), Item.wakfu_id)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
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
    
    Détails complets d'un item.
    """
    item = Item.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    
    return jsonify({
        'item': item.to_dict()
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
