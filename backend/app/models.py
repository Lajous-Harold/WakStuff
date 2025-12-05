"""
WakStuff Models V2 - Architecture complète basée sur les endpoints Wakfu API
Date: 2025-12-03
Version: 2.0

Architecture:
    collectibleResources (666) → skillId → Métier
      ├─ resourceId → resources (170) → resourceType (6)
      └─ collectLootListId → harvestLoots (1,221) → itemId → items (452)
"""

from datetime import datetime, timezone
from .database import db
from .models_utils import DictSerializable


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================================
# CORE MODELS (Unchanged)
# ============================================================================

class ImportBatch(db.Model, DictSerializable):
    """Historique des imports de données"""
    __tablename__ = "import_batches"

    id = db.Column(db.Integer, primary_key=True)
    batch_type = db.Column(db.String(64), default="full_import")
    started_at = db.Column(db.DateTime(timezone=True), default=now_utc, nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    game_version = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), default="running")
    total_items = db.Column(db.Integer, default=0)
    items_imported = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)
    import_metadata = db.Column(db.JSON, nullable=True)

    raw_items = db.relationship("ItemRaw", back_populates="batch")


class ItemRaw(db.Model, DictSerializable):
    """JSON brut de l'API Wakfu pour debug/reprocessing"""
    __tablename__ = "item_raw"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, index=True)
    raw_json = db.Column(db.JSON, nullable=False)
    import_batch_id = db.Column(db.Integer, db.ForeignKey("import_batches.id"), nullable=False)
    
    batch = db.relationship("ImportBatch", back_populates="raw_items")


class Action(db.Model, DictSerializable):
    """Actions Wakfu (actions.json) pour décoder les effets des items"""
    __tablename__ = "actions"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    effect = db.Column(db.Text)
    description = db.Column(db.JSON)  # {"fr": "...", "en": "..."}
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=now_utc)


class State(db.Model, DictSerializable):
    """États Wakfu (states.json) pour les buffs/debuffs"""
    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    title = db.Column(db.JSON)  # {"fr": "...", "en": "..."}
    description = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=now_utc)


# ============================================================================
# MÉTIERS & CATÉGORIES
# ============================================================================

class RecipeCategory(db.Model, DictSerializable):
    """
    Catégories de recettes / Métiers depuis recipeCategories.json (14 métiers)
    
    Métiers de récolte (5):
    - skillId 64: Paysan (Cultures)
    - skillId 71: Forestier (Arbres)
    - skillId 72: Herboriste (Plantes Sauvages)
    - skillId 73: Mineur (Minerais)
    - skillId 75: Pêcheur (Poissons)
    
    Métiers de craft (9):
    - Armurier, Bijoutier, Bricoleur, Cordonnier, Cuisinier, etc.
    """
    __tablename__ = "recipe_categories"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    name = db.Column(db.String(128), nullable=False)  # "Paysan", "Forestier", etc.
    title = db.Column(db.JSON)  # {"fr": "Paysan", "en": "Farmer", ...}
    description = db.Column(db.JSON, nullable=True)
    
    # Type de catégorie
    category_type = db.Column(db.String(32), nullable=False)  # "harvest" ou "craft"
    
    # Pour les métiers de récolte uniquement
    skill_id = db.Column(db.Integer, nullable=True, index=True)  # 64, 71, 72, 73, 75
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


class ItemType(db.Model, DictSerializable):
    """
    Types d'items depuis itemTypes.json (96 types)
    Ex: Potion, Nourriture, Ressource, Équipement, etc.
    """
    __tablename__ = "item_types"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    title = db.Column(db.JSON)  # {"fr": "Potion", "en": "Potion", ...}
    category = db.Column(db.String(64), nullable=True)  # Groupement custom
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


class EquipmentItemType(db.Model, DictSerializable):
    """
    Types d'équipements depuis equipmentItemTypes.json (31 types)
    Ex: Anneau, Amulette, Cape, Bottes, etc.
    """
    __tablename__ = "equipment_item_types"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    title = db.Column(db.JSON)  # {"fr": "Anneau", "en": "Ring", ...}
    equipment_positions = db.Column(db.JSON, nullable=True)  # [1, 2, ...] positions
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


