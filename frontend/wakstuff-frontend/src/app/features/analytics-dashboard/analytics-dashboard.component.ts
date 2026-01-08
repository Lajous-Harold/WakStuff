import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  AnalyticsService,
  TopResource,
  TopCraft,
  JobAnalytics,
  LevelDistribution,
  RarityDistribution,
  ComplexCraft,
} from '../../core/services/analytics.service';
import { StatsService } from '../../core/services/stats.service';
import { environment } from '../../core/config';

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './analytics-dashboard.component.html',
  styleUrls: ['./analytics-dashboard.component.scss'],
})
export class AnalyticsDashboardComponent implements OnInit {
  // KPIs
  totalItems = signal<number>(0);
  totalRecipes = signal<number>(0);
  totalResources = signal<number>(0);
  totalJobItems = signal<number>(0);

  // Analytics data
  topResources = signal<TopResource[]>([]);
  topCrafts = signal<TopCraft[]>([]);
  jobStats = signal<JobAnalytics[]>([]);
  levelDist = signal<{ items: LevelDistribution[]; recipes: LevelDistribution[] } | null>(null);
  rarityDist = signal<RarityDistribution[]>([]);
  complexCrafts = signal<ComplexCraft[]>([]);

  loading = signal<boolean>(false);
  error = signal<string | null>(null);

  constructor(private analyticsService: AnalyticsService, private statsService: StatsService) {}

  ngOnInit(): void {
    this.loadAllData();
  }

  loadAllData(): void {
    this.loading.set(true);
    this.error.set(null);

    // KPIs
    this.statsService.getOverview().subscribe({
      next: (data) => {
        this.totalItems.set(data.total_items);
        this.totalRecipes.set(data.total_recipes);
        this.totalResources.set(data.total_resources);
        this.totalJobItems.set(data.total_job_items);
      },
      error: (err) => console.error('Error loading KPIs', err),
    });

    // Top resources
    this.analyticsService.getTopResources(10).subscribe({
      next: (data) => this.topResources.set(data.top_resources),
      error: (err) => console.error('Error loading top resources', err),
    });

    // Top crafts
    this.analyticsService.getTopCrafts(10).subscribe({
      next: (data) => this.topCrafts.set(data.top_crafts),
      error: (err) => console.error('Error loading top crafts', err),
    });

    // Job stats
    this.analyticsService.getAnalyticsByJob().subscribe({
      next: (data) => this.jobStats.set(data.jobs),
      error: (err) => console.error('Error loading job stats', err),
    });

    // Level distribution
    this.analyticsService.getLevelDistribution().subscribe({
      next: (data) => this.levelDist.set(data),
      error: (err) => console.error('Error loading level dist', err),
    });

    // Rarity distribution
    this.analyticsService.getRarityDistribution().subscribe({
      next: (data) => this.rarityDist.set(data.distribution),
      error: (err) => console.error('Error loading rarity dist', err),
    });

    // Complex crafts
    this.analyticsService.getComplexCrafts(10).subscribe({
      next: (data) => {
        this.complexCrafts.set(data.complex_crafts);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading complex crafts', err);
        this.loading.set(false);
      },
    });
  }

  getItemImageUrl(iconGfxId: number | null | undefined): string {
    if (!iconGfxId) return '';
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  getItemName(item: any): string {
    if (!item) return 'Inconnu';
    if (typeof item.title === 'object' && item.title !== null) {
      return item.title.fr || item.title.en || 'Inconnu';
    }
    return item.title || item.name || 'Inconnu';
  }

  getRarityClass(rarity: number): string {
    const rarityMap: { [key: number]: string } = {
      0: 'common',
      1: 'rare',
      2: 'mythical',
      3: 'legendary',
      4: 'relic',
      5: 'souvenir',
      7: 'epic',
    };
    return rarityMap[rarity] || 'common';
  }
}
