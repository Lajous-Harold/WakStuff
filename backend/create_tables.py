"""
Script d'initialisation de la base de données WakStuff
Crée toutes les tables nécessaires selon le plan de refonte

Usage:
    python create_tables.py
    
Options:
    --drop : Supprime les tables existantes avant de les recréer (ATTENTION!)
"""

import sys
from pathlib import Path

# Ajouter le répertoire backend au path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from app.database import db
from app.models import (
    ImportBatch, ItemRaw, Action, State,
    RecipeCategory, ItemType, EquipmentItemType, ResourceType,
    Resource, CollectibleResource, HarvestLoot, HarvestResource,
    JobItem, Item, ItemCategory,
    Recipe, RecipeIngredient, RecipeResult,
    EquipmentItem
)


def init_database(drop_existing=False):
    """
    Initialise la base de données WakStuff
    
    Args:
        drop_existing: Si True, supprime les tables existantes
    """
    print("\n" + "="*80)
    print("🗄️  WakStuff Database Initialization - V2 (Refonte Complète)")
    print("="*80)

    app = create_app()

    with app.app_context():
        if drop_existing:
            print("\n⚠️  WARNING: Dropping all existing tables!")
            response = input("Continue? (yes/no): ")

            if response.lower() != 'yes':
                print("❌ Aborted by user")
                return

            print("\n🗑️  Dropping existing tables...")
            db.drop_all()
            print("   ✅ Tables dropped")

        print("\n🏗️  Creating tables...")
        db.create_all()
        print("   ✅ Tables created")

        # Liste des tables créées (conforme au plan de refonte)
        print("\n📋 Database tables:")
        print("-" * 80)

        # Tables de base
        print("\n📦 Base Tables:")
        print("   ✓ import_batches     - Historique des imports")
        print("   ✓ item_raw           - JSON brut pour debug")
        print("   ✓ actions            - Actions Wakfu")
        print("   ✓ states             - États/buffs")

        # Tables métiers & catégories
        print("\n🏷️  Métiers & Catégories:")
        print("   ✓ recipe_categories  - 14 métiers officiels (dont 5 récolte)")
        print("   ✓ item_types         - 96 types d'items")
        print("   ✓ equipment_item_types - 31 types d'équipements")
        print("   ✓ resource_types     - 6 types de ressources")

        # Tables récolte
        print("\n🌾 Système de Récolte:")
        print("   ✓ resources          - 170 ressources récoltables")
        print("   ✓ collectable_resources - 666 actions de collecte")
        print("   ✓ harvest_loots      - 1,221 items droppés")
        print("   ✓ harvest_resources  - 452 items de récolte (enrichi)")

        # Tables items
        print("\n📦 Items:")
        print("   ✓ items              - Items normalisés (enrichi)")
        print("   ✓ job_items          - 8,576 items de métiers")
        print("   ✓ item_categories    - Catégories custom")
        print("   ✓ equipment_items    - Équipements")

        # Tables craft
        print("\n🔨 Craft:")
        print("   ✓ recipes            - Recettes (simplifié)")
        print("   ✓ recipe_ingredients - 34,571 ingrédients")
        print("   ✓ recipe_results     - 5,543 résultats")

        print("-" * 80)
        print("\n✅ Database initialized successfully!")
        
        # Vérifier les tables créées
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Total tables created: {len(tables)} (Expected: 19)")

        print("\n📚 Next steps:")
        print("   1. Run data import: python -m app.pipeline.full_import")
        print("   2. Verify data: flask shell")
        print("   3. Start API server: flask run")
        print("="*80 + "\n")


def main():
    """Point d'entrée du script."""
    drop = '--drop' in sys.argv
    
    if drop:
        print("\n⚠️  Drop mode enabled - existing tables will be deleted!")
    
    init_database(drop_existing=drop)


if __name__ == '__main__':
    main()