class ResourceType(db.Model, DictSerializable):
    """
    Types de ressources depuis resourceTypes.json (6 types)
    
    Types identifiés:
    - 1: Arbres (skillId 71 - Forestier)
    - 2: Cultures (skillId 64 - Paysan)
    - 7: Minerais (skillId 73 - Mineur)
    - 10: Plantes Sauvages (skillId 72 - Herboriste)
    - 20: Poissons (skillId 75 - Pêcheur)
    """
    __tablename__ = "resource_types"

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False, unique=True, index=True)  # 1, 2, 7, 10, 20
    
    title = db.Column(db.JSON)  # {"fr": "Arbres", "en": "Trees", ...}
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


# ============================================================================
# SYSTÈME DE RÉCOLTE (Harvest System)
# ============================================================================

class Resource(db.Model, DictSerializable):
    """
    Ressources récoltables depuis resources.json (170 ressources)
    Représente les sources dans le monde (ex: Frêne, Blé, Fer, Lin)
    """
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    title = db.Column(db.JSON, nullable=False)  # {"fr": "Frêne", "en": "Ash", ...}
    description = db.Column(db.JSON, nullable=True)
    
    # Type de ressource
    resource_type_id = db.Column(db.Integer, db.ForeignKey("resource_types.type_id"), nullable=False, index=True)
    resource_type = db.relationship("ResourceType")
    
    raw_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


class CollectibleResource(db.Model, DictSerializable):
    """
    Actions de collecte depuis collectibleResources.json (666 actions)
    Une action = un clic sur une ressource dans le jeu
    
    CLEF: skillId détermine le métier requis (64, 71, 72, 73, 75)
    """
    __tablename__ = "collectable_resources"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Métier requis (CRITIQUE pour le mapping)
    skill_id = db.Column(db.Integer, nullable=False, index=True)  # 64, 71, 72, 73, 75
    recipe_category_id = db.Column(db.Integer, db.ForeignKey("recipe_categories.id"), nullable=True)
    recipe_category = db.relationship("RecipeCategory")
    
    # Ressource source
    resource_id = db.Column(db.Integer, nullable=False)
    resource_wakfu_id = db.Column(db.Integer, nullable=False, index=True)
    resource = db.relationship("Resource", foreign_keys="[CollectibleResource.resource_id]", primaryjoin="CollectibleResource.resource_id==Resource.id")
    resource_index = db.Column(db.Integer, default=0)
    
    # Niveau requis
    skill_level_required = db.Column(db.Integer, nullable=False, index=True)
    
    # Item requis pour collecter (ex: pioche)
    collect_item_id = db.Column(db.Integer, nullable=True)
    
    # Loot list (items droppés)
    collect_loot_list_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Temps de collecte (ms)
    duration = db.Column(db.Integer, default=3000)
    
    # Nombre de joueurs simultanés
    simultaneous_player = db.Column(db.Integer, default=1)
    
    # Facteur XP
    xp_factor = db.Column(db.Float, default=1.0)
    
    raw_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Index composés pour performance
    __table_args__ = (
        db.Index('idx_cl_skill_level', 'skill_id', 'skill_level_required'),
        db.Index('idx_cl_resource_skill', 'resource_wakfu_id', 'skill_id'),
    )


class HarvestLoot(db.Model, DictSerializable):
    """
    Items droppés lors de la collecte depuis harvestLoots.json (1,221 loots)
    Relie les actions de collecte aux items obtenus
    """
    __tablename__ = "harvest_loots"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Item droppé
    item_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Liste de loot (plusieurs loots peuvent partager la même liste)
    list_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Quantités
    quantity = db.Column(db.Integer, default=1)
    quantity_min = db.Column(db.Integer, default=1)
    quantity_max = db.Column(db.Integer, default=1)
    quantity_per_item = db.Column(db.Integer, default=1)
    
    # Taux de drop (0.0 à 1.0)
    drop_rate = db.Column(db.Float, default=1.0, index=True)
    max_roll = db.Column(db.Integer, default=1)
    
    # Prospection requise
    required_prospection = db.Column(db.Integer, default=0)
    
    # Si item_id est en fait une autre loot list (récursif)
    item_is_loot_list = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Index composés
    __table_args__ = (
        db.Index('idx_list_item', 'list_id', 'item_id'),
        db.Index('idx_item_list', 'item_id', 'list_id'),  # Reverse lookup
        db.Index('idx_drop_rate', 'drop_rate'),
    )


