import { Component, OnInit, ChangeDetectionStrategy, signal, computed } from '@angular/core';
import { Router } from '@angular/router';
import { ItemsService, ItemFilters } from '../../../core/services/items.service';
import { ImportStatusService } from '../../../core/services/import-status.service';
import { Item } from '../../../core/models';
import {
  LoadingSpinnerComponent,
  ErrorMessageComponent,
  PaginationComponent,
  PaginationConfig,
  SearchBarComponent,
} from '../../../shared/components';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import { environment } from '../../../core/config';
import { cleanWakfuText } from '../../../shared/utils';

@Component({
  selector: 'app-items-list',
  standalone: true,
  imports: [
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    PaginationComponent,
    SearchBarComponent,
    EmptyStateComponent,
  ],
  templateUrl: './items-list.component.html',
  styleUrl: './items-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ItemsListComponent implements OnInit {
  items = signal<Item[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);
  hasData = signal(true);
  equipmentTypes = signal<any[]>([]);

  // Filtres
  filters = signal<ItemFilters>({
    page: 1,
    per_page: 25,
  });

  // Pagination
  totalItems = signal(0);
  totalPages = signal(0);

  paginationConfig = computed<PaginationConfig>(() => ({
    currentPage: this.filters().page || 1,
    totalPages: this.totalPages(),
    pageSize: this.filters().per_page || 25,
    totalItems: this.totalItems(),
  }));

  constructor(
    private itemsService: ItemsService,
    private importStatusService: ImportStatusService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadEquipmentTypes();
    this.loadItems();
  }

  loadEquipmentTypes(): void {
    this.itemsService.getEquipmentTypes().subscribe({
      next: (response) => {
        this.equipmentTypes.set(response.equipment_types || []);
      },
      error: (err) => {
        console.error("Erreur lors du chargement des types d'équipement", err);
      },
    });
  }

  loadItems(): void {
    this.loading.set(true);
    this.error.set(null);

    // Vérifier d'abord si des données ont été importées
    this.importStatusService.checkImportStatus().subscribe({
      next: (hasData) => {
        if (!hasData) {
          // Pas de données importées, afficher l'état vide
          this.hasData.set(false);
          this.items.set([]);
          this.totalItems.set(0);
          this.totalPages.set(0);
          this.loading.set(false);
          return;
        }

        // Des données existent, on peut charger les items
        this.itemsService.getItems(this.filters()).subscribe({
          next: (response) => {
            this.items.set(response.items);
            this.totalItems.set(response.total);
            this.totalPages.set(response.pages);
            this.hasData.set(response.total > 0 || !!this.filters().search);
            this.loading.set(false);
          },
          error: (err) => {
            console.error('Erreur lors du chargement des items', err);
            this.error.set('Erreur lors du chargement des items');
            this.loading.set(false);
          },
        });
      },
      error: (err) => {
        console.error('Erreur lors de la vérification du statut', err);
        this.hasData.set(false);
        this.loading.set(false);
      },
    });
  }

  onSearch(query: string): void {
    this.filters.update((f) => ({ ...f, search: query, page: 1 }));
    this.loadItems();
  }

  onPageChange(page: number): void {
    this.filters.update((f) => ({ ...f, page }));
    this.loadItems();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(pageSize: number): void {
    this.filters.update((f) => ({ ...f, per_page: pageSize, page: 1 }));
    this.loadItems();
  }

  onEquipmentTypeChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const value = select.value ? Number(select.value) : undefined;
    this.filters.update((f) => ({ ...f, equipment_type_id: value, page: 1 }));
    this.loadItems();
  }

  onRarityChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    const value = select.value ? Number(select.value) : undefined;
    this.filters.update((f) => ({ ...f, rarity: value, page: 1 }));
    this.loadItems();
  }

  onLevelMinChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value ? Number(input.value) : undefined;
    this.filters.update((f) => ({ ...f, level_min: value, page: 1 }));
    this.loadItems();
  }

  onLevelMaxChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value ? Number(input.value) : undefined;
    this.filters.update((f) => ({ ...f, level_max: value, page: 1 }));
    this.loadItems();
  }

  getItemImageUrl(iconGfxId: number): string {
    // Utiliser le proxy backend pour éviter les problèmes CORS avec le CDN Ankama
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  viewDetails(wakfuId: number): void {
    this.router.navigate(['/items', wakfuId]);
  }

  getRarityClass(rarity: number): string {
    const rarities = [
      'common', // 0 - Ancien objet (blanc)
      'unusual', // 1 - Inhabituel (blanc)
      'rare', // 2 - Rare (cyan)
      'mythical', // 3 - Mythique (orange)
      'legendary', // 4 - Légendaire (jaune)
      'relic', // 5 - Relique (violet) - property 8
      'souvenir', // 6 - Souvenir (cyan)
      'epic', // 7 - Épique (rose) - property 12
    ];
    return rarities[rarity] || 'common';
  }

  getRarityLabel(rarity: number): string {
    const labels = [
      'Ancien objet', // 0 - Blanc
      'Inhabituel', // 1 - Blanc
      'Rare', // 2 - Cyan
      'Mythique', // 3 - Orange
      'Légendaire', // 4 - Jaune
      'Relique', // 5 - Violet (property 8)
      'Souvenir', // 6 - Cyan
      'Épique', // 7 - Rose (property 12)
    ];
    return labels[rarity] || 'Commun';
  }

  getCleanText(text: string | null | undefined): string {
    return cleanWakfuText(text);
  }
}
