import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs';
import {
  ItemsService,
  WakstuffItem,
  ItemsListResponse,
  CategoryStats,
} from '../../../core/services/items.service';
import { WakfuDataService, CategoryInfo } from '../../../core/services/wakfu-data.service';
import { CategoryLabelPipe, RarityLabelPipe } from '../../../shared/pipes';

@Component({
  selector: 'app-items-list',
  standalone: true,
  imports: [CommonModule, FormsModule, CategoryLabelPipe, RarityLabelPipe],
  templateUrl: './items-list.html',
  styleUrls: ['./items-list.scss'],
})
export class ItemsList implements OnInit {
  items: WakstuffItem[] = [];
  total = 0;
  loading = false;
  reloading = false;
  error: string | null = null;

  // Filtres
  searchQuery = '';
  selectedCategory = '';
  selectedRarity = '';
  minLevel: number | null = null;
  maxLevel: number | null = null;
  showDetails = false;

  // Pagination
  pageIndex = 0;
  pageSize = 25;
  pageSizeOptions = [25, 50, 100];

  // Données pour les filtres
  categories: CategoryInfo[] = [];
  rarities = ['common', 'unusual', 'rare', 'mythical', 'legendary', 'relic', 'souvenir', 'epic'];

  get totalPages(): number {
    if (this.pageSize <= 0) return 1;
    const pages = Math.ceil(this.total / this.pageSize);
    return pages > 0 ? pages : 1;
  }

  get pageStartIndex(): number {
    if (this.total === 0) return 0;
    return this.pageIndex * this.pageSize + 1;
  }

  get pageEndIndex(): number {
    return Math.min(this.total, (this.pageIndex + 1) * this.pageSize);
  }

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private itemsService: ItemsService,
    private wakfuDataService: WakfuDataService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadItems();
  }

  private loadCategories(): void {
    this.wakfuDataService.getCategories().subscribe({
      next: (categories) => {
        this.categories = categories.sort((a, b) => a.name.localeCompare(b.name));
      },
      error: (err) => {
        console.error('Erreur lors du chargement des catégories:', err);
      },
    });
  }

  private loadItems(): void {
    this.loading = true;
    this.error = null;

    const params = {
      limit: this.pageSize,
      offset: this.pageIndex * this.pageSize,
      category: this.selectedCategory || undefined,
      rarity: this.selectedRarity || undefined,
      minLevel: this.minLevel ?? undefined,
      maxLevel: this.maxLevel ?? undefined,
      search: this.searchQuery || undefined,
      details: this.showDetails,
    };

    this.itemsService
      .list(params)
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (response: ItemsListResponse) => {
          this.items = response.items;
          this.total = response.total;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = err?.message ?? 'Erreur lors du chargement des items';
          this.items = [];
          this.total = 0;
          this.cdr.detectChanges();
        },
      });
  }

  changePageSize(rawValue: string | number): void {
    const size = typeof rawValue === 'string' ? parseInt(rawValue, 10) : rawValue;

    if (!Number.isFinite(size) || size <= 0) {
      return;
    }

    this.pageSize = size;
    this.pageIndex = 0;
    this.loadItems();
  }

  onSearchChange(): void {
    this.pageIndex = 0;
    this.loadItems();
  }

  onCategoryChange(): void {
    this.pageIndex = 0;
    this.loadItems();
  }

  onRarityChange(): void {
    this.pageIndex = 0;
    this.loadItems();
  }

  onLevelChange(): void {
    this.pageIndex = 0;
    this.loadItems();
  }

  onDetailsToggle(): void {
    this.loadItems();
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.selectedRarity = '';
    this.minLevel = null;
    this.maxLevel = null;
    this.pageIndex = 0;
    this.loadItems();
  }

  canGoPrevious(): boolean {
    return this.pageIndex > 0;
  }

  canGoNext(): boolean {
    return (this.pageIndex + 1) * this.pageSize < this.total;
  }

  goToFirstPage(): void {
    if (!this.canGoPrevious()) return;
    this.pageIndex = 0;
    this.loadItems();
  }

  goToLastPage(): void {
    if (!this.canGoNext()) return;
    this.pageIndex = this.totalPages - 1;
    this.loadItems();
  }

  goToPreviousPage(): void {
    if (!this.canGoPrevious()) return;
    this.pageIndex--;
    this.loadItems();
  }

  goToNextPage(): void {
    if (!this.canGoNext()) return;
    this.pageIndex++;
    this.loadItems();
  }

  reload(): void {
    this.reloading = true;
    this.pageIndex = 0;
    this.loadItems();
    this.reloading = false;
  }

  onImageError(event: Event, item: WakstuffItem): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
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

  viewItemDetails(item: WakstuffItem): void {
    this.router.navigate(['/items', item.id]);
  }
}
