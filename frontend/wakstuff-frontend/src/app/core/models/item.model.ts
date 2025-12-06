export interface Item {
  id: number;
  wakfu_id: number;
  title: string;
  description?: string;
  level: number;
  rarity: number; // 0-7
  item_type_id: number;
  item_type_title?: string;
  equipment_type_id?: number;
  equipment_type_title?: string;
  icon_gfx_id?: number;
  image_url?: string;
}

export interface ItemType {
  id: number;
  wakfu_id: number;
  title: string;
  category: string;
}

export interface ItemProperty {
  id: number;
  wakfu_id: number;
  name: string;
  description?: string;
}

export interface Action {
  id: number;
  wakfu_id: number;
  description: string;
}

export interface Effect {
  actionId: number;
  params?: any[];
  action?: Action;
}

export interface ItemStatistic {
  label: string;
  value: number;
  action_id: number;
}

export interface RecipeCategory {
  id: number;
  wakfu_id: number;
  name: string;
  title: string;
  category_type: string;
}

export interface RecipeDetail {
  id: number;
  wakfu_id: number;
  level: number;
  recipe_category_id?: number;
  category?: RecipeCategory;
  quantity_needed?: number;
  quantity_produced?: number;
}

export interface JobItem {
  id: number;
  wakfu_id: number;
  harvest_skill_id?: number;
  craft_skill_id?: number;
}

export interface ItemDetail extends Item {
  item_type?: ItemType;
  equipment_type?: ItemType;
  properties?: ItemProperty[];
  use_effects?: Effect[];
  use_critical_effects?: Effect[];
  equip_effects?: Effect[];
  use_effects_enriched?: Effect[];
  use_critical_effects_enriched?: Effect[];
  equip_effects_enriched?: Effect[];
  statistics?: { [key: string]: ItemStatistic };
  used_in_recipes?: RecipeDetail[];
  produced_by_recipes?: RecipeDetail[];
  job_item?: JobItem;
}

export interface ItemsListResponse {
  items: Item[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Pour compatibilité avec code existant
export interface Recipe {
  id: number;
  wakfu_id: number;
  level: number;
  recipe_category_id: number;
  recipe_category_name?: string;
}
