# 🔍 Analyse des Flux de Données Backend ↔️ Frontend

**Date**: 6 décembre 2025  
**Avancement vérifié**: ✅ TODO.md à jour (85% Phase 3)  
**État global**: Système fonctionnel avec gestion d'erreurs robuste

---

## 📊 État de l'Avancement

### ✅ Documentation

- **TODO.md**: À jour, Phase 3 à 85%
- **PROJECT_STRUCTURE.md**: Structure complète documentée
- **VISUAL_SUMMARY.md**: Architecture visualisée

### ✅ Backend (75%)

- Routes API complètes avec gestion d'erreurs
- Modèles SQLAlchemy avec `to_dict()` via `DictSerializable`
- Système de craft tree récursif implémenté

### ✅ Frontend (85%)

- Services Angular avec typage TypeScript
- Gestion d'état avec signals
- Vérification import status avant appels API
- Composants avec EmptyState

---

## 🔄 Flux Backend → Frontend

### 1. **Route `/api/stats/overview`**

#### Backend (`backend/app/stats/routes.py`)

```python
@bp.route('/overview', methods=['GET'])
def get_stats_overview():
    try:
        total_items = Item.query.count()
        total_resources = Resource.query.count()
        # ...
    except Exception:
        db.session.rollback()
        return jsonify({
            'total_items': 0,
            'total_resources': 0,
            # ... tous à 0
        })
```

**✅ Points positifs:**

- Toujours retourne 200 (pas de 500)
- `db.session.rollback()` en cas d'erreur
- Retourne des stats à 0 si pas de données

#### Frontend (`services/stats.service.ts` → `import-status.service.ts`)

```typescript
checkImportStatus(): Observable<boolean> {
  return this.http.get<GlobalStats>(`${this.apiUrl}/stats/overview`).pipe(
    map(stats => stats.total_items > 0 || stats.total_resources > 0),
    tap(hasData => this.hasImportedData.set(hasData))
  );
}
```

**✅ Points positifs:**

- Vérifie si des données existent
- Cache le résultat dans un signal
- Utilisé avant tous les appels API

**⚠️ RISQUES POTENTIELS:**

1. **Race condition**: Si plusieurs composants appellent `checkImportStatus()` en même temps
   - **Impact**: Faible - RxJS gère bien les Observable multiples
   - **Solution actuelle**: Acceptable
2. **Stats vides != base de données vide**: Si `total_items=0` mais d'autres tables ont des données
   - **Impact**: Moyen - L'utilisateur verra "Pas de données" alors qu'il y en a
   - **Solution recommandée**: Vérifier aussi `total_recipes` et `total_job_items`

---

### 2. **Route `/api/items`**

#### Backend (`backend/app/items/routes.py`)

```python
@bp.route('', methods=['GET'])
def get_items():
    try:
        query = Item.query
        # Filtres...
        pagination = query.paginate(page=page, per_page=per_page)

        return jsonify({
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
    except Exception:
        db.session.rollback()
        return jsonify({
            'items': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'pages': 0
        })
```

**✅ Points positifs:**

- Try/catch global
- Retourne toujours la structure attendue
- Gestion de pagination

#### Modèle Backend (`backend/app/models.py` + `models_utils.py`)

```python
class Item(db.Model, DictSerializable):
    title = db.Column(db.JSON, nullable=False)  # {"fr": "...", "en": "..."}
    description = db.Column(db.JSON, nullable=True)
    level = db.Column(db.Integer, nullable=True)
    rarity = db.Column(db.Integer, nullable=True)
    # ...

class DictSerializable:
    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result
```

**⚠️ RISQUE CRITIQUE #1: Format des données JSON**

Le backend stocke `title` comme `{"fr": "Épée", "en": "Sword"}` mais le frontend attend `string`:

```typescript
// Frontend model (item.model.ts)
export interface Item {
  title: string; // ❌ INCOMPATIBILITÉ
  description?: string;
  // ...
}
```

**Conséquences:**

- Le frontend reçoit `title: {"fr": "Épée"}` au lieu de `"Épée"`
- Affichage cassé: `[object Object]` dans les templates
- Aucune erreur TypeScript (type `any` accepté par défaut)

**Solutions:**

**Option A - Backend sérialiseur custom** (RECOMMANDÉ)

