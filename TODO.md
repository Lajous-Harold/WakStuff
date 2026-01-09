# TODO - WakStuff

## 📌 État Actuel (9 Janvier 2026 - 18h25)

**Dernière mise à jour:** 9 janvier 2026 - 18h25  
**Branche active:** refonte-wakstuff  
**Dernier commit:** Corrections comparaison items (title vs name, stat 1068)

### ✅ PRIORITÉ 2.5 Complétée - Item Comparator (9 Janvier 2026 - 18h25)

**Fonctionnalités Principales:**

- ✅ **Backend Endpoint POST `/api/items/compare`**:

  - Parsing `equip_effects` avec `item.to_dict()` pour éviter les None
  - Extraction actionId + params pour toutes les stats d'équipement
  - Lookup Action table pour noms français (description.fr)
  - Nettoyage avancé des syntaxes Wakfu: `[#charac XXX]`, `{[...]}`, `[#1]`, accolades orphelines
  - Fallback sur `action.effect` pour stats avec descriptions complexes (ex: action 1068)
  - Support equipment_type (extraction titre français depuis dict)
  - Retour structure: `{items: [{wakfu_id, title, level, rarity, icon_gfx_id, equipment_type}], stats: {statName: {action_id, values: [val1, val2]}}}`

- ✅ **Frontend ItemCompareComponent**:

  - Recherche autocomplete avec debounce 300ms sur nom d'item
  - Limite stricte de 2 items (pas 3)
  - Filtrage intelligent: item 2 filtré par equipment_type_id de item 1
  - Dropdown avec preview (icône, nom, niveau, étoiles rareté)
  - Interface CompareResponse corrigée: `title` au lieu de `name`
  - Méthodes de nettoyage: cleanText() et cleanStatLabel() pour syntaxe Wakfu
  - Système de rareté: 8 niveaux avec classes nominales (common, rare, legendary, etc.)
  - Images via proxy backend: `/api/proxy/icon/<icon_gfx_id>`

- ✅ **Affichage Comparaison**:
  - Cartes items: Image, titre nettoyé, niveau, badges rareté (gradients), type équipement
  - Badge "🏆 Meilleur" sur l'item avec le meilleur score global
  - Tableau stats: Noms de stats nettoyés, valeurs colorées (vert=meilleur, rouge=pire, gris=neutre)
  - Indicateurs visuels: ▲ pour meilleur, ▼ pour pire
  - Design responsive avec SCSS moderne

**Bugs Corrigés:**

1. **✅ Stats vides (backend)**:

   - Cause: `item.equip_effects` retournait None avec SQLAlchemy
   - Solution: Utilisé `item.to_dict().get('equip_effects')` pour données complètes

2. **✅ Images non chargées**:

   - Cause: Angular dev server (4200) ne pouvait pas accéder backend proxy (5000)
   - Solution: proxy.conf.json + angular.json + redémarrage Angular
   - Config: `/api/*` → `http://localhost:5000`

3. **✅ AttributeError equipment_type.name**:

   - Cause: Model utilisait `title` pas `name`
   - Solution: Changé vers `equipment_type.title`

4. **✅ Equipment type retourne dict**:

   - Cause: `equipment_type.title` est JSON avec traductions
   - Solution: Extraction français: `title.get('fr', title.get('en', str(title)))`

5. **✅ Noms items "Item 23240"**:

   - Cause: Frontend HTML utilisait `item.name` mais backend retournait `item.title`
   - Solution: Interface TypeScript corrigée + toutes références HTML mises à jour

6. **✅ Stat avec caractères "{" et "}"**:
   - Cause: Action 1068 "Maîtrise Élémentaire variable" avec syntaxe conditionnelle complexe Wakfu
   - Investigation: `{[~3]?[#1] Maîtrise [#3]:[#1] Maîtrise sur [#2] élément{[>2]?s:}}`
   - Solution:
     - Nettoyage amélioré: enlever tous `{}[]` orphelins après traitement
     - Fallback sur `action.effect` si description devient vide
     - Résultat: "Maîtrise Élémentaire dans un nombre variable d'éléments [18.0, 38.0]"
   - **Aucune perte de données**: Toutes les stats préservées avec noms corrects

