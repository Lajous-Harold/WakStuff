import { Item } from './item.model';
import { Resource } from './resource.model';
import { Recipe } from './recipe.model';

export interface GlobalStats {
  total_items: number;
  total_resources: number;
  total_recipes: number;
  total_job_items: number;
  items_by_rarity: Record<string, number>;
  recipes_by_category: Record<string, number>;
  level_distribution: Record<string, number>;
}

export interface GlobalSearchResult {
  items: Item[];
  resources: Resource[];
  recipes: Recipe[];
  total: number;
  page?: number;
  per_page?: number;
}

export interface ImportBatch {
  id: number;
  timestamp: string;
  total_entries: number;
}