class HarvestResource(db.Model, DictSerializable):
    """
    Vue consolidée des items récoltables (452 items)
    REFACTORISÉ avec les nouvelles relations
    """
    __tablename__ = "harvest_resources"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Infos de base
    name = db.Column(db.String(256))
    level = db.Column(db.Integer, index=True)
    rarity = db.Column(db.Integer, index=True)
    icon_gfx_id = db.Column(db.Integer)
    
    # Métier (NOUVELLE ARCHITECTURE)
    skill_id = db.Column(db.Integer, nullable=True, index=True)  # 64, 71, 72, 73, 75
    job_id = db.Column(db.Integer, nullable=True, index=True)  # 1-6 (legacy compat)
    
    # Type de ressource
    resource_type_id = db.Column(db.Integer, db.ForeignKey("resource_types.type_id"), nullable=True, index=True)
    resource_type = db.relationship("ResourceType")
    
    # Type d'item
    item_type_id = db.Column(db.Integer, nullable=True, index=True)
    
    # Statistiques de drop
    min_drop_rate = db.Column(db.Float, nullable=True)
    max_drop_rate = db.Column(db.Float, nullable=True)
    avg_drop_rate = db.Column(db.Float, nullable=True)
    
    # Quantités
    min_quantity = db.Column(db.Integer, default=1)
    max_quantity = db.Column(db.Integer, default=1)
    
    # Prospection
    required_prospection = db.Column(db.Integer, default=0)
    
    # Nombre de sources différentes
    source_count = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=now_utc)
    
    # Index composés
    __table_args__ = (
        db.Index('idx_hr_skill_level', 'skill_id', 'level'),
        db.Index('idx_hr_job_level', 'job_id', 'level'),
        db.Index('idx_hr_resource_type', 'resource_type_id', 'level'),
    )


# ============================================================================
# ITEMS & JOB ITEMS
# ============================================================================

class JobItem(db.Model, DictSerializable):
    """
    Items de métiers depuis jobsItems.json (8,576 items)
    Version légère des items utilisée pour les crafts
    """
    __tablename__ = "job_items"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Métier lié
    job_id = db.Column(db.Integer, nullable=True, index=True)  # ID métier Wakfu
    recipe_category_id = db.Column(db.Integer, db.ForeignKey("recipe_categories.id"), nullable=True)
    recipe_category = db.relationship("RecipeCategory")
    
    # Infos de base
    title = db.Column(db.JSON)  # {"fr": "...", "en": "..."}
    description = db.Column(db.JSON, nullable=True)
    
    level = db.Column(db.Integer, nullable=True, index=True)
    rarity = db.Column(db.Integer, nullable=True, index=True)
    
    # Type d'item
    item_type_id = db.Column(db.Integer, nullable=True, index=True)
    
    # Visuel
    icon_gfx_id = db.Column(db.Integer, nullable=True)
    
    # Données complètes
    raw_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Index composés
    __table_args__ = (
        db.Index('idx_job_level', 'job_id', 'level'),
        db.Index('idx_type_rarity', 'item_type_id', 'rarity'),
    )


class ItemCategory(db.Model, DictSerializable):
    """Catégories custom pour classification des items"""
    __tablename__ = "item_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


class Item(db.Model, DictSerializable):
    """
    Items complets depuis items.json (8,321 items)
    ENRICHI avec les nouvelles relations
    """
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Infos multilingues
    title = db.Column(db.JSON, nullable=False)  # {"fr": "...", "en": "..."}
    description = db.Column(db.JSON, nullable=True)
    
    # Infos de base
    level = db.Column(db.Integer, nullable=True, index=True)
    rarity = db.Column(db.Integer, nullable=True, index=True)
    
    # Types
    item_type_id = db.Column(db.Integer, nullable=True, index=True)
    
    equipment_type_id = db.Column(db.Integer, nullable=True)
    
    # Catégorisation custom
    category_id = db.Column(db.Integer, db.ForeignKey("item_categories.id"), nullable=True)
    category = db.relationship("ItemCategory", backref="items")
    
    # Visuel
    icon_gfx_id = db.Column(db.Integer, nullable=True)
    
    # Effets (parsés et enrichis)
    use_effects = db.Column(db.JSON, nullable=True)
    use_critical_effects = db.Column(db.JSON, nullable=True)
    equip_effects = db.Column(db.JSON, nullable=True)
    
    # Propriétés spéciales
    item_properties = db.Column(db.JSON, nullable=True)  # [1, 7, 8, ...]
    
    # Lien avec JobItem
    job_item_id = db.Column(db.Integer, nullable=True)
    
    # Données complètes
    raw_data = db.Column(db.JSON)
    needs_review = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=now_utc)
    
    # Index composés
    __table_args__ = (
        db.Index('idx_level_rarity', 'level', 'rarity'),
        db.Index('idx_item_type_level', 'item_type_id', 'level'),
    )


