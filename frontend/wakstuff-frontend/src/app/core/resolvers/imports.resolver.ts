import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { ImportsService, ImportBatchDto } from '../services/imports.service';
import { catchError, of, tap, map } from 'rxjs';

export const importsResolver: ResolveFn<ImportBatchDto[]> = () => {
  const service = inject(ImportsService);

  return service.list().pipe(
    map((batches) => {
      const validBatches = Array.isArray(batches) ? batches : [];
      return validBatches;
    }),
    catchError((err) => {
      return of([]);
    })
  );
};
