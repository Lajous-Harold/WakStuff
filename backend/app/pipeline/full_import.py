"""
Pipeline d'import complet pour toutes les données Wakfu.

Ce module gère l'import de:
- Items (items.json)
- Actions (actions.json) - pour décoder les effets
- États (states.json) - pour les buffs/debuffs
- Jobs (jobs.json) - pour les métiers
- Types d'items (itemTypes.json) - pour la classification
- Recettes (recipes.json, recipeCategories.json) - pour le craft calculator

Démarque les imports précédents pour éviter les doublons.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..database import db
from ..models import (
    Action,
    ImportBatch,
    Item,
    ItemCategory,
    ItemRaw,
    Job,
    Recipe,
    State,
)
from ..wakfu_client import WakfuClient
from .classifier import classify_item, enrich_item_types_from_api, get_item_rarity_label
from .effect_parser import parse_all_item_effects
from .sanitize import sanitize_item

logger = logging.getLogger(__name__)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def run_full_wakfu_import(batch: Optional[ImportBatch] = None) -> ImportBatch:
    """
    Import complet de toutes les données Wakfu:
    1. Récupère la version actuelle
    2. Import des données de référence (actions, states, jobs, itemTypes)
    3. Import des items avec classification et parsing d'effets
    4. Import des recettes de craft
    5. Démarque les données obsolètes

    Returns:
        Le batch d'import créé ou mis à jour
    """
    client = WakfuClient()
    current_version = client.get_current_version()

    logger.info(f"Démarrage import Wakfu version {current_version}")

    if batch is None:
        batch = ImportBatch(status="running", game_version=current_version)
        db.session.add(batch)
        db.session.flush()
    else:
        batch.game_version = current_version

    try:
        # Étape 1: Importer les données de référence
        logger.info("Import des actions...")
        actions_data = _import_actions(client, current_version)

        logger.info("Import des états...")
        states_data = _import_states(client, current_version)

        logger.info("Import des jobs...")
        try:
            jobs_data = _import_jobs(client, current_version)
        except Exception as e:
            logger.warning(f"Échec de l'import des jobs (non critique): {e}")
            jobs_data = []

        logger.info("Import des types d'items...")
        item_types_map = _import_item_types(client, current_version)

        # Étape 2: Importer les items avec enrichissement
        logger.info("Import des items...")
        total_items, error_count = _import_items_with_effects(
            client,
            batch,
            current_version,
            actions_data,
            states_data,
            jobs_data,
            item_types_map,
        )

        # Étape 3: Importer les recettes de craft
        logger.info("Import des recettes...")
        _import_recipes(client, current_version)

        # Étape 4: Démarquer les anciennes données si changement de version
        _deprecate_old_data(current_version)

        # Finaliser le batch
        batch.total_items = total_items
        batch.error_count = error_count
        batch.status = "success"
        batch.ended_at = now_utc()

        db.session.commit()
        logger.info(f"Import terminé: {total_items} items, {error_count} erreurs")

        return batch

    except Exception as e:
        logger.error(f"Erreur lors de l'import: {e!r}", exc_info=True)
        batch.status = "failed"
        batch.ended_at = now_utc()
        db.session.commit()
        raise


def _import_actions(client: WakfuClient, version: str) -> List[Dict[str, Any]]:
    """Import des actions depuis actions.json."""
    actions_data = client.fetch_all_actions(version)

    for action_raw in actions_data:
        definition = action_raw.get("definition", {})
        wakfu_id = definition.get("id")

        if not wakfu_id:
            continue

        action = Action.query.filter_by(wakfu_id=wakfu_id).first()
        if action is None:
            action = Action(wakfu_id=wakfu_id)
            db.session.add(action)

        action.effect = definition.get("effect")
        action.description = action_raw.get("description", {})

    db.session.commit()
    logger.info(f"Actions importées: {len(actions_data)}")

    return actions_data


def _import_states(client: WakfuClient, version: str) -> List[Dict[str, Any]]:
    """Import des états depuis states.json."""
    states_data = client.fetch_all_states(version)

    for state_raw in states_data:
        definition = state_raw.get("definition", {})
        wakfu_id = definition.get("id")

        if not wakfu_id:
            continue

        state = State.query.filter_by(wakfu_id=wakfu_id).first()
        if state is None:
            state = State(wakfu_id=wakfu_id)
            db.session.add(state)

        state.title = state_raw.get("title", {})
        state.description = state_raw.get("description", {})

    db.session.commit()
    logger.info(f"États importés: {len(states_data)}")

    return states_data


def _import_jobs(client: WakfuClient, version: str) -> List[Dict[str, Any]]:
    """Import des jobs depuis jobs.json."""
    jobs_data = client.fetch_all_jobs(version)

    for job_raw in jobs_data:
        definition = job_raw.get("definition", {})
        wakfu_id = definition.get("id")

        if not wakfu_id:
            continue

        job = Job.query.filter_by(wakfu_id=wakfu_id).first()
        if job is None:
            job = Job(wakfu_id=wakfu_id)
            db.session.add(job)

        job.title = job_raw.get("title", {})
        job.description = job_raw.get("description", {})

    db.session.commit()
    logger.info(f"Jobs importés: {len(jobs_data)}")

    return jobs_data


def _import_item_types(
    client: WakfuClient, version: str
) -> Dict[int, Dict[str, Any]]:
    """Import et enrichissement des types d'items depuis itemTypes.json."""
    item_types_data = client.fetch_all_item_types(version)
    item_types_map = enrich_item_types_from_api(item_types_data)

    # Créer/mettre à jour les catégories dans la DB
    categories_created = set()

    for type_id, type_info in item_types_map.items():
        category_name = type_info.get("category", "misc")

        if category_name not in categories_created:
            category = ItemCategory.query.filter_by(name=category_name).first()
            if category is None:
                category = ItemCategory(name=category_name)
                db.session.add(category)

            # Ajouter ce typeId à la catégorie
            type_ids = category.type_ids or []
            if type_id not in type_ids:
                type_ids.append(type_id)
                category.type_ids = type_ids

            categories_created.add(category_name)

    db.session.commit()
    logger.info(f"Types d'items importés: {len(item_types_map)}")

    return item_types_map


