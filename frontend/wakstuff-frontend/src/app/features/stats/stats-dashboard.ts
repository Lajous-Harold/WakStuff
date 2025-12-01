import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { finalize } from 'rxjs';
import { WakfuDataService, WakfuStats } from '../../core/services/wakfu-data.service';

@Component({
  selector: 'app-stats-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stats-dashboard.html',
  styleUrls: ['./stats-dashboard.scss'],
})
export class StatsDashboard implements OnInit {
  stats: WakfuStats | null = null;
  loading = false;
  error: string | null = null;

  constructor(
    private wakfuDataService: WakfuDataService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadStats();
  }

  private loadStats(): void {
    this.loading = true;
    this.error = null;

    this.wakfuDataService
      .getStats()
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (stats: WakfuStats) => {
          this.stats = stats;
          this.cdr.detectChanges();
        },
        error: (err: any) => {
          this.error = err?.message ?? 'Erreur lors du chargement des statistiques';
          this.cdr.detectChanges();
        },
      });
  }

  getRarityEntries(): Array<{ rarity: string; count: number }> {
    if (!this.stats?.items?.by_rarity) return [];
    return Object.entries(this.stats.items.by_rarity)
      .map(([rarity, count]) => ({ rarity, count: count as number }))
      .sort((a, b) => b.count - a.count);
  }

  getCategoryEntries(): Array<{ category: string; count: number }> {
    if (!this.stats?.items?.by_category) return [];
    return Object.entries(this.stats.items.by_category)
      .map(([category, count]) => ({ category, count: count as number }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);
  }

  formatCategoryName(fullCategory: string): string {
    const parts = fullCategory.split('.');
    return parts[parts.length - 1] || fullCategory;
  }

  getRarityClass(rarity: string): string {
    return `rarity-${rarity.toLowerCase()}`;
  }

  getRarityPercentage(count: number): number {
    if (!this.stats?.items?.total) return 0;
    return Math.round((count / this.stats.items.total) * 100);
  }

  getCategoryPercentage(count: number): number {
    if (!this.stats?.items?.total) return 0;
    return Math.round((count / this.stats.items.total) * 100);
  }

  viewCategory(category: string): void {
    this.router.navigate(['/items'], {
      queryParams: { category },
    });
  }

  viewRarity(rarity: string): void {
    this.router.navigate(['/items'], {
      queryParams: { rarity },
    });
  }

  reload(): void {
    this.loadStats();
  }
}
