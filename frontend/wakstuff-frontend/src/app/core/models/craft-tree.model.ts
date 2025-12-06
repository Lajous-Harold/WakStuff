export interface CraftTreeNode {
  item_id: number;
  item_wakfu_id: number;
  item_title: string;
  quantity: number;
  level: number;
  is_resource: boolean; // true si ressource primordiale (non-craftable)
  recipe_wakfu_id?: number;
  children: CraftTreeNode[]; // Ingrédients nécessaires (récursif)
  user_has?: boolean; // Marqué par l'utilisateur comme possédé
}

export interface CraftTreeResponse {
  recipe: {
    id: number;
    wakfu_id: number;
    level: number;
    recipe_category_id: number;
  };
  craft_tree: CraftTreeNode;
}
