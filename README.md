# WakStuff – V1 README

WakStuff est un projet de tooling autour des données du jeu **Wakfu**.

La V1 permet de :

- Récupérer les données officielles d’items Wakfu via le CDN Ankama (JSON)
- Nettoyer et normaliser ces données dans une base **PostgreSQL**
- Exposer une API Flask pour consulter les items normalisés
- Consommer cette API depuis un front **Angular 21 standalone** avec :

  - Un tableau de bord d’imports
  - Une liste simple des items

> ⚠️ WakStuff V1 est prévue pour un usage **dev / perso / non commercial**.

---

## 1. Stack technique

### Backend

- **Langage** : Python 3.13
- **Framework** : Flask
- **ORM** : Flask-SQLAlchemy
- **CORS** : flask-cors
- **HTTP client** : requests
- **Base de données** : PostgreSQL (via Docker)

### Frontend

- **Framework** : Angular 21
- **Mode** : Standalone components + nouveau contrôle de flux (`@if`, `@for`)
- **Langage** : TypeScript
- **Build** : npm / Angular CLI

### Infrastructure

- **Orchestration** : docker-compose
- **Services** :

  - `db` (Postgres 16)
  - `backend` (Flask en Python 3.13)
  - `frontend` (Angular, optionnel en conteneur — dev surtout via `ng serve`)

---

## 2. Structure du projet

```text
WakStuff/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py          # create_app, enregistrement blueprints, CORS, db.create_all()
│  │  ├─ config.py            # Config Flask (DATABASE_URL, etc.)
│  │  ├─ database.py          # Initialisation SQLAlchemy
│  │  ├─ models.py            # ImportBatch, ItemRaw, Item
│  │  ├─ wakfu_client/
│  │  │  ├─ __init__.py
│  │  │  └─ client.py         # Récupération config.json + items.json
│  │  ├─ pipeline/
│  │  │  ├─ __init__.py
│  │  │  ├─ sanitize.py       # sanitize_item, normalisation item brut → Item
│  │  │  └─ import_items.py   # run_full_import, orchestration ETL
│  │  ├─ items/
│  │  │  ├─ __init__.py
│  │  │  └─ routes.py         # /api/items, /api/items/<id>
│  │  └─ imports/
│  │     ├─ __init__.py
│  │     └─ routes.py         # /api/imports/run, /api/imports
│  ├─ wsgi.py                 # Point d’entrée Flask
│  └─ requirements.txt
│
├─ frontend/
│  └─ wakstuff-frontend/
│     ├─ src/
│     │  ├─ main.ts           # bootstrapApplication(App, appConfig)
│     │  ├─ app/
│     │  │  ├─ app.ts         # composant racine (header + router-outlet)
│     │  │  ├─ app.config.ts  # provideRouter, provideHttpClient
│     │  │  ├─ app.routes.ts  # routes /items et /imports
│     │  │  ├─ core/
│     │  │  │  ├─ config.ts   # API_BASE_URL
│     │  │  │  └─ services/
│     │  │  │     ├─ items.service.ts
│     │  │  │     └─ imports.service.ts
│     │  │  └─ features/
│     │  │     ├─ items/items-list/
│     │  │     │  ├─ items-list.ts
│     │  │     │  └─ items-list.html
│     │  │     └─ imports/imports-dashboard/
│     │  │        ├─ imports-dashboard.ts
│     │  │        └─ imports-dashboard.html
│     │  └─ ...
│     └─ package.json
│
└─ infra/
   ├─ docker-compose.yml      # services db, backend, frontend
   ├─ backend.Dockerfile
   ├─ frontend.Dockerfile
   └─ env/
      ├─ .env.database        # config Postgres
      └─ .env.backend         # config backend (Flask, DB, options)
```

---

## 3. Modèle de données (V1)

### 3.1. ImportBatch

Table : `import_batches`

- `id` (int, PK)
- `started_at` (datetime, timezone-aware, UTC)
- `ended_at` (datetime, timezone-aware, UTC, nullable)
- `game_version` (str) – version de gamedata utilisée (issue de `config.json`)
- `status` (str) – `running` / `success` / `failed`
- `total_items` (int)
- `error_count` (int)

### 3.2. ItemRaw

Table : `item_raw`

- `id` (int, PK)
- `wakfu_id` (int, index)
- `raw_json` (JSON) – item brut tel que fourni par `items.json`
- `import_batch_id` (FK → ImportBatch)

Permet de :

- rejouer un import sans retélécharger l’API,
- débugger les mappings,
- analyser les changements entre versions.

### 3.3. Item

Table : `items`

