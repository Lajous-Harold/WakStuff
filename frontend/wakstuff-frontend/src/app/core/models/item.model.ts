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

export interface ItemDetail extends Item {
  recipes_using: Recipe[];
  recipes_producing: Recipe[];
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
