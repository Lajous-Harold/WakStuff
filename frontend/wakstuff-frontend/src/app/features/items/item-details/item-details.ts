import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs';
import { ItemsService, WakstuffItem } from '../../../core/services/items.service';
import { WakfuDataService, Recipe } from '../../../core/services/wakfu-data.service';

@Component({
  selector: 'app-item-details',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './item-details.html',
  styleUrls: ['./item-details.scss'],
})
export class ItemDetails implements OnInit {
  item: WakstuffItem | null = null;
  recipe: Recipe | null = null;
  loading = false;
  loadingRecipe = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private itemsService: ItemsService,
    private wakfuDataService: WakfuDataService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = +params['id'];
      if (id) {
        this.loadItem(id);
      }
    });
  }

  private loadItem(id: number): void {
    this.loading = true;
    this.error = null;

    this.itemsService
      .getById(id, true)
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (item) => {
          this.item = item;
          this.loadRecipe(item.wakfu_id);
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = err?.message ?? "Erreur lors du chargement de l'item";
          this.cdr.detectChanges();
        },
      });
  }

  private loadRecipe(wakfuId: number): void {
    this.loadingRecipe = true;

    this.wakfuDataService
      .getRecipe(wakfuId)
      .pipe(
        finalize(() => {
          this.loadingRecipe = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (recipe) => {
          this.recipe = recipe;
          this.cdr.detectChanges();
        },
        error: () => {
          this.recipe = null;
          this.cdr.detectChanges();
        },
      });
  }

  getRarityClass(rarity: string | null): string {
    if (!rarity) return 'rarity-common';
    return `rarity-${rarity.toLowerCase()}`;
  }

  getCategoryBadge(category: string | null): string {
    if (!category) return 'N/A';
    const parts = category.split('.');
    return parts[parts.length - 1] || category;
  }

  goBack(): void {
    this.router.navigate(['/items']);
  }

  viewCraftCalculator(): void {
    if (this.item) {
      this.router.navigate(['/craft-calculator'], {
        queryParams: { itemId: this.item.wakfu_id },
      });
    }
  }

  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
  }
}
