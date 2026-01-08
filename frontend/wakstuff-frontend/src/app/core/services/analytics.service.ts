import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../config';

export interface TopResource {
  item: any;
  usage_count: number;
}

export interface TopCraft {
  item: any;
  recipe_count: number;
}

export interface JobAnalytics {
  category: any;
  recipe_count: number;
}

export interface LevelDistribution {
  level_range: string;
  count: number;
}

export interface RarityDistribution {
  rarity: number;
  name: string;
  count: number;
}

export interface ComplexCraft {
  recipe: any;
  result_name: string | null;
  ingredient_count: number;
}

@Injectable({
  providedIn: 'root',
})
export class AnalyticsService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getTopResources(limit: number = 10): Observable<{ top_resources: TopResource[]; total: number }> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<{ top_resources: TopResource[]; total: number }>(
      `${this.apiUrl}/analytics/top-resources`,
      { params }
    );
  }

  getTopCrafts(limit: number = 10): Observable<{ top_crafts: TopCraft[]; total: number }> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<{ top_crafts: TopCraft[]; total: number }>(
      `${this.apiUrl}/analytics/top-crafts`,
      { params }
    );
  }

  getAnalyticsByJob(): Observable<{ jobs: JobAnalytics[]; total: number }> {
    return this.http.get<{ jobs: JobAnalytics[]; total: number }>(
      `${this.apiUrl}/analytics/by-job`
    );
  }

  getLevelDistribution(): Observable<{
    items: LevelDistribution[];
    recipes: LevelDistribution[];
  }> {
    return this.http.get<{ items: LevelDistribution[]; recipes: LevelDistribution[] }>(
      `${this.apiUrl}/analytics/level-distribution`
    );
  }

  getRarityDistribution(): Observable<{ distribution: RarityDistribution[] }> {
    return this.http.get<{ distribution: RarityDistribution[] }>(
      `${this.apiUrl}/analytics/rarity-distribution`
    );
  }

  getComplexCrafts(
    limit: number = 10
  ): Observable<{ complex_crafts: ComplexCraft[]; total: number }> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<{ complex_crafts: ComplexCraft[]; total: number }>(
      `${this.apiUrl}/analytics/complex-crafts`,
      { params }
    );
  }
}
