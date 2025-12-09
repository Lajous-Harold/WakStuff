export interface HarvestResource {
  id: number;
  item_id: number;
  name: string;
  level: number;
  rarity: number;
  icon_gfx_id: number;
  skill_id: number;
  job_id?: number;
  resource_type_id?: number;
  item_type_id?: number;
  min_drop_rate?: number;
  max_drop_rate?: number;
  avg_drop_rate?: number;
}

export interface HarvestResourcesResponse {
  resources: HarvestResource[];
  total: number;
}

export interface HarvestJob {
  skill_id: number;
  name: string;
  icon: string;
}
