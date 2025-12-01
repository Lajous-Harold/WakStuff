"""
Script de migration pour créer/mettre à jour les nouvelles tables.

Usage:
    python migrate_db.py
"""

import sys
from pathlib import Path

# Ajouter le backend au path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from app import create_app
from app.database import db
from app.models import Action, State, Job, ItemCategory, Recipe, HarvestResource

print("Création de l'application Flask...")
app = create_app()

with app.app_context():
    print("Création des nouvelles tables...")
    
    # Créer toutes les tables
    db.create_all()
    
    print("✓ Tables créées avec succès!")
    
    # Afficher les tables existantes
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f"\nTables dans la base de données ({len(tables)}):")
    for table in sorted(tables):
        print(f"  - {table}")
    
    print("\n✓ Migration terminée!")
