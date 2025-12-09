export interface CraftTreeNode {
  item_id: number;
  item_wakfu_id: number;
  item_title: string;
  quantity: number;
  level: number;
  is_resource: boolean;
  recipe_wakfu_id?: number;
  children: CraftTreeNode[];
  user_has?: boolean;
  max_depth_reached?: boolean;
  cycle_detected?: boolean;
}

export interface CraftTreeResponse {
  recipe: {
    id: number;
    wakfu_id: number;
    level: number;
    recipe_category_id: number;
  } | null;
  craft_tree: CraftTreeNode;
}
