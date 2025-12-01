import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../config';

export interface HarvestResource {
  item_id: number;
  name: string;
  level: number | null;
  rarity: string | null;
  icon_gfx_id: number | null;
  quantity_min: number;
  quantity_max: number;
  drop_rate: number;
  list_id: number | null;
}

export interface HarvestResourcesResponse {
  total: number;
  resources: HarvestResource[];
}

@Injectable({
  providedIn: 'root',
})
export class HarvestResourcesService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/api/wakfu/harvest-resources`;

  getHarvestResources(): Observable<HarvestResourcesResponse> {
    return this.http.get<HarvestResourcesResponse>(this.apiUrl);
  }
}
