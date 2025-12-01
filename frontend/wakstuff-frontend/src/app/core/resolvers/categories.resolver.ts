import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { CategoryInfo, WakfuDataService } from '../services/wakfu-data.service';

export const categoriesResolver: ResolveFn<CategoryInfo[]> = () => {
  const wakfuDataService = inject(WakfuDataService);
  return wakfuDataService.getCategories();
};
