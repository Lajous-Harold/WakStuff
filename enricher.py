import os
import json
import argparse
from datetime import datetime

DATA_DIR = "data"
OUTPUT_DIR = "output"
OUTPUT_FILE = "items_enriched.json"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def load_json(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def detect_rarity(props):
    rarities = ["Relique", "Épique", "Légendaire", "Mythique", "Rare", "Commun"]
    for r in rarities:
        if any(r in p for p in (props or [])):
            return r
    return "Commun"

def enrich_items(limit=None):
    log("[INFO] Chargement des données sources...")
    items = load_json("items")
    if limit:
        items = items[:limit]

    actions = load_json("actions")
    equipment_types = load_json("equipmentItemTypes")
    item_types = load_json("itemTypes")
    properties = load_json("itemProperties")
    states = load_json("states")

    equipment_map = {e.get("id"): e.get("name", {}).get("fr", "") for e in equipment_types if isinstance(e, dict)}
    item_type_map = {t.get("id"): t.get("title", {}).get("fr", "") for t in item_types if isinstance(t, dict)}
    property_map = {p.get("id"): p.get("name", {}).get("fr", "") for p in properties if isinstance(p, dict)}
    action_map = {a.get("id"): a.get("description", {}).get("fr", "") for a in actions if isinstance(a, dict) and "description" in a}
    state_map = {s.get("id"): s.get("name", {}).get("fr", "") for s in states if isinstance(s, dict)}

    enriched = []
    for item in items:
        definition = item.get("definition", {})
        base = definition.get("item", {})

        obj = {
            "id": base.get("id"),
            "name": item.get("title", {}).get("fr", ""),
            "level": base.get("level", 0),
            "type": equipment_map.get(base.get("itemTypeId"), "Inconnu"),
            "category": item_type_map.get(base.get("itemTypeId"), "Inconnu"),
            "rarity": base.get("rarity"),
            "properties": [property_map.get(p) for p in base.get("properties", []) if p in property_map],
            "effects": [],
            "states": [],
            "gfxId": base.get("graphicParameters", {}).get("gfxId", None),
        }

        for effect in definition.get("equipEffects", []):
            effect_def = effect.get("effect", {}).get("definition", {})
            action_id = effect_def.get("actionId")
            if action_id in action_map:
                obj["effects"].append(action_map[action_id])

        if base.get("states"):
            obj["states"] = [state_map.get(s.get("stateId"), "") for s in base["states"]]

        obj["rarete"] = detect_rarity(obj["properties"])
        enriched.append(obj)

    return enriched

def save(items):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4, ensure_ascii=False)

    log(f"[OK] Fichier enrichi enregistré : {path}")

def main():
    parser = argparse.ArgumentParser(description="Traitement des objets Wakfu enrichis.")
    parser.add_argument("--limit", type=int, help="Nombre maximal d'objets à traiter (défaut : tous)", default=None)
    args = parser.parse_args()

    log("[INFO] Démarrage de l'enrichissement des items...")
    items = enrich_items(limit=args.limit)

    # Tri final
    rarity_order = ["Commun", "Rare", "Mythique", "Légendaire", "Épique", "Relique"]
    items.sort(key=lambda x: (
        x.get("category", "Inconnu"),
        x.get("type", "Inconnu"),
        rarity_order.index(x.get("rarete", "Commun")) if x.get("rarete") in rarity_order else 0,
        x.get("level", 0)
    ))

    save(items)
    log(f"[INFO] Traitement terminé. {len(items)} objets enrichis.")

if __name__ == "__main__":
    main()
