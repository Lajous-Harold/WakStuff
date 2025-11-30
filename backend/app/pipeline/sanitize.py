from typing import Any, Dict


def _normalize_text(value: Any) -> str:
    """
    Convertit un champ texte potentiel (str, dict de langues, etc.) en string simple.
    - str -> strip()
    - dict -> essaie 'fr', puis 'en', sinon la première valeur str
    - list/tuple -> première valeur str
    - autres -> str(value)
    """
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        # ex: {"fr": "...", "en": "..."}
        for lang in ("fr", "en", "fr_FR", "en_US"):
            v = value.get(lang)
            if isinstance(v, str):
                return v.strip()
        # sinon première valeur str
        for v in value.values():
            if isinstance(v, str):
                return v.strip()
        return ""

    if isinstance(value, (list, tuple, set)):
        for v in value:
            if isinstance(v, str):
                return v.strip()
        return ""

    # fallback: on caste en string
    return str(value).strip()


def sanitize_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforme un item brut de l'API Wakfu en structure normalisée WakStuff.
    V1 : mapping simple, très tolérant. Tout ce qu'on ne comprend pas est
    mis dans `stats` ou déclenche needs_review.
    """

    # --- extraction "coeur" de l'item (id, level...) ---
    definition = raw.get("definition") or {}
    item_def = definition.get("item") or {}

    wakfu_id = (
        item_def.get("id")
        or raw.get("id")
        or raw.get("wakfuId")
        or raw.get("uid")
    )

    level = item_def.get("level") or raw.get("level")

    # Si on n'a même pas d'id, on considère que l'item est inutilisable en V1
    if wakfu_id is None:
        raise ValueError("Item sans wakfu_id exploitable")

    # --- name / description ---
    name = _normalize_text(
        raw.get("name")
        or raw.get("title")
        or definition.get("title")
        or item_def.get("title")
    )

    description = _normalize_text(
        raw.get("description")
        or definition.get("description")
        or item_def.get("description")
    )

    # --- champs simples : rarity / type / element ---
    rarity = raw.get("rarity") or item_def.get("rarity")
    item_type = raw.get("type") or item_def.get("type")
    element = raw.get("element") or item_def.get("element")

    # --- stats : on met ce qu'on trouve, mais on force un dict ---
    stats = raw.get("stats") or definition.get("stats") or {}
    if not isinstance(stats, dict):
        stats = {"raw": stats}

    # --- flag review ---
    needs_review = not (wakfu_id and name)

    return {
        "wakfu_id": wakfu_id,
        "name": name or f"Item #{wakfu_id}",
        "rarity": rarity,
        "level": level,
        "type": item_type,
        "element": element,
        "stats": stats,
        "description": description,
        "needs_review": needs_review,
    }
