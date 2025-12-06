import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { StatsService } from '../../core/services/stats.service';
import { ImportStatusService } from '../../core/services/import-status.service';
import { GlobalStats, GlobalSearchResult, ImportBatch } from '../../core/models';
import {
  LoadingSpinnerComponent,
  ErrorMessageComponent,
  SearchBarComponent,
  StatCardComponent,
} from '../../shared/components';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    SearchBarComponent,
    StatCardComponent,
    DatePipe,
    EmptyStateComponent,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent implements OnInit {
  stats = signal<GlobalStats | null>(null);
  recentImports = signal<ImportBatch[]>([]);
  searchResults = signal<GlobalSearchResult | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);
  searching = signal(false);
  hasData = signal(true);

  constructor(
    private statsService: StatsService,
    private importStatusService: ImportStatusService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Vérifier d'abord si des données ont été importées
    this.importStatusService.checkImportStatus().subscribe({
      next: (hasData) => {
        if (!hasData) {
          // Pas de données importées
          this.hasData.set(false);
          this.stats.set({
            total_items: 0,
            total_resources: 0,
            total_recipes: 0,
            total_job_items: 0,
            items_by_rarity: {},
            recipes_by_category: {},
            level_distribution: {},
          });
          this.loading.set(false);
          return;
        }
        // Des données existent, charger le dashboard
        this.loadDashboard();
      },
      error: () => {
        this.hasData.set(false);
        this.loading.set(false);
      },
    });
  }

  loadDashboard(): void {
    this.loading.set(true);
    this.error.set(null);

    this.statsService.getOverview().subscribe({
      next: (data) => {
        this.stats.set(data);
        this.statsService.stats.set(data);
        const totalData =
          (data.total_items || 0) + (data.total_resources || 0) + (data.total_recipes || 0);
        this.hasData.set(totalData > 0);
        this.loadRecentImports();
      },
      error: (err) => {
        console.error('Erreur lors du chargement des statistiques', err);
        this.error.set('Erreur lors du chargement des statistiques');
        this.loading.set(false);
      },
    });
  }

  loadRecentImports(): void {
    this.statsService.getRecentImports(5).subscribe({
      next: (data) => {
        this.recentImports.set(data.batches);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des imports récents', err);
        this.loading.set(false);
      },
    });
  }

  onSearch(query: string): void {
    if (!query.trim()) {
      this.searchResults.set(null);
      return;
    }

    this.searching.set(true);
    this.statsService.globalSearch(query, 20).subscribe({
      next: (results) => {
        this.searchResults.set(results);
        this.searching.set(false);
      },
      error: (err) => {
        console.error('Erreur recherche globale', err);
        this.searching.set(false);
      },
    });
  }

  navigateTo(type: 'item' | 'recipe' | 'resource', wakfuId: number): void {
    if (type === 'item') {
      this.router.navigate(['/items', wakfuId]);
    } else if (type === 'recipe') {
      this.router.navigate(['/craft', wakfuId]);
    } else if (type === 'resource') {
      this.router.navigate(['/resources', wakfuId]);
    }
  }

  goToPage(page: string): void {
    this.router.navigate([`/${page}`]);
  }
}
