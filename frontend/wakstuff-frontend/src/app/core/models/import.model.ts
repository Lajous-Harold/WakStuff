export interface ImportResult {
  status: string;
  batch_id: number;
  stats: any;
  metadata: ImportMetadata;
  message: string;
  started_at?: string;
  completed_at?: string;
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

export interface PhaseStats {
  [key: string]: number;
}

export interface ImportMetadata {
  stats: {
    phase_1?: PhaseStats;
    phase_2?: PhaseStats;
    phase_3?: PhaseStats;
    phase_4?: PhaseStats;
    [key: string]: PhaseStats | undefined;
  };
  summary?: {
    grand_total: number;
    phase_1_total: number;
    phase_2_total: number;
    phase_3_total: number;
    phase_4_total: number;
  };
}

export interface ImportBatch {
  id: number;
  batch_type: string;
  started_at: string;
  completed_at?: string;
  ended_at?: string;
  status: 'in_progress' | 'completed' | 'failed';
  items_imported?: number;
  import_metadata?: ImportMetadata;
  error_message?: string;
  error_count?: number;
  game_version?: string;
  total_items?: number;
}
