# WakStuff

Plateforme complète d'analyse et de gestion des données du jeu **Wakfu** (Ankama).

## Vue d'ensemble

WakStuff est un système d'import, classification et analyse des données du MMORPG Wakfu. Il récupère automatiquement toutes les données depuis l'API officielle, parse les effets d'items, classifie les objets par catégorie, et fournit des outils avancés comme un calculateur de craft récursif.

## Fonctionnalités principales

### Backend

- **Import complet automatisé** : Actions, States, Jobs, ItemTypes, Items, Recipes
- **Parser d'effets intelligent** : Décodage des templates Wakfu (ex: `{[>2]?s:}`, `[#1]`, `[~3]`)
- **Classification automatique** : 45 catégories basées sur les typeIds réels de l'API Wakfu
  - 16 catégories d'équipements (armes 1H/2H, armures, accessoires, pets, montures...)
  - 11 catégories de ressources (minerais, plantes, bois, poissons, crafting...)
  - 3 catégories de consommables (nourriture, potions, buffs)
  - 15 catégories diverses (quêtes, sacs, sublimations, recettes, reliques...)
- **Calculateur de craft récursif** : Calcule toutes les ressources nécessaires à la fabrication
- **API REST complète** : Statistiques, recherche, filtrage par catégorie
- **Support multilingue** : FR/EN/ES/PT pour les descriptions d'effets

### Frontend

- Interface Angular 21 moderne avec composants standalone
- Dashboard des imports avec historique et statistiques
- Liste des items avec filtres avancés (catégorie, rareté, niveau, recherche)
- Calculateur de craft avec arbre visuel et calcul des ressources
- Vue des catégories organisées par groupes
- Dashboard de statistiques avec graphiques
- Page détails item avec recettes et effets parsés
- Affichage des icônes via proxy (contournement CORS)

### Infrastructure

- Docker Compose pour dev et prod
- PostgreSQL 16 avec migrations automatiques
- pgAdmin 4 pré-configuré
- Proxy d'images pour CDN Ankama

> ⚠️ Usage personnel / non commercial uniquement. Données Wakfu © Ankama.

---

## Stack technique

**Backend**

