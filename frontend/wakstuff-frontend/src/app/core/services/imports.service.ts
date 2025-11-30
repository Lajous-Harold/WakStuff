import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config';

export interface ImportBatchDto {
  id: number;
  game_version: string | null;
  started_at: string | null;
  ended_at: string | null;
  status: string;
  total_items: number;
  error_count: number;
}

export interface RunImportResponse {
  batch_id: number;
  game_version: string | null;
  started_at: string | null;
  ended_at: string | null;
  status: string;
  total_items: number;
  error_count: number;
}

@Injectable({ providedIn: 'root' })
export class ImportsService {
  private readonly baseUrl = `${API_BASE_URL}/api/imports`;

  constructor(private http: HttpClient) {}

  run(): Observable<RunImportResponse> {
    return this.http.post<RunImportResponse>(`${this.baseUrl}/run`, {});
  }

  list(): Observable<ImportBatchDto[]> {
    return this.http.get<ImportBatchDto[]>(`${this.baseUrl}/`);
  }
}
