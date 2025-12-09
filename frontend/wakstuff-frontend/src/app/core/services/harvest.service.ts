import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { HarvestResource, HarvestResourcesResponse } from '../models/harvest.model';
import { environment } from '../config';

export interface HarvestResourceFilters {
  skill_id?: number;
  level_min?: number;
  level_max?: number;
  search?: string;
  page?: number;
  per_page?: number;
}

@Injectable({
  providedIn: 'root',
})
export class HarvestService {
  private readonly apiUrl = `${environment.apiUrl}/harvest`;

  constructor(private http: HttpClient) {}

  getHarvestResources(
    filters: HarvestResourceFilters = {}
  ): Observable<{ resources: HarvestResource[]; total: number }> {
    let params = new HttpParams();

    // Forcer per_page à 500 pour récupérer toutes les ressources (max 452)
    const filtersWithDefaults = {
      ...filters,
      per_page: filters.per_page || 500,
    };

    Object.keys(filtersWithDefaults).forEach((key) => {
      const value = filtersWithDefaults[key as keyof HarvestResourceFilters];
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, value.toString());
      }
    });

    return this.http.get<HarvestResourcesResponse>(`${this.apiUrl}/resources`, { params }).pipe(
      map((response) => ({
        resources: response.harvest_resources,
        total: response.total,
      }))
    );
  }
}
