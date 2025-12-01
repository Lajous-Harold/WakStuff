import { Routes } from '@angular/router';
import { ItemsList } from './features/items/items-list/items-list';
import { ItemDetails } from './features/items/item-details/item-details';
import { ImportsDashboard } from './features/imports/imports-dashboard/imports-dashboard';
import { CraftCalculator } from './features/craft-calculator/craft-calculator';
import { CategoriesView } from './features/categories/categories-view';
import { StatsDashboard } from './features/stats/stats-dashboard';
import { importsResolver } from './core/resolvers/imports.resolver';

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
