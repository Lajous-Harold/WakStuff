"""
Routes pour gérer l'import complet des données Wakfu.
"""

import logging
from flask import Blueprint, jsonify
from ..pipeline.full_import import run_full_wakfu_import
from ..database import db
from ..models import ImportBatch, Action, State, Job, Item, Recipe

logger = logging.getLogger(__name__)

bp = Blueprint("wakfu_data", __name__, url_prefix="/api/wakfu")


@bp.route("/import/full", methods=["POST"])
def trigger_full_import():
    """
    Lance un import complet de toutes les données Wakfu.
    Endpoint: POST /api/wakfu/import/full
    """
    try:
        batch = run_full_wakfu_import()

        return jsonify(
            {
                "success": True,
                "batch_id": batch.id,
                "version": batch.game_version,
                "total_items": batch.total_items,
                "error_count": batch.error_count,
                "status": batch.status,
            }
        ), 200

    except Exception as e:
        logger.error(f"Erreur import complet: {e!r}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Retourne des statistiques sur les données importées.
    Endpoint: GET /api/wakfu/stats
    """
    try:
        stats = {
            "items": {
                "total": Item.query.count(),
                "by_category": _get_items_by_category(),
                "by_rarity": _get_items_by_rarity(),
            },
            "actions": Action.query.count(),
            "states": State.query.count(),
            "jobs": Job.query.count(),
            "recipes": Recipe.query.count(),
            "last_import": _get_last_import_info(),
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Erreur stats: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/categories", methods=["GET"])
def get_categories():
    """
    Liste toutes les catégories d'items disponibles avec détails.
    Endpoint: GET /api/wakfu/categories
    """
    from ..models import ItemCategory
    from ..pipeline.wakfu_config import WAKFU_ITEM_CATEGORIES

    try:
        categories = ItemCategory.query.all()
        result = []
        
        for cat in categories:
            # Récupérer la config pour les labels
            config = WAKFU_ITEM_CATEGORIES.get(cat.name, {})
            
            # Extraire le groupe et le nom court
            parts = cat.name.split(".")
            group = parts[0] if len(parts) > 1 else "other"
            short_name = parts[-1]
            
            result.append({
                "id": cat.id,
                "name": cat.name,
                "short_name": short_name,
                "group": group,
                "description": cat.description,
                "label_fr": config.get("label_fr", cat.name),
                "label_en": config.get("label_en", cat.name),
                "type_ids": cat.type_ids or [],
                "item_count": len(cat.items),
            })

        # Trier par groupe puis par nom
        result.sort(key=lambda x: (x["group"], x["name"]))

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Erreur categories: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/recipes/<int:item_id>", methods=["GET"])
def get_item_recipes(item_id):
    """
    Retourne toutes les recettes qui produisent un item donné.
    Endpoint: GET /api/wakfu/recipes/<item_id>
    """
    try:
        recipes = Recipe.query.filter_by(result_item_id=item_id).all()

        result = []
        for recipe in recipes:
            result.append(
                {
                    "id": recipe.id,
                    "wakfu_id": recipe.wakfu_id,
                    "ingredients": recipe.ingredients,
                    "job_id": recipe.job_id,
                    "craft_level": recipe.craft_level,
                }
            )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Erreur recipes: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/craft-calculator/<int:item_id>", methods=["GET"])
def calculate_craft_resources(item_id):
    """
    Calcule récursivement toutes les ressources nécessaires pour crafter un item.
    Endpoint: GET /api/wakfu/craft-calculator/<item_id>
    """
    try:
        resources = _calculate_recursive_resources(item_id)

        return jsonify(
            {"item_id": item_id, "total_resources": resources, "tree": _build_craft_tree(item_id)}
        ), 200

    except Exception as e:
        logger.error(f"Erreur craft calculator: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/categories/grouped", methods=["GET"])
def get_categories_grouped():
    """
    Liste les catégories groupées par type (equipments, resources, consumables, etc.).
    Endpoint: GET /api/wakfu/categories/grouped
    """
    from ..models import ItemCategory
    from ..pipeline.wakfu_config import WAKFU_ITEM_CATEGORIES
    from collections import defaultdict

    try:
        categories = ItemCategory.query.all()
        grouped = defaultdict(list)
        
        for cat in categories:
            config = WAKFU_ITEM_CATEGORIES.get(cat.name, {})
            parts = cat.name.split(".")
            group = parts[0] if len(parts) > 1 else "other"
            
            grouped[group].append({
                "id": cat.id,
                "name": cat.name,
                "label_fr": config.get("label_fr", cat.name),
                "label_en": config.get("label_en", cat.name),
                "item_count": len(cat.items),
            })
        
        # Convertir en liste et trier
        result = []
        for group_name, cats in grouped.items():
            cats.sort(key=lambda x: x["name"])
            result.append({
                "group": group_name,
                "categories": cats,
                "total_items": sum(c["item_count"] for c in cats)
            })
        
        result.sort(key=lambda x: x["group"])
        
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Erreur categories grouped: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route("/harvest-resources", methods=["GET"])
def get_harvest_resources():
    """
    Liste toutes les ressources de récolte avec leurs informations.
    Endpoint: GET /api/wakfu/harvest-resources
    """
    from ..models import HarvestResource, Item
    from sqlalchemy import func

    try:
        # Récupérer toutes les ressources avec les infos des items associés
        resources = (
            db.session.query(HarvestResource, Item)
            .outerjoin(Item, Item.wakfu_id == HarvestResource.item_id)
            .all()
        )

        result = []
        for resource, item in resources:
            result.append({
                "item_id": resource.item_id,
                "name": item.name if item else f"Item #{resource.item_id}",
                "level": item.level if item else None,
                "rarity": item.rarity if item else None,
                "icon_gfx_id": item.icon_gfx_id if item else None,
                "quantity_min": resource.quantity_min,
                "quantity_max": resource.quantity_max,
                "drop_rate": resource.drop_rate,
                "list_id": resource.list_id,
            })

        # Trier par nom
        result.sort(key=lambda x: x["name"])

        return jsonify({
            "total": len(result),
            "resources": result
        }), 200

    except Exception as e:
        logger.error(f"Erreur harvest resources: {e!r}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# Fonctions utilitaires


def _get_items_by_category():
    """Compte les items par catégorie."""
    from sqlalchemy import func
    from ..models import ItemCategory

    result = (
        db.session.query(ItemCategory.name, func.count(Item.id))
        .join(Item, ItemCategory.id == Item.category_id, isouter=True)
        .group_by(ItemCategory.name)
        .all()
    )

    return {name: count for name, count in result}


def _get_items_by_rarity():
    """Compte les items par rareté."""
    from sqlalchemy import func

    result = (
        db.session.query(Item.rarity, func.count(Item.id))
        .group_by(Item.rarity)
        .all()
    )

    return {rarity or "unknown": count for rarity, count in result}


def _get_last_import_info():
    """Retourne les infos du dernier import."""
    last_batch = ImportBatch.query.order_by(ImportBatch.started_at.desc()).first()

    if not last_batch:
        return None

    return {
        "batch_id": last_batch.id,
        "version": last_batch.game_version,
        "started_at": last_batch.started_at.isoformat(),
        "ended_at": last_batch.ended_at.isoformat() if last_batch.ended_at else None,
        "status": last_batch.status,
        "total_items": last_batch.total_items,
        "error_count": last_batch.error_count,
    }


def _calculate_recursive_resources(item_id: int, quantity: int = 1) -> dict:
    """
    Calcule récursivement les ressources nécessaires pour crafter un item.

    Args:
        item_id: ID Wakfu de l'item à crafter
        quantity: Quantité désirée

    Returns:
        Dict {item_id: total_quantity_needed}
    """
    resources = {}

    # Trouver la recette
    recipe = Recipe.query.filter_by(result_item_id=item_id).first()

    if not recipe:
        # Pas de recette = ressource de base
        resources[item_id] = quantity
        return resources

    # Pour chaque ingrédient
    for ingredient in recipe.ingredients:
        ing_item_id = ingredient["item_id"]
        ing_quantity = ingredient["quantity"] * quantity

        # Récursion
        sub_resources = _calculate_recursive_resources(ing_item_id, ing_quantity)

        # Fusionner les résultats
        for res_id, res_qty in sub_resources.items():
            resources[res_id] = resources.get(res_id, 0) + res_qty

    return resources


def _build_craft_tree(item_id: int, quantity: int = 1, depth: int = 0, max_depth: int = 10):
    """
    Construit un arbre de craft récursif.

    Args:
        item_id: ID Wakfu de l'item
        quantity: Quantité
        depth: Profondeur actuelle (pour éviter les boucles infinies)
        max_depth: Profondeur maximale

    Returns:
        Dict représentant l'arbre de craft
    """
    if depth >= max_depth:
        return {"item_id": item_id, "quantity": quantity, "ingredients": []}

    item = Item.query.filter_by(wakfu_id=item_id).first()
    recipe = Recipe.query.filter_by(result_item_id=item_id).first()

    tree = {
        "item_id": item_id,
        "name": item.name if item else f"Item #{item_id}",
        "quantity": quantity,
        "ingredients": [],
    }

    if recipe:
        tree["recipe_id"] = recipe.wakfu_id
        tree["job_id"] = recipe.job_id
        tree["craft_level"] = recipe.craft_level

        for ingredient in recipe.ingredients:
            ing_id = ingredient["item_id"]
            ing_qty = ingredient["quantity"] * quantity

            sub_tree = _build_craft_tree(ing_id, ing_qty, depth + 1, max_depth)
            tree["ingredients"].append(sub_tree)

    return tree
