import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { HarvestResourcesService, HarvestResourcesResponse } from '../services/harvest-resources.service';

export const harvestResourcesResolver: ResolveFn<HarvestResourcesResponse> = () => {
  const harvestResourcesService = inject(HarvestResourcesService);
  return harvestResourcesService.getHarvestResources();
};
