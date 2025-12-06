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

  importAll(): Observable<ImportResult> {
    return this.http.post<ImportResult>(`${this.apiUrl}/imports/full`, {});
  }

  getImportHistory(): Observable<any> {
    return this.http.get(`${this.apiUrl}/imports/history`);
  }
}
