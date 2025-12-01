# TODO - WakStuff

## Phase 1: Setup Initial ✅ TERMINÉ

- [x] Migrer la base de données
- [x] Tester la connexion API
- [x] Lancer l'import complet
- [x] Vérifier les résultats
- [x] Système de classification (35+ catégories)
- [x] Parser d'effets multilingue
- [x] Calculateur de craft récursif
- [x] Interface de test visuelle

---

## Phase 2: Frontend - Interface Utilisateur ✅ TERMINÉ

### Vue des Catégories ✅

- [x] Composant `categories-view`
- [x] Grid de cartes avec compteurs
- [x] Navigation vers items par catégorie
- [x] Organisation par groupes parents
- [x] Badges colorés par type

### Page Items Améliorée ✅

- [x] Filtre par catégorie (dropdown)
- [x] Filtre par rareté avec couleurs
- [x] Filtre par niveau (min/max)
- [x] Recherche textuelle
- [x] Badges visuels (catégorie, niveau, rareté)
- [x] Affichage des effets parsés lisibles
- [x] Pagination serveur-side

### Page Détails Item ✅

- [x] Layout amélioré avec sections
- [x] Affichage catégorie et badges
- [x] Effets parsés en texte lisible
- [x] Affichage de la recette si craftable
- [x] Bouton vers calculateur de craft
- [x] Navigation entre items

---

## Phase 3: Calculateur de Craft Frontend ✅ TERMINÉ

### MVP ✅

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
