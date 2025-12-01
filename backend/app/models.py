from datetime import datetime, timezone
from .database import db


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class ImportBatch(db.Model):
    __tablename__ = "import_batches"

    id = db.Column(db.Integer, primary_key=True)
    started_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    ended_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    game_version = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(32), default="running")
    total_items = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)

    raw_items = db.relationship("ItemRaw", back_populates="batch")


class ItemRaw(db.Model):
    """
    JSON brut de l’API Wakfu (items.json) pour debug / reprocessing.
    """

    __tablename__ = "item_raw"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, index=True)

    raw_json = db.Column(db.JSON, nullable=False)

    import_batch_id = db.Column(
        db.Integer,
        db.ForeignKey("import_batches.id"),
        nullable=False,
    )
    batch = db.relationship("ImportBatch", back_populates="raw_items")


class Action(db.Model):
    """
    Actions Wakfu (actions.json) pour décoder les effets des items.
    """
    __tablename__ = "actions"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    effect = db.Column(db.Text)
    description = db.Column(db.JSON)  # {"fr": "...", "en": "...", ...}

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )


class State(db.Model):
    """
    États Wakfu (states.json) pour les buffs/debuffs.
    """
    __tablename__ = "states"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    title = db.Column(db.JSON)  # {"fr": "...", "en": "...", ...}
    description = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )


class Job(db.Model):
    """
    Métiers Wakfu (jobs.json).
    """
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    title = db.Column(db.JSON)  # {"fr": "...", "en": "...", ...}
    description = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )


class ItemCategory(db.Model):
    """
    Catégories d'items pour classification (équipements, ressources, consommables, etc.).
    """
    __tablename__ = "item_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    description = db.Column(db.Text)

    # Règles de classification basées sur les typeId
    type_ids = db.Column(db.JSON)  # Liste des typeId appartenant à cette catégorie


class Recipe(db.Model):
    """
    Recettes de craft Wakfu pour calculateur de ressources.
    """
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    result_item_id = db.Column(db.Integer, db.ForeignKey("items.wakfu_id"))
    job_id = db.Column(db.Integer)  # ID du métier requis

    ingredients = db.Column(db.JSON)  # [{"item_id": 123, "quantity": 5}, ...]
    craft_level = db.Column(db.Integer)  # Niveau requis du métier

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )


class Item(db.Model):
    """
    Item normalisé WakStuff, utilisé par le front.
    """

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    wakfu_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    name = db.Column(db.String(255), nullable=False)
    rarity = db.Column(db.String(64))
    level = db.Column(db.Integer)

    type = db.Column(db.String(128))
    element = db.Column(db.String(64))

    # Catégorisation
    category_id = db.Column(db.Integer, db.ForeignKey("item_categories.id"))
    category = db.relationship("ItemCategory", backref="items")

    icon_gfx_id = db.Column(db.Integer)

    stats = db.Column(db.JSON)
    description = db.Column(db.Text)

    # Effets parsés avec descriptions complètes
    parsed_effects = db.Column(db.JSON)  # Résultat du parseEffect

    needs_review = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )


class HarvestResource(db.Model):
    """
    Ressources de récolte depuis harvestLoots.json.
    Ce sont les items obtenus en récoltant (bois, minerai, plantes, etc.)
    """

    __tablename__ = "harvest_resources"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False, unique=True, index=True)
    
    # Infos du loot
    quantity_min = db.Column(db.Integer, default=1)
    quantity_max = db.Column(db.Integer, default=1)
    drop_rate = db.Column(db.Float, default=1.0)
    list_id = db.Column(db.Integer, nullable=True)
    
    # Note: Le nom et les détails de l'item ne sont pas dans harvestLoots.json
    # Ces ressources ne sont pas dans items.json, donc on stocke seulement les IDs
    
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=now_utc,
        onupdate=now_utc,
        nullable=False,
    )
