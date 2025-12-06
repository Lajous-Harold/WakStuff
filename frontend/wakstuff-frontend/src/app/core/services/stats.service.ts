import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GlobalStats, GlobalSearchResult, ImportBatch } from '../models/stats.model';
import { environment } from '../config';

@Injectable({
  providedIn: 'root',
})
export class StatsService {
  private readonly apiUrl = environment.apiUrl;

  // Signal pour cache
  stats = signal<GlobalStats | null>(null);

  constructor(private http: HttpClient) {}

  getOverview(): Observable<GlobalStats> {
    return this.http.get<GlobalStats>(`${this.apiUrl}/stats/overview`);
  }

  globalSearch(query: string, limit: number = 20, page: number = 1): Observable<GlobalSearchResult> {
    return this.http.get<GlobalSearchResult>(`${this.apiUrl}/stats/global`, {
      params: { 
        query, 
        limit: limit.toString(),
        page: page.toString()
      },
    });
  }

  getRecentImports(limit: number = 5): Observable<{ batches: ImportBatch[] }> {
    return this.http.get<{ batches: ImportBatch[] }>(`${this.apiUrl}/stats/recent`, {
      params: { limit: limit.toString() },
    });
  }
}
