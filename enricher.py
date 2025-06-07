import os
from config import RAW_DIR, OUT_DIR
from utils import load_json, save_json, log
import time

def enrich_items():
    log("[INFO] Début enrichissement des items")
    os.makedirs(OUT_DIR, exist_ok=True)

    items = load_json(os.path.join(RAW_DIR, "items.json"))
    actions = load_json(os.path.join(RAW_DIR, "actions.json"))
    equipment = load_json(os.path.join(RAW_DIR, "equipmentItemTypes.json"))
    item_types = load_json(os.path.join(RAW_DIR, "itemTypes.json"))
    properties = load_json(os.path.join(RAW_DIR, "itemProperties.json"))
    states = load_json(os.path.join(RAW_DIR, "states.json"))

    # Dictionnaires sécurisés
    equip_map = {}
    for e in equipment:
        if isinstance(e, dict):
            id_ = e.get("id")
            name = e.get("title", {}).get("fr")
            if id_ and name:
                equip_map[id_] = name

    type_map = {}
    for t in item_types:
        if isinstance(t, dict):
            id_ = t.get("id")
            name = t.get("title", {}).get("fr")
            if id_ and name:
                type_map[id_] = name

    prop_map = {}
    for p in properties:
        if isinstance(p, dict):
            id_ = p.get("id")
            name = p.get("name", {}).get("fr") if isinstance(p.get("name"), dict) else None
            if id_ and name:
                prop_map[id_] = name

    action_map = {}
    for a in actions:
        if isinstance(a, dict):
            id_ = a.get("definition", {}).get("id")
            desc = a.get("description", {}).get("fr")
            if id_ and desc:
                action_map[id_] = desc

    state_map = {}
    for s in states:
        if isinstance(s, dict):
            id_ = s.get("id")
            name = s.get("name", {}).get("fr")
            if id_ and name:
                state_map[id_] = name

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

if __name__ == "__main__":
    log("[INFO] Lancement manuel de processor.py")
    start = time.time()

    enrich_items()

    log(f"[INFO] processor.py terminé en {time.time() - start:.2f} secondes.")
