import { Component, input, output, computed } from '@angular/core';

export interface PaginationConfig {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalItems: number;
}

@Component({
  selector: 'app-pagination',
  standalone: true,
  template: `
    <div class="pagination-container">
      <div class="pagination-info">
        Affichage {{ startItem() }}-{{ endItem() }} sur {{ config().totalItems }} résultats
      </div>

      <nav class="pagination-nav" aria-label="Navigation par pages">
        <button
          class="pagination-btn"
          [disabled]="config().currentPage === 1"
          (click)="pageChange.emit(1)"
          aria-label="Première page"
        >
          ⟪
        </button>

        <button
          class="pagination-btn"
          [disabled]="config().currentPage === 1"
          (click)="pageChange.emit(config().currentPage - 1)"
          aria-label="Page précédente"
        >
          ‹
        </button>

        @for (page of visiblePages(); track page) { @if (page === '...') {
        <span class="pagination-ellipsis">…</span>
        } @else {
        <button
          class="pagination-btn"
          [class.active]="page === config().currentPage"
          (click)="pageChange.emit(typeof page === 'number' ? page : config().currentPage)"
          [attr.aria-current]="page === config().currentPage ? 'page' : null"
        >
          {{ page }}
        </button>
        } }

        <button
          class="pagination-btn"
          [disabled]="config().currentPage === config().totalPages"
          (click)="pageChange.emit(config().currentPage + 1)"
          aria-label="Page suivante"
        >
          ›
        </button>

        <button
          class="pagination-btn"
          [disabled]="config().currentPage === config().totalPages"
          (click)="pageChange.emit(config().totalPages)"
          aria-label="Dernière page"
        >
          ⟫
        </button>
      </nav>

      <div class="pagination-size">
        <label for="page-size">Par page:</label>
        <select id="page-size" [value]="config().pageSize" (change)="onPageSizeChange($event)">
          <option value="10">10</option>
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>
  `,
  styles: [
    `
      .pagination-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem;
        gap: 1rem;
        flex-wrap: wrap;
      }

      .pagination-info {
        color: #666;
        font-size: 0.9rem;
      }

      .pagination-nav {
        display: flex;
        gap: 0.25rem;
      }

      .pagination-btn {
        min-width: 36px;
        height: 36px;
        padding: 0.5rem;
        border: 1px solid #ddd;
        background: white;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.2s;

        &:hover:not(:disabled) {
          background: #f0f0f0;
          border-color: #3498db;
        }

        &:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }

        &.active {
          background: #3498db;
          color: white;
          border-color: #3498db;
        }
      }

      .pagination-ellipsis {
        display: flex;
        align-items: center;
        padding: 0 0.5rem;
        color: #999;
      }

      .pagination-size {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        label {
          font-size: 0.9rem;
          color: #666;
        }

        select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;

          &:hover {
            border-color: #3498db;
          }
        }
      }
    `,
  ],
})
export class PaginationComponent {
  config = input.required<PaginationConfig>();
  pageChange = output<number>();
  pageSizeChange = output<number>();

  startItem = computed(() => (this.config().currentPage - 1) * this.config().pageSize + 1);

  endItem = computed(() =>
    Math.min(this.config().currentPage * this.config().pageSize, this.config().totalItems)
  );

  visiblePages = computed(() => {
    const current = this.config().currentPage;
    const total = this.config().totalPages;
    const delta = 2; // Pages à afficher de chaque côté

    const pages: (number | string)[] = [];

    // Toujours afficher première page
    pages.push(1);

    // Calculer la plage autour de la page courante
    const rangeStart = Math.max(2, current - delta);
    const rangeEnd = Math.min(total - 1, current + delta);

    // Ajouter ellipsis si nécessaire
    if (rangeStart > 2) {
      pages.push('...');
    }

    // Ajouter pages intermédiaires
    for (let i = rangeStart; i <= rangeEnd; i++) {
      pages.push(i);
    }

    // Ajouter ellipsis si nécessaire
    if (rangeEnd < total - 1) {
      pages.push('...');
    }

    // Toujours afficher dernière page si > 1
    if (total > 1) {
      pages.push(total);
    }

    return pages;
  });

  onPageSizeChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.pageSizeChange.emit(Number(select.value));
  }
}
