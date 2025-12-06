import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RecipeModel, RecipeDetail, RecipesListResponse, CraftTreeResponse } from '../models';
import { environment } from '../config';

export interface RecipeFilters {
  search?: string;
  category_id?: number;
  level_min?: number;
  level_max?: number;
  page?: number;
  per_page?: number;
}

@Injectable({
  providedIn: 'root',
})
export class RecipesService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getRecipes(filters: RecipeFilters = {}): Observable<RecipesListResponse> {
    let params = new HttpParams();

    Object.keys(filters).forEach((key) => {
      const value = filters[key as keyof RecipeFilters];
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, value.toString());
      }
    });

    return this.http.get<RecipesListResponse>(`${this.apiUrl}/recipes`, { params });
  }

  getRecipeDetail(wakfuId: number): Observable<RecipeDetail> {
    return this.http.get<RecipeDetail>(`${this.apiUrl}/recipes/${wakfuId}`);
  }

  getCraftTree(wakfuId: number): Observable<CraftTreeResponse> {
    return this.http.get<CraftTreeResponse>(`${this.apiUrl}/recipes/${wakfuId}/tree`);
  }

  getCategories(): Observable<any> {
    return this.http.get(`${this.apiUrl}/recipes/categories`);
  }
}