- `id` (int, PK)
- `wakfu_id` (int, unique, index)
- `name` (str) – nom normalisé (fr priorité, fallback en)
- `rarity` (str, nullable)
- `level` (int, nullable)
- `type` (str, nullable)
- `element` (str, nullable)
- `stats` (JSON) – stats/effects normalisés (V1 : structure simple)
- `description` (text, nullable)
- `needs_review` (bool) – indique si des champs clés manquent ou sont douteux
- `created_at` (datetime, timezone-aware, UTC)
- `updated_at` (datetime, timezone-aware, UTC)

C’est cette table qui est consommée par le frontend.

---

## 4. Pipeline d’import (Wakfu → WakStuff)

### 4.1. Source de données

WakStuff V1 consomme les données officielles Wakfu exposées via le CDN Ankama :

1. `config.json` pour connaître la **version courante** de la gamedata
2. `items.json` pour récupérer la liste complète des items pour cette version

(La logique exacte de parsing de ces fichiers est encapsulée dans `WakfuClient`.)

### 4.2. WakfuClient

Fichier : `backend/app/wakfu_client/client.py`

Responsabilités :

- Télécharger `config.json` et en déduire la propriété `game_version` (clé `version`, `gameDataVersion`, etc.)
- Construire l’URL des données : `${base_url}/${game_version}/items.json`
- Télécharger et parser `items.json`
- Exposer :

  - `get_current_version()` → str
  - `fetch_all_items(version: str | None = None)` → `list[dict]`
  - `iter_all_items(version: str | None = None)` → itérateur sur les items bruts

### 4.3. Sanitize & normalisation

Fichier : `backend/app/pipeline/sanitize.py`

- `_normalize_text(value)`

  - gère les champs texte sous forme de `str`, dict de langues (`{"fr": ..., "en": ...}`), listes, etc.
  - renvoie une `str` propre (`strip()`), ou `""` en dernier recours

- `sanitize_item(raw)`

  - prend un item brut JSON
  - extrait :

    - `wakfu_id`
    - `name` (priorité FR puis EN)
    - `description`
    - `rarity`, `type`, `element`
    - `stats` (ou un conteneur simple si le format n’est pas encore maîtrisé)

  - calcule `needs_review` si des champs critiques manquent (id ou name)
  - renvoie un dict prêt à alimenter le modèle `Item`

### 4.4. Orchestration : run_full_import

Fichier : `backend/app/pipeline/import_items.py`

- Lit la version courante via `WakfuClient.get_current_version()`
- Crée un `ImportBatch` (status `running`, `game_version` = version courante)
- Itère sur `WakfuClient.iter_all_items(version)`

  - stocke chaque item brut dans `ItemRaw`
  - passe l’item à `sanitize_item`
  - effectue un **upsert** dans `Item` basé sur `wakfu_id`
  - incrémente `total_items` et `error_count` si une exception survient

- Termine le batch :

  - `status` → `success` (ou `failed` si tu choisis de gérer ce cas plus tard)
  - `ended_at` → datetime UTC

---

## 5. API HTTP (V1)

### 5.1. Healthcheck

- `GET /health`
- Réponse : `{ "status": "ok" }`

### 5.2. Imports

#### POST `/api/imports/run`

Lance un import complet des items Wakfu (version courante) vers WakStuff.

- Effets :

  - crée un `ImportBatch`
  - télécharge `items.json`
  - remplit `item_raw` et `items`

- Réponse typique :

```json
{
  "batch_id": 1,
  "status": "success",
  "total_items": 12345,
  "error_count": 12
}
```

#### GET `/api/imports/`

Liste les derniers imports.

- Réponse : tableau de `ImportBatch` sérialisés (id, dates, status, total_items, error_count, game_version éventuelle).

### 5.3. Items

#### GET `/api/items/`

Retourne une liste d’items normalisés (limite raisonnable côté backend, ex : 100 premiers, à faire évoluer vers pagination si besoin).

- Réponse typique :

```json
[
  {
    "id": 1,
    "wakfu_id": 1234,
    "name": "Nom de l’item",
    "rarity": "rare",
    "level": 50,
    "type": "weapon",
    "element": "fire",
    "needs_review": false
  },
  ...
]
```

#### GET `/api/items/<id>`

Retourne le détail d’un item.

- Champs supplémentaires possibles : `stats`, `description`, dates de création / mise à jour.

---

## 6. Frontend (Angular 21)

### 6.1. Config API

Fichier : `src/app/core/config.ts`

```ts
export const API_BASE_URL = "http://localhost:5000";
```

> En dev : le front (`ng serve` sur 4200) appelle le backend Flask sur `localhost:5000`.
> En mode Docker complet, il faudra adapter cette valeur (par ex. `http://backend:5000`).