def _import_items_with_effects(
    client: WakfuClient,
    batch: ImportBatch,
    version: str,
    actions_data: List[Dict[str, Any]],
    states_data: List[Dict[str, Any]],
    jobs_data: List[Dict[str, Any]],
    item_types_map: Dict[int, Dict[str, Any]],
) -> tuple[int, int]:
    """
    Import des items avec parsing des effets et classification.

    Returns:
        (total_items, error_count)
    """
    total_items = 0
    error_count = 0

    for raw in client.iter_all_items(version=version):
        total_items += 1

        try:
            # 1. Sanitize l'item
            clean = sanitize_item(raw)
            wakfu_id = clean["wakfu_id"]

            # 2. Classifier l'item
            classification = classify_item(raw)

            # 3. Parser les effets
            parsed_effects = parse_all_item_effects(
                raw, actions_data, states_data, jobs_data
            )

            # 4. Stocker le brut
            raw_entry = ItemRaw(
                wakfu_id=wakfu_id,
                raw_json=raw,
                batch=batch,
            )
            db.session.add(raw_entry)

            # 5. Créer/mettre à jour l'item
            item = Item.query.filter_by(wakfu_id=wakfu_id).first()
            if item is None:
                item = Item(wakfu_id=wakfu_id)
                db.session.add(item)

            # Mettre à jour les champs
            item.name = clean["name"]
            item.level = clean["level"]
            item.type = clean["type"]
            item.element = clean["element"]
            item.icon_gfx_id = clean["icon_gfx_id"]
            item.stats = clean["stats"]
            item.description = clean["description"]
            item.needs_review = clean["needs_review"]

            # Rareté avec label
            if clean.get("rarity"):
                try:
                    rarity_id = int(clean["rarity"].replace("rarity_", ""))
                    item.rarity = get_item_rarity_label(rarity_id)
                except (ValueError, AttributeError):
                    item.rarity = clean["rarity"]

            # Catégorie - Reconstru le chemin complet
            category_path = classification["category"]
            if classification.get("subcategory") and classification["subcategory"] != "general":
                # Si la subcategory contient déjà un point, elle est déjà complète
                if "." in classification["subcategory"]:
                    category_path = f"{classification['category']}.{classification['subcategory']}"
                else:
                    category_path = f"{classification['category']}.{classification['subcategory']}"
            
            category = ItemCategory.query.filter_by(name=category_path).first()
            if not category:
                # Fallback: chercher une catégorie qui commence par le même préfixe
                category = ItemCategory.query.filter(ItemCategory.name.like(f"{classification['category']}%")).first()
            if category:
                item.category = category

            # Effets parsés
            item.parsed_effects = parsed_effects

            # Commit par batch de 100 pour performance
            if total_items % 100 == 0:
                db.session.commit()
                logger.info(f"Progress: {total_items} items importés...")

        except Exception as exc:
            error_count += 1
            logger.warning(f"Erreur traitement item: {exc!r}")
            continue

    db.session.commit()
    return total_items, error_count


def _import_recipes(client: WakfuClient, version: str):
    """Import des recettes de craft depuis recipes.json."""
    try:
        recipes_data = client.fetch_all_recipes(version)

        for recipe_raw in recipes_data:
            definition = recipe_raw.get("definition", {})
            wakfu_id = definition.get("id")

            if not wakfu_id:
                continue

            recipe = Recipe.query.filter_by(wakfu_id=wakfu_id).first()
            if recipe is None:
                recipe = Recipe(wakfu_id=wakfu_id)
                db.session.add(recipe)

            # Récupérer les ingrédients et le résultat
            result_id = definition.get("productedItemId")
            ingredients_raw = definition.get("ingredients", [])

            ingredients = []
            for ing in ingredients_raw:
                ingredients.append(
                    {"item_id": ing.get("itemId"), "quantity": ing.get("quantity", 1)}
                )

            recipe.result_item_id = result_id
            recipe.ingredients = ingredients
            recipe.job_id = definition.get("jobId")
            recipe.craft_level = definition.get("level")

        db.session.commit()
        logger.info(f"Recettes importées: {len(recipes_data)}")

    except Exception as e:
        logger.warning(f"Impossible d'importer les recettes: {e!r}")


def _deprecate_old_data(current_version: str):
    """
    Démarque les données des versions précédentes.

    Pour l'instant, on garde tout mais on pourrait:
    - Ajouter un champ 'deprecated' sur les items
    - Supprimer les items qui n'existent plus
    - Archiver les anciennes versions
    """
    last_batch = (
        ImportBatch.query.order_by(ImportBatch.started_at.desc())
        .filter(ImportBatch.game_version != current_version)
        .first()
    )

    if last_batch:
        logger.info(
            f"Changement de version détecté: {last_batch.game_version} -> {current_version}"
        )
        # TODO: Implémenter la logique de démarquage
        # Par exemple: marquer comme deprecated les items absents de la nouvelle version
    else:
        logger.info("Première importation ou même version")
