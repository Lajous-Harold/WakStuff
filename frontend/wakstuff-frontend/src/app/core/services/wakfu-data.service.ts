import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config';

export interface WakfuStats {
  items: {
    total: number;
    by_category: Record<string, number>;
    by_rarity: Record<string, number>;
  };
  actions: number;
  states: number;
  jobs: number;
  recipes: number;
  last_import: {
    batch_id: number;
    version: string;
    started_at: string;
    ended_at: string;
    status: string;
    total_items: number;
    error_count: number;
  } | null;
}

export interface CategoryInfo {
  id: number;
  name: string;
  description: string | null;
  item_count: number;
}

export interface RecipeIngredient {
  item_id: number;
  item_name: string;
  quantity: number;
}

export interface Recipe {
  id: number;
  wakfu_id: number;
  result_id: number;
  result_name: string;
  level: number;
  xp: number;
  ingredients: RecipeIngredient[];
}

export interface CraftTreeItem {
  item_id: number;
  item_name: string;
  quantity_needed: number;
  recipe?: {
    id: number;
    level: number;
    xp: number;
    ingredients: CraftTreeItem[];
  };
  is_base_resource: boolean;
}

export interface CraftCalculation {
  target_item_id: number;
  target_item_name: string;
  target_quantity: number;
  craft_tree: CraftTreeItem;
  total_base_resources: Record<string, { item_id: number; quantity: number }>;
  total_xp: number;
}

export interface ImportBatch {
  id: number;
  batch_type: string;
  started_at: string;
  completed_at: string | null;
  status: string;
  total_imported: number;
  error_message: string | null;
}

@Injectable({ providedIn: 'root' })
export class WakfuDataService {
  private readonly baseUrl = `${API_BASE_URL}/api/wakfu`;

  constructor(private http: HttpClient) {}

  /**
   * Récupère les statistiques globales Wakfu
   */
  getStats(): Observable<WakfuStats> {
    return this.http.get<WakfuStats>(`${this.baseUrl}/stats`);
  }

  /**
   * Récupère toutes les catégories avec leurs compteurs
   */
  getCategories(): Observable<CategoryInfo[]> {
    return this.http.get<CategoryInfo[]>(`${this.baseUrl}/categories`);
  }

  /**
   * Récupère la recette d'un item
   */
  getRecipe(itemId: number): Observable<Recipe> {
    return this.http.get<Recipe>(`${this.baseUrl}/recipes/${itemId}`);
  }

  /**
   * Calcule l'arbre de craft complet pour un item
   */
  calculateCraft(itemId: number, quantity: number = 1): Observable<CraftCalculation> {
    const params = new HttpParams().set('quantity', quantity.toString());
    return this.http.get<CraftCalculation>(`${this.baseUrl}/craft-calculator/${itemId}`, {
      params,
    });
  }

  /**
   * Lance un import complet des données Wakfu
   */
  importFull(): Observable<{ message: string; batch_id: number }> {
    return this.http.post<{ message: string; batch_id: number }>(`${this.baseUrl}/import/full`, {});
  }

  /**
   * Récupère l'historique des imports
   */
  getImportHistory(limit: number = 20): Observable<ImportBatch[]> {
    const params = new HttpParams().set('limit', limit.toString());
    return this.http.get<ImportBatch[]>(`${this.baseUrl}/imports`, { params });
  }
}
