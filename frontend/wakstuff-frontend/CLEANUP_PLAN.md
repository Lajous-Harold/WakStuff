# Nettoyage Frontend - Plan d'Action

## 📋 Fichiers/Dossiers à Supprimer

### ❌ Dossiers Complets à Supprimer

```powershell
# Exécuter depuis: frontend/wakstuff-frontend/src/app

# 1. harvest-resources (obsolète - remplacé par resources)
Remove-Item -Recurse -Force features/harvest-resources

# 2. harvest (ancien dossier - déjà supprimé)
# Remove-Item -Recurse -Force features/harvest  # DÉJÀ FAIT
```

### ❌ Fichiers Individuels à Supprimer

```powershell
# Exécuter depuis: frontend/wakstuff-frontend/src/app/core/services

# 1. harvest-resources.service.ts (remplacé par resources.service.ts)
Remove-Item core/services/harvest-resources.service.ts

# 2. wakfu-data.service.ts (non utilisé, architecture obsolète)
Remove-Item core/services/wakfu-data.service.ts
```

---

## ✅ Fichiers/Dossiers à Conserver et Adapter

### 📁 features/craft/

**Statut**: ✅ CONSERVER - Base solide pour page Crafting
**Fichiers**:

- `craft-calculator.ts` - À adapter pour nouvelle spec
- `craft-calculator.html` - À mettre à jour avec @for/@if
- `craft-calculator.scss` - À conserver
- `craft-tree-node.component.ts` - À renommer en craft-node.component.ts

**Actions**:

1. Renommer `craft-tree-node.component.ts` → `craft-node.component.ts`
2. Remplacer `*ngFor/*ngIf` par `@for/@if`
3. Migrer vers signals() au lieu de BehaviorSubject
4. Ajouter support craft-tree récursif

---

### 📁 features/imports/

**Statut**: ✅ CONSERVER - Base déjà présente
**Structure actuelle**: `imports-dashboard/`

**Actions**:

1. Renommer `imports-dashboard.component.ts` → `imports.component.ts`
2. Vérifier utilisation `@for/@if` (pas `*ngFor/*ngIf`)
3. Ajouter les 4 boutons selon spec:
   - Import complet (conserver données)
   - Import complet (vider avant)
   - Vider base de données
   - Afficher stats

---

### 📁 features/items/

**Statut**: ✅ CONSERVER - Structure OK
**Structure actuelle**:

- `items-list/`
- `item-details/`

**Actions**:

1. Renommer `items-list` → `items-list.component.ts/html/scss` (flatten)
2. Renommer `item-details` → `item-detail.component.ts/html/scss` (flatten)
3. Mettre à jour avec `@for/@if`
4. Ajouter bouton "Ajouter aux favoris" ⭐
5. Utiliser signals() pour filtres

---

### 📁 core/services/

**Statut**: ✅ CONSERVER - Adapter selon spec
**Fichiers existants**:

- `items.service.ts` ✅
- `recipes.service.ts` ✅
- `imports.service.ts` ✅
- ~~`harvest-resources.service.ts`~~ ❌ SUPPRIMER
- ~~`wakfu-data.service.ts`~~ ❌ SUPPRIMER

**À CRÉER**:

- `resources.service.ts` (remplace harvest-resources)
- `stats.service.ts` (pour dashboard)
- `favorites.service.ts` (gestion favoris localStorage)
- `jobs.service.ts` (pour page jobs/métiers)
- `encyclopedia.service.ts` (pour encyclopédie - Phase 3)

---

### 📁 shared/

**Statut**: ✅ CONSERVER - Excellente base
**Structure actuelle**:

- `pipes/` ✅ (rarity-color, rarity-label, level-display, category-\*)
- `utils/` ✅ (wakfu-text.utils, formatting.utils)

**À AJOUTER**:

- `components/loading-spinner/`
- `components/error-message/`
- `components/pagination/`
- `components/search-bar/`
- `components/stat-card/`

---

## 🛠️ Script Complet de Nettoyage

