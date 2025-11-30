from datetime import datetime, timezone
from typing import Optional, Any, Dict

from ..database import db
from ..models import ImportBatch, Item, ItemRaw
from ..wakfu_client import WakfuClient
from .sanitize import sanitize_item


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _extract_wakfu_id(raw: Dict[str, Any]) -> Optional[int]:
    """
    Détecte l'ID wakfu d'un item brut.
    Format observé dans le JSON Wakfu :
      {"definition": {"item": {"id": 2021, "level": ...}}}
    On garde aussi quelques fallbacks au cas où.
    """
    definition = raw.get("definition") or {}
    item_def = definition.get("item") or {}

    wakfu_id = (
        item_def.get("id")
        or raw.get("id")
        or raw.get("wakfuId")
        or raw.get("uid")
    )

    return wakfu_id


def run_full_import(batch: Optional[ImportBatch] = None) -> ImportBatch:
    """
    Import complet :
    - lit la version courante via config.json
    - importe items.json pour cette version
    - stocke la version dans ImportBatch.game_version
    """
    client = WakfuClient()
    current_version = client.get_current_version()

    if batch is None:
        batch = ImportBatch(status="running", game_version=current_version)
        db.session.add(batch)
        db.session.flush()
    else:
        batch.game_version = current_version

    total_items = 0
    error_count = 0

    last_batch = (
        ImportBatch.query.order_by(ImportBatch.started_at.desc())
        .filter(ImportBatch.id != batch.id)
        .first()
    )
    if last_batch and last_batch.game_version != current_version:
        print(
            f"[INFO] Changement de version détecté : "
            f"{last_batch.game_version} -> {current_version}"
        )

    for raw in client.iter_all_items(version=current_version):
        total_items += 1

        wakfu_id = _extract_wakfu_id(raw)
        if wakfu_id is None:
            # On ne tente même pas l'insert si on n'a pas d'ID exploitable
            error_count += 1
            print("[WARN] Item sans wakfu_id, ignoré")
            continue

        try:
            # 1) stock brut
            raw_entry = ItemRaw(
                wakfu_id=wakfu_id,
                raw_json=raw,
                batch=batch,
            )
            db.session.add(raw_entry)

            # 2) normalisation
            clean = sanitize_item(raw)

            item = Item.query.filter_by(wakfu_id=clean["wakfu_id"]).first()
            if item is None:
                item = Item(wakfu_id=clean["wakfu_id"])
                db.session.add(item)

            item.name = clean["name"]
            item.rarity = clean["rarity"]
            item.level = clean["level"]
            item.type = clean["type"]
            item.element = clean["element"]
            item.stats = clean["stats"]
            item.description = clean["description"]
            item.needs_review = clean["needs_review"]

        except Exception as exc:
            error_count += 1
            print(f"[WARN] Erreur traitement item {wakfu_id}: {exc!r}")
            # IMPORTANT : on ne commit pas ici, on laisse passer au suivant
            # et on ne fait pas rollback() dans la boucle, pour ne pas tout perdre.

    batch.total_items = total_items
    batch.error_count = error_count
    batch.status = "success"
    batch.ended_at = now_utc()

    db.session.commit()
    return batch
