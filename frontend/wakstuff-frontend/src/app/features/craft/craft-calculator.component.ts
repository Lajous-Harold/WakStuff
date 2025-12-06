import { Component, OnInit, ChangeDetectionStrategy, signal, computed } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { RecipesService } from '../../core/services/recipes.service';
import { ImportStatusService } from '../../core/services/import-status.service';
import { CraftTreeNode } from '../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../shared/components';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { FormsModule } from '@angular/forms';

interface InventoryItem {
  wakfu_id: number;
  quantity: number;
}

@Component({
  selector: 'app-craft-calculator',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent, FormsModule, EmptyStateComponent],
  templateUrl: './craft-calculator.component.html',
  styleUrl: './craft-calculator.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CraftCalculatorComponent implements OnInit {
  craftTree = signal<CraftTreeNode | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);
  hasData = signal(true);

  targetWakfuId = signal<number | null>(null);
  targetQuantity = signal(1);
  inventory = signal<InventoryItem[]>([]);

  constructor(
    private route: ActivatedRoute,
    private recipesService: RecipesService,
    private importStatusService: ImportStatusService
  ) {}

  ngOnInit(): void {
    // Vérifier d'abord si des données ont été importées
    this.importStatusService.checkImportStatus().subscribe({
      next: (hasData) => {
        if (!hasData) {
          // Pas de données importées
          this.hasData.set(false);
          return;
        }

        // Des données existent, charger normalement
        this.route.params.subscribe((params) => {
          const wakfuId = params['wakfuId'];
          if (wakfuId) {
            this.targetWakfuId.set(Number(wakfuId));
            this.loadCraftTree(Number(wakfuId));
          }
        });
      },
      error: () => {
        this.hasData.set(false);
      },
    });
  }

  loadCraftTree(wakfuId: number): void {
    this.loading.set(true);
    this.error.set(null);

    this.recipesService.getCraftTree(wakfuId).subscribe({
      next: (response) => {
        this.craftTree.set(response.craft_tree);
        this.hasData.set(true);
        this.loading.set(false);
      },
      error: (err) => {
        // Ne pas logger les 404, c'est juste une recette introuvable
        if (err.status === 404) {
          this.error.set('Recette introuvable');
        } else {
          console.error("Erreur lors du chargement de l'arbre de craft", err);
          this.error.set("Erreur lors du chargement de l'arbre de craft");
        }
        this.loading.set(false);
      },
    });
  }

  searchRecipe(event: Event): void {
    const input = event.target as HTMLInputElement;
    const wakfuId = Number(input.value);

    if (wakfuId && !isNaN(wakfuId)) {
      // Vérifier d'abord si des données existent
      if (this.importStatusService.hasImportedData() === false) {
        // Pas de données, ne pas faire l'appel
        this.hasData.set(false);
        return;
      }

      this.targetWakfuId.set(wakfuId);
      this.loadCraftTree(wakfuId);
    }
  }

  updateQuantity(quantity: number): void {
    if (quantity > 0) {
      this.targetQuantity.set(quantity);
    }
  }

  toggleUserHas(node: CraftTreeNode): void {
    node.user_has = !node.user_has;
    // Force update
    this.craftTree.set({ ...this.craftTree()! });
  }

  getTotalQuantity(node: CraftTreeNode): number {
    return node.quantity * this.targetQuantity();
  }

  getNodeClass(node: CraftTreeNode): string {
    if (node.user_has) return 'has';
    if (node.children && node.children.length > 0) return 'craftable';
    return 'resource';
  }

  getNodeIcon(node: CraftTreeNode): string {
    if (node.user_has) return '✓';
    if (node.children && node.children.length > 0) return '⚒️';
    return '📦';
  }
}
