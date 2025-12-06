# TODO - WakStuff

## 📚 Documentation Disponible

**Avant de commencer une tâche, consultez la documentation de refonte :**

- **[INDEX.md](./INDEX.md)** - Guide de navigation et vue d'ensemble
- **[SYNTHESE.md](./SYNTHESE.md)** - Synthèse visuelle de l'avancement
- **[REFONTE_PLAN.md](./REFONTE_PLAN.md)** - Plan détaillé étape par étape
- **[ANALYSE_JSON.md](./ANALYSE_JSON.md)** - Détails des données JSON
- **[SCHEMA_BDD.md](./SCHEMA_BDD.md)** - Schéma de base de données

---

## 🎯 Phase Actuelle : FRONTEND FINALIZATION (Phase 3)

### 📊 Progression : [█████████████████-] 85%

### ✅ Complété

- [x] Backend Flask - 75% (routes principales OK)
- [x] Services Angular - 100% (Items, Recipes, Imports, WakfuData)
- [x] Composants principaux - 100% (Dashboard, Items, Craft, Imports, Resources)
- [x] Résolution de 64 erreurs de compilation TypeScript
- [x] Alignement des modèles frontend/backend
- [x] Création du blueprint stats avec 3 endpoints

### 🔜 En cours (Prochaines 48h)

- [ ] **Tests de compilation Angular** (Priorité 1)

  - [ ] Vérifier que les 64 erreurs sont résolues
  - [ ] Test `ng build --configuration production`
  - [ ] Validation TypeScript stricte

- [ ] **Tests des endpoints backend** (Priorité 1)

  - [ ] Test `/api/stats/overview`
  - [ ] Test `/api/search/global`
  - [ ] Test `/api/imports/recent`
  - [ ] Test `/api/recipes/craft-tree/<id>`

- [ ] **Documentation finale** (Priorité 2)
  - [x] Mise à jour TODO.md
  - [ ] Mise à jour FRONTEND_SPEC.md
  - [ ] Mise à jour BACKEND_ENDPOINTS_TODO.md
  - [ ] Capture d'écran des pages

---

## 📅 Roadmap Détaillée

### Phase 1: Base de Données (2-3 jours) - TERMINÉ

**Progression : 100%**

- [x] Analyse des données JSON
- [x] Conception du schéma BDD
- [x] Création des migrations SQL
- [x] Script d'import Python
- [x] Import des données
- [x] Validation et tests
- [x] Optimisation (index, vues)

### Phase 2: Backend Flask (4-5 jours) - EN COURS

**Progression : 75%**

- [x] Modèles SQLAlchemy (16 modèles)
- [x] Routes API RESTful
  - [x] `/api/items` (GET, filters)
  - [x] `/api/items/<wakfu_id>` (GET details)
  - [x] `/api/recipes` (GET, filters)
  - [x] `/api/recipes/<wakfu_id>` (GET details)
  - [x] `/api/recipes/craft-tree/<wakfu_id>` (GET tree)
  - [x] `/api/resources` (GET, filters)
  - [x] `/api/stats/overview` (GET stats)
  - [x] `/api/search/global` (GET search)
  - [x] `/api/imports/recent` (GET imports)
  - [x] `/api/imports/import-all` (POST)
- [ ] Services métier
  - [x] CraftCalculator (build_craft_tree)
  - [ ] SearchService (global search basique créé)
  - [ ] HarvestOptimizer
- [ ] Tests unitaires (couverture > 80%)

### Phase 3: Frontend Angular (4-5 jours) - EN COURS

**Progression : 85%**

- [x] Services HTTP Angular
  - [x] ItemsService (getItems, getItemDetail)
  - [x] RecipesService (getRecipes, getCraftTree)
  - [x] ImportsService (importAll, getImportHistory)
  - [x] WakfuDataService (getStats)
- [x] Composants de visualisation
  - [x] Dashboard (stats, search, recent imports)
  - [x] ItemsList & ItemDetails (avec filtres)
  - [x] CraftCalculator & CraftTree (récursif)
  - [x] ImportsDashboard (avec phases)
  - [x] ResourcesList (harvest zones)
  - [x] GlobalSearch (composant)
- [x] UX/UI améliorée
- [x] Responsive design
- [ ] Tests e2e (0%)

### Phase 4: Fonctionnalités Avancées (3-4 jours) - À VENIR

**Progression : 0%**

- [ ] Calculateur de craft récursif avec visualisation
- [ ] Recherche globale full-text
- [ ] Optimiseur de récolte
- [ ] Système de favoris (optionnel)

### Phase 5: Documentation & Déploiement (1-2 jours) - À VENIR

