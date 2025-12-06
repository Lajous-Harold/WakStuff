import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Item, ItemDetail, ItemsListResponse } from '../models';
import { environment } from '../config';

export interface ItemFilters {
  search?: string;
  item_type_id?: number;
  equipment_type_id?: number | string; // Peut être un ID (number) ou une catégorie groupée (string)
  rarity?: number;
  level_min?: number;
  level_max?: number;
  page?: number;
  per_page?: number;
}

@Injectable({
  providedIn: 'root',
})
export class ItemsService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getItems(filters: ItemFilters = {}): Observable<ItemsListResponse> {
    let params = new HttpParams();

    Object.keys(filters).forEach((key) => {
      const value = filters[key as keyof ItemFilters];
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, value.toString());
      }
    });

    return this.http.get<ItemsListResponse>(`${this.apiUrl}/items`, { params });
  }

  getItemDetail(wakfuId: number): Observable<{ item: ItemDetail }> {
    return this.http.get<{ item: ItemDetail }>(`${this.apiUrl}/items/${wakfuId}`);
  }

  getItemTypes(): Observable<any> {
    return this.http.get(`${this.apiUrl}/items/types`);
  }

  getEquipmentTypes(grouped: boolean = true): Observable<any> {
    const params = new HttpParams().set('grouped', grouped.toString());
    return this.http.get(`${this.apiUrl}/items/equipment-types`, { params });
  }
}
