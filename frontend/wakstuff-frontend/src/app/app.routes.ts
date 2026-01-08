import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },

  // Dashboard
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },

  // Search
  {
    path: 'search',
    loadComponent: () =>
      import('./features/search/search-page.component').then((m) => m.SearchPageComponent),
  },

  // Imports
  {
    path: 'imports',
    loadComponent: () =>
      import('./features/imports/imports-dashboard/imports-dashboard.component').then(
        (m) => m.ImportsDashboardComponent
      ),
  },

  // Items
  {
    path: 'items',
    loadComponent: () =>
      import('./features/items/items-list/items-list.component').then((m) => m.ItemsListComponent),
  },
  {
    path: 'items/:wakfuId',
    loadComponent: () =>
      import('./features/items/item-details/item-details.component').then(
        (m) => m.ItemDetailsComponent
      ),
  },

  // Resources
  {
    path: 'resources',
    loadComponent: () =>
      import('./features/resources/resources-list/resources-list.component').then(
        (m) => m.ResourcesListComponent
      ),
  },
  {
    path: 'resources/:wakfuId',
    loadComponent: () =>
      import('./features/resources/resource-details/resource-details.component').then(
        (m) => m.ResourceDetailsComponent
      ),
  },

  // Harvest Resources
  {
    path: 'harvest',
    loadComponent: () =>
      import('./features/harvest/harvest-resources.component').then(
        (m) => m.HarvestResourcesComponent
      ),
  },

  // Harvest Optimizer
  {
    path: 'harvest-optimizer',
    loadComponent: () =>
      import('./features/harvest-optimizer/harvest-optimizer.component').then(
        (m) => m.HarvestOptimizerComponent
      ),
  },

  // Analytics Dashboard
  {
    path: 'analytics',
    loadComponent: () =>
      import('./features/analytics-dashboard/analytics-dashboard.component').then(
        (m) => m.AnalyticsDashboardComponent
      ),
  },

  // Crafting
  {
    path: 'craft',
    loadComponent: () =>
      import('./features/craft/craft-jobs/craft-jobs.component').then((m) => m.CraftJobsComponent),
  },
  {
    path: 'craft/job/:categoryId',
    loadComponent: () =>
      import('./features/craft/craft-recipes-list/craft-recipes-list.component').then(
        (m) => m.CraftRecipesListComponent
      ),
  },
  {
    path: 'craft/recipe/:wakfuId',
    loadComponent: () =>
      import('./features/craft/craft-recipe-detail/craft-recipe-detail.component').then(
        (m) => m.CraftRecipeDetailComponent
      ),
  },
  {
    path: 'craft/calculator/:itemId',
    loadComponent: () =>
      import('./features/craft/craft-calculator/craft-calculator.component').then(
        (m) => m.CraftCalculatorComponent
      ),
  },
  {
    path: 'craft/my-crafts',
    loadComponent: () =>
      import('./features/craft/my-crafts/my-crafts.component').then((m) => m.MyCraftsComponent),
  },
  {
    path: 'craft/:itemId',
    loadComponent: () =>
      import('./features/craft/craft-calculator/craft-calculator.component').then(
        (m) => m.CraftCalculatorComponent
      ),
  },

  // Favorites (Phase 2) - TODO
  // {
  //   path: 'favorites',
  //   loadComponent: () => import('./features/favorites/favorites.component').then(m => m.FavoritesComponent)
  // },

  // Jobs (Phase 2) - TODO
  // {
  //   path: 'jobs',
  //   loadComponent: () => import('./features/jobs/jobs-list/jobs-list.component').then(m => m.JobsListComponent)
  // },
  // {
  //   path: 'jobs/:categoryId',
  //   loadComponent: () => import('./features/jobs/job-details/job-details.component').then(m => m.JobDetailsComponent)
  // },
  // {
  //   path: 'jobs/:categoryId/xp-calculator',
  //   loadComponent: () => import('./features/jobs/xp-calculator/xp-calculator.component').then(m => m.XpCalculatorComponent)
  // },

  // Encyclopedia (Phase 3) - TODO
  // {
  //   path: 'encyclopedia',
  //   loadComponent: () => import('./features/encyclopedia/encyclopedia.component').then(m => m.EncyclopediaComponent)
  // },

  // Comparator (Phase 3) - TODO
  // {
  //   path: 'comparator',
  //   loadComponent: () => import('./features/comparator/comparator.component').then(m => m.ComparatorComponent)
  // },

  // Harvest Zones (Phase 3) - TODO
  // {
  //   path: 'harvest-zones',
  //   loadComponent: () => import('./features/harvest-zones/harvest-zones.component').then(m => m.HarvestZonesComponent)
  // },

  // Profile (Phase 3) - TODO
  // {
  //   path: 'profile',
  //   loadComponent: () => import('./features/profile/profile.component').then(m => m.ProfileComponent)
  // },

  // Catch-all
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
