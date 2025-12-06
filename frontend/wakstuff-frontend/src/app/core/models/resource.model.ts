export interface Resource {
  id: number;
  wakfu_id: number;
  title: string;
  description?: string;
  level: number;
  resource_type_id: number;
  resource_type_title?: string;
  type_name?: string; // Alias de resource_type_title
}

export interface ResourceType {
  id: number;
  wakfu_id: number;
  title: string;
}

export interface CollectibleResource {
  id: number;
  resource_wakfu_id: number;
  resource_title: string;
  zone_name?: string;
  zone_id?: number;
}

export interface HarvestLoot {
  id: number;
  item_id: number;
  item_wakfu_id: number; // ID Wakfu de l'item looté
  item_title: string;
  quantity: number;
}

export interface ResourceDetail extends Resource {
  harvest_loots: HarvestLoot[];
  recipes_using: any[];
  used_in_recipes?: any[]; // Alias de recipes_using
  type_name?: string;
  description?: string;
}

export interface ResourcesListResponse {
  resources: Resource[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