### 6.2. Services

#### ItemsService

Fichier : `src/app/core/services/items.service.ts`

- `list()` → `GET /api/items/`
- `get(id)` → `GET /api/items/<id>`

#### ImportsService

Fichier : `src/app/core/services/imports.service.ts`

- `run()` → `POST /api/imports/run`
- `list()` → `GET /api/imports/`

### 6.3. Composant ItemsList

Fichier : `src/app/features/items/items-list/items-list.ts`

- Standalone component : chargé directement via la route `/items`
- Au `ngOnInit()`, appelle `reload()` qui :

  - met `loading = true`
  - appelle `ItemsService.list()`
  - stocke la réponse dans `items`
  - gère les erreurs (message `error` + liste vide)

Template : `items-list.html`

- Bouton _Recharger_
- Affichage conditionnel via `@if` / `@for` (nouvelle syntaxe Angular)
- Liste des items (id, nom, niveau, rareté)

### 6.4. Composant ImportsDashboard

Fichier : `src/app/features/imports/imports-dashboard/imports-dashboard.ts`

- Affiche la liste des `ImportBatch`
- Bouton _Lancer un import_ → `ImportsService.run()`
- Recharge la liste après un import

Template : `imports-dashboard.html`

- Bouton d’action
- Message de statut du dernier import
- Tableau des derniers imports (id, dates, status, total_items, error_count)

---

## 7. Lancer le projet (V1)

### 7.1. Prérequis

- Docker + docker-compose
- Python 3.13 (pour dev local backend hors Docker, optionnel)
- Node.js moderne (LTS) + npm (pour dev front hors Docker)

### 7.2. Configuration des fichiers d’environnement

Dans `infra/env/.env.database` :

```env
POSTGRES_USER=wakstuff
POSTGRES_PASSWORD=wakstuff
POSTGRES_DB=wakstuff
```

Dans `infra/env/.env.backend` (exemple minimal) :

```env
FLASK_APP=wsgi:app
FLASK_ENV=development
DATABASE_URL=postgresql+psycopg2://wakstuff:wakstuff@db:5432/wakstuff
```

> Ces fichiers ne doivent **pas** être commit (ajouter à `.gitignore`).

### 7.3. Lancer DB + backend (via Docker)

Depuis le dossier `infra/` :

```bash
cd infra

# Build et lancement DB + backend
docker compose up --build db backend
```

Tester le backend :

- Ouvrir `http://localhost:5000/health`

  - Réponse attendue : `{ "status": "ok" }`

### 7.4. Lancer un import (API)

Invocation HTTP (via Postman / curl / Invoke-RestMethod) :

```bash
POST http://localhost:5000/api/imports/run
```

Réponse attendue : JSON avec `batch_id`, `status`, `total_items`, `error_count`.

Vérifier la liste des imports :

```bash
GET http://localhost:5000/api/imports/
```

Vérifier la liste des items :

```bash
GET http://localhost:5000/api/items/
```

### 7.5. Lancer le frontend en dev

Depuis `frontend/wakstuff-frontend/` :

```bash
cd frontend/wakstuff-frontend
npm install
npm start
# ou: npx ng serve
```

Frontend accessible sur : `http://localhost:4200`

- Page **Imports** : permet de lancer un import et de voir les derniers batches
- Page **Items** : affiche la liste des items importés

### 7.6. Option : lancer aussi le frontend via Docker

Lorsque le Dockerfile frontend est configuré avec le bon chemin de build :

```bash
cd infra

# Build et lancement de l'ensemble
docker compose up --build
```

Le frontend sera alors servi par Nginx (port mappé sur `4200` ou autre selon `docker-compose.yml`).

> Dans ce mode, il faudra adapter `API_BASE_URL` côté Angular pour appeler `http://backend:5000` au lieu de `http://localhost:5000`.

---

## 8. Limitations et pistes de V2

V1 se concentre sur :

- la récupération de données officielles,
- une première normalisation simple,
- l’exposition d’une API REST utilisable,
- un front minimal pour piloter les imports et visualiser les items.

Pistes de V2 :

- **Builder manuel** : interface front pour éditer/corriger un item (type, élément, stats…) et marquer `needs_review = false`.
- **Assistance IA** : proposition automatique de normalisation / catégories / descriptions à partir du JSON brut.
- **Pagination et filtres avancés** sur `/api/items/` et la liste front.
- **Historisation des versions** : comparer les items entre deux versions de gamedata.
- **Migration vers Alembic** pour une gestion fine des schémas DB.

WakStuff V1 fournit ainsi une base technique saine pour itérer sur la qualité des données et la richesse du front sans changer de stack ou de paradigme.