**Fichiers Créés/Modifiés:**

- Backend: `app/items/routes.py` (endpoint compare_items avec nettoyage avancé)
- Frontend TypeScript: `item-compare.service.ts`, `item-compare.ts`
- Frontend HTML: `item-compare.html`
- Frontend SCSS: `item-compare.scss`
- Frontend Utils: `wakfu-text.utils.ts` (cleanWakfuText, cleanWakfuStatDescription)
- Config: `proxy.conf.json`, `angular.json`
- Routes: `app.routes.ts` (route /item-compare)

**Tests Validés:**

- ✓ Recherche autocomplete fonctionnelle
- ✓ Filtrage par type d'équipement
- ✓ Parsing complet de toutes les stats
- ✓ Noms de stats nettoyés et lisibles
- ✓ Stats spéciales (action 1068) avec nom descriptif
- ✓ Images via proxy backend
- ✓ Design professionnel avec rareté colorée

### 🚧 En Cours - Aucune tâche active

### 🎉 Accomplissements Récents (Session du 9 Janvier)

**✅ PRIORITÉ 2.2 - Advanced Filters (9 Janvier 2026 - 00h05):**

- ✅ **Sorting System**:
  - Backend: `sort_by` et `sort_order` pour items (name, level, rarity, created_at) et recipes (name, level)
  - Frontend: Select dropdowns dans items-list et craft-recipes-list
  - Methodes: onSortByChange(), onSortOrderChange()
- ✅ **Clear All Filters**:
  - Bouton "🗑️ Effacer tous les filtres" avec garde @if (hasActiveFilters())
  - Méthodes hasActiveFilters() et clearAllFilters() pour items-list et craft-recipes-list
  - Reset intelligent (garde catégorie dans craft-recipes-list)

**✅ PRIORITÉ 2.2 - Advanced Filters (9 Janvier 2026 - 00h05):**

- ✅ **Sorting System**:
  - Backend: `sort_by` et `sort_order` pour items (name, level, rarity, created_at) et recipes (name, level)
  - Frontend: Select dropdowns dans items-list et craft-recipes-list
  - Methodes: onSortByChange(), onSortOrderChange()
- ✅ **Clear All Filters**:
  - Bouton "🗑️ Effacer tous les filtres" avec garde @if (hasActiveFilters())
  - Méthodes hasActiveFilters() et clearAllFilters() pour items-list et craft-recipes-list
  - Reset intelligent (garde catégorie dans craft-recipes-list)

**✅ PRIORITÉ 2.3 - Harvest Optimizer (9 Janvier 2026 - 00h10):**

- ✅ **Backend Endpoints**:
  - GET `/api/harvest/zones`: Liste zones de récolte avec filtres (level, skill_id, resource_ids)
  - POST `/api/harvest/optimize`: Calcul itinéraire optimal (efficiency, distance, parcours)
  - 8 zones fictives avec coordonnées, level_range, skill_ids, resource_ids
  - Algorithme: Tri par efficacité (match_count), calcul distances euclidiennes
- ✅ **Frontend Component**:
  - HarvestService: getZones(), optimizeRoute() avec interfaces TypeScript
  - HarvestOptimizerComponent: Input ressources, niveau joueur, max zones
  - UI: Tags ressources, optimisation, résultats avec efficacité (high/medium/low)
  - Export: Téléchargement itinéraire .txt avec détails zones
  - Navigation: Route /harvest-optimizer avec icône 🗺️
- ✅ **Build Production**: Nouveau chunk harvest-optimizer (19.49kB)

**✅ PRIORITÉ 2.4 - Analytics Dashboard (9 Janvier 2026 - 00h15):**

- ✅ **Backend Endpoints** (6 routes):
  - GET `/api/analytics/top-resources`: Top 10 ressources les plus demandées (usage_count)
  - GET `/api/analytics/top-crafts`: Top 10 items les plus craftés (recipe_count)
  - GET `/api/analytics/by-job`: Statistiques par métier (recipe_count par catégorie)
  - GET `/api/analytics/level-distribution`: Distribution items/recipes par tranche de 10 niveaux
  - GET `/api/analytics/rarity-distribution`: Répartition items par rareté (0-7)
  - GET `/api/analytics/complex-crafts`: Top 10 crafts les plus complexes (ingredient_count)
  - Toutes les routes avec lookup JobItem first, Item fallback
