import os
from config import RAW_DIR, OUT_DIR
from utils import load_json, save_json, log

def enrich_items():
    log("[INFO] Début enrichissement des items")
    os.makedirs(OUT_DIR, exist_ok=True)

    items = load_json(os.path.join(RAW_DIR, "items.json"))
    actions = load_json(os.path.join(RAW_DIR, "actions.json"))
    equipment = load_json(os.path.join(RAW_DIR, "equipmentItemTypes.json"))
    item_types = load_json(os.path.join(RAW_DIR, "itemTypes.json"))
    properties = load_json(os.path.join(RAW_DIR, "itemProperties.json"))
    states = load_json(os.path.join(RAW_DIR, "states.json"))

    # Mapping sécurisé
    equip_map = {e.get("id"): e.get("title", {}).get("fr") for e in equipment if isinstance(e, dict)}
    type_map = {t.get("id"): t.get("title", {}).get("fr") for t in item_types if isinstance(t, dict)}
    prop_map = {p.get("id"): p.get("name", {}).get("fr") for p in properties if isinstance(p, dict)}
    action_map = {
        a.get("definition", {}).get("id"): a.get("description", {}).get("fr")
        for a in actions if isinstance(a, dict) and "definition" in a and "description" in a
    }
    state_map = {s.get("id"): s.get("name", {}).get("fr") for s in states if isinstance(s, dict)}

    enriched = []

    for item in items:
        d = item.get("definition", {}).get("item", {})
        enriched.append({
            "id": item.get("id"),
            "name": item.get("title", {}).get("fr", ""),
            "level": d.get("level"),
            "type": equip_map.get(d.get("equipmentTypeId")),
            "category": type_map.get(d.get("baseParameters", {}).get("itemTypeId")),
            "properties": [prop_map.get(p) for p in d.get("properties", []) if p in prop_map],
            "effects": [
                action_map.get(e.get("definition", {}).get("actionId"))
                for e in item.get("equipEffects", []) if isinstance(e, dict)
            ],
            "states": [
                state_map.get(s.get("stateId"))
                for s in d.get("states", []) if isinstance(s, dict)
            ],
        })

    output_path = os.path.join(OUT_DIR, "items_enriched.json")
    save_json(enriched, output_path)
    log(f"[OK] Données enrichies sauvegardées : {output_path}")