**Progression : 40%**

- [x] Documentation technique
- [ ] Documentation API (Swagger/OpenAPI)
- [ ] Guide d'installation mis à jour
- [ ] CI/CD (GitHub Actions)
- [ ] Déploiement Docker Compose
- [ ] Guide de contribution

---

## 🎯 Tâches Prioritaires (Cette Semaine)

### Haute Priorité 🔴

1. **Vérifier compilation Angular** - Phase 3 (30min)
2. **Tester tous les endpoints** - Phase 2-3 (1-2h)
3. **Corriger dernières erreurs** - Phase 3 (1-2h)
4. **Tests e2e basiques** - Phase 3 (2-3h)

### Moyenne Priorité 🟡

5. Finaliser documentation technique - Phase 5 (2h)
6. Tests unitaires backend - Phase 2 (4-6h)
7. Optimiser performances - Phase 4 (2-3h)

### Basse Priorité 🟢

8. Améliorer UI/UX - Phase 3 (variable)
9. Ajouter tests e2e complets - Phase 3 (4-6h)
10. Setup CI/CD - Phase 5 (2-4h)

---

## 📋 Anciennes Tâches (Référence)

### Phase 1: Setup Initial ✅ TERMINÉ

- [x] Migrer la base de données
- [x] Tester la connexion API
- [x] Lancer l'import complet
- [x] Vérifier les résultats
- [x] Système de classification (35+ catégories)
- [x] Parser d'effets multilingue
- [x] Calculateur de craft récursif
- [x] Interface de test visuelle

### Phase 2: Frontend - Interface Utilisateur ✅ TERMINÉ

- [x] Composant `categories-view`
- [x] Grid de cartes avec compteurs
- [x] Navigation vers items par catégorie
- [x] Filtre par catégorie/rareté/niveau
- [x] Recherche textuelle
- [x] Badges visuels
- [x] Page détails item
- [x] Affichage des effets parsés

### Phase 3: Calculateur de Craft Frontend ✅ TERMINÉ

- [x] Service `wakfu-data.service.ts` avec endpoint craft-calculator
- [x] Composant `craft-calculator`
- [x] Recherche d'item par nom avec debounce
- [x] Affichage arbre de craft visuel (récursif)
- [x] Liste des ressources totales nécessaires
- [x] Sélecteur de quantité (1-999)
- [x] Arbre collapsible/expandable
- [x] Badges de catégorie par item

### Améliorations

- [ ] Couleurs par type de ressource
- [ ] Export liste de courses (JSON/CSV)
- [ ] Sauvegarde de favoris
- [ ] Affichage des icônes d'items

---

## Phase 4: Statistiques Dashboard ✅ TERMINÉ

### Dashboard Stats ✅

- [x] Composant `stats-dashboard`
- [x] Stats globales (items, recettes, actions, états, métiers)
- [x] Distribution par rareté avec barres de progression
- [x] Top 10 catégories avec graphiques
- [x] Navigation vers items filtrés
- [x] Pipes personnalisés (rarity-color, category-badge, level-display)
- [x] Utilities de formatage (formatNumber, calculatePercentage, formatDate)

---

## Phase 5: Corrections et Améliorations Backend

### API Backend ✅

- [x] Ajout filtres avancés sur `/api/items` (rarity, level_min, level_max, search)
- [x] Fix total filtré (query.count() au lieu du total global)
- [x] Fix classification des items (reconstruction du chemin complet avec subcategory)
- [x] Headers HTTP pour éviter 403 du CDN Ankama (User-Agent, Referer, Origin)
- [x] Gestion d'erreur pour import des jobs (non critique)

### Corrections Frontend ✅

- [x] Mise à jour interfaces TypeScript pour correspondre à l'API
- [x] Fix CategoryInfo (name au lieu de category, item_count au lieu de count)
- [x] Fix WakfuStats (structure items.total, items.by_rarity, etc.)
- [x] Fix templates HTML pour utiliser les bonnes propriétés
- [x] Suppression de getLevelRanges() qui n'existe pas dans l'API

---

## Phase 6: Recherche Avancée (À FAIRE)

### Filtres

- [ ] Multi-catégories avec checkboxes
- [ ] Range slider pour niveau
- [ ] Filtre par élément
- [ ] Filtre par métier (recettes)

### Recherche

- [x] Recherche textuelle de base (search parameter)
- [ ] Full-text search PostgreSQL
- [ ] Recherche dans descriptions
- [ ] Recherche dans effets
- [ ] Auto-complete avec suggestions

### Tris

- [ ] Par nom (A-Z)
- [x] Par niveau (croissant par défaut)
- [ ] Par rareté
- [ ] Par date d'ajout