- ✅ **Frontend Component**:
  - AnalyticsService: 6 méthodes avec interfaces TypeScript typées
  - AnalyticsDashboardComponent: 4 KPIs + 6 sections de visualisation
  - KPIs: Total items, recipes, resources, job_items avec gradient cards
  - Sections: Top resources, top crafts, complex crafts, rarity grid, job grid, level bars
  - UI moderne: Gradients, hover effects, responsive design
  - Navigation: Route /analytics avec icône 📊
- ✅ **Build Production**: Nouveau chunk analytics-dashboard (19.96kB)
- ✅ **Integration**: Blueprint analytics enregistré dans `__init__.py` avec url_prefix="/api/analytics"

**Build Status:**

- Total initial: 316.64kB (vs 317.88kB avant)
- Lazy chunks: +2 nouveaux (harvest-optimizer 19.49kB, analytics-dashboard 19.96kB)
- ⚠️ 1 warning CSS (item-details 8.37kB > 8kB budget)

### ✅ PRIORITÉ 1 Complétée (8 Janvier 2026)

- ✅ **Backend Tests**: 3 endpoints testés et fonctionnels (/api/stats/overview, /api/stats/global, /api/imports/batches)
- ✅ **Build Production**: Angular build réussi, dist/ généré (309kB initial, lazy chunks optimisés)
- ✅ **Budgets CSS**: Ajustés à 16kB max pour anyComponentStyle
- ⚠️ 1 warning CSS restant (item-details: 8.37kB > 8kB) - peut être optimisé en PRIORITÉ 3

### ✅ PRIORITÉ 2.1 Complétée (8 Janvier 2026)

- ✅ **Service CraftFavoritesService**: localStorage avec signals Angular
- ✅ **Page "Mes Crafts"**: Affichage, renommage, duplication, suppression
- ✅ **Import/Export JSON**: Sauvegarde et restauration complètes
- ✅ **Intégration Calculator**: Bouton "⭐ Sauvegarder" dans le calculateur
- ✅ **Navigation**: Lien "Mes Crafts" depuis la page métiers
- ✅ **Build Production**: Nouveau chunk my-crafts (11.77kB) généré avec succès

### ✅ PRIORITÉ 2.2 Complétée - Auto-complete & Display Fixes (8 Janvier 2026 - 23h58)

**Auto-complete:**

- ✅ **GlobalSearchService**: Service de recherche avec auto-complete et debounce
- ✅ **SearchAutocompleteComponent**: Composant réutilisable avec:
  - Auto-complétion (max 5 suggestions)
  - Navigation clavier (↑ ↓ Enter Escape)
  - Highlight des mots recherchés
  - Icônes des items
  - Loading indicator
- ✅ **SearchPageComponent**: Page de recherche globale
- ✅ **Build Production**: Nouveau chunk search-page (20.43kB) - Total: 317.88kB initial

**Display Fixes - JobItem vs Item:**

- ✅ **Bug identifié**: RecipeIngredient.item_id référence JobItem.wakfu_id (pas Item.wakfu_id)
- ✅ **Impact**: 100% des recettes affichaient "Item #xxxx" sans nom ni image
- ✅ **Solution appliquée**: Lookup JobItem d'abord, puis Item en fallback
- ✅ **Fichiers corrigés**:
  - `recipes/routes.py`: GET /api/recipes (liste), GET /api/recipes/:id (détail), by-result, by-ingredient
  - `craft_tree.py`: Tous les nœuds de l'arbre récursif
  - `stats/routes.py`: Recherche globale de recettes
- ✅ **Validation**:
  - ✓ Noms des recettes affichés ("Kwelsh Corbique" au lieu de "Item #12464")
  - ✓ Icônes affichés (icon_gfx_id correctement résolu)
  - ✓ Ingrédients avec noms ("Gésiers de Corbac" au lieu de "Item #5439")
  - ✓ Recherche fonctionnelle (trouve "Amulette du Corbac", "Fromage du Corbac", etc.)
  - ✓ Catégories de recettes avec noms/icônes

