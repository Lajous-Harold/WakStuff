"""
Pipeline d'import complet pour toutes les données Wakfu V2.

Ce module gère l'import en 4 phases selon le plan de refonte:

PHASE 1: Métiers et Types
- RecipeCategory (14 métiers depuis recipeCategories.json)
- ItemType (96 types depuis itemTypes.json)
- EquipmentItemType (31 types depuis equipmentItemTypes.json)
- ResourceType (6 types depuis resourceTypes.json)

PHASE 2: Ressources et Récolte
- Resource (170 ressources depuis resources.json)
- CollectibleResource (666 actions depuis collectibleResources.json)
- HarvestLoot (1,221 loots depuis harvestLoots.json)
- HarvestResource (452 ressources reconstruites)

PHASE 3: Items et JobItems
- JobItem (8,576 items depuis jobsItems.json)
- Item (items enrichis depuis items.json)

PHASE 4: Craft
- Recipe (recettes simplifiées depuis recipes.json)
- RecipeIngredient (34,571 ingrédients depuis recipeIngredients.json)
- RecipeResult (5,543 résultats depuis recipeResults.json)
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..database import db
from ..models import (
    Action,
    CollectibleResource,
    EquipmentItem,
    EquipmentItemType,
    HarvestLoot,
    HarvestResource,
    ImportBatch,
    Item,
    ItemCategory,
    ItemRaw,
    ItemType,
    JobItem,
    Recipe,
    RecipeCategory,
    RecipeIngredient,
    RecipeResult,
    Resource,
    ResourceType,
    State,
)

logger = logging.getLogger(__name__)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ========== MAPPINGS CRITIQUES ==========

SKILL_TO_JOB = {
    64: {"id": 1, "name": "Paysan", "category_type": "harvest"},
    71: {"id": 2, "name": "Forestier", "category_type": "harvest"},
    72: {"id": 6, "name": "Herboriste", "category_type": "harvest"},
    73: {"id": 3, "name": "Mineur", "category_type": "harvest"},
    75: {"id": 4, "name": "Pêcheur", "category_type": "harvest"},
}

RESOURCE_TYPE_MAPPING = {
    1: {"name": "Arbres", "skill_id": 71, "job_id": 2},
    2: {"name": "Cultures", "skill_id": 64, "job_id": 1},
    7: {"name": "Minerais", "skill_id": 73, "job_id": 3},
    10: {"name": "Plantes Sauvages", "skill_id": 72, "job_id": 6},
    20: {"name": "Poissons", "skill_id": 75, "job_id": 4},
}


def load_json(filename: str, data_dir: str = "/app/sandbox/json_data") -> List[Dict]:
    """Charge un fichier JSON depuis le dossier de données."""
    filepath = Path(data_dir) / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ========== PHASE 1: MÉTIERS ET TYPES ==========

def import_recipe_categories() -> int:
    """Import des RecipeCategory depuis recipeCategories.json (14 métiers)."""
    logger.info("Phase 1.1: Import des RecipeCategory...")
    categories = load_json('recipeCategories.json')
    count = 0
    
    for cat in categories:
        name = cat['title'].get('fr', 'Unknown')
        wakfu_id = cat['definition']['id']
        
        # Détection du type de métier
        skill_id = None
        category_type = "craft"
        
        for sid, info in SKILL_TO_JOB.items():
            if info['name'].lower() in name.lower():
                skill_id = sid
                category_type = "harvest"
                break
        
        recipe_cat = RecipeCategory(
            wakfu_id=wakfu_id,
            name=name,
            title=cat['title'],
            description=cat.get('description'),
            category_type=category_type,
            skill_id=skill_id
        )
        db.session.add(recipe_cat)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} RecipeCategory importés")
    return count


def import_item_types() -> int:
    """Import des ItemType depuis itemTypes.json (96 types)."""
    logger.info("Phase 1.2: Import des ItemType...")
    item_types = load_json('itemTypes.json')
    count = 0
    
    for it in item_types:
        # Certains types n'ont pas de title
        if 'title' not in it:
            continue
            
        item_type = ItemType(
            wakfu_id=it['definition']['id'],
            title=it['title'],
            category=it.get('category')
        )
        db.session.add(item_type)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} ItemType importés")
    return count


def import_equipment_item_types() -> int:
    """Import des EquipmentItemType depuis equipmentItemTypes.json (31 types)."""
    logger.info("Phase 1.3: Import des EquipmentItemType...")
    equipment_types = load_json('equipmentItemTypes.json')
    count = 0
    
    for et in equipment_types:
        equipment_type = EquipmentItemType(
            wakfu_id=et['definition']['id'],
            title=et['title'],
            equipment_positions=et['definition'].get('equipmentPositions', [])
        )
        db.session.add(equipment_type)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} EquipmentItemType importés")
    return count


def import_resource_types() -> int:
    """Import des ResourceType depuis resourceTypes.json (6 types)."""
    logger.info("Phase 1.4: Import des ResourceType...")
    resource_types = load_json('resourceTypes.json')
    count = 0
    
    for rt in resource_types:
        resource_type = ResourceType(
            type_id=rt['definition']['id'],
            title=rt.get('title', {})
        )
        db.session.add(resource_type)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} ResourceType importés")
    return count


# ========== PHASE 2: RESSOURCES ET RÉCOLTE ==========

def import_resources() -> int:
    """Import des Resource depuis resources.json (170 ressources)."""
    logger.info("Phase 2.1: Import des Resource...")
    resources = load_json('resources.json')
    count = 0
    
    for res in resources:
        definition = res.get('definition', {})
        resource = Resource(
            wakfu_id=definition.get('id'),
            title=res.get('title', {}),
            description=res.get('description'),
            resource_type_id=definition.get('resourceType'),
            raw_data=res
        )
        db.session.add(resource)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} Resource importés")
    return count


def import_collectable_resources() -> int:
    """Import des CollectibleResource depuis collectibleResources.json (666 actions)."""
    logger.info("Phase 2.2: Import des CollectibleResource...")
    collectibles = load_json('collectibleResources.json')
    count = 0
    
    for col in collectibles:
        # Trouver le RecipeCategory correspondant au skillId
        recipe_cat = RecipeCategory.query.filter_by(skill_id=col['skillId']).first()
        
        collectable = CollectibleResource(
            wakfu_id=col['id'],
            skill_id=col['skillId'],
            recipe_category_id=recipe_cat.id if recipe_cat else None,
            resource_id=col['resourceId'],
            resource_wakfu_id=col['resourceId'],
            resource_index=col.get('resourceIndex', 0),
            skill_level_required=col['skillLevelRequired'],
            collect_item_id=col.get('collectItemId'),
            collect_loot_list_id=col['collectLootListId'],
            duration=col.get('duration', 3000),
            simultaneous_player=col.get('simultaneousPlayer', 1),
            xp_factor=col.get('xpFactor', 1.0),
            raw_data=col
        )
        db.session.add(collectable)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} CollectibleResource importés")
    return count


def import_harvest_loots() -> int:
    """Import des HarvestLoot depuis harvestLoots.json (1,221 loots)."""
    logger.info("Phase 2.3: Import des HarvestLoot...")
    loots = load_json('harvestLoots.json')
    count = 0
    
    for loot in loots:
        harvest_loot = HarvestLoot(
            wakfu_id=loot['id'],
            item_id=loot['itemId'],
            list_id=loot['listId'],
            quantity=loot.get('quantity', 1),
            quantity_min=loot.get('quantityMin', 1),
            quantity_max=loot.get('quantityMax', 1),
            quantity_per_item=loot.get('quantityPerItem', 1),
            drop_rate=loot.get('dropRate', 1.0),
            max_roll=loot.get('maxRoll', 1),
            required_prospection=loot.get('requiredProspection', 0),
            item_is_loot_list=loot.get('itemIsLootList', False)
        )
        db.session.add(harvest_loot)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} HarvestLoot importés")
    return count


def rebuild_harvest_resources() -> int:
    """Reconstruit HarvestResource à partir des HarvestLoot et JobItem."""
    logger.info("Phase 2.4: Reconstruction des HarvestResource...")
    
    # Supprimer anciennes données
    HarvestResource.query.delete()
    
    # Pour chaque item unique dans HarvestLoot
    unique_items = db.session.query(HarvestLoot.item_id).distinct().all()
    count = 0
    
    for (item_id,) in unique_items:
        # Récupérer toutes les entrées de loot pour cet item
        loots = HarvestLoot.query.filter_by(item_id=item_id).all()
        
        # Trouver le JobItem correspondant
        job_item = JobItem.query.filter_by(wakfu_id=item_id).first()
        
        if not job_item:
            continue
        
        # Calculer les statistiques de drop
        drop_rates = [l.drop_rate for l in loots]
        quantities = [(l.quantity_min, l.quantity_max) for l in loots]
        
        # Déterminer le métier via CollectibleResource
        collectable = CollectibleResource.query.filter(
            CollectibleResource.collect_loot_list_id.in_([l.list_id for l in loots])
        ).first()
        
        skill_id = collectable.skill_id if collectable else None
        job_info = SKILL_TO_JOB.get(skill_id, {}) if skill_id else {}
        job_id = job_info.get('id')
        
        # Déterminer le resource_type_id via le mapping inversé
        resource_type_id = None
        if skill_id:
            for rt_id, rt_info in RESOURCE_TYPE_MAPPING.items():
                if rt_info.get('skill_id') == skill_id:
                    resource_type_id = rt_id
                    break
        
        # Créer HarvestResource
        harvest_resource = HarvestResource(
            item_id=item_id,
            name=job_item.title.get('fr') if isinstance(job_item.title, dict) else str(job_item.title),
            level=job_item.level,
            rarity=job_item.rarity,
            icon_gfx_id=job_item.icon_gfx_id,
            job_id=job_id,
            skill_id=skill_id,
            resource_type_id=resource_type_id,
            item_type_id=job_item.item_type_id,
            min_drop_rate=min(drop_rates) if drop_rates else None,
            max_drop_rate=max(drop_rates) if drop_rates else None,
            avg_drop_rate=sum(drop_rates)/len(drop_rates) if drop_rates else None,
            min_quantity=min(q[0] for q in quantities) if quantities else 1,
            max_quantity=max(q[1] for q in quantities) if quantities else 1,
            required_prospection=max(l.required_prospection for l in loots),
            source_count=len(set(l.list_id for l in loots))
        )
        db.session.add(harvest_resource)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} HarvestResource reconstruits")
    return count


# ========== PHASE 3: ITEMS ET JOBITEMS ==========

def import_job_items() -> int:
    """Import des JobItem depuis jobsItems.json (8,576 items)."""
    logger.info("Phase 3.1: Import des JobItem...")
    job_items = load_json('jobsItems.json')
    count = 0
    
    for ji in job_items:
        definition = ji.get('definition', {})
        
        job_item = JobItem(
            wakfu_id=definition.get('id'),
            job_id=None,
            recipe_category_id=None,
            title=ji.get('title', {}),
            description=ji.get('description'),
            level=definition.get('level'),
            rarity=definition.get('rarity'),
            item_type_id=definition.get('itemTypeId'),
            icon_gfx_id=definition.get('graphicParameters', {}).get('gfxId'),
            raw_data=ji
        )
        db.session.add(job_item)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} JobItem importés")
    return count


def import_items() -> int:
    """Import des Item enrichis depuis items.json."""
    logger.info("Phase 3.2: Import des Item...")
    items = load_json('items.json')
    count = 0
    
    for item_data in items:
        definition = item_data.get('definition', {})
        item_obj = definition.get('item', {})
        item_id = item_obj.get('id')
        
        # Croiser avec JobItem si disponible
        job_item = JobItem.query.filter_by(wakfu_id=item_id).first()
        
        item = Item(
            wakfu_id=item_id,
            title=item_data.get('title', {}),
            description=item_data.get('description'),
            level=item_obj.get('level'),
            rarity=item_obj.get('baseParameters', {}).get('rarity'),
            item_type_id=item_obj.get('baseParameters', {}).get('itemTypeId'),
            equipment_type_id=None,  # Non disponible dans items.json
            icon_gfx_id=item_obj.get('graphicParameters', {}).get('gfxId'),
            use_effects=definition.get('useEffects'),
            use_critical_effects=definition.get('useCriticalEffects'),
            equip_effects=definition.get('equipEffects'),
            item_properties=item_obj.get('properties'),
            job_item_id=job_item.wakfu_id if job_item else None,
            raw_data=item_data
        )
        db.session.add(item)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} Item importés")
    return count


# ========== PHASE 4: CRAFT ==========

def import_recipes() -> int:
    """Import des Recipe depuis recipes.json."""
    logger.info("Phase 4.1: Import des Recipe...")
    recipes = load_json('recipes.json')
    count = 0
    
    for recipe_data in recipes:
        recipe_id = recipe_data.get('id')
        category_id = recipe_data.get('categoryId')
        
        # Trouver le RecipeCategory correspondant
        recipe_cat = None
        if category_id:
            recipe_cat = RecipeCategory.query.filter_by(wakfu_id=category_id).first()
        
        recipe = Recipe(
            wakfu_id=recipe_id,
            level=recipe_data.get('level'),
            recipe_category_id=recipe_cat.id if recipe_cat else None,
            raw_data=recipe_data
        )
        db.session.add(recipe)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} Recipe importés")
    return count


def import_recipe_ingredients() -> int:
    """Import des RecipeIngredient depuis recipeIngredients.json (34,571 ingrédients)."""
    logger.info("Phase 4.2: Import des RecipeIngredient...")
    ingredients = load_json('recipeIngredients.json')
    count = 0
    
    for ing in ingredients:
        ingredient = RecipeIngredient(
            recipe_id=ing['recipeId'],
            recipe_wakfu_id=ing['recipeId'],
            item_id=ing['itemId'],
            quantity=ing['quantity']
        )
        db.session.add(ingredient)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} RecipeIngredient importés")
    return count


def import_recipe_results() -> int:
    """Import des RecipeResult depuis recipeResults.json (5,543 résultats)."""
    logger.info("Phase 4.3: Import des RecipeResult...")
    results = load_json('recipeResults.json')
    count = 0
    
    for res in results:
        result = RecipeResult(
            recipe_id=res['recipeId'],
            recipe_wakfu_id=res['recipeId'],
            producted_item_id=res['productedItemId'],
            producted_item_quantity=res.get('productedItemQuantity', 1),
            product_order=res.get('productOrder', 0)
        )
        db.session.add(result)
        count += 1
    
    db.session.commit()
    logger.info(f"✓ {count} RecipeResult importés")
    return count


# ========== ORCHESTRATION PRINCIPALE ==========

def run_full_wakfu_import(batch: Optional[ImportBatch] = None) -> ImportBatch:
    """Import complet de toutes les données Wakfu en 4 phases."""
    # Créer les tables si elles n'existent pas AVANT tout
    logger.info("🔧 Vérification/création des tables...")
    from .. import models  # Import models to register them
    try:
        db.create_all()
        logger.info("✅ Tables créées")
    except Exception as e:
        logger.info(f"✅ Tables déjà existantes ({str(e)[:50]})")
    
    if batch is None:
        batch = ImportBatch(
            batch_type="full_import",
            status="in_progress",
            started_at=now_utc()
        )
        db.session.add(batch)
        db.session.commit()
    
    try:
        logger.info("=" * 60)
        logger.info("DÉBUT DE L'IMPORT COMPLET WAKFU V2")
        logger.info("=" * 60)
        
        stats = {"phase_1": {}, "phase_2": {}, "phase_3": {}, "phase_4": {}}
        
        # PHASE 1
        logger.info("\n🔷 PHASE 1: MÉTIERS ET TYPES")
        stats["phase_1"]["recipe_categories"] = import_recipe_categories()
        stats["phase_1"]["item_types"] = import_item_types()
        stats["phase_1"]["equipment_item_types"] = import_equipment_item_types()
        stats["phase_1"]["resource_types"] = import_resource_types()
        phase_1_total = sum(stats["phase_1"].values())
        logger.info(f"✅ Phase 1 terminée: {phase_1_total} entrées")
        
        # PHASE 2
        logger.info("\n🔷 PHASE 2: RESSOURCES ET RÉCOLTE")
        stats["phase_2"]["resources"] = import_resources()
        stats["phase_2"]["collectable_resources"] = import_collectable_resources()
        stats["phase_2"]["harvest_loots"] = import_harvest_loots()
        stats["phase_2"]["harvest_resources"] = rebuild_harvest_resources()
        phase_2_total = sum(stats["phase_2"].values())
        logger.info(f"✅ Phase 2 terminée: {phase_2_total} entrées")
        
        # PHASE 3
        logger.info("\n🔷 PHASE 3: ITEMS ET JOBITEMS")
        stats["phase_3"]["job_items"] = import_job_items()
        stats["phase_3"]["items"] = import_items()
        phase_3_total = sum(stats["phase_3"].values())
        logger.info(f"✅ Phase 3 terminée: {phase_3_total} entrées")
        
        # PHASE 4
        logger.info("\n🔷 PHASE 4: CRAFT")
        stats["phase_4"]["recipes"] = import_recipes()
        stats["phase_4"]["recipe_ingredients"] = import_recipe_ingredients()
        stats["phase_4"]["recipe_results"] = import_recipe_results()
        phase_4_total = sum(stats["phase_4"].values())
        logger.info(f"✅ Phase 4 terminée: {phase_4_total} entrées")
        
        # FINALISATION
        total_imported = phase_1_total + phase_2_total + phase_3_total + phase_4_total
        
        batch.status = "completed"
        batch.completed_at = now_utc()
        batch.items_imported = total_imported
        batch.import_metadata = {
            "stats": stats,
            "summary": {
                "phase_1_total": phase_1_total,
                "phase_2_total": phase_2_total,
                "phase_3_total": phase_3_total,
                "phase_4_total": phase_4_total,
                "grand_total": total_imported
            }
        }
        db.session.commit()
        
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ IMPORT COMPLET TERMINÉ: {total_imported} entrées")
        logger.info("=" * 60)
        
        return batch
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'import: {e}", exc_info=True)
        batch.status = "failed"
        batch.error_message = str(e)
        batch.completed_at = now_utc()
        db.session.commit()
        raise


# ========== UTILITAIRES ==========

def clear_all_data():
    """Supprime toutes les données importées."""
    logger.warning("⚠️ Suppression de toutes les données...")
    
    RecipeResult.query.delete()
    RecipeIngredient.query.delete()
    Recipe.query.delete()
    Item.query.delete()
    JobItem.query.delete()
    HarvestResource.query.delete()
    HarvestLoot.query.delete()
    CollectibleResource.query.delete()
    Resource.query.delete()
    ResourceType.query.delete()
    EquipmentItemType.query.delete()
    ItemType.query.delete()
    RecipeCategory.query.delete()
    
    db.session.commit()
    logger.info("✓ Toutes les données ont été supprimées")


def get_import_stats() -> Dict[str, int]:
    """Retourne les statistiques du contenu de la base de données."""
    return {
        "recipe_categories": RecipeCategory.query.count(),
        "item_types": ItemType.query.count(),
        "equipment_item_types": EquipmentItemType.query.count(),
        "resource_types": ResourceType.query.count(),
        "resources": Resource.query.count(),
        "collectable_resources": CollectibleResource.query.count(),
        "harvest_loots": HarvestLoot.query.count(),
        "harvest_resources": HarvestResource.query.count(),
        "job_items": JobItem.query.count(),
        "items": Item.query.count(),
        "recipes": Recipe.query.count(),
        "recipe_ingredients": RecipeIngredient.query.count(),
        "recipe_results": RecipeResult.query.count(),
    }
