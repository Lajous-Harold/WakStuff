import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { WakfuDataService, CategoryInfo } from '../../core/services/wakfu-data.service';

interface CategoryGroup {
  parent: string;
  categories: CategoryInfo[];
  totalCount: number;
}

@Component({
  selector: 'app-categories-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './categories-view.html',
  styleUrls: ['./categories-view.scss'],
})
export class CategoriesView implements OnInit {
  categories: CategoryInfo[] = [];
  groupedCategories: CategoryGroup[] = [];
  loading = false;
  error: string | null = null;

  constructor(
    private wakfuDataService: WakfuDataService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadCategories();
  }

  private loadCategories(): void {
    this.loading = true;
    this.error = null;

    this.wakfuDataService
      .getCategories()
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (categories: CategoryInfo[]) => {
          this.categories = categories;
          this.groupCategories(categories);
          this.cdr.detectChanges();
        },
        error: (err: any) => {
          this.error = err?.message ?? 'Erreur lors du chargement des catégories';
          this.cdr.detectChanges();
        },
      });
  }

  private groupCategories(categories: CategoryInfo[]): void {
    const groups = new Map<string, CategoryInfo[]>();

    categories.forEach((category) => {
      const parts = category.name.split('.');
      const parent = parts.length > 1 ? parts[0] : 'Autres';

      if (!groups.has(parent)) {
        groups.set(parent, []);
      }
      groups.get(parent)!.push(category);
    });

    this.groupedCategories = Array.from(groups.entries())
      .map(([parent, cats]) => ({
        parent,
        categories: cats.sort((a, b) => b.item_count - a.item_count),
        totalCount: cats.reduce((sum, cat) => sum + cat.item_count, 0),
      }))
      .sort((a, b) => b.totalCount - a.totalCount);
  }

  getCategoryName(fullCategory: string): string {
    const parts = fullCategory.split('.');
    return parts[parts.length - 1] || fullCategory;
  }

  getCategoryIcon(parent: string): string {
    const icons: Record<string, string> = {
      equipments: '⚔️',
      resources: '📦',
      consumables: '🍖',
      cosmetics: '👕',
      quest: '📜',
      sublimations: '✨',
      pets: '🐾',
      mounts: '🐴',
      haven_worlds: '🏰',
      Autres: '📋',
    };
    return icons[parent] || '📋';
  }

  viewCategory(category: string): void {
    this.router.navigate(['/items'], {
      queryParams: { category },
    });
  }

  reload(): void {
    this.loadCategories();
  }
}
