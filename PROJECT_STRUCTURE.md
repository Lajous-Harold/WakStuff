# Structure du Projet WakStuff

## Vue d'ensemble

```plaintext
WakStuff/
│
├── README.md                          # Documentation principale complète
├── TODO.md                            # Roadmap et tâches
├── PROJECT_STRUCTURE.md               # Ce fichier
├── VISUAL_SUMMARY.md                  # Diagramme ASCII de l'architecture
│
├── backend/
│   ├── wsgi.py                       # Point d'entrée Flask
│   ├── requirements.txt              # Dépendances Python
│   ├── migrate_db.py                 # Migration base de données
│   ├── test_wakfu_import.py         # Tests de connexion et parsing
│   │
│   ├── examples/
│   │   └── craft_calculator_example.py
│   │
│   └── app/
│       ├── __init__.py               # Initialisation Flask + blueprints
│       ├── config.py                 # Configuration
│       ├── database.py               # Setup SQLAlchemy
│       ├── models.py                 # Modèles BDD (7 tables)
│       │
│       ├── items/routes.py           # API items (avec filtres)
│       ├── imports/routes.py         # API imports
│       ├── proxy/routes.py           # Proxy icônes
│       │
│       ├── wakfu_data/               # API données Wakfu complètes
│       │   └── routes.py             # Import, stats, catégories, craft
│       │
│       ├── test_views/               # Interface de test HTML
│       │   └── routes.py
│       │
│       ├── wakfu_client/             # Client API Wakfu
│       │   └── client.py             # Fetch config, items, actions, etc.
│       │
│       └── pipeline/                 # Pipeline d'import
│           ├── full_import.py        # Orchestration import complet
│           ├── effect_parser.py      # Parse templates d'effets
│           ├── classifier.py         # Classification par typeId
│           ├── wakfu_config.py       # Catégories, raretés, éléments
│           ├── import_items.py       # Import simple (legacy)
│           └── sanitize.py           # Sanitization
│
├── frontend/wakstuff-frontend/
│   └── src/app/
│       ├── core/
│       │   ├── services/
│       │   │   ├── imports.service.ts
│       │   │   └── items.service.ts
│       │   └── resolvers/
│       │       ├── imports.resolver.ts
│       │       └── items.resolver.ts
│       │
│       └── features/
│           ├── imports/imports-dashboard/
│           └── items/items-list/
│
└── infra/
    ├── docker-compose.yml
    ├── backend.Dockerfile
    ├── frontend.Dockerfile
    ├── servers.json              # Config pgAdmin
    └── env/                      # Variables d'environnement
```

---

## Modèles de Base de Données

### Relations

┌─────────────────┐
│ ImportBatch │
├─────────────────┤
│ id │
│ game_version │◄─── Version Wakfu (ex: 1.82.1.28)
│ status │
│ total_items │
│ error_count │
└─────────────────┘

┌─────────────────┐
│ Action │
├─────────────────┤
│ id │
│ wakfu_id │◄─── ID unique Wakfu
│ effect │
│ description │◄─── JSON multilingue
└─────────────────┘

┌─────────────────┐
│ State │
├─────────────────┤
│ id │
│ wakfu_id │
│ title │◄─── JSON multilingue
│ description │
└─────────────────┘

┌─────────────────┐
│ Job │
├─────────────────┤
│ id │
│ wakfu_id │
│ title │◄─── JSON multilingue
│ description │
└─────────────────┘

┌─────────────────────┐
│ ItemCategory │
├─────────────────────┤
│ id │
│ name │◄─── "equipments.weapons"
│ description │
│ type_ids │◄─── JSON [108, 110, ...]
└─────────────────────┘
▲
│
│ category_id
│
┌─────────────────────┐
│ Item │
├─────────────────────┤
│ id │
│ wakfu_id │
│ name │
│ rarity │
│ level │
│ type │
│ category_id │◄─── ✨ NOUVEAU
│ parsed_effects │◄─── ✨ NOUVEAU (JSON)
│ stats │
│ description │
└─────────────────────┘
▲
│ result_item_id
│
┌─────────────────────┐
│ Recipe │
├─────────────────────┤
│ id │
│ wakfu_id │
│ result_item_id │◄─── Produit cet item
│ job_id │◄─── Métier requis
│ ingredients │◄─── JSON [{item_id, qty}, ...]
│ craft_level │
└─────────────────────┘

```

## 🔄 Flux d'Import Complet

```