---

## Phase 7: Analytics & Comparateur (À FAIRE)

### Analytics Craft

- [ ] Ressources les plus utilisées
- [ ] Items les plus craftés
- [ ] Arbre de dépendances le plus profond
- [ ] Crafts par niveau de métier

### Comparateur

- [ ] Sélection de 2-3 items
- [ ] Comparaison side-by-side
- [ ] Highlight des différences
- [ ] Recommandations

---

## Phase 6: Fonctionnalités Avancées

### Build Optimizer

- [ ] Sélection de classe
- [ ] Objectif (DPS/Tank/Support)
- [ ] Suggestion d'équipement optimal
- [ ] Calcul stats totales du build

### Wiki Interactif

- [ ] Pages dédiées par item
- [ ] Historique des modifications
- [ ] Liens vers ressources externes
- [ ] Guides de farming

---

## Optimisations Techniques

### Performance

- [ ] Cache Redis pour items/icônes fréquents
- [ ] Pagination serveur (améliorer `/api/items`)
- [ ] Lazy loading images
- [ ] Service Worker pour offline
- [ ] Compression des réponses API

### DevOps

- [ ] CI/CD GitHub Actions
- [ ] Tests unitaires backend (pytest)
- [ ] Tests E2E frontend (Playwright/Cypress)
- [ ] Docker multi-stage builds optimisés
- [ ] Health checks pour containers

### Database

- [ ] Index sur colonnes fréquemment filtrées
- [ ] Vue matérialisée pour stats
- [ ] Backup automatique quotidien
- [ ] Monitoring (Prometheus/Grafana)

---

## Mobile & PWA

- [ ] Progressive Web App (manifest.json)
- [ ] Service Worker pour cache
- [ ] App installable (Add to Home Screen)
- [ ] Mode hors ligne basique
- [ ] Notifications push (nouveaux items)
- [ ] Dark mode

---

## Internationalisation (i18n)

- [ ] Support FR/EN/ES/PT dans l'interface
- [ ] Sélecteur de langue
- [ ] Utiliser descriptions multilingues des items
- [ ] Traductions des labels UI
- [ ] Format dates/nombres localisés

---

## Design & UX

- [ ] Design system cohérent (colors, spacing, typography)
- [ ] Animations de transition fluides
- [ ] Loading skeletons
- [ ] Error states conviviaux
- [ ] Empty states engageants
- [ ] Tooltips informatifs
- [ ] Responsive design complet

---

## Sécurité & Auth (optionnel)

- [ ] Authentification utilisateurs (JWT)
- [ ] Profils utilisateurs
- [ ] Listes de favoris personnelles
- [ ] Builds sauvegardés
- [ ] Partage de builds (liens publics)
- [ ] Rate limiting API (contre abus)

---

## Quick Wins (Faciles & Impactants)

### Cette semaine

1. **Badges de catégorie** sur items (30min) ⭐
2. **Affichage effets parsés** au lieu de JSON (1h) ⭐
3. **Filtre par rareté** avec couleurs (1h) ⭐
4. **Page catégories** simple grid (2h) ⭐

### Semaine prochaine

1. **MVP calculateur de craft** frontend (1 jour) ⭐⭐
2. **Page détails item** améliorée (2h) ⭐
3. **Recherche full-text** simple (3h) ⭐

---

## Ordre Recommandé

### Sprint 1 (Cette semaine)

1. Quick wins (badges, filtres, catégories)
2. Améliorer page détails item

### Sprint 2 (Semaine prochaine)

1. MVP calculateur de craft
2. Recherche avancée basique

### Sprint 3 (Mois suivant)

1. Analytics & dashboard
2. Comparateur d'items
3. Optimisations performance

---

**Priorité**: Se concentrer sur les Quick Wins et le calculateur de craft frontend en priorité.

Les données backend sont déjà complètes et fonctionnelles! 🚀

- [ ] Recherche dans les noms
- [ ] Recherche dans les descriptions
- [ ] Recherche dans les effets
- [ ] Suggestions auto-complete

### 4.3 Tris

- [ ] Par nom
- [ ] Par niveau
- [ ] Par rareté
- [ ] Par date d'ajout

## 📊 Phase 5: Statistiques & Analytics (LONG TERME)

### 5.1 Dashboard Général

- [ ] Graphique items par catégorie
- [ ] Graphique items par rareté
- [ ] Graphique items par niveau
- [ ] Top 10 items les plus rares

### 5.2 Analytics de Recettes