```powershell
# Nettoyage Frontend WakStuff
# Exécuter depuis: C:\Users\Harold\Documents\GitHub\WakStuff\frontend\wakstuff-frontend

Write-Host "🧹 Nettoyage du frontend WakStuff..." -ForegroundColor Cyan

# 1. Supprimer dossiers obsolètes
Write-Host "❌ Suppression de features/harvest-resources..." -ForegroundColor Yellow
if (Test-Path "src/app/features/harvest-resources") {
    Remove-Item -Recurse -Force "src/app/features/harvest-resources"
    Write-Host "✅ features/harvest-resources supprimé" -ForegroundColor Green
} else {
    Write-Host "⚠️ features/harvest-resources déjà supprimé" -ForegroundColor Gray
}

# 2. Supprimer services obsolètes
Write-Host "❌ Suppression de harvest-resources.service.ts..." -ForegroundColor Yellow
if (Test-Path "src/app/core/services/harvest-resources.service.ts") {
    Remove-Item "src/app/core/services/harvest-resources.service.ts"
    Write-Host "✅ harvest-resources.service.ts supprimé" -ForegroundColor Green
} else {
    Write-Host "⚠️ harvest-resources.service.ts déjà supprimé" -ForegroundColor Gray
}

Write-Host "❌ Suppression de wakfu-data.service.ts..." -ForegroundColor Yellow
if (Test-Path "src/app/core/services/wakfu-data.service.ts") {
    Remove-Item "src/app/core/services/wakfu-data.service.ts"
    Write-Host "✅ wakfu-data.service.ts supprimé" -ForegroundColor Green
} else {
    Write-Host "⚠️ wakfu-data.service.ts déjà supprimé" -ForegroundColor Gray
}

# 3. Vérifier les imports dans app.routes.ts
Write-Host "🔍 Vérification de app.routes.ts..." -ForegroundColor Yellow
$routesContent = Get-Content "src/app/app.routes.ts" -Raw
if ($routesContent -match "harvest-resources|HarvestResources") {
    Write-Host "⚠️ ATTENTION: app.routes.ts contient encore des références à harvest-resources" -ForegroundColor Red
    Write-Host "   → Mettre à jour manuellement app.routes.ts" -ForegroundColor Red
} else {
    Write-Host "✅ app.routes.ts propre" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Nettoyage terminé !" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "  1. Créer resources.service.ts" -ForegroundColor White
Write-Host "  2. Créer favorites.service.ts" -ForegroundColor White
Write-Host "  3. Créer stats.service.ts" -ForegroundColor White
Write-Host "  4. Créer jobs.service.ts" -ForegroundColor White
Write-Host "  5. Mettre à jour app.routes.ts avec nouvelles routes" -ForegroundColor White
Write-Host "  6. Remplacer *ngFor/*ngIf par @for/@if dans tous les templates" -ForegroundColor White
```

---

## 📦 Checklist Post-Nettoyage

### Vérifications Obligatoires

- [ ] **Aucune erreur de compilation**: `ng serve` démarre sans erreur
- [ ] **Aucune référence à harvest-resources**: Chercher avec `grep -r "harvest-resources" src/`
- [ ] **Aucune référence à wakfu-data**: Chercher avec `grep -r "wakfu-data" src/`
- [ ] **app.routes.ts propre**: Pas de routes vers composants supprimés
- [ ] **Tous les imports services OK**: Aucun import vers services supprimés

### Structure Attendue Après Nettoyage

```
src/app/
├── core/
│   ├── services/
│   │   ├── imports.service.ts ✅
│   │   ├── items.service.ts ✅
│   │   ├── recipes.service.ts ✅
│   │   ├── resources.service.ts (à créer)
│   │   ├── stats.service.ts (à créer)
│   │   ├── favorites.service.ts (à créer)
│   │   └── jobs.service.ts (à créer)
│   └── models/ (à créer)
├── features/
│   ├── craft/ ✅
│   ├── imports/ ✅
│   ├── items/ ✅
│   ├── dashboard/ (à créer)
│   ├── resources/ (à créer)
│   ├── favorites/ (à créer)
│   └── jobs/ (à créer)
└── shared/
    ├── pipes/ ✅
    ├── utils/ ✅
    └── components/ (à enrichir)
```

---

## 🚀 Commandes Post-Nettoyage

```powershell
# 1. Vérifier compilation
cd C:\Users\Harold\Documents\GitHub\WakStuff\frontend\wakstuff-frontend
ng serve

# 2. Rechercher références obsolètes
cd src
grep -r "harvest-resources" .
grep -r "wakfu-data" .
grep -r "HarvestResources" .

# 3. Vérifier aucune utilisation *ngFor/*ngIf (syntaxe obsolète)
grep -r "\*ngFor" . --include="*.html"
grep -r "\*ngIf" . --include="*.html"

# Si des résultats: les remplacer par @for/@if
```

---

## ⚠️ Points d'Attention

1. **Ne PAS supprimer** `features/craft/` - contient du code réutilisable
2. **Ne PAS supprimer** `shared/pipes/` - pipes de formatage utiles
3. **Vérifier app.routes.ts** avant de supprimer un composant
4. **Commit après chaque suppression** pour pouvoir rollback si besoin

---

## 📝 Template Commit Git

```bash
# Après nettoyage
git add -A
git commit -m "chore(frontend): clean obsolete files and services

- Remove features/harvest-resources (replaced by resources)
- Remove harvest-resources.service.ts (replaced by resources.service.ts)
- Remove wakfu-data.service.ts (unused legacy service)
- Update app.routes.ts to remove obsolete imports

Preparing for new Angular 17+ architecture with @for/@if and signals()"
```

---

**Prêt pour le nettoyage !** 🧹✨
