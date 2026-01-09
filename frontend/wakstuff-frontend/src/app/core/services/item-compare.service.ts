import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config';

export interface CompareRequest {
  item_ids: number[];
}

export interface CompareStat {
  action_id: number;
  values: (number | null)[];
}

export interface CompareResponse {
  items: Array<{
    wakfu_id: number;
    title: string;
    level: number;
    rarity: number;
    icon_gfx_id: number;
    equipment_type?: string;
  }>;
  stats: { [statName: string]: CompareStat };
}

@Injectable({
  providedIn: 'root',
})
export class ItemCompareService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${API_BASE_URL}/items`;

  /**
   * Compare 2-3 items et retourne les différences de stats
   */
  compareItems(itemIds: number[]): Observable<CompareResponse> {
    return this.http.post<CompareResponse>(`${this.apiUrl}/compare`, {
      item_ids: itemIds,
    });
  }

  /**
   * Formatte une valeur de stat pour affichage
   */
  formatStatValue(value: number | null): string {
    if (value === null || value === undefined) {
      return '-';
    }
    return value > 0 ? `+${value}` : `${value}`;
  }

  /**
   * Détermine la classe CSS pour colorer une stat
   */
  getStatColorClass(values: (number | null)[], index: number): string {
    const numericValues = values.filter((v): v is number => v !== null);
    if (numericValues.length === 0) return 'neutral';

    const maxValue = Math.max(...numericValues);
    const minValue = Math.min(...numericValues);
    const currentValue = values[index];

    if (currentValue === null) return 'neutral';
    if (currentValue === maxValue && maxValue !== minValue) return 'best';
    if (currentValue === minValue && maxValue !== minValue) return 'worst';
    return 'neutral';
  }
}
