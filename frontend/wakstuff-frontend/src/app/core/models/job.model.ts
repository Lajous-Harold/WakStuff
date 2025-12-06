import { Recipe } from './recipe.model';

export interface Job {
  id: number;
  wakfu_id: number;
  name: string;
  category_type: string;
  skill_id: number;
  icon_url?: string;
}

export interface JobStats {
  total_recipes: number;
  min_level: number;
  max_level: number;
  most_used_resources: ResourceUsage[];
}

export interface ResourceUsage {
  resource_id: number;
  resource_title: string;
  usage_count: number;
}

export interface JobDetail {
  job: Job;
  recipes: Recipe[];
  stats: JobStats;
}

export interface XPLevel {
  level: number;
  xp_required: number;
  cumulative_xp: number;
}

export interface RecipeXP {
  recipe_wakfu_id: number;
  recipe_level: number;
  xp_granted: number;
}

export interface XPCalculatorData {
  xp_per_level: XPLevel[];
  recipes_xp: RecipeXP[];
}
