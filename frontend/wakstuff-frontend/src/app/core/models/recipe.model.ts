export interface Recipe {
  id: number;
  wakfu_id: number;
  level: number;
  recipe_category_id: number;
  recipe_category_name?: string;
  name?: string; // Nom de la recette (optionnel dans les listes)
  title?: string; // Alias de name
}

export interface RecipeIngredient {
  id: number;
  recipe_wakfu_id: number;
  item_id: number;
  item_title: string;
  item_wakfu_id: number;
  quantity: number;
}

export interface RecipeResult {
  id: number;
  recipe_wakfu_id: number;
  produced_item_id: number;
  produced_item_title: string;
  produced_item_wakfu_id: number;
  quantity: number;
}

export interface RecipeDetail {
  recipe: Recipe;
  ingredients: RecipeIngredient[];
  results: RecipeResult[];
}

export interface RecipesListResponse {
  recipes: Recipe[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