**Display Fixes - Correction complète icon_gfx_id (8 Janvier 2026 - 23h58):**

- ✅ **Backend enrichi**: icon_gfx_id ajouté partout
  - models_utils.py: Gestion robuste des dicts vides
  - recipes/routes.py: icon_gfx_id + vérification titres vides + lookup JobItem/Item
  - stats/routes.py: icon_gfx_id + lookup JobItem/Item pour recipes
  - craft_tree.py: icon_gfx_id dans tous les nœuds de l'arbre
- ✅ **Frontend STRICT icon_gfx_id**: Utilisation exclusive (pas de fallback)
  - recipe.model.ts: Interface Recipe avec icon_gfx_id
  - craft-recipes-list: Images des recettes par catégorie (64x64px) + méthode getItemIconUrl()
  - craft-recipe-detail: Ingrédients et résultats avec gardes @if
  - craft-calculator: Materials avec garde conditionnelle
  - craft-tree-node: Tous les nœuds avec garde conditionnelle
  - search-page: Items, recipes, resources avec icon_gfx_id strict
  - search-autocomplete: Suggestions avec double garde (@if showIcons && icon_gfx_id)
  - my-crafts: Ajout de recipeIconGfxId dans SavedCraftList
- ✅ **Migration Angular moderne**:
  - Tous les `*ngIf` remplacés par `@if` (syntaxe control flow Angular 17+)
  - 8 composants craft/harvest/jobs migrés
  - Prêt pour futures migrations Angular
- ✅ **Correction erreurs TypeScript**:
  - Toutes les images avec gardes conditionnelles `@if (icon_gfx_id)`
  - 0 erreurs de compilation
  - Warning CSS line-clamp corrigé (ajout standard property)
  - craft-calculator: MaterialSummary avec icônes
- ✅ **Header navigation**: Liens "Recherche" et "Mes Crafts" ajoutés
- ⏸️ **Tests utilisateur**: En attente de validation complète

**Fichiers modifiés:**

- Backend (4): models_utils.py, recipes/routes.py, stats/routes.py, craft_tree.py
- Frontend (12): models, components HTML/TS, services, craft-recipes-list (+ getItemIconUrl)

---

## 🎯 TODO List - Organisation par Priorité

> **Usage:** Réfère-toi à ce document pour savoir quoi intégrer ensuite.  
> Les tâches sont organisées en 3 catégories : **🔧 FIX**, **✨ AJOUTS**, **⚡ OPTIMISATIONS**  
> Ordre de traitement : FIX → AJOUTS → OPTIMISATIONS → TESTS → DEVOPS → DOCUMENTATION

---

## 🔧 PRIORITÉ 1 - FIX & CORRECTIONS

> Corriger les bugs et problèmes existants avant d'ajouter de nouvelles features.

### Backend - Tests Endpoints Manquants

- [x] Tester endpoint `/api/stats/overview` ✅ 200 OK
- [x] Tester endpoint `/api/stats/global` ✅ 200 OK (recherche globale items/recipes/resources)
- [x] Tester endpoint `/api/imports/batches` ✅ 200 OK
- [x] Vérifier tous les endpoints retournent codes HTTP corrects ✅

### Frontend - Tests & Validation Craft

