export interface ImportResult {
  success: boolean;
  import_id: number;
  timestamp: string;
  grand_total: number;
  phase_1_total: number;
  phase_2_total: number;
  phase_3_total: number;
  phase_4_total: number;
  timing: {
    phase_1: number;
    phase_2: number;
    phase_3: number;
    phase_4: number;
    total: number;
  };
}

export interface ImportStats {
  recipe_categories: number;
  item_types: number;
  equipment_item_types: number;
  resource_types: number;
  resources: number;
  collectable_resources: number;
  harvest_loots: number;
  job_items: number;
  items: number;
  recipes: number;
  recipe_ingredients: number;
  recipe_results: number;
  total: number;
}

export interface ImportBatch {
  id: number;
  timestamp: string;
  total_entries: number;
}
