"""
Script de test pour vérifier le système d'import complet Wakfu.

Ce script:
1. Teste la connexion à l'API Wakfu
2. Vérifie que toutes les ressources sont accessibles
3. Teste le parser d'effets
4. Affiche quelques statistiques

Usage:
    python test_wakfu_import.py
"""

import sys
from pathlib import Path

# Ajouter le backend au path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app.wakfu_client import WakfuClient
from app.pipeline.effect_parser import parse_effect
from app.pipeline.classifier import classify_item, get_item_rarity_label

print("=" * 60)
print("Test du Système d'Import Wakfu")
print("=" * 60)

print("\n1. Test de connexion à l'API Wakfu...")
try:
    client = WakfuClient()
    version = client.get_current_version()
    print(f"   Version détectée: {version}")
except Exception as e:
    print(f"   Erreur: {e}")
    sys.exit(1)

print("\n2. Test de téléchargement des ressources...")

resources_to_test = [
    ("actions.json", "fetch_all_actions"),
    ("states.json", "fetch_all_states"),
    ("jobs.json", "fetch_all_jobs"),
    ("itemTypes.json", "fetch_all_item_types"),
    ("items.json", "fetch_all_items"),
]

resource_data = {}

for resource_name, method_name in resources_to_test:
    try:
        method = getattr(client, method_name)
        data = method(version)
        count = len(data) if isinstance(data, list) else "N/A"
        resource_data[resource_name] = data
        print(f"   {resource_name}: {count} entrées")
    except Exception as e:
        print(f"   {resource_name}: Non disponible ({e})")
        resource_data[resource_name] = []

print("\n3. Test du parser d'effets...")

if resource_data.get("actions.json") and resource_data.get("items.json"):
    try:
        # Prendre le premier item avec des effets
        actions_data = resource_data["actions.json"]
        items_data = resource_data["items.json"]
        
        item_with_effects = None
        for item in items_data[:100]:  # Tester les 100 premiers
            definition = item.get("definition", {})
            if definition.get("equipEffects") or definition.get("useEffects"):
                item_with_effects = item
                break
        
        if item_with_effects:
            definition = item_with_effects.get("definition", {})
            item_def = definition.get("item", {})
            level = item_def.get("level", 1)
            
            effects = definition.get("equipEffects", [])
            if effects:
                effect = effects[0].get("effect", {})
                parsed = parse_effect(effect, level, actions_data)
                
                if parsed.get("description"):
                    print(f"   Parsing réussi!")
                    print(f"      Item niveau {level}")
                    desc = parsed["description"]
                    if isinstance(desc, dict) and "en" in desc:
                        print(f"      Effect (EN): {desc['en'][:60]}...")
                else:
                    print(f"   Parsing sans résultat")
        else:
            print(f"   Aucun item avec effets trouvé dans les 100 premiers")
            
    except Exception as e:
        print(f"   Erreur parsing: {e}")
else:
    print(f"   Données insuffisantes pour tester le parser")

print("\n4. Test du classificateur d'items...")

if resource_data.get("items.json"):
    try:
        items_data = resource_data["items.json"]
        
        # Classifier quelques items
        categories_found = {}
        
        for item in items_data[:200]:  # Classifier les 200 premiers
            classification = classify_item(item)
            category = classification["category"]
            categories_found[category] = categories_found.get(category, 0) + 1
        
        print(f"   Classification réussie!")
        print(f"      Catégories trouvées (sur 200 items):")
        for cat, count in sorted(categories_found.items(), key=lambda x: -x[1])[:5]:
            print(f"      - {cat}: {count} items")
            
    except Exception as e:
        print(f"   Erreur classification: {e}")
else:
    print(f"   Données insuffisantes pour tester le classificateur")

print("\n5. Test du mapping de raretés...")
try:
    rarities = [0, 1, 2, 3, 4, 5, 6, 7]
    print(f"   Raretés disponibles:")
    for rarity_id in rarities:
        label = get_item_rarity_label(rarity_id)
        print(f"      - {rarity_id} → {label}")
except Exception as e:
    print(f"   Erreur raretés: {e}")

print("\n" + "=" * 60)
print("Statistiques")
print("=" * 60)

total_items = len(resource_data.get("items.json", []))
total_actions = len(resource_data.get("actions.json", []))
total_states = len(resource_data.get("states.json", []))
total_jobs = len(resource_data.get("jobs.json", []))
total_types = len(resource_data.get("itemTypes.json", []))

print(f"Items disponibles:       {total_items:,}")
print(f"Actions disponibles:     {total_actions:,}")
print(f"États disponibles:       {total_states:,}")
print(f"Jobs disponibles:        {total_jobs:,}")
print(f"Types d'items:           {total_types:,}")

print("\n" + "=" * 60)
print("Tests terminés!")
print("=" * 60)
print("\nPour lancer l'import complet:")
print("  1. Assurez-vous que la base de données est configurée")
print("  2. Exécutez: python migrate_db.py")
print("  3. Lancez le serveur: python wsgi.py")
print("  4. Appelez: POST http://localhost:5000/api/wakfu/import/full")
print("\nOu utilisez directement le module Python:")
print("  from app.pipeline.full_import import run_full_wakfu_import")
print("  batch = run_full_wakfu_import()")
