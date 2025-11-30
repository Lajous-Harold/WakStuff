import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { finalize } from 'rxjs';
import { ItemsService, WakstuffItem } from '../../../core/services/items.service';

@Component({
  selector: 'app-items-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './items-list.html',
  styleUrls: ['./items-list.scss'],
})
export class ItemsList implements OnInit {
  items: WakstuffItem[] = [];
  filteredItems: WakstuffItem[] = [];
  pagedItems: WakstuffItem[] = [];

  loading = false;
  reloading = false;
  error: string | null = null;
  searchQuery = '';

  pageIndex = 0; // 0-based
  pageSize = 25;
  pageSizeOptions = [25, 50, 100];

  get totalItems(): number {
    return this.filteredItems.length;
  }

  get totalPages(): number {
    if (this.pageSize <= 0) return 1;
    const pages = Math.ceil(this.totalItems / this.pageSize);
    return pages > 0 ? pages : 1;
  }

  get pageStartIndex(): number {
    if (this.totalItems === 0) return 0;
    return this.pageIndex * this.pageSize + 1;
  }

  get pageEndIndex(): number {
    return Math.min(this.totalItems, (this.pageIndex + 1) * this.pageSize);
  }

  constructor(
    private route: ActivatedRoute,
    private itemsService: ItemsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loading = true;

    this.route.data.subscribe({
      next: (data) => {
        const resolved = data['items'];
        this.items = this.toArray(resolved);
        this.filteredItems = [...this.items];
        this.pageIndex = 0;
        this.updatePagedItems();
        this.loading = false;
        this.error = null;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement des items';
        this.items = [];
        this.filteredItems = [];
        this.pagedItems = [];
        this.loading = false;
      },
    });
  }

  /**
   * Force n'importe quelle valeur à être un WakstuffItem[].
   * - si c'est déjà un tableau => on le garde
   * - si c'est un objet avec une propriété .items tableau => on prend ça
   * - sinon => []
   */
  private toArray(value: any): WakstuffItem[] {
    if (Array.isArray(value)) {
      return value as WakstuffItem[];
    }

    if (value && typeof value === 'object' && Array.isArray(value.items)) {
      return value.items as WakstuffItem[];
    }

    return [];
  }

  private updatePagedItems(): void {
    const start = this.pageIndex * this.pageSize;
    const end = start + this.pageSize;
    this.pagedItems = this.filteredItems.slice(start, end);
  }

  changePageSize(rawValue: string | number): void {
    const size = typeof rawValue === 'string' ? parseInt(rawValue, 10) : rawValue;

    if (!Number.isFinite(size) || size <= 0) {
      return;
    }

    this.pageSize = size;
    this.pageIndex = 0;
    this.updatePagedItems();
  }

  onSearchChange(): void {
    const query = this.searchQuery.toLowerCase().trim();

    if (!query) {
      this.filteredItems = [...this.items];
    } else {
      this.filteredItems = this.items.filter((item) => {
        return (
          item.name.toLowerCase().includes(query) ||
          item.type?.toLowerCase().includes(query) ||
          item.rarity?.toLowerCase().includes(query) ||
          item.element?.toLowerCase().includes(query) ||
          item.id.toString().includes(query) ||
          item.wakfu_id.toString().includes(query)
        );
      });
    }

    this.pageIndex = 0;
    this.updatePagedItems();
  }

  canGoPrevious(): boolean {
    return this.pageIndex > 0;
  }

  canGoNext(): boolean {
    return (this.pageIndex + 1) * this.pageSize < this.totalItems;
  }

  goToFirstPage(): void {
    if (!this.canGoPrevious()) return;
    this.pageIndex = 0;
    this.updatePagedItems();
  }

  goToLastPage(): void {
    if (!this.canGoNext()) return;
    this.pageIndex = this.totalPages - 1;
    this.updatePagedItems();
  }

  goToPreviousPage(): void {
    if (!this.canGoPrevious()) return;
    this.pageIndex--;
    this.updatePagedItems();
  }

  goToNextPage(): void {
    if (!this.canGoNext()) return;
    this.pageIndex++;
    this.updatePagedItems();
  }

  reload(): void {
    this.reloading = true;
    this.error = null;
    this.cdr.detectChanges();

    this.itemsService
      .list()
      .pipe(
        finalize(() => {
          this.reloading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (items) => {
          this.items = this.toArray(items as any);
          this.searchQuery = '';
          this.filteredItems = [...this.items];
          this.pageIndex = 0;
          this.updatePagedItems();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = err?.message ?? 'Erreur lors du rechargement des items';
          this.cdr.detectChanges();
        },
      });
  }

  onImageError(event: Event, item: WakstuffItem): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
  }
}