┌────────────────────────────────────────────────────────┐
│ │
│ POST /api/wakfu/import/full │
│ │
└────────────────┬───────────────────────────────────────┘
│
▼
┌────────────────────────────────────────────────────────┐
│ run_full_wakfu_import() │
└────────────────┬───────────────────────────────────────┘
│
┌──────────┴──────────┐
│ │
▼ ▼
┌──────────┐ ┌──────────┐
│ config. │ │ Créer │
│ json │────────>│ Batch │
└──────────┘ └──────────┘
│
┌────────────────────┼────────────────────┐
│ │ │
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ actions. │ │ states. │ │ jobs. │
│ json │ │ json │ │ json │
└────┬─────┘ └────┬─────┘ └────┬─────┘
│ │ │
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Table │ │ Table │ │ Table │
│ actions │ │ states │ │ jobs │
└──────────┘ └──────────┘ └──────────┘
│
▼
┌──────────┐
│itemTypes.│
│ json │
└────┬─────┘
│
▼
┌──────────┐
│ Table │
│categories│
└──────────┘
│
┌───────────────────┼───────────────────┐
│ │ │
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ items. │ │sanitize │ │classify │
│ json │──────>│_item() │──────>│_item() │
└──────────┘ └──────────┘ └──────────┘
│
▼
┌──────────┐
│parse_all │
│_effects()│
└────┬─────┘
│
▼
┌──────────┐
│ Table │
│ items │
└──────────┘
│
▼
┌──────────┐
│ recipes. │
│ json │
└────┬─────┘
│
▼
┌──────────┐
│ Table │
│ recipes │
└──────────┘

```

---

## Endpoints API

**Routes principales**:
Backend API
│
├── /api/items
│   ├── GET  /                    # Liste items (filtres existants)
│   ├── GET  /:id                 # Détails item
│   └── ...
│
├── /api/imports
│   ├── POST /                    # Import items (ancien)
│   └── ...
│
└── /api/wakfu                    # ✨ NOUVEAU
    ├── POST   /import/full       # Lance import complet
    ├── GET    /stats             # Statistiques complètes
    ├── GET    /categories        # Liste catégories
    ├── GET    /recipes/:id       # Recettes pour item
    └── GET    /craft-calculator/:id  # Calcul ressources
```

---

## Catégories d'Items (35+)

**Structure hiérarchique**:
equipments/
├── helmets/ # Casques (typeId: 119)
├── chest/ # Plastrons (136)
├── shoulders/ # Épaulettes (133)
├── legs/ # Pantalons (138)
├── boots/ # Bottes (139)
├── belt/ # Ceintures (134)
├── back/ # Capes (132)
├── amulet/ # Amulettes (120)
├── ring/ # Anneaux (103)
├── shield/ # Boucliers (189)
├── weapons/
│ ├── one_handed/ # Armes 1 main (108-117)
│ └── two_handed/ # Armes 2 mains (223+)
├── pet/ # Familiers (582)
├── mount/ # Montures (611)
├── costume/ # Costumes (647)
└── emblem/ # Emblèmes (646)

resources/
├── ore/ # Minerais (475)
├── plants/ # Plantes (476)
├── wood/ # Bois (477)
├── fish/ # Poissons (478)
├── meat/ # Viandes (479)
├── cereals/ # Céréales (480)
├── vegetables/ # Légumes (481)
├── leather/ # Cuirs (515)
├── gems/ # Gemmes (516)
├── cloth/ # Tissus (517)
└── crafting_materials/ # Matériaux craft (482+)

consumables/
├── food/ # Nourriture (520-523)
├── potions/ # Potions (100)
└── buffs/ # Buffs (528-529)

others/
├── quest_items/ # Quête (518-519)
├── bags/ # Sacs (519)
├── keys/ # Clés (530)
├── runes/ # Runes (812)
├── sublimations/ # Sublimations (808)
└── tokens/ # Jetons (650)

````

---

## Configuration (wakfu_config.py)

**Exemples**:
```python
WAKFU_ITEM_CATEGORIES = {
    "equipments.helmets": {
        "type_ids": [119],
        "description": "Casques et coiffes"
    },
    # ... 35+ catégories
}

WAKFU_RARITIES = {
    0: {"name": "common", "color": "#FFFFFF"},
    # ... 8 raretés
}

WAKFU_ELEMENTS = {
    1: {"name": "fire", "label_fr": "Feu"},
    # ... 6 éléments
}
````

---

## Fichiers Principaux

### Backend

**full_import.py**

- Import orchestration complète
- Gestion des versions
- Tracking des erreurs
- Batch processing

### `effect_parser.py`

- Parsing des templates d'actions
- Évaluation des conditions
- Support multilingue
- Gestion des cas spéciaux

### `classifier.py`

- Classification par typeId
- Heuristiques intelligentes
- Enrichissement depuis API
- Support catégories custom

### `wakfu_data/routes.py`

- Endpoint import
- Endpoint statistiques
- Endpoint catégories
- Calculateur de craft

---

## Commandes Utiles

```bash
# Setup
cd backend
pip install -r requirements.txt
python migrate_db.py

# Tests
python test_wakfu_import.py

# Import
python wsgi.py
curl -X POST http://localhost:5000/api/wakfu/import/full

# Stats
curl http://localhost:5000/api/wakfu/stats

# Craft Calculator
python examples/craft_calculator_example.py 2021
```

---

**Documentation complète**: Voir `README.md` pour tous les détails.