- [ ] Ressources les plus demandées
- [ ] Items les plus craftés
- [ ] Arbre de dépendances le plus profond
- [ ] Items craftables par niveau de métier

### 5.3 Comparateur d'Équipements

- [ ] Sélectionner 2-3 items
- [ ] Comparaison side-by-side des stats
- [ ] Highlight des différences
- [ ] Recommandation basée sur build

## 🎮 Phase 6: Fonctionnalités Avancées (LONG TERME)

### 6.1 Build Optimizer

- [ ] Sélection de classe
- [ ] Sélection de niveau
- [ ] Objectif (DPS, Tank, Support)
- [ ] Suggestion d'équipement optimal
- [ ] Calcul des stats totales

### 6.2 Market Analyzer

- [ ] Si API des prix disponible
- [ ] Tendances de prix
- [ ] Crafts les plus rentables
- [ ] Alertes de prix

### 6.3 Wiki Interactif

- [ ] Pages dédiées par item
- [ ] Historique des versions
- [ ] Notes communautaires
- [ ] Guides de farming

### 6.4 API GraphQL

- [ ] Schéma GraphQL complet
- [ ] Requêtes complexes optimisées
- [ ] Subscriptions pour updates temps réel
- [ ] Playground GraphiQL

## 🚀 Optimisations Techniques

### Performance

- [ ] Cache Redis pour items fréquents
- [ ] Pagination améliorée
- [ ] Lazy loading des images
- [ ] Service worker pour offline

### DevOps

- [ ] CI/CD avec GitHub Actions
- [ ] Tests automatisés backend
- [ ] Tests E2E frontend
- [ ] Docker compose pour dev

### Database

- [ ] Index additionnels si slow queries
- [ ] Vue matérialisée pour stats
- [ ] Backup automatique
- [ ] Monitoring Prometheus

## 📱 Mobile & PWA

- [ ] Progressive Web App
- [ ] App installable
- [ ] Mode hors ligne
- [ ] Notifications push
- [ ] Dark mode

## 🌐 i18n - Internationalisation

- [ ] Support FR/EN/ES/PT
- [ ] Utiliser les descriptions multilingues
- [ ] Sélecteur de langue
- [ ] Traductions interface

## 🎨 Design & UX

- [ ] Design system cohérent
- [ ] Animations fluides
- [ ] Loading states
- [ ] Error states friendly
- [ ] Empty states engageants
- [ ] Tooltips informatifs

## 🔐 Sécurité & Auth (si nécessaire)

- [ ] Authentification utilisateurs
- [ ] Favoris personnels
- [ ] Listes de craft sauvegardées
- [ ] Partage de builds
- [ ] Rate limiting API

## 📝 Documentation

- [ ] JSDoc pour tous les services
- [ ] Storybook pour composants
- [ ] Guide de contribution
- [ ] Exemples d'usage API
- [ ] Vidéos tutoriels

## 🎯 Quick Wins (Faciles et Impactants)

1. **Badges de catégorie** sur les items (30min)

   - Petit badge coloré avec icône

2. **Affichage des effets parsés** (1h)

   - Remplacer les JSON bruts par texte lisible

3. **Filtre par rareté** avec couleurs (1h)

   - Utiliser les couleurs de `WAKFU_RARITIES`

4. **Page catégories** simple (2h)

   - Grid de cartes avec compteurs

5. **Bouton "Voir recette"** (30min)
   - Sur page détails, si craftable

## 🎪 MVP Calculateur de Craft (1 journée)

Fonctionnalités minimales:

- [x] Backend déjà prêt
- [ ] Service Angular pour appeler `/craft-calculator/:id`
- [ ] Composant simple avec arbre texte
- [ ] Affichage de la liste de ressources
- [ ] Styling basique

Résultat:

```typescript
// craft-calculator.service.ts
getCraftTree(itemId: number): Observable<CraftTree> {
  return this.http.get<CraftTree>(
    `${this.apiUrl}/wakfu/craft-calculator/${itemId}`
  );
}

// craft-calculator.component.ts
loadCraft(itemId: number) {
  this.craftService.getCraftTree(itemId).subscribe(
    tree => this.craftTree = tree
  );
}
```

---

## 🎯 Ordre Recommandé

### Cette semaine:

1. ✅ Setup & import initial
2. Page catégories
3. Améliorer liste items (badges)

### Semaine prochaine:

1. MVP calculateur de craft
2. Affichage effets parsés
3. Filtres avancés

### Mois prochain:

1. Recherche full-text
2. Comparateur d'équipements
3. Dashboard stats

---

**Note:** Garde une copie des JSONs bruts dans `item_raw` - très utile pour debug et améliorer le parser!

Bon développement! 🚀
