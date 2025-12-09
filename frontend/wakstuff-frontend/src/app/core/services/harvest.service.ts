import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
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

  getHarvestResources(filters: HarvestResourceFilters = {}): Observable<HarvestResourcesResponse> {
    let params = new HttpParams();

    Object.keys(filters).forEach((key) => {
      const value = filters[key as keyof HarvestResourceFilters];
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, value.toString());
      }
    });

    return this.http.get<HarvestResourcesResponse>(`${this.apiUrl}/resources`, { params });
  }
}
