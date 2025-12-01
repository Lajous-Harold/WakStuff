import { Routes } from '@angular/router';
import { ItemsList } from './features/items/items-list/items-list';
import { ItemDetails } from './features/items/item-details/item-details';
import { ImportsDashboard } from './features/imports/imports-dashboard/imports-dashboard';
import { CraftCalculator } from './features/craft-calculator/craft-calculator';
import { CategoriesView } from './features/categories/categories-view';
import { StatsDashboard } from './features/stats/stats-dashboard';
import { HarvestResourcesComponent } from './features/harvest-resources/harvest-resources-list/harvest-resources';
import { importsResolver } from './core/resolvers/imports.resolver';
import { categoriesResolver } from './core/resolvers/categories.resolver';
import { harvestResourcesResolver } from './core/resolvers/harvest-resources.resolver';

export const routes: Routes = [
  { path: '', redirectTo: 'items', pathMatch: 'full' },

  {
    path: 'items',
    component: ItemsList,
  },

  {
    path: 'items/:id',
    component: ItemDetails,
  },

  {
    path: 'categories',
    component: CategoriesView,
  },

  {
    path: 'harvest-resources',
    component: HarvestResourcesComponent,
  },

  {
    path: 'stats',
    component: StatsDashboard,
  },

  {
    path: 'craft-calculator',
    component: CraftCalculator,
  },

  {
    path: 'imports',
    component: ImportsDashboard,
    resolve: {
      batches: importsResolver,
    },
  },

  { path: '**', redirectTo: 'items' },
];
