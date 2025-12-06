import { Component, OnInit, ChangeDetectionStrategy, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { ResourcesService, ResourceFilters } from '../../../core/services/resources.service';
import { ImportStatusService } from '../../../core/services/import-status.service';
import { Resource, ResourceType } from '../../../core/models';
import {
  LoadingSpinnerComponent,
  ErrorMessageComponent,
  PaginationComponent,
  PaginationConfig,
  SearchBarComponent,
} from '../../../shared/components';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-resources-list',
  standalone: true,
  imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    PaginationComponent,
    SearchBarComponent,
    EmptyStateComponent,
  ],
  templateUrl: './resources-list.component.html',
  styleUrl: './resources-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourcesListComponent implements OnInit {
  resources = signal<Resource[]>([]);
  resourceTypes = signal<ResourceType[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);
  hasData = signal(true);

  filters = signal<ResourceFilters>({
    page: 1,
    per_page: 25,
  });

  totalItems = signal(0);
  totalPages = signal(0);

  paginationConfig = computed<PaginationConfig>(() => ({
    currentPage: this.filters().page || 1,
    totalPages: this.totalPages(),
    pageSize: this.filters().per_page || 25,
    totalItems: this.totalItems(),
  }));

  constructor(
    private resourcesService: ResourcesService,
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
          this.resources.set([]);
          this.totalItems.set(0);
          this.totalPages.set(0);
          this.loading.set(false);
          return;
        }
        // Des données existent, charger normalement
        this.loadResourceTypes();
        this.loadResources();
      },
      error: () => {
        this.hasData.set(false);
        this.loading.set(false);
      },
    });
  }

  loadResourceTypes(): void {
    this.resourcesService.getResourceTypes().subscribe({
      next: (response) => {
        this.resourceTypes.set(response.types);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des types de ressources', err);
      },
    });
  }

  loadResources(): void {
    this.loading.set(true);
    this.error.set(null);

    this.resourcesService.getResources(this.filters()).subscribe({
      next: (response) => {
        this.resources.set(response.resources);
        this.totalItems.set(response.total);
        this.totalPages.set(response.total_pages);
        this.hasData.set(response.total > 0 || !!this.filters().search);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Erreur lors du chargement des ressources', err);
        this.error.set('Erreur lors du chargement des ressources');
        this.loading.set(false);
      },
    });
  }

  onSearch(query: string): void {
    this.filters.update((f) => ({ ...f, search: query, page: 1 }));
    this.loadResources();
  }

  onPageChange(page: number): void {
    this.filters.update((f) => ({ ...f, page }));
    this.loadResources();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(pageSize: number): void {
    this.filters.update((f) => ({ ...f, per_page: pageSize, page: 1 }));
    this.loadResources();
  }

  viewDetails(wakfuId: number): void {
    this.router.navigate(['/resources', wakfuId]);
  }
}
