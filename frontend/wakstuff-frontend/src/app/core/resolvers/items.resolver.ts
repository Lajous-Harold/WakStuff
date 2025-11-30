import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { ItemsService, WakstuffItem } from '../services/items.service';
import { catchError, of, tap, map } from 'rxjs';

export const itemsResolver: ResolveFn<WakstuffItem[]> = () => {
  const service = inject(ItemsService);

  return service.list().pipe(
    map((items) => {
      const validItems = Array.isArray(items) ? items : [];
      return validItems;
    }),
    catchError((err) => {
      return of([]);
    }),
  );
};
