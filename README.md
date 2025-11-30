# WakStuff

Projet de tooling autour des données du jeu **Wakfu** (Ankama).

## Fonctionnalités

- Import automatique des données d'items depuis le CDN officiel Wakfu
- Normalisation et stockage dans PostgreSQL
- API REST Flask avec endpoints paginés
- Interface Angular 21 moderne :
  - Tableau de bord des imports avec historique
  - Liste paginée et recherchable des items
  - Affichage des icônes via proxy (contournement CORS)
- Configuration pgAdmin intégrée

> ⚠️ Usage personnel / non commercial uniquement.

---

## Stack technique

**Backend**

- Python 3.13 + Flask + SQLAlchemy
- PostgreSQL 16
- Proxy d'images pour CDN Ankama

**Frontend**

- Angular 21 (standalone components)
- TypeScript + SCSS
- Pagination client-side + recherche temps réel

**Infrastructure**

- Docker Compose
- pgAdmin 4 auto-configuré
- Nginx (production)

---

## Structure

```
WakStuff/
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ models.py              # ImportBatch, ItemRaw, Item
│  │  ├─ wakfu_client/          # Client API Wakfu
│  │  ├─ pipeline/              # ETL & normalisation
│  │  ├─ items/routes.py        # /api/items
│  │  ├─ imports/routes.py      # /api/imports
│  │  └─ proxy/routes.py        # /api/proxy/icon/<id>
│  └─ wsgi.py
│
├─ frontend/wakstuff-frontend/
│  └─ src/app/
│     ├─ core/                  # Services & resolvers
│     └─ features/
│        ├─ items/
│        └─ imports/
│
└─ infra/
   ├─ docker-compose.yml
   ├─ servers.json              # Config pgAdmin
   └─ env/                      # Variables d'environnement
```

---

## Modèle de données

### ImportBatch

- Historique des imports (date, version gamedata, statut, compteurs)

### ItemRaw

- JSON brut de l'API Wakfu (pour debug/replay)

### Item

- Données normalisées : `wakfu_id`, `name`, `level`, `rarity`, `type`, `element`
- `icon_gfx_id` : identifiant de l'icône
- `icon_url` : URL générée via proxy backend
- `needs_review` : flag qualité données
- `stats` (JSON) : effets et paramètres

---

## API Backend

### Imports

- `POST /api/imports/run` - Lance un import complet
- `GET /api/imports/` - Liste des imports

### Items

- `GET /api/items/` - Liste paginée (limit/offset)
- `GET /api/items/<id>` - Détail d'un item

### Proxy

- `GET /api/proxy/icon/<icon_gfx_id>` - Proxy vers CDN Ankama

### Healthcheck

- `GET /health` - Status API

---

## Démarrage

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

### 2. Lancer avec Docker

```bash
cd infra
docker compose up --build db backend pgadmin
```

- Backend : http://localhost:5000
- pgAdmin : http://localhost:5050

### 3. Importer les données

```bash
# Via API
curl -X POST http://localhost:5000/api/imports/run

# Ou depuis l'interface Angular (voir ci-dessous)
```

### 4. Frontend (dev)

```bash
cd frontend/wakstuff-frontend
npm install
npm start
```

Frontend : http://localhost:4200

---

## Fonctionnalités frontend

### Page Imports (`/imports`)

- Bouton "Lancer un import"
- Historique des imports (pagination 10/25/50)
- Affichage : date, version, statut, nombre d'items, erreurs

### Page Items (`/items`)

- Liste paginée (25/50/100 items)
- Recherche en temps réel (nom, type, rareté, niveau)
- Affichage : icône, nom, niveau, rareté, type
- Flag "À revoir" pour items incomplets

---

## pgAdmin

Configuration auto au premier lancement :

- Serveur "WakStuff Database" pré-configuré
- Connexion automatique (credentials depuis `.env`)
- Accès : http://localhost:5050

---

## Architecture technique

### Pipeline d'import

1. **WakfuClient** : télécharge `config.json` pour détecter la version, puis `items.json`
2. **sanitize_item()** : normalise chaque item brut (textes multilangues, types, stats)
3. **run_full_import()** :
   - Crée un `ImportBatch`
   - Pour chaque item : stocke JSON brut + version normalisée
   - Upsert basé sur `wakfu_id`

### Proxy d'icônes

Les icônes du CDN Ankama ne sont pas chargables directement (CORS/Referrer Policy).
Le proxy backend (`/api/proxy/icon/<id>`) :

- Télécharge l'image depuis Ankama
- La retourne avec headers CORS corrects
- Évite les erreurs de chargement cross-origin

### Frontend Angular

- **Standalone components** (pas de NgModule)
- **Resolvers** : pré-chargement des données avant affichage route
- **Services HTTP** : encapsulation des appels API
- **Pagination client-side** : calcul des pages/slices
- **Recherche réactive** : filtrage en mémoire

---

## Améliorations futures

- Cache Redis pour le proxy d'icônes
- Pagination côté serveur pour `/api/items`
- Interface d'édition manuelle des items
- Historisation des versions gamedata
- Système de suggestions IA pour normalisation
- Export/import de données
- Tests unitaires et e2e

---

## Licence

Projet personnel non commercial. Données Wakfu © Ankama.
