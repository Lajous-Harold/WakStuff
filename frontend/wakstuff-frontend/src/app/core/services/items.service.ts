import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { API_BASE_URL } from '../config';

export interface WakstuffItem {
  id: number;
  wakfu_id: number;
  name: string;
  level: number | null;
  rarity: string | null;
  type: string | null;
  category?: string | null;
  element?: string | null;
  icon_gfx_id?: number | null;
  icon_url?: string | null;
  parsed_effects?: string[] | null;
  needs_review: boolean;
}

export interface ItemsListResponse {
  items: WakstuffItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface CategoryStats {
  category: string;
  count: number;
}

export interface ItemsStats {
  total_items: number;
  by_rarity: Record<string, number>;
  by_category: CategoryStats[];
  needs_review_count: number;
}

export interface ListItemsParams {
  limit?: number;
  offset?: number;
  category?: string;
  rarity?: string;
  minLevel?: number;
  maxLevel?: number;
  search?: string;
  details?: boolean;
}

@Injectable({ providedIn: 'root' })
export class ItemsService {
  private readonly baseUrl = `${API_BASE_URL}/api/items`;

  constructor(private http: HttpClient) {}

  list(params: ListItemsParams = {}): Observable<ItemsListResponse> {
    let httpParams = new HttpParams();

    if (params.limit !== undefined) httpParams = httpParams.set('limit', params.limit.toString());
    if (params.offset !== undefined)
      httpParams = httpParams.set('offset', params.offset.toString());
    if (params.category) httpParams = httpParams.set('category', params.category);
    if (params.rarity) httpParams = httpParams.set('rarity', params.rarity);
    if (params.minLevel !== undefined)
      httpParams = httpParams.set('level_min', params.minLevel.toString());
    if (params.maxLevel !== undefined)
      httpParams = httpParams.set('level_max', params.maxLevel.toString());
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.details) httpParams = httpParams.set('details', 'true');

    return this.http.get<ItemsListResponse>(this.baseUrl, { params: httpParams });
  }

  getById(id: number, details: boolean = true): Observable<WakstuffItem> {
    const params = new HttpParams().set('details', details.toString());
    return this.http.get<WakstuffItem>(`${this.baseUrl}/${id}`, { params });
  }

  getCategories(): Observable<CategoryStats[]> {
    return this.http.get<CategoryStats[]>(`${this.baseUrl}/categories`);
  }

  getStats(): Observable<ItemsStats> {
    return this.http.get<ItemsStats>(`${this.baseUrl}/stats`);
  }
}
