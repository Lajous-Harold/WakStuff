import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RecipesService } from '../../../core/services/recipes.service';
import { CraftTreeNode, CraftTreeResponse } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../shared/components/error-message/error-message.component';
import { CraftTreeNodeComponent } from '../craft-tree-node/craft-tree-node.component';
import { CraftFavoritesService } from '../../../core/services/craft-favorites.service';
import { environment } from '../../../core/config';

interface MaterialSummary {
  item_wakfu_id: number;
  item_title: string;
  icon_gfx_id?: number;
  total_quantity: number;
  is_resource: boolean;
}

@Component({
  selector: 'app-craft-calculator',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    CraftTreeNodeComponent,
  ],
  templateUrl: './craft-calculator.component.html',
  styleUrl: './craft-calculator.component.scss',
})
export class CraftCalculatorComponent implements OnInit {
  loading = signal(false);
  error = signal<string | null>(null);

  craftTree = signal<CraftTreeResponse | null>(null);
  wakfuId = signal<number>(0);
  quantity = signal<number>(1);
  maxDepth = signal<number>(10);

  // Owned items tracking
  ownedItems = signal<Set<number>>(new Set());

  // Computed materials list
  materials = computed(() => {
    const tree = this.craftTree();
    if (!tree) return [];

    const owned = this.ownedItems();
    const materialsMap = new Map<number, MaterialSummary>();

    const traverse = (node: CraftTreeNode, multiplier: number) => {
      // Skip if user owns this item
      if (owned.has(node.item_wakfu_id)) {
        return;
      }

      // If it's a leaf resource, add to materials
      if (node.is_resource || !node.children || node.children.length === 0) {
        const existing = materialsMap.get(node.item_wakfu_id);
        if (existing) {
          existing.total_quantity += node.quantity * multiplier;
        } else {
          materialsMap.set(node.item_wakfu_id, {
            item_wakfu_id: node.item_wakfu_id,
            item_title: node.item_title,
            icon_gfx_id: node.icon_gfx_id,
            total_quantity: node.quantity * multiplier,
            is_resource: node.is_resource,
          });
        }
        return;
      }

      // If it's a craftable item, recurse into children
      if (node.children) {
        for (const child of node.children) {
          traverse(child, multiplier * node.quantity);
        }
      }
    };

    if (tree.craft_tree) {
      traverse(tree.craft_tree, 1);
    }

    return Array.from(materialsMap.values()).sort((a, b) => {
      if (a.is_resource !== b.is_resource) {
        return a.is_resource ? -1 : 1;
      }
      return a.item_title.localeCompare(b.item_title);
    });
  });

  constructor(
    private recipesService: RecipesService,
    private craftFavorites: CraftFavoritesService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = +params['itemId'];
      this.wakfuId.set(id);
      this.loadCraftTree();
    });
  }

  loadCraftTree(): void {
    this.loading.set(true);
    this.error.set(null);

    this.recipesService.getCraftTree(this.wakfuId(), this.quantity(), this.maxDepth()).subscribe({
      next: (response: CraftTreeResponse) => {
        this.craftTree.set(response);
        this.loading.set(false);
      },
      error: (err: any) => {
        this.error.set("Erreur lors du chargement de l'arbre de craft");
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  onQuantityChange(): void {
    if (this.quantity() < 1) {
      this.quantity.set(1);
    }
    this.loadCraftTree();
  }

  onMaxDepthChange(): void {
    if (this.maxDepth() < 1) {
      this.maxDepth.set(1);
    }
    if (this.maxDepth() > 20) {
      this.maxDepth.set(20);
    }
    this.loadCraftTree();
  }

  toggleOwned(itemId: number): void {
    const current = this.ownedItems();
    const newSet = new Set(current);

    if (newSet.has(itemId)) {
      newSet.delete(itemId);
    } else {
      newSet.add(itemId);
    }

    this.ownedItems.set(newSet);
  }

  isOwned(itemId: number): boolean {
    return this.ownedItems().has(itemId);
  }

  getItemIconUrl(itemId: number): string {
    return `${environment.apiUrl}/proxy/icon/${itemId}`;
  }

  exportMaterials(): void {
    const mats = this.materials();
    const text = mats.map((m) => `${m.item_title}: ${m.total_quantity}`).join('\n');

    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `materials-${this.wakfuId()}.txt`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  saveCraftList(): void {
    const tree = this.craftTree();
    if (!tree || !tree.craft_tree) {
      return;
    }

    const craftListName = prompt('Nom de la craft list:', tree.craft_tree.item_title);
    if (!craftListName) {
      return;
    }

    const materials = this.materials().map((m) => ({
      itemId: m.item_wakfu_id,
      itemName: m.item_title,
      quantity: m.total_quantity,
    }));

    this.craftFavorites.addCraftList({
      name: craftListName,
      recipeId: tree.craft_tree.item_wakfu_id,
      recipeName: tree.craft_tree.item_title,
      recipeIconGfxId: tree.craft_tree.icon_gfx_id,
      quantity: this.quantity(),
      maxDepth: this.maxDepth(),
      skipOwnedItems: this.ownedItems().size > 0,
      materials,
    });

    alert('✅ Craft list sauvegardée !');
  }

  goBack(): void {
    window.history.back();
  }

  viewItem(wakfuId: number): void {
    this.router.navigate(['/items', wakfuId]);
  }
}
