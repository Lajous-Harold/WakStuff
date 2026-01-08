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

export interface HarvestZone {
  id: number;
  name: string;
  level_range: [number, number];
  coordinates: { x: number; y: number };
  skill_ids: number[];
  resource_ids: number[];
  description?: string;
}

export interface HarvestZonesResponse {
  zones: HarvestZone[];
  total: number;
}

export interface OptimizeRequest {
  resource_ids: number[];
  player_level: number;
  max_zones?: number;
}

export interface RecommendedZone {
  zone: HarvestZone;
  efficiency: number;
  matched_resources: number[];
  distance_to_next?: number;
}

export interface OptimizeResponse {
  recommended_zones: RecommendedZone[];
  total_distance: number;
  itinerary: string;
  resources_covered: number;
  resources_requested: number;
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

  getZones(filters?: {
    level_min?: number;
    level_max?: number;
    skill_id?: number;
    resource_ids?: number[];
  }): Observable<HarvestZonesResponse> {
    let params = new HttpParams();

    if (filters?.level_min) {
      params = params.set('level_min', filters.level_min.toString());
    }
    if (filters?.level_max) {
      params = params.set('level_max', filters.level_max.toString());
    }
    if (filters?.skill_id) {
      params = params.set('skill_id', filters.skill_id.toString());
    }
    if (filters?.resource_ids && filters.resource_ids.length > 0) {
      params = params.set('resource_ids', filters.resource_ids.join(','));
    }

    return this.http.get<HarvestZonesResponse>(`${this.apiUrl}/zones`, { params });
  }

  optimizeRoute(request: OptimizeRequest): Observable<OptimizeResponse> {
    return this.http.post<OptimizeResponse>(`${this.apiUrl}/optimize`, request);
  }
}
