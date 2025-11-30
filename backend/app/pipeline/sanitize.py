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
        for lang in ("fr", "en", "fr_FR", "en_US"):
            v = value.get(lang)
            if isinstance(v, str):
                return v.strip()
        for v in value.values():
            if isinstance(v, str):
                return v.strip()
        return ""

    if isinstance(value, (list, tuple, set)):
        for v in value:
            if isinstance(v, str):
                return v.strip()
        return ""

    return str(value).strip()


def _normalize_rarity(raw_rarity: Any) -> str | None:
    """
    Transforme la rareté brute (souvent un entier) en string exploitable.
    V1 : on ne connaît pas encore le mapping officiel, donc on génère
    des labels du style 'rarity_1', 'rarity_2', etc.
    """
    if raw_rarity is None:
        return None

    try:
        r_int = int(raw_rarity)
        return f"rarity_{r_int}"
    except (TypeError, ValueError):
        if isinstance(raw_rarity, str):
            return raw_rarity.strip() or None
        return str(raw_rarity)


def _normalize_type(raw_type: Any, raw_type_id: Any) -> str | None:
    """
    Transforme type / typeId en string exploitable.
    Si le type texte existe déjà dans l'item, on le garde.
    Sinon on génère un label du style 'type_120'.
    """
    if isinstance(raw_type, str) and raw_type.strip():
        return raw_type.strip()

    if raw_type_id is None:
        return None

    try:
        t_int = int(raw_type_id)
        return f"type_{t_int}"
    except (TypeError, ValueError):
        if isinstance(raw_type_id, str):
            return raw_type_id.strip() or None
        return str(raw_type_id)


def sanitize_item(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforme un item brut de l'API Wakfu en structure normalisée WakStuff.
    V1.5 : on va chercher les infos dans definition.item.baseParameters
    et on stocke aussi les blocs utiles dans `stats`.
    """
    definition = raw.get("definition") or {}
    item_def = definition.get("item") or {}
    base_params = item_def.get("baseParameters") or {}
    graphic_params = item_def.get("graphicParameters") or {}

    wakfu_id = (
        item_def.get("id") or raw.get("id") or raw.get("wakfuId") or raw.get("uid")
    )

    level = item_def.get("level") or raw.get("level")

    gfx_id = graphic_params.get("gfxId") or graphic_params.get("femaleGfxId")

    if wakfu_id is None:
        raise ValueError("Item sans wakfu_id exploitable")

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

    raw_rarity = (
        raw.get("rarity") or item_def.get("rarity") or base_params.get("rarity")
    )
    rarity = _normalize_rarity(raw_rarity)

    raw_type = raw.get("type") or item_def.get("type")
    raw_type_id = (
        base_params.get("itemTypeId")
        or raw.get("itemTypeId")
        or item_def.get("itemTypeId")
        or item_def.get("typeId")
    )
    item_type = _normalize_type(raw_type, raw_type_id)

    element = raw.get("element") or item_def.get("element")

    stats: Dict[str, Any] = {}

    stats["baseParameters"] = base_params
    stats["useParameters"] = item_def.get("useParameters") or {}
    stats["graphicParameters"] = graphic_params

    if gfx_id is not None:
        stats["icon_gfx_id"] = gfx_id

    stats["equipEffects"] = (
        definition.get("equipEffects") or raw.get("equipEffects") or []
    )
    stats["useEffects"] = definition.get("useEffects") or raw.get("useEffects") or []

    needs_review = not (wakfu_id and name and item_type)

    return {
        "wakfu_id": wakfu_id,
        "name": name or f"Item #{wakfu_id}",
        "rarity": rarity,
        "level": level,
        "type": item_type,
        "element": element,
        "stats": stats,
        "icon_gfx_id": gfx_id,
        "description": description,
        "needs_review": needs_review,
    }
