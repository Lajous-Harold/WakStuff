import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ImportResult } from '../models';
import { environment } from '../config';

@Injectable({
  providedIn: 'root',
})
export class ImportsService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  importAll(clearBefore: boolean = true): Observable<ImportResult> {
    return this.http.post<ImportResult>(`${this.apiUrl}/imports/full`, {
      clear_before: clearBefore,
    });
  }

  getImportBatches(limit: number = 20): Observable<any> {
    return this.http.get(`${this.apiUrl}/imports/batches?limit=${limit}`);
  }

  clearAllData(): Observable<any> {
    return this.http.post(`${this.apiUrl}/imports/clear`, { confirm: true });
  }

  clearImportHistory(): Observable<any> {
    return this.http.post(`${this.apiUrl}/imports/clear-history`, { confirm: true });
  }

  getImportStats(): Observable<any> {
    return this.http.get(`${this.apiUrl}/imports/stats`);
  }
}
