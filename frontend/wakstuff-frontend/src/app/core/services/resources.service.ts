import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Resource,
  ResourceType,
  ResourceDetail,
  ResourcesListResponse,
  CollectibleResource,
} from '../models/resource.model';
import { environment } from '../config';

export interface ResourceFilters {
  resource_type_id?: number;
  level_min?: number;
  level_max?: number;
  search?: string;
  page?: number;
  per_page?: number;
}

@Injectable({
  providedIn: 'root',
})
export class ResourcesService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getResources(filters: ResourceFilters = {}): Observable<ResourcesListResponse> {
    let params = new HttpParams();

    Object.keys(filters).forEach((key) => {
      const value = filters[key as keyof ResourceFilters];
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, value.toString());
      }
    });

    return this.http.get<ResourcesListResponse>(`${this.apiUrl}/resources`, { params });
  }

  getResourceDetail(wakfuId: number): Observable<ResourceDetail> {
    return this.http.get<ResourceDetail>(`${this.apiUrl}/resources/${wakfuId}`);
  }

  getCollectibleResources(): Observable<{ resources: CollectibleResource[] }> {
    return this.http.get<{ resources: CollectibleResource[] }>(`${this.apiUrl}/harvest/resources`);
  }

  getResourceTypes(): Observable<{ types: ResourceType[] }> {
    return this.http.get<{ types: ResourceType[] }>(`${this.apiUrl}/resources/types`);
  }
}
