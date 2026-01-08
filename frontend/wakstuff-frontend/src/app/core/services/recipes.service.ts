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
  sort_by?: 'name' | 'level';
  sort_order?: 'asc' | 'desc';
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

  getCraftTree(
    itemWakfuId: number,
    quantity: number = 1,
    maxDepth: number = 10
  ): Observable<CraftTreeResponse> {
    let params = new HttpParams()
      .set('quantity', quantity.toString())
      .set('max_depth', maxDepth.toString());

    return this.http.get<CraftTreeResponse>(`${this.apiUrl}/recipes/craft-tree/${itemWakfuId}`, {
      params,
    });
  }

  getCategories(categoryType?: 'harvest' | 'craft'): Observable<any> {
    let params = new HttpParams();
    if (categoryType) {
      params = params.set('category_type', categoryType);
    }
    return this.http.get(`${this.apiUrl}/categories`, { params });
  }

  getRecipesByResult(itemWakfuId: number): Observable<{ recipes: RecipeModel[]; results: any[] }> {
    return this.http.get<{ recipes: RecipeModel[]; results: any[] }>(
      `${this.apiUrl}/recipes/by-result/${itemWakfuId}`
    );
  }

  getRecipesByIngredient(
    itemWakfuId: number
  ): Observable<{ recipes: RecipeModel[]; ingredients: any[] }> {
    return this.http.get<{ recipes: RecipeModel[]; ingredients: any[] }>(
      `${this.apiUrl}/recipes/by-ingredient/${itemWakfuId}`
    );
  }

  getCategoryRecipes(
    categoryId: number,
    filters: RecipeFilters = {}
  ): Observable<RecipesListResponse> {
    return this.getRecipes({ ...filters, category_id: categoryId });
  }
}
