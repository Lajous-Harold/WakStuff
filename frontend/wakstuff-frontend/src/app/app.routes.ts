import { Routes } from '@angular/router';
import { ItemsList } from './features/items/items-list/items-list';
import { ImportsDashboard } from './features/imports/imports-dashboard/imports-dashboard';
import { itemsResolver } from './core/resolvers/items.resolver';
import { importsResolver } from './core/resolvers/imports.resolver';

export const routes: Routes = [
  { path: '', redirectTo: 'items', pathMatch: 'full' },

  {
    path: 'items',
    component: ItemsList,
    resolve: {
      items: itemsResolver,
    },
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
