export type FavoriteType = 'item' | 'resource' | 'recipe';

export interface Favorite {
  type: FavoriteType;
  wakfu_id: number;
  title: string;
  added_at: string; // ISO timestamp
}

export interface FavoritesCollection {
  items: number[];
  resources: number[];
  recipes: number[];
  version: string; // Pour compatibilité future
}