# ============================================================================
# SYSTÈME DE CRAFT (Recipes)
# ============================================================================

class Recipe(db.Model, DictSerializable):
    """
    Recettes depuis recipes.json (5,543 recettes)
    SIMPLIFIÉ: relations dans tables séparées
    """
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Niveau et métier
    level = db.Column(db.Integer, nullable=True, index=True)
    
    # Catégorie de recette
    recipe_category_id = db.Column(db.Integer, db.ForeignKey("recipe_categories.id"), nullable=True, index=True)
    recipe_category = db.relationship("RecipeCategory")
    
    # Données brutes
    raw_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Relations
    ingredients = db.relationship("RecipeIngredient", foreign_keys="[RecipeIngredient.recipe_wakfu_id]", primaryjoin="Recipe.wakfu_id==RecipeIngredient.recipe_wakfu_id", back_populates="recipe", cascade="all, delete-orphan")
    results = db.relationship("RecipeResult", foreign_keys="[RecipeResult.recipe_wakfu_id]", primaryjoin="Recipe.wakfu_id==RecipeResult.recipe_wakfu_id", back_populates="recipe", cascade="all, delete-orphan")


class RecipeIngredient(db.Model, DictSerializable):
    """
    Ingrédients des recettes depuis recipeIngredients.json (34,571 entrées)
    NOUVEAU: relation normalisée
    """
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True)
    
    # Recette
    recipe_id = db.Column(db.Integer, nullable=False, index=True)
    recipe_wakfu_id = db.Column(db.Integer, nullable=False, index=True)
    recipe = db.relationship("Recipe", foreign_keys="[RecipeIngredient.recipe_wakfu_id]", primaryjoin="RecipeIngredient.recipe_wakfu_id==Recipe.wakfu_id", back_populates="ingredients")
    
    # Item ingrédient
    item_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Quantité requise
    quantity = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Index composés pour craft tree
    __table_args__ = (
        db.Index('idx_recipe_item', 'recipe_wakfu_id', 'item_id'),
        db.Index('idx_item_recipes', 'item_id', 'recipe_wakfu_id'),  # Reverse lookup
    )


class RecipeResult(db.Model, DictSerializable):
    """
    Résultats des recettes depuis recipeResults.json (5,543 entrées)
    NOUVEAU: relation normalisée
    """
    __tablename__ = "recipe_results"

    id = db.Column(db.Integer, primary_key=True)
    
    # Recette
    recipe_id = db.Column(db.Integer, nullable=False, index=True)
    recipe_wakfu_id = db.Column(db.Integer, nullable=False, index=True)
    recipe = db.relationship("Recipe", foreign_keys="[RecipeResult.recipe_wakfu_id]", primaryjoin="RecipeResult.recipe_wakfu_id==Recipe.wakfu_id", back_populates="results")
    
    # Item produit
    producted_item_id = db.Column(db.Integer, nullable=False, index=True)
    
    # Quantité produite
    producted_item_quantity = db.Column(db.Integer, default=1)
    
    # Ordre de production
    product_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)
    
    # Index
    __table_args__ = (
        db.Index('idx_recipe_result', 'recipe_wakfu_id', 'producted_item_id'),
        db.Index('idx_item_produced_by', 'producted_item_id'),  # Recipes produisant cet item
    )


# ============================================================================
# ÉQUIPEMENTS (Placeholder - à enrichir plus tard)
# ============================================================================

class EquipmentItem(db.Model, DictSerializable):
    """Équipements (placeholder pour future expansion)"""
    __tablename__ = "equipment_items"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    title = db.Column(db.JSON)
    level = db.Column(db.Integer, index=True)
    rarity = db.Column(db.Integer)
    
    equipment_type_id = db.Column(db.Integer, nullable=True)
    
    raw_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), default=now_utc)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Utilities
    'now_utc',
    
    # Core Models
    'ImportBatch',
    'ItemRaw',
    'Action',
    'State',
    
    # Métiers & Catégories
    'RecipeCategory',
    'ItemType',
    'EquipmentItemType',
    'ResourceType',
    
    # Système de Récolte
    'Resource',
    'CollectibleResource',
    'HarvestLoot',
    'HarvestResource',
    
    # Items
    'JobItem',
    'ItemCategory',
    'Item',
    
    # Craft
    'Recipe',
    'RecipeIngredient',
    'RecipeResult',
    
    # Équipements
    'EquipmentItem',
]