```python
class Item(db.Model, DictSerializable):
    def to_dict(self):
        result = super().to_dict()
        # Extraire la langue par défaut (fr)
        if isinstance(result.get('title'), dict):
            result['title'] = result['title'].get('fr', '')
        if isinstance(result.get('description'), dict):
            result['description'] = result['description'].get('fr', '')
        return result
```

**Option B - Frontend transformation**

```typescript
getItems(filters: ItemFilters = {}): Observable<ItemsListResponse> {
  return this.http.get<any>(`${this.apiUrl}/items`, { params }).pipe(
    map(response => ({
      ...response,
      items: response.items.map(item => ({
        ...item,
        title: typeof item.title === 'object' ? item.title.fr : item.title,
        description: typeof item.description === 'object' ? item.description.fr : item.description
      }))
    }))
  );
}
```

---

### 3. **Route `/api/items/<wakfu_id>`**

#### Backend

```python
@bp.route('/<int:wakfu_id>', methods=['GET'])
def get_item_detail(wakfu_id):
    item = Item.query.filter_by(wakfu_id=wakfu_id).first_or_404()
    return jsonify({'item': item.to_dict()})
```

**⚠️ RISQUE #2: 404 non géré côté backend avec try/catch**

- `first_or_404()` lève une exception Werkzeug qui retourne un 404
- Mais le `try/except` au-dessus ne le capture pas (c'est une exception HTTP)
- Le frontend gère bien le 404 (ne le log pas)

**État actuel**: ✅ OK - Le 404 est une réponse HTTP valide, pas une erreur

---

### 4. **Route `/api/recipes/craft-tree/<item_wakfu_id>`**

#### Backend (`backend/app/recipes/routes.py`)

```python
@bp.route('/craft-tree/<int:item_wakfu_id>', methods=['GET'])
def get_craft_tree(item_wakfu_id):
    quantity = request.args.get('quantity', 1, type=int)
    max_depth = request.args.get('max_depth', 10, type=int)

    try:
        tree = build_craft_tree(item_wakfu_id, quantity, max_depth)
        return jsonify(tree)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
```

#### Utilitaire Backend (`backend/app/utils/craft_tree.py`)

```python
def build_craft_tree(item_wakfu_id: int, quantity: int = 1, max_depth: int = 10,
                     _depth: int = 0, _visited: Set[int] = None) -> Dict[str, Any]:
    # Vérification cycle
    if item_wakfu_id in _visited:
        return {
            'item_id': item_wakfu_id,
            'quantity': quantity,
            'depth': _depth,
            'cycle_detected': True,
            'ingredients': []
        }

    # Récupération récursive des ingrédients
    # ...
```

**⚠️ RISQUE #3: Structure de retour incompatible**

Le backend retourne:

```python
{
    'item_id': 123,
    'item': {...},  # to_dict() complet
    'quantity': 5,
    'depth': 0,
    'is_craftable': True,
    'recipes': [...],
    'total_ingredients': {...}
}
```

Le frontend attend (`craft-tree.model.ts`):

```typescript
interface CraftTreeResponse {
  recipe: { id; wakfu_id; level; recipe_category_id };
  craft_tree: CraftTreeNode;
}

interface CraftTreeNode {
  item_id: number;
  item_wakfu_id: number;
  item_title: string; // ❌ Pas dans le retour backend
  quantity: number;
  level: number; // ❌ Pas directement disponible
  is_resource: boolean; // ❌ Backend retourne is_craftable
  recipe_wakfu_id?: number;
  children: CraftTreeNode[];
  user_has?: boolean;
}
```

**Conséquences:**

- `item_title` sera `undefined`
- `level` sera `undefined` (il faut extraire de `item.level`)
- `is_resource` ne correspond pas à `is_craftable` (logique inversée)
- `children` vs `ingredients` (nom différent)

**Solution - Adapter le backend pour correspondre au contrat frontend:**

```python
def build_craft_tree(item_wakfu_id: int, quantity: int = 1, max_depth: int = 10,
                     _depth: int = 0, _visited: Set[int] = None) -> Dict[str, Any]:
    # ... récupération item ...

    result = {
        'item_id': item_wakfu_id,
        'item_wakfu_id': item_wakfu_id,
        'item_title': item.title.get('fr', '') if isinstance(item.title, dict) else item.title,
        'quantity': quantity,
        'level': item.level or 0,
        'is_resource': not bool(recipe_results),  # Inversé par rapport à is_craftable
        'recipe_wakfu_id': recipe.wakfu_id if recipe_results else None,
        'children': [],  # Au lieu de 'ingredients'
        'user_has': False
    }
```

---

### 5. **Route `/api/resources`**

#### Backend (`backend/app/resources/routes.py`)

```python
@bp.route('', methods=['GET'])
def get_resources():
    try:
        query = Resource.query
        # Filtres...
        pagination = query.paginate(...)
        return jsonify({
            'resources': [r.to_dict() for r in pagination.items],
            # ...
        })
    except Exception:
        db.session.rollback()
        return jsonify({'resources': [], 'total': 0, ...})
```

**⚠️ MÊME PROBLÈME: `title` JSON multilingue**

Même problème que pour les items. Le modèle `Resource` a:

```python
title = db.Column(db.JSON, nullable=False)  # {"fr": "Frêne", "en": "Ash"}
```

---

### 6. **Route `/api/stats/global`**

#### Backend

```python
@bp.route('/global', methods=['GET'])
def global_search():
    query_text = request.args.get('query', '').strip()

    try:
        # Recherche dans items, resources, recipes
        items = Item.query.filter(...).limit(limit).all()
        resources = Resource.query.filter(...).limit(limit).all()
        recipes = Recipe.query.join(Item, ...).filter(...).limit(limit).all()

        return jsonify({
            'items': [item.to_dict() for item in items],
            'resources': [res.to_dict() for res in resources],
            'recipes': [recipe.to_dict() for recipe in recipes],
            'total': len(items) + len(resources) + len(recipes)
        })
    except Exception:
        db.session.rollback()
        return jsonify({'items': [], 'resources': [], 'recipes': [], 'total': 0})
```

**✅ Points positifs:**

- Gère la query vide
- Try/catch global
- Retourne toujours la structure attendue

**⚠️ RISQUE #4: Performance avec `limit()` mais pas d'offset**

- Pas de pagination, juste une limite
- Si 1000 résultats mais `limit=20`, l'utilisateur ne peut pas voir les autres
- La recherche globale fait 3 requêtes SQL séparées

**Amélioration possible:**

```python
# Ajouter un offset pour pagination
offset = request.args.get('offset', 0, type=int)
items = Item.query.filter(...).offset(offset).limit(limit).all()
```

---

### 7. **Route `/api/imports/full`**

#### Backend (`backend/app/imports/routes.py`)

```python
@bp.route('/full', methods=['POST'])
def launch_full_import():
    try:
        data = request.get_json() or {}
        clear_before = data.get('clear_before', False)

        if clear_before:
            clear_all_data()

        batch = run_full_wakfu_import()
        stats = get_import_stats()

        return jsonify({
            "status": "success",
            "batch_id": batch.id,
            "stats": stats,
            "metadata": batch.import_metadata,
            "message": "...",
            "started_at": batch.started_at.isoformat() if batch.started_at else None,
            "completed_at": batch.completed_at.isoformat() if batch.completed_at else None
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de l'import: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
```

**✅ Points positifs:**

- Logging d'erreurs
- Retourne des timestamps ISO
- Structure claire success/error

**⚠️ RISQUE #5: Import long bloque la requête**

- `run_full_wakfu_import()` peut prendre 30 secondes ou plus
- La requête HTTP reste ouverte pendant tout ce temps
- Risque de timeout côté serveur/proxy/client

**Solutions:**

1. **Job asynchrone avec Celery** (idéal)
2. **Threading avec polling** (compromis)

   ```python
   import threading

   def launch_async_import():
       batch = ImportBatch(status='running')
       db.session.add(batch)
       db.session.commit()

       thread = threading.Thread(target=run_full_wakfu_import, args=(batch.id,))
       thread.start()

       return batch

   # Endpoint POST retourne immédiatement
   # Endpoint GET /api/imports/status/<batch_id> pour polling
   ```

---

## 🚨 Résumé des Risques Identifiés

### 🔴 CRITIQUE (Bloquants fonctionnels)

#### 1. **Format JSON multilingue non géré** ✅ **CORRIGÉ**

- **Localisation**: Backend `models.py` → Frontend tous services
- **Impact**: Affichage cassé `[object Object]`
- **Fichiers concernés**:
  - `backend/app/models.py` (Item, Resource, Recipe, RecipeCategory, etc.)
  - `frontend/src/app/core/models/*.model.ts`
  - `frontend/src/app/core/services/*.service.ts`

**✅ Solution implémentée**: Méthode `to_dict(lang='fr')` customisée dans `DictSerializable`:

```python
# backend/app/models_utils.py
class DictSerializable:
    def to_dict(self, lang='fr'):
        """Convertit le modèle en dictionnaire."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)

            # Gérer les types spéciaux
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, dict) and column.name in ['title', 'description', 'name']:
                # Extraire la langue demandée pour les champs multilingues
                result[column.name] = value.get(lang, value.get('fr', value.get('en', '')))
            else:
                result[column.name] = value

        return result
```

#### 2. **Structure CraftTree incompatible** ✅ **CORRIGÉ**

- **Localisation**: `backend/app/utils/craft_tree.py` ↔️ `frontend/core/models/craft-tree.model.ts`
- **Impact**: Données mal mappées, affichage cassé dans craft calculator

**✅ Solution implémentée**: `build_craft_tree()` réécrit pour retourner le format `CraftTreeNode`

**Modifications**:

- `backend/app/utils/craft_tree.py`: Structure complètement réécrite
- `backend/app/recipes/routes.py`: Endpoint adapté pour retourner `{recipe, craft_tree}`
- Champs ajoutés: `item_wakfu_id`, `item_title`, `level`, `is_resource`, `children`, `user_has`
- Extraction automatique du titre en français via `to_dict(lang='fr')`

---

### 🟠 MAJEUR (Limitations fonctionnelles)

#### 3. **Import synchrone bloquant**

- **Localisation**: `backend/app/imports/routes.py:launch_full_import()`
- **Impact**: Timeout possible, UX bloquée pendant 30+ secondes
- **Solution**: Job asynchrone ou threading avec polling

#### 4. **Recherche globale sans pagination** ✅ **CORRIGÉ**

- **Localisation**: `backend/app/stats/routes.py:global_search()`
- **Impact**: Résultats limités, pas d'accès aux suivants

**✅ Solution implémentée**: Ajout de la pagination avec `page` et `offset`

**Modifications**:

- Backend: `global_search()` accepte maintenant `?page=1&limit=20`
- Frontend: `StatsService.globalSearch(query, limit, page)` mis à jour
- Modèle: `GlobalSearchResult` inclut `page` et `per_page`
- Calcul offset: `offset = (page - 1) * limit`

---

### 🟡 MINEUR (Améliorations recommandées)

#### 5. **Vérification import status fragile** ✅ **CORRIGÉ**

- **Localisation**: `frontend/core/services/import-status.service.ts`
- **Impact**: Peut manquer des données si seuls recipes ou job_items sont importés

**✅ Solution implémentée**: Vérification étendue à toutes les tables principales

**Modification**:

```typescript
const hasData =
  stats.total_items > 0 ||
  stats.total_resources > 0 ||
  stats.total_recipes > 0 ||
  stats.total_job_items > 0; // ✅ Ajouté
```

#### 6. **Pas de cache HTTP côté backend**

- **Impact**: Performances sous-optimales
- **Solution**: Ajouter headers `Cache-Control` pour données statiques

---

## ✅ Points Forts du Système Actuel

1. **Gestion d'erreurs robuste**: Try/catch partout, rollback systématique
2. **Pas de 500 errors**: Retourne toujours 200 avec données vides si besoin
3. **404 non loggés**: Frontend ne pollue pas la console
4. **Import status check**: Évite les appels inutiles sur base vide
5. **EmptyState UX**: L'utilisateur comprend qu'il doit importer des données
6. **Typage TypeScript**: Modèles définis (même s'ils ne matchent pas encore)
7. **Signals Angular**: État réactif moderne

---

## 📋 Plan d'Action Recommandé

### Phase 1 - Corrections critiques (2-3h) ✅ **TERMINÉE**

1. ✅ **FAIT** - Modifier `DictSerializable.to_dict()` pour gérer JSON multilingues
2. ✅ **FAIT** - Adapter `build_craft_tree()` pour correspondre à `CraftTreeNode`
3. ✅ **FAIT** - Adapter route `/api/recipes/craft-tree` pour retourner le bon format
4. ✅ **FAIT** - Améliorer vérification import status (toutes les tables)
5. ✅ **FAIT** - Ajouter pagination à la recherche globale

### Phase 2 - Améliorations majeures (4-5h) 📝 **EN ATTENTE**

6. ⏳ Implémenter import asynchrone avec polling (non critique pour l'instant)
7. ⏳ Tester affichage items/resources/recipes dans le frontend
8. ⏳ Vérifier que le craft calculator affiche correctement l'arbre

### Phase 3 - Optimisations (2-3h) 📝 **FUTUR**

9. 🚀 Ajouter cache HTTP
10. 🚀 Ajouter tests unitaires backend
11. 🚀 Ajouter tests e2e frontend

---

## 📝 Checklist de Validation

### Backend ✅ **Corrections appliquées**

- [x] `to_dict()` retourne des strings pour title/description
- [x] `build_craft_tree()` retourne la structure `CraftTreeNode`
- [x] Route `/api/recipes/craft-tree` retourne `{recipe, craft_tree}`
- [x] Recherche globale paginée avec `page` et `offset`
- Import asynchrone implémenté
- Recherche globale paginée
- Tests unitaires passent

### Frontend

- [ ] Affichage correct des titres d'items
- [ ] Craft calculator affiche l'arbre correctement
- [ ] Pas d'erreurs console (hors 404 légitimes)
- [ ] EmptyState s'affiche quand approprié

### Intégration 🧪 **Tests requis**

- [ ] Test end-to-end: Import → Affichage items → Craft tree
- [ ] Test: Base vide → EmptyState → Import → Données affichées
- [ ] Test: Recherche globale → Résultats corrects → Pagination
- [ ] Test: Pagination items/resources/recipes

---

## 🎯 Résumé des Corrections Appliquées

### ✅ 1. Format JSON multilingue (CRITIQUE)

**Fichier**: `backend/app/models_utils.py`

- Ajout paramètre `lang='fr'` à `to_dict()`
- Détection automatique des champs multilingues (`title`, `description`, `name`)
- Extraction intelligente avec fallback: `lang` → `'fr'` → `'en'` → première valeur
- Propagation à `to_dict_with_relations()`

### ✅ 2. Structure CraftTree (CRITIQUE)

**Fichiers**: `backend/app/utils/craft_tree.py`, `backend/app/recipes/routes.py`

- Réécriture complète de `build_craft_tree()` pour format `CraftTreeNode`
- Ajout champs: `item_wakfu_id`, `item_title`, `level`, `is_resource`, `children`, `user_has`
- Route retourne maintenant `{recipe: {...}, craft_tree: {...}}`
- Utilisation de `to_dict(lang='fr')` pour extraction titre

### ✅ 3. Import status robuste (MINEUR)

**Fichier**: `frontend/src/app/core/services/import-status.service.ts`

- Vérification étendue: `total_items || total_resources || total_recipes || total_job_items`
- Évite les faux négatifs si seulement certaines tables importées

### ✅ 4. Pagination recherche globale (MAJEUR)

**Fichiers**: `backend/app/stats/routes.py`, `frontend/src/app/core/services/stats.service.ts`, `frontend/src/app/core/models/stats.model.ts`

- Backend: Ajout paramètres `page` et calcul `offset = (page - 1) * limit`
- Frontend: `globalSearch(query, limit, page)` mis à jour
- Modèle: `GlobalSearchResult` inclut `page` et `per_page`
- Retour cohérent même en cas d'erreur
- [ ] Import asynchrone implémenté
- [ ] Recherche globale paginée
- [ ] Tests unitaires passent

### Frontend

- [ ] Affichage correct des titres d'items
- [ ] Craft calculator affiche l'arbre correctement
- [ ] Import status vérifie toutes les tables
- [ ] Pas d'erreurs console (hors 404 légitimes)
- [ ] EmptyState s'affiche quand approprié

### Intégration 🧪 **Tests requis**

- [ ] Test end-to-end: Import → Affichage items → Craft tree
- [ ] Test: Base vide → EmptyState → Import → Données affichées
- [ ] Test: Recherche globale → Résultats corrects → Pagination
- [ ] Test: Pagination items/resources/recipes

---

## 🔄 Prochaines Étapes Recommandées

1. **Rebuild du backend Docker**: `docker compose up -d --build backend`
2. **Test manuel**: Vérifier l'affichage des items dans le frontend
3. **Test craft calculator**: Chercher une recette et vérifier l'arbre
4. **Recherche globale**: Tester la pagination
5. **Import asynchrone**: Considérer l'implémentation si timeout fréquent

---

**Date de dernière mise à jour**: 6 décembre 2025 - 18:30  
**Statut**: ✅ 4/5 corrections critiques/majeures appliquées  
**Import asynchrone**: ⏳ En attente (non bloquant)  
**Prochaine révision**: Après tests manuels des corrections
