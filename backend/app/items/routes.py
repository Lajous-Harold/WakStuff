from flask import Blueprint, jsonify, request
from ..imports.routes import build_icon_url
from ..database import db
from ..models import Item, ItemCategory

items_bp = Blueprint("items", __name__)


def serialize_item(item: Item, include_details: bool = False) -> dict:
    """Sérialise un item avec option d'inclure les détails complets."""
    result = {
        "id": item.id,
        "wakfu_id": item.wakfu_id,
        "name": item.name,
        "rarity": item.rarity,
        "level": item.level,
        "type": item.type,
        "element": item.element,
        "icon_gfx_id": item.icon_gfx_id,
        "icon_url": build_icon_url(item.icon_gfx_id),
        "needs_review": item.needs_review,
        "category": item.category.name if item.category else None,
    }
    
    if include_details:
        result["stats"] = item.stats
        result["description"] = item.description
        result["parsed_effects"] = item.parsed_effects
    
    return result


@items_bp.get("/")
def list_items():
    """
    Liste paginée des items.

    Query params:
      - limit      (int, optionnel, défaut = 100, 0 = tous les items)
      - offset     (int, optionnel, défaut = 0)
      - category   (str, optionnel, filtre par catégorie)
      - rarity     (str, optionnel, filtre par rareté)
      - level_min  (int, optionnel, niveau minimum)
      - level_max  (int, optionnel, niveau maximum)
      - search     (str, optionnel, recherche dans le nom)
      - details    (bool, optionnel, inclure stats/description/parsed_effects)
    """
    try:
        limit = int(request.args.get("limit", 100))
    except ValueError:
        limit = 100
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    offset = max(0, offset)
    
    category_filter = request.args.get("category")
    rarity_filter = request.args.get("rarity")
    search_filter = request.args.get("search")
    include_details = request.args.get("details", "false").lower() in ("true", "1", "yes")
    
    level_min = None
    level_max = None
    
    try:
        level_min_str = request.args.get("level_min")
        if level_min_str:
            level_min = int(level_min_str)
    except (ValueError, TypeError):
        level_min = None
    
    try:
        level_max_str = request.args.get("level_max")
        if level_max_str:
            level_max = int(level_max_str)
    except (ValueError, TypeError):
        level_max = None

    query = Item.query
    
    if category_filter:
        category = ItemCategory.query.filter_by(name=category_filter).first()
        if category:
            query = query.filter_by(category_id=category.id)
    
    if rarity_filter:
        query = query.filter_by(rarity=rarity_filter)
    
    if level_min is not None and level_min > 0:
        query = query.filter(Item.level >= level_min)
    
    if level_max is not None and level_max > 0:
        query = query.filter(Item.level <= level_max)
    
    if search_filter:
        query = query.filter(Item.name.ilike(f"%{search_filter}%"))
    
    query = query.order_by(Item.level.asc(), Item.id.asc())

    # Compter le total d'items correspondant aux filtres
    total = query.count()

    if limit == 0:
        items = query.offset(offset).all()
    else:
        limit = max(1, limit)
        items = query.limit(limit).offset(offset).all()

    return jsonify(
        {
            "items": [serialize_item(i, include_details=include_details) for i in items],
            "total": total,
            "limit": limit if limit > 0 else total,
            "offset": offset,
        }
    )


@items_bp.get("/<int:item_id>")
def get_item(item_id: int):
    """Récupère un item par son ID avec tous les détails."""
    item = Item.query.get_or_404(item_id)
    return serialize_item(item, include_details=True)

