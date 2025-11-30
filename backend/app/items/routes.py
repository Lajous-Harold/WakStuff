from flask import Blueprint, jsonify, request
from ..imports.routes import build_icon_url
from ..database import db
from ..models import Item

items_bp = Blueprint("items", __name__)


def serialize_item(item: Item) -> dict:
    return {
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
    }


@items_bp.get("/")
def list_items():
    """
    Liste paginée des items.

    Query params:
      - limit  (int, optionnel, défaut = 100, 0 = tous les items)
      - offset (int, optionnel, défaut = 0)
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

    query = Item.query.order_by(Item.level.asc(), Item.id.asc())

    if limit == 0:
        items = query.offset(offset).all()
    else:
        limit = max(1, limit)
        items = query.limit(limit).offset(offset).all()

    total = db.session.query(db.func.count(Item.id)).scalar() or 0

    return jsonify(
        {
            "items": [serialize_item(i) for i in items],
            "total": total,
            "limit": limit if limit > 0 else total,
            "offset": offset,
        }
    )


@items_bp.get("/<int:item_id>")
def get_item(item_id: int):
    item = Item.query.get_or_404(item_id)

    return {
        "id": item.id,
        "wakfu_id": item.wakfu_id,
        "name": item.name,
        "rarity": item.rarity,
        "level": item.level,
        "type": item.type,
        "element": item.element,
        "stats": item.stats,
        "icon_gfx_id": item.icon_gfx_id,
        "icon_url": build_icon_url(item.icon_gfx_id),
        "description": item.description,
        "needs_review": item.needs_review,
    }, 200
