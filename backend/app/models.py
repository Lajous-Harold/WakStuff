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

    icon_gfx_id = db.Column(db.Integer)

    stats = db.Column(db.JSON)
    description = db.Column(db.Text)

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
