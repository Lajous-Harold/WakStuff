import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
  element?: string | null;
  needs_review: boolean;
}

export interface ItemsListResponse {
  items: WakstuffItem[];
  total: number;
  limit: number;
  offset: number;
}

@Injectable({ providedIn: 'root' })
export class ItemsService {
  private readonly baseUrl = `${API_BASE_URL}/api/items`;

  constructor(private http: HttpClient) {}

  list(): Observable<WakstuffItem[]> {
    // limit=0 pour récupérer tous les items
    return this.http
      .get<ItemsListResponse>(`${this.baseUrl}/?limit=0`)
      .pipe(map((response) => response.items || []));
  }

  getById(id: number): Observable<WakstuffItem> {
    return this.http.get<WakstuffItem>(`${this.baseUrl}/${id}`);
  }
}