- Python 3.13 + Flask + SQLAlchemy
- PostgreSQL 16
- Parser d'effets (regex-based, multilingue)
- Classificateur intelligent (45 catégories basées sur l'API Wakfu v1.90.1.47)
- Calculateur de craft récursif
- Proxy d'images pour CDN Ankama

**Frontend**

- Angular 21 (standalone components)
- TypeScript + SCSS
- RxJS pour la gestion des états
- Services: ItemsService, WakfuDataService, ImportsService
- Composants: items-list, item-details, craft-calculator, categories-view, stats-dashboard, imports-dashboard
- Pipes personnalisés: rarity-color, category-badge, level-display
- Utilities: formatNumber, calculatePercentage, formatDate
- Pagination serveur-side + filtres avancés + recherche temps réel

**Infrastructure**

- Docker Compose
- pgAdmin 4 auto-configuré
- Nginx (production)

---

## Architecture du système

### Pipeline d'import

```
API Wakfu → WakfuClient → Import Pipeline → Database
              ↓              ↓         ↓
         Version    →   Classifier  Parser
         Detection      (35+ cats)  (Effects)
```

**Étapes:**

1. Détection de la version Wakfu via `config.json`
2. Téléchargement des ressources (actions, states, jobs, itemTypes, items, recipes)
3. Classification des items par `typeId` et heuristiques
4. Parsing des effets avec templates (ex: `{[>2]?s:}` → "s" si valeur > 2)
5. Stockage en base avec relations
6. Calcul des dépendances de craft

### Modèle de données

```
ImportBatch (historique)
    ↓
Actions, States, Jobs (référentiels)
    ↓
ItemCategory (35+ catégories)
    ↓
Item (wakfu_id, name, level, rarity, category, parsed_effects)
    ↓
Recipe (ingredients, craft_level, job_id)
```

---

## Structure du projet

```
WakStuff/
├─ backend/
│  ├─ app/
│  │  ├─ models.py              # Models: Action, State, Job, ItemCategory, Item, Recipe
│  │  ├─ wakfu_client/          # Client API Wakfu (version detection, downloads)
│  │  ├─ pipeline/
│  │  │  ├─ full_import.py      # Orchestration import complet
│  │  │  ├─ effect_parser.py    # Parsing templates d'effets
│  │  │  ├─ classifier.py       # Classification par typeId
│  │  │  ├─ wakfu_config.py     # Catégories, raretés, éléments
│  │  │  ├─ import_items.py     # Import simple (legacy)
│  │  │  └─ sanitize.py         # Normalisation
│  │  ├─ items/routes.py        # GET /api/items (avec filtres catégorie)
│  │  ├─ imports/routes.py      # POST /api/imports/run
│  │  ├─ proxy/routes.py        # GET /api/proxy/icon/<id>
│  │  ├─ wakfu_data/routes.py   # API Wakfu complète (import, stats, craft)
│  │  └─ test_views/routes.py   # Interface de test visuelle
│  ├─ migrate_db.py             # Migration base de données
│  ├─ test_wakfu_import.py      # Tests de connexion et parsing
│  ├─ examples/
│  │  └─ craft_calculator_example.py
│  └─ wsgi.py
│
├─ frontend/wakstuff-frontend/
│  └─ src/app/
│     ├─ core/
│     │  ├─ services/
│     │  │  ├─ items.service.ts         # Service items (filtres, détails)
│     │  │  ├─ wakfu-data.service.ts    # Service API Wakfu (stats, craft)
│     │  │  └─ imports.service.ts       # Service imports
│     │  └─ resolvers/
│     │     ├─ items.resolver.ts
│     │     └─ imports.resolver.ts
│     ├─ features/
│     │  ├─ items/
│     │  │  ├─ items-list/              # Liste avec filtres avancés
│     │  │  └─ item-details/            # Page détails + recette
│     │  ├─ craft-calculator/           # Calculateur de craft
│     │  ├─ categories/
│     │  │  └─ categories-view/         # Vue des catégories groupées
│     │  ├─ stats/
│     │  │  └─ stats-dashboard/         # Dashboard statistiques
│     │  └─ imports/
│     │     └─ imports-dashboard/       # Dashboard imports
│     ├─ shared/
│     │  ├─ pipes/
│     │  │  ├─ rarity-color.pipe.ts
│     │  │  ├─ category-badge.pipe.ts
│     │  │  └─ level-display.pipe.ts
│     │  └─ utils/
│     │     └─ formatting.utils.ts      # formatNumber, calculatePercentage, etc.
│     └─ app.routes.ts                  # 6 routes configurées
│
└─ infra/
   ├─ docker-compose.yml
   ├─ backend.Dockerfile
   ├─ frontend.Dockerfile
   ├─ servers.json              # Config pgAdmin
   └─ env/                      # Variables d'environnement
```

---

## Modèle de données

### ImportBatch

- Historique des imports : date, version gamedata, statut, compteurs

### Action

- Actions Wakfu (effets) : `wakfu_id`, `effect`, `description` (JSON multilingue)

### State

- États/buffs : `wakfu_id`, `title`, `description` (JSON multilingue)

### Job

- Métiers craftables : `wakfu_id`, `title`, `description` (JSON multilingue)

### ItemCategory

- Catégories d'items (35+) : `name` (ex: "equipments.weapons"), `type_ids`, `description`

### Item

- Items normalisés :
  - Identifiants : `wakfu_id`, `name`
  - Caractéristiques : `level`, `rarity`, `type`, `element`
  - Classification : `category_id` → ItemCategory
  - Effets : `parsed_effects` (JSON multilingue décodé)
  - Métadonnées : `icon_gfx_id`, `icon_url`, `stats`, `needs_review`

### Recipe

- Recettes de craft :
  - `wakfu_id`, `result_item_id` → Item
  - `job_id` → Job (métier requis)
  - `ingredients` (JSON : `[{item_id, quantity}, ...]`)
  - `craft_level` (niveau de métier requis)

### ItemRaw

- JSON brut de l'API (pour debug/replay)

---

## API Backend

### Import et données Wakfu (`/api/wakfu`)

- `POST /import/full` - Lance l'import complet (actions, states, jobs, items, recipes)
- `GET /stats` - Statistiques complètes (totaux, répartition par catégorie)
- `GET /categories` - Liste des catégories avec compteurs
- `GET /recipes/:wakfu_id` - Recette d'un item spécifique
- `GET /craft-calculator/:wakfu_id?quantity=X` - Calcul récursif des ressources

### Items (`/api/items`)

- `GET /` - Liste paginée
  - Params: `limit`, `offset`, `category`, `rarity`, `level_min`, `level_max`, `search`, `details`
  - Filtres par catégorie, rareté, niveau, recherche textuelle
  - Mode détails avec `parsed_effects` complets
- `GET /:id` - Détail d'un item avec effets parsés complets

### Imports (`/api/imports`)

- `POST /run` - Lance un import (utilise désormais le système complet)
- `GET /` - Liste des imports historiques

### Proxy (`/api/proxy`)

- `GET /icon/<icon_gfx_id>` - Proxy vers CDN Ankama (contournement CORS)

### Test visuel (`/test`)

- `GET /` - Interface HTML de test complète

### Healthcheck

- `GET /health` - Status API

---

## Démarrage rapide

### 1. Configuration

Créer les fichiers dans `infra/env/` :

**.env.database**

```env
POSTGRES_USER=wakstuff
POSTGRES_PASSWORD=wakstuff
POSTGRES_DB=wakstuff
```

**.env.backend**

```env
FLASK_APP=wsgi:app
FLASK_ENV=development
DATABASE_URL=postgresql+psycopg2://wakstuff:wakstuff@db:5432/wakstuff
ICON_BASE_URL=https://static.ankama.com/wakfu/portal/game/item/115
```

**.env.pgadmin**

```env
PGADMIN_DEFAULT_EMAIL=admin@wakstuff.local
PGADMIN_DEFAULT_PASSWORD=admin
```

> ⚠️ Ne pas commit ces fichiers (`.gitignore`)

### 2. Lancer l'infrastructure

```bash
cd infra
docker compose up --build db backend pgadmin -d
```

Services disponibles:

- Backend : http://localhost:5000
- pgAdmin : http://localhost:5050
- Interface de test : http://localhost:5000/test

### 3. Migrer la base de données

```bash
cd backend
python migrate_db.py
```

Crée toutes les tables (ImportBatch, Action, State, Job, ItemCategory, Item, Recipe).

### 4. Importer les données Wakfu

**Via l'interface de test** (recommandé):

1. Ouvrir http://localhost:5000/test
2. Cliquer sur "Lancer Import Complet"
3. Attendre 5-10 minutes (selon connexion)
4. Consulter les statistiques

**Via API**:

```bash
curl -X POST http://localhost:5000/api/wakfu/import/full
```

**Via Python**:

```python
from app import create_app
from app.pipeline.full_import import run_full_wakfu_import

app = create_app()
with app.app_context():
    batch = run_full_wakfu_import()
    print(f"Import terminé: {batch.total_items} items")
```

### 5. Tester le système

**Vérifier les statistiques**:

```bash
curl http://localhost:5000/api/wakfu/stats
```

**Lister les catégories**:

```bash
curl http://localhost:5000/api/wakfu/categories
```

**Rechercher des items par catégorie**:

```bash
curl "http://localhost:5000/api/items?category=equipments.weapons&limit=10"
```

**Calculer les ressources pour un craft**:

```bash
# Exemple avec un item craftable (ID Wakfu)
curl "http://localhost:5000/api/wakfu/craft-calculator/12345?quantity=1"
```

### 6. Frontend (développement)

```bash
cd frontend/wakstuff-frontend
npm install
npm start
```

Frontend disponible : http://localhost:4200

**Pages disponibles**:

- Items : http://localhost:4200/items
- Catégories : http://localhost:4200/categories
- Calculateur : http://localhost:4200/craft-calculator
- Stats : http://localhost:4200/stats
- Imports : http://localhost:4200/imports

---

## Fonctionnalités détaillées

### Interface de test (`/test`)

Interface HTML complète pour tester toutes les fonctionnalités sans code:

**Import des données**

- Bouton de lancement d'import
- Indicateur de progression
- Résumé JSON du résultat

**Statistiques**

- Cartes visuelles avec totaux (items, recettes, catégories, actions, états, métiers)
- Répartition des items par catégorie
- Mise à jour en temps réel

**Catégories**

- Liste complète des 35+ catégories
- Compteur d'items par catégorie
- Export JSON

**Items**

- Filtre par catégorie (dropdown)
- Mode détaillé avec effets parsés
- Affichage des badges (catégorie, niveau)
- Pagination (20 items)

**Calculateur de craft**

- Saisie d'un ID d'item
- Sélection de quantité
- Affichage de l'arbre JSON complet
- Liste des ressources nécessaires

### Frontend Angular

**Navigation principale** (5 routes):

- `/items` - Liste des items avec filtres
- `/items/:id` - Détails d'un item
- `/categories` - Vue des catégories
- `/craft-calculator` - Calculateur de craft
- `/stats` - Dashboard statistiques
- `/imports` - Historique des imports

**Page Items (`/items`)**

- Filtres avancés : catégorie (dropdown), rareté (8 raretés), niveau (min/max), recherche textuelle
- Affichage des effets parsés (optionnel)
- Badges colorés par rareté
- Pagination (25/50/100)
- Clic sur item → page détails

**Page Détails Item (`/items/:id`)**

- Informations complètes : nom, niveau, rareté, catégorie, type, élément
- Effets parsés en liste lisible
- Recette si craftable (ingrédients + métier + niveau requis)
- Bouton vers calculateur de craft

**Page Calculateur (`/craft-calculator`)**

- Recherche d'item avec suggestions (debounce 300ms)
- Sélection de quantité (1-999)
- Arbre de craft visuel (récursif, expandable)
- Résumé des ressources de base nécessaires
- Badges de catégorie pour chaque item

**Page Catégories (`/categories`)**

- Organisation par groupes parents (équipements, ressources, consommables)
- Cartes cliquables avec compteurs d'items
- Navigation directe vers items filtrés par catégorie

**Page Statistiques (`/stats`)**

- Vue d'ensemble : totaux (items, recettes, catégories, actions, états, métiers)
- Distribution par rareté avec barres de progression
- Top 10 catégories avec graphiques
- Répartition par tranche de niveau

**Page Imports (`/imports`)**

- Bouton "Lancer un import"
- Historique paginé (10/25/50)
- Colonnes : date, version, statut, items, erreurs
- Indicateurs visuels de statut

### Parser d'effets

Le système parse les templates Wakfu complexes:

**Exemples de templates**:

- `[#1]` → valeur du paramètre 1
- `{[>2]?s:}` → "s" si valeur > 2 (pluriel)
- `{[<10]?petit:gros}` → "petit" si < 10, sinon "gros"
- `[~3]` → valeur du paramètre 3 sans signe

**Support multilingue**:

```json
{
  "fr": "+[#1] en Maîtrise Feu",
  "en": "+[#1] Fire Mastery",
  "es": "+[#1] de Maestría de Fuego",
  "pt": "+[#1] de Maestria Fogo"
}
```

### Classification automatique

35+ catégories basées sur `typeId`:

**Équipements**: casques, plastrons, épaulettes, jambes, bottes, ceintures, capes, amulettes, anneaux, boucliers, armes (1 main, 2 mains), familiers, montures, costumes, emblèmes

**Ressources**: minerais, plantes, bois, poissons, viandes, céréales, légumes, cuirs, gemmes, tissus, matériaux de craft

**Consommables**: nourriture, potions, buffs

**Autres**: items de quête, sacs, clés, runes, sublimations, jetons

### Calculateur de craft récursif

Calcule automatiquement toutes les ressources nécessaires:

**Exemple**: Craft d'une "Épée Légendaire"

```
Épée Légendaire (x1)
├─ Lame en Acier (x1)
│  ├─ Minerai de fer (x5)
│  └─ Charbon (x3)
└─ Manche en bois (x1)
   └─ Bois de frêne (x10)

Ressources totales:
- 5x Minerai de fer [resources.ore]
- 3x Charbon [resources.ore]
- 10x Bois de frêne [resources.wood]
```

**Fonctionnalités**:

- Récursion illimitée (avec limite de sécurité)
- Agrégation des quantités
- Détection des ressources de base
- Support des quantités multiples

---

## pgAdmin

Configuration auto au premier lancement :

- Serveur "WakStuff Database" pré-configuré
- Connexion automatique (credentials depuis `.env`)
- Accès : http://localhost:5050

---

## Architecture technique détaillée

### Pipeline d'import complet

**1. Détection de version**

```python
client = WakfuClient()
version = client.get_current_version()  # Ex: "1.82.1.28"
```

**2. Téléchargement des ressources**

- `actions.json` → ~1200+ actions
- `states.json` → ~300+ états
- `jobs.json` → ~20+ métiers
- `itemTypes.json` → Mapping typeId → catégorie
- `items.json` → ~5000+ items
- `recipes.json` → ~1500+ recettes

**3. Import séquentiel**

```
Actions → States → Jobs → ItemCategories → Items (classify + parse) → Recipes
```

**4. Classification**

```python
def classify_item(item_data):
    type_id = item_data["definition"]["item"]["baseParameters"]["itemTypeId"]
    return get_category_from_type_id(type_id)
```

**5. Parsing d'effets**

```python
def parse_effect(effect, level, actions_data):
    # Résout [#1], {[>2]?s:}, [~3], etc.
    return {"description": {"fr": "...", "en": "...", ...}}
```

**6. Upsert en base**

- Basé sur `wakfu_id` unique
- Préserve les données existantes
- Track des erreurs

### Proxy d'icônes

**Problème**: Les icônes du CDN Ankama ne sont pas chargables directement (CORS/Referrer Policy).

**Solution**: Le proxy backend (`/api/proxy/icon/<id>`) :

1. Télécharge l'image depuis Ankama
2. La retourne avec headers CORS corrects
3. Cache en mémoire (optionnel)

```python
@proxy_bp.get("/icon/<int:icon_gfx_id>")
def proxy_icon(icon_gfx_id: int):
    icon_url = f"{ICON_BASE_URL}/{icon_gfx_id}.png"
    response = requests.get(icon_url)
    return Response(response.content, mimetype="image/png",
                    headers={"Access-Control-Allow-Origin": "*"})
```

### Frontend Angular moderne

**Standalone components** (pas de NgModule):

```typescript
@Component({
  selector: 'app-items-list',
  standalone: true,
  imports: [CommonModule, ...],
  templateUrl: './items-list.html'
})
```

**Resolvers** pour pré-chargement:

```typescript
export const itemsResolver: ResolveFn<Item[]> = (route, state) => {
  return inject(ItemsService).getItems();
};
```

**Services HTTP** encapsulés:

```typescript
getItems(limit = 100, offset = 0, category?: string): Observable<ItemsResponse> {
  let params = new HttpParams()
    .set('limit', limit.toString())
    .set('offset', offset.toString());
  if (category) params = params.set('category', category);
  return this.http.get<ItemsResponse>(`${API_URL}/items`, { params });
}
```

---

## Tests et validation

### Test de connexion et parsing

```bash
cd backend
python test_wakfu_import.py
```

Vérifie:

- Connexion à l'API Wakfu
- Téléchargement des ressources
- Parsing des effets
- Classification des items
- Mapping des raretés

### Exemple d'utilisation du calculateur

```bash
python examples/craft_calculator_example.py 12345
```

Affiche l'arbre de craft complet pour l'item spécifié.

### Interface de test visuelle

```
http://localhost:5000/test
```

Permet de tester toutes les fonctionnalités via navigateur sans écrire de code.

---

## pgAdmin

Configuration automatique au premier lancement:

- Serveur "WakStuff Database" pré-configuré
- Connexion automatique (credentials depuis `.env`)
- Accès : http://localhost:5050

**Explorer les données**:

1. Se connecter avec `admin@wakstuff.local` / `admin`
2. Serveurs → WakStuff Database
3. Databases → wakstuff → Schemas → public → Tables

---

## Développement

### Ajouter une nouvelle catégorie

**1. Modifier `wakfu_config.py`**:

```python
WAKFU_ITEM_CATEGORIES = {
    # ...
    "new.category": {
        "type_ids": [123, 456],
        "description": "Description de la catégorie"
    }
}
```

**2. Relancer l'import**:

```bash
curl -X POST http://localhost:5000/api/wakfu/import/full
```

### Améliorer le parser d'effets

**Fichier**: `backend/app/pipeline/effect_parser.py`

**Ajouter un nouveau pattern**:

```python
def _parse_template(template, params, level):
    # Votre logique ici
    if "[custom]" in template:
        return template.replace("[custom]", str(params[0]))
    # ...
```

### Ajouter un nouvel endpoint

**Fichier**: `backend/app/wakfu_data/routes.py`

```python
@bp.get("/custom-endpoint")
def custom_endpoint():
    # Votre logique
    return jsonify({"result": "data"})
```

---

## Fichiers de référence

- **README.md** - Ce fichier
- **TODO.md** - Roadmap et tâches à venir
- **PROJECT_STRUCTURE.md** - Structure détaillée du projet
- **VISUAL_SUMMARY.txt** - Diagramme ASCII de l'architecture

---

## Améliorations futures

### Court terme

- Mode sombre pour l'interface
- Sauvegarde des favoris utilisateur
- Export CSV/JSON des listes d'items
- Graphiques interactifs avec Chart.js ou D3

### Moyen terme

- Cache Redis pour proxy d'icônes
- Recherche full-text sur descriptions avec PostgreSQL FTS
- Comparateur d'items side-by-side
- Historique de navigation

### Long terme

- Build optimizer (suggestion d'équipement par niveau)
- Analytics de recettes (ressources les plus utilisées)
- API GraphQL
- Progressive Web App
- Mode hors ligne avec Service Workers
- Authentification utilisateur et collections personnelles

---

## Contribution

Projet personnel en développement actif. Les suggestions et retours sont bienvenus.

**Pour contribuer**:

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Ouvrir une Pull Request

---

## Licence

Projet personnel non commercial. Toutes les données Wakfu sont la propriété d'Ankama Games.

**Disclaimer**: Ce projet n'est pas affilié à, endorsé par, ou de quelque manière que ce soit associé officiellement à Ankama Games ou Wakfu.

---

## Contact & Support

Pour questions ou problèmes:

- Ouvrir une issue sur GitHub
- Consulter la documentation dans les fichiers `.md`
- Tester via l'interface : http://localhost:5000/test

---

**Dernière mise à jour**: Décembre 2025  
**Version**: 2.1 (Frontend complet + Filtres avancés + Calculateur visuel + Statistiques)