- [x] Frontend dev server démarré ✅ http://localhost:4200
- [ ] 🔴 **Tests manuels requis** (à faire via navigateur):
  - Tester craft calculator avec items variés (Pain Complet, Chapeau, Armure)
  - Tester arbre récursif avec max depth 1, 3, 5, 10
  - Tester toggle owned items (skip correct dans l'arbre)
  - Tester export materials (.txt)
  - Vérifier chargement icônes via proxy sur tous items
  - Valider navigation entre les 5 pages craft

> **Note**: Ces tests nécessitent une validation manuelle via navigateur.  
> Pour automatisation → voir PRIORITÉ 4 (Tests Playwright).

### Build & Production

- [x] `ng build --configuration production` ✅ Build réussi
- [x] Budgets CSS ajustés (anyComponentStyle: 16kB max) ✅
- [x] Validation TypeScript stricte ✅ Aucune erreur
- [ ] ⚠️ Warning CSS: item-details.component.scss (8.37kB > 8kB) - Optimisation recommandée
- [ ] Tester app buildée localement (dist/wakstuff-frontend)

---

## ✨ PRIORITÉ 2 - AJOUTS (Nouvelles Features)

> Ajouter de nouvelles fonctionnalités dans l'ordre logique d'intégration.

---

## 📋 2.1 - SYSTÈME CRAFT - Extensions

### Craft Lists Sauvegardées

- [x] Service favoris avec localStorage ✅
- [x] Sauvegarder craft lists dans localStorage ✅
- [x] Page "Mes Crafts" avec listes sauvegardées ✅
- [x] Renommer craft lists ✅
- [x] Dupliquer craft lists ✅
- [x] Partager craft lists (copier JSON) - via Export ✅
- [x] Export favoris JSON ✅
- [x] Import favoris JSON ✅

**✅ Section 2.1 COMPLÉTÉE** - Toutes les fonctionnalités de craft lists sont implémentées et fonctionnelles.

---

## 🔍 2.2 - SYSTÈME RECHERCHE - Features Avancées

### Auto-complete & UX

- [x] Auto-complete avec suggestions (max 5 résultats) ✅
- [x] Highlight query dans résultats de recherche ✅
- [x] Keyboard navigation (arrows) dans suggestions ✅
- [x] Afficher icônes dans suggestions ✅

**✅ Auto-complete COMPLET** - Service GlobalSearchService + SearchAutocompleteComponent + Page de recherche

### Filtres Avancés (En cours - 9 Janvier 2026)

- [x] **Tri items**: Tri par nom, niveau, rareté, date d'ajout ✅
  - Backend: Paramètres sort_by et sort_order dans /api/items
  - Frontend: Selects pour choisir tri et ordre (↑↓)
  - Ordre: Croissant/Décroissant pour tous les critères
- [ ] 🔄 **Tri recettes**: Tri par nom, niveau dans craft-recipes-list
- [ ] Multi-catégories avec checkboxes
- [ ] Filtre par élément (Feu, Eau, etc.)
- [ ] Filtre par métier pour recettes
- [ ] Bouton "Clear all filters" global
- [ ] Compteur de filtres actifs
- [ ] Sauvegarde filtres dans localStorage

---

## 🌾 2.3 - SYSTÈME HARVEST - Optimiseur

### Backend - Zones & Resources

- [ ] Créer endpoint `/api/harvest/zones` (liste zones avec coords)
- [ ] Créer endpoint `/api/harvest/optimize` (calcul chemins)
- [ ] Algorithme calcul chemin optimal entre zones
- [ ] Filtrage zones par niveau requis
- [ ] Groupement ressources par zone

### Frontend - Interface Optimiseur

- [ ] Page harvest optimizer avec input liste ressources
- [ ] Affichage zones suggérées triées par efficacité
- [ ] Carte interactive des zones (Leaflet ou similaire)
- [ ] Affichage niveau requis par zone
- [ ] Export itinéraire .txt
- [ ] Coloration ressources par difficulté

---

## 📊 2.4 - SYSTÈME ANALYTICS - Dashboard & Stats

### Backend - Endpoints Stats

- [ ] Endpoint `/api/analytics/top-resources` (ressources les plus demandées)
- [ ] Endpoint `/api/analytics/top-crafts` (items les plus craftés)
- [ ] Endpoint `/api/analytics/deep-trees` (arbres les plus profonds)
- [ ] Endpoint `/api/analytics/by-job` (stats par métier)

### Frontend - Visualisations

- [ ] Graphiques items par catégorie (Chart.js ou recharts)
- [ ] Graphiques items par rareté (pie chart)
- [ ] Top 10 ressources les plus demandées
- [ ] Distribution crafts par niveau métier
- [ ] Timeline imports de données
- [ ] KPIs dashboard (total items, recettes, etc.)

---

## ⚖️ 2.5 - SYSTÈME COMPARATEUR - Équipements

### Backend

- [x] Endpoint `/api/items/compare` (POST avec liste IDs) ✅
- [x] Calcul différences stats entre items ✅
- [x] Identification meilleurs/pires valeurs ✅
- [ ] Calcul stats totales si set complet
- [ ] Recommandations basées sur classe/build

### Frontend - Interface Comparateur

- [x] Service ItemCompareService ✅
- [x] Composant sélection 2-3 items ✅
- [x] Page comparaison side-by-side ✅
- [x] Highlight différences (positif vert, négatif rouge) ✅
- [x] Badge item gagnant ✅
- [x] Export comparaison .txt ✅
- [ ] Export comparaison PDF ou image
- [ ] Bouton "Remplacer par" avec suggestions
- [ ] Comparaison depuis détail d'item (bouton "Comparer avec...")

**✅ Section 2.5 PARTIELLEMENT COMPLÉTÉE** - Fonctionnalités de base opérationnelles, améliorations optionnelles en attente.

---

## ⭐ 2.6 - SYSTÈME FAVORIS - Features Backend (optionnel)

### Backend Auth

- [ ] JWT authentication
- [ ] Endpoint `/api/auth/register`
- [ ] Endpoint `/api/auth/login`
- [ ] Endpoint `/api/auth/refresh`
- [ ] Middleware protection routes
- [ ] Rate limiting API (contre abus)

### Frontend Auth

- [ ] Page login/register
- [ ] AuthService avec JWT storage
- [ ] Guards pour routes protégées
- [ ] Interceptor pour ajouter token
- [ ] Gestion refresh token
- [ ] Déconnexion automatique si token expiré

### Features Authentifiées

- [ ] Profils utilisateurs
- [ ] Bouton "Ajouter aux favoris" sur item detail
- [ ] Page "Mes Favoris" avec liste backend
- [ ] Favoris persistés backend
- [ ] Craft lists sauvegardées backend
- [ ] Synchronisation multi-device
- [ ] Builds sauvegardés
- [ ] Partage builds (liens publics)

---

## 📱 2.7 - PWA & MOBILE - Progressive Web App

### PWA Setup

- [ ] Créer manifest.json (nom, icônes, couleurs)
- [ ] Icônes PWA (192x192, 512x512)
- [ ] Service worker pour offline
- [ ] Cache API responses (CacheFirst strategy)
- [ ] Cache assets statiques
- [ ] Offline fallback page
- [ ] Bouton "Installer l'app"
- [ ] Notifications push (optionnel)

### Mobile UX

- [ ] Responsive design amélioré (tables → cards)
- [ ] Touch gestures (swipe collapse/expand)
- [ ] Menu hamburger pour mobile
- [ ] Bottom navigation (mobile)
- [ ] Optimiser tailles touch targets (min 44px)

### Dark Mode

- [ ] Toggle dark mode (header)
- [ ] Sauvegarde préférence localStorage
- [ ] Variables CSS pour couleurs
- [ ] Thème sombre pour tous composants
- [ ] Adaptation graphiques pour dark mode

---

## 🌐 2.8 - INTERNATIONALISATION - i18n

### Setup i18n

- [ ] Installer ngx-translate
- [ ] Créer fichiers de traduction (fr.json, en.json, es.json, pt.json)
- [ ] Configurer TranslateModule
- [ ] Sélecteur de langue dans header
- [ ] Sauvegarde langue dans localStorage

### Traductions

- [ ] Traduire labels UI (boutons, titres, etc.)
- [ ] Traduire messages d'erreur
- [ ] Traduire tooltips et placeholders
- [ ] Utiliser descriptions multilingues items (déjà en DB)
- [ ] Formater dates selon locale
- [ ] Formater nombres selon locale

---

## 🎨 2.9 - POLISH - Finitions UX/UI

### Animations & Transitions

- [ ] Page transitions (Angular animations)
- [ ] Fade-in pour listes
- [ ] Skeleton loaders généralisés
- [ ] Smooth scroll
- [ ] Ripple effects boutons

### Error & Empty States

- [ ] Error pages (404, 500)
- [ ] Empty states engageants (illustrations)
- [ ] Toast notifications (succès/erreur)
- [ ] Confirmation modals (supprimer favoris)
- [ ] Loading states généralisés

### Accessibility

- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Focus indicators
- [ ] Alt text images
- [ ] Contrast ratios WCAG AA

---

## ⚡ PRIORITÉ 3 - OPTIMISATIONS

> Optimiser les performances et l'UX après avoir intégré tous les modules et vérifié leur coordination.

### UX/UI - Système Craft

- [ ] Ajouter loading states (skeleton pendant getCraftTree)
- [ ] Ajouter error handling (message si item non craftable)
- [ ] Ajouter tooltips informatifs (hover → niveau + rareté)
- [ ] Ajouter animations collapse/expand (Angular animations)
- [ ] Améliorer empty states (si aucune recette)
- [ ] Couleurs par type de ressource (craft vs harvest)

### Recherche - Améliorations Performance

- [ ] Implémenter full-text search PostgreSQL (tsvector)
- [ ] Créer index GIN sur items.title et items.description
- [ ] Modifier endpoint `/api/search/global` pour utiliser full-text
- [ ] Optimiser debounce frontend
- [ ] Ajouter recherche dans effets parsés

### Performance Backend

- [ ] Setup Redis container
- [ ] Cache getCraftTree pour items populaires (TTL 1h)
- [ ] Cache icônes proxy (TTL 24h)
- [ ] Index additionnels sur colonnes filtrées (level, rarity, etc.)
- [ ] Optimiser requêtes N+1 avec eager loading
- [ ] Vue matérialisée pour stats dashboard

### Performance Frontend

- [ ] Analyser bundles (webpack-bundle-analyzer)
- [ ] Optimiser bundles si >2MB
- [ ] Lazy loading modules routes
- [ ] Virtual scrolling pour grandes listes (CDK)
- [ ] Lazy loading images (intersection observer)
- [ ] Tree-shaking imports inutilisés

### Database

- [ ] Vérifier index existants sont utilisés
- [ ] Analyser slow queries avec EXPLAIN
- [ ] Optimiser requêtes récurrentes

---

## 🧪 PRIORITÉ 4 - TESTS AUTOMATISÉS

> Ajouter les tests automatisés après avoir stabilisé les features.

### Tests Unitaires Backend (pytest)

- [ ] Tests craft_tree.py (build_craft_tree avec fixtures)
- [ ] Tests recipes/routes.py (enrichissement)
- [ ] Tests items/routes.py (filtres)
- [ ] Tests models.py (to_dict, relations)
- [ ] Tests search.py (full-text search)
- [ ] Couverture >80%

### Tests E2E Frontend (Playwright)

- [ ] Setup Playwright
- [ ] Test: Navigation /craft → jobs → recipes → detail → calculator
- [ ] Test: Craft calculator quantity change
- [ ] Test: Owned items toggle
- [ ] Test: Export materials
- [ ] Test: Search global
- [ ] Test: Filtres items
- [ ] Test: Responsive mobile

---

## 🔧 PRIORITÉ 5 - DEVOPS & PRODUCTION

> Setup CI/CD et déploiement après avoir les features et tests en place.

### CI/CD Pipeline

- [ ] GitHub Actions: Build backend
- [ ] GitHub Actions: Build frontend
- [ ] GitHub Actions: Tests backend
- [ ] GitHub Actions: Tests frontend
- [ ] GitHub Actions: Lint (flake8, eslint)
- [ ] GitHub Actions: Deploy staging
- [ ] GitHub Actions: Deploy production

### Docker Optimizations

- [ ] Multi-stage builds (réduire taille images)
- [ ] Health checks dans docker-compose
- [ ] Secrets management (dotenv, secrets)
- [ ] Logging centralisé (stdout/stderr)

### Monitoring

- [ ] Setup Prometheus (métriques backend)
- [ ] Setup Grafana (dashboards)
- [ ] Logs structurés JSON
- [ ] Alerting (CPU, RAM, errors)
- [ ] APM (Application Performance Monitoring)

### Déploiement

- [ ] Setup hébergement (Azure/AWS/Netlify)
- [ ] Configuration variables d'environnement
- [ ] Setup domaine custom
- [ ] SSL/HTTPS
- [ ] CDN pour assets statiques

---

## 📚 PRIORITÉ 6 - DOCUMENTATION

> Documenter tout après avoir stabilisé le code.

### Documentation Technique

- [ ] README.md: Guide installation complet
- [ ] ARCHITECTURE.md: Diagrammes système
- [ ] API.md: Documentation tous endpoints avec exemples
- [ ] FRONTEND_SPEC.md: Architecture frontend
- [ ] CONTRIBUTING.md: Guide contribution
- [ ] CHANGELOG.md: Historique versions

### Documentation API

- [ ] Setup Swagger/OpenAPI
- [ ] Swagger UI intégré sur /api/docs
- [ ] Documenter tous les endpoints
- [ ] Exemples requêtes/réponses
- [ ] Codes d'erreur documentés

### Screenshots & Vidéos

- [ ] Capturer les 5 pages craft
- [ ] Capturer dashboard
- [ ] Capturer items list & detail
- [ ] Capturer harvest resources
- [ ] Vidéo tutoriel: Utiliser craft calculator
- [ ] Vidéo tutoriel: Optimiser récolte

- [ ] Page harvest optimizer avec input liste ressources
- [ ] Affichage zones suggérées triées par efficacité
- [ ] Carte interactive des zones (Leaflet ou similaire)
- [ ] Affichage niveau requis par zone
- [ ] Export itinéraire .txt
- [ ] Coloration ressources par difficulté

---

## 📊 SYSTÈME ANALYTICS - Dashboard & Stats

### Backend - Endpoints Stats

- [ ] Endpoint `/api/analytics/top-resources` (ressources les plus demandées)
- [ ] Endpoint `/api/analytics/top-crafts` (items les plus craftés)
- [ ] Endpoint `/api/analytics/deep-trees` (arbres les plus profonds)

---

## 📊 RÉFÉRENCE - Accomplissements Complets

### Phase 1: Base de Données - ✅ TERMINÉ

- [x] Analyse des données JSON
- [x] Conception du schéma BDD
- [x] Création des migrations SQL
- [x] Script d'import Python
- [x] Import des données
- [x] Validation et tests
- [x] Optimisation (index, vues)

### Phase 2: Backend Flask - ✅ 90% TERMINÉ

- [x] Modèles SQLAlchemy (16 modèles)
- [x] Routes API RESTful (10+ endpoints)
- [x] Services métier (CraftCalculator, SearchService)
- [x] Enrichissement des données (recipes avec item_title)
- [x] Proxy icons avec cache
- [ ] HarvestOptimizer
- [ ] Tests unitaires (couverture >80%)

### Phase 3: Frontend Angular - ✅ 90% TERMINÉ

- [x] Services HTTP Angular (5 services)
- [x] Composants de visualisation (Dashboard, Items, Craft, Imports, Resources)
- [x] Système craft complet (5 composants)
- [x] Modèles TypeScript alignés avec backend
- [x] UX/UI améliorée (icônes via proxy, validation navigation, export)
- [x] Responsive design
- [ ] Tests e2e (0%)

### Phase 4: Fonctionnalités Avancées - ⏳ 35% EN COURS

- [x] Calculateur de craft récursif avec visualisation
- [x] Arbre de craft collapsible/expandable
- [x] Export liste de courses (.txt)
- [ ] Recherche globale full-text
- [ ] Optimiseur de récolte
- [ ] Système de favoris
- [ ] Comparateur d'équipements

### Phase 5: Documentation & Déploiement - ⏳ 40% EN COURS

- [x] Documentation technique (guides refonte)
- [ ] Documentation API (Swagger/OpenAPI)
- [ ] Guide d'installation mis à jour
- [ ] CI/CD (GitHub Actions)
- [ ] Déploiement Docker Compose
- [ ] Guide de contribution

---

**Note:** Garde une copie des JSONs bruts dans `item_raw` - très utile pour debug et améliorer le parser!

Les données backend sont complètes et le système de craft est fonctionnel! 🚀
