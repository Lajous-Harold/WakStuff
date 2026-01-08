import {
  Component,
  OnInit,
  ChangeDetectionStrategy,
  signal,
  computed,
  effect,
  ElementRef,
  viewChildren,
  afterNextRender,
  Injector,
} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
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

  // Valeur de recherche synchronisée avec la barre de recherche
  searchValue = signal<string>('');

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
    private router: Router,
    private route: ActivatedRoute,
    private injector: Injector
  ) {
    // Effect pour synchroniser les valeurs des inputs avec le signal filters
    afterNextRender(
      () => {
        effect(
          () => {
            const currentFilters = this.filters();
            this.syncInputsWithFilters(currentFilters);
          },
          { injector: this.injector }
        );
      },
      { injector: this.injector }
    );
  }

  ngOnInit(): void {
    // Restaurer les filtres depuis les query params
    this.route.queryParams.subscribe((params) => {
      const filters: ItemFilters = {
        page: params['page'] ? Number(params['page']) : 1,
        per_page: params['per_page'] ? Number(params['per_page']) : 25,
        search: params['search'] || undefined,
        equipment_type_id: params['equipment_type_id'] || undefined,
        rarity: params['rarity'] ? Number(params['rarity']) : undefined,
        level_min: params['level_min'] ? Number(params['level_min']) : undefined,
        level_max: params['level_max'] ? Number(params['level_max']) : undefined,
      };
      this.filters.set(filters);

      // Synchroniser la valeur de recherche avec la barre de recherche
      this.searchValue.set(params['search'] || '');
    });

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

  private updateUrl(): void {
    // Créer les query params à partir des filtres
    const queryParams: any = {};
    const currentFilters = this.filters();

    if (currentFilters.page && currentFilters.page !== 1) {
      queryParams['page'] = currentFilters.page;
    }
    if (currentFilters.per_page && currentFilters.per_page !== 25) {
      queryParams['per_page'] = currentFilters.per_page;
    }
    if (currentFilters.search) {
      queryParams['search'] = currentFilters.search;
    }
    if (currentFilters.equipment_type_id) {
      queryParams['equipment_type_id'] = currentFilters.equipment_type_id;
    }
    if (currentFilters.rarity !== undefined) {
      queryParams['rarity'] = currentFilters.rarity;
    }
    if (currentFilters.level_min) {
      queryParams['level_min'] = currentFilters.level_min;
    }
    if (currentFilters.level_max) {
      queryParams['level_max'] = currentFilters.level_max;
    }

    // Mettre à jour l'URL sans recharger le composant
    // Ne pas utiliser 'merge' pour permettre la suppression des paramètres vides
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams,
      replaceUrl: true,
    });
  }

  loadItems(): void {
    this.loading.set(true);
    this.error.set(null);

    // Mettre à jour l'URL avec les filtres actuels
    this.updateUrl();

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
    // Si la query est vide, la mettre à undefined pour la retirer de l'URL
    const searchValue = query.trim() || undefined;
    this.filters.update((f) => ({ ...f, search: searchValue, page: 1 }));
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
    const rawValue = select.value;
    // Garder en string si c'est une catégorie groupée (weapon_1h, weapon_2h, etc.)
    // Convertir en number si c'est un ID numérique
    const value = rawValue ? (isNaN(Number(rawValue)) ? rawValue : Number(rawValue)) : undefined;
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

  onSortByChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.filters.update((f) => ({ ...f, sort_by: select.value as any, page: 1 }));
    this.loadItems();
  }

  onSortOrderChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.filters.update((f) => ({ ...f, sort_order: select.value as any, page: 1 }));
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

  hasActiveFilters(): boolean {
    const f = this.filters();
    return !!(
      f.search ||
      f.equipment_type_id ||
      f.rarity !== undefined ||
      f.level_min ||
      f.level_max ||
      (f.sort_by && f.sort_by !== 'level') ||
      (f.sort_order && f.sort_order !== 'asc')
    );
  }

  clearAllFilters(): void {
    this.searchValue.set('');
    this.filters.set({
      page: 1,
      per_page: 25,
      sort_by: 'level',
      sort_order: 'asc',
    });
    this.loadItems();
  }

  private syncInputsWithFilters(filters: ItemFilters): void {
    // Synchroniser equipment type select
    const equipmentSelect = document.getElementById('equipment-type') as HTMLSelectElement;
    if (equipmentSelect) {
      equipmentSelect.value = filters.equipment_type_id?.toString() || '';
    }

    // Synchroniser rarity select
    const raritySelect = document.getElementById('rarity') as HTMLSelectElement;
    if (raritySelect) {
      raritySelect.value = filters.rarity !== undefined ? filters.rarity.toString() : '';
    }

    // Synchroniser level min input
    const levelMinInput = document.getElementById('level-min') as HTMLInputElement;
    if (levelMinInput) {
      levelMinInput.value = filters.level_min?.toString() || '';
    }

    // Synchroniser level max input
    const levelMaxInput = document.getElementById('level-max') as HTMLInputElement;
    if (levelMaxInput) {
      levelMaxInput.value = filters.level_max?.toString() || '';
    }
  }
}
