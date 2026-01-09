import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ItemCompareService, type CompareResponse } from '../../core/services/item-compare.service';
import { ItemsService } from '../../core/services/items.service';
import { debounceTime, distinctUntilChanged, switchMap, of } from 'rxjs';
import { Subject } from 'rxjs';
import { cleanWakfuText, cleanWakfuStatDescription } from '../../shared/utils';
import { environment } from '../../core/config';

interface ItemOption {
  wakfu_id: number;
  name: string;
  level: number;
  rarity: number;
  icon_gfx_id: number;
  equipment_type_id?: number;
}

@Component({
  selector: 'app-item-compare',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './item-compare.html',
  styleUrl: './item-compare.scss',
})
export class ItemCompareComponent {
  private readonly compareService = inject(ItemCompareService);
  private readonly itemsService = inject(ItemsService);

  // Recherche items
  searchQuery1 = '';
  searchQuery2 = '';
  searchResults1 = signal<ItemOption[]>([]);
  searchResults2 = signal<ItemOption[]>([]);
  showDropdown1 = signal(false);
  showDropdown2 = signal(false);

  // Items sélectionnés
  selectedItem1 = signal<ItemOption | null>(null);
  selectedItem2 = signal<ItemOption | null>(null);

  // State
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly result = signal<CompareResponse | null>(null);

  // Search subjects
  private searchSubject1 = new Subject<string>();
  private searchSubject2 = new Subject<string>();

  constructor() {
    // Setup search pour item 1
    this.searchSubject1
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        switchMap((query) => {
          if (query.length < 2) {
            return of({ items: [], total: 0, page: 1, per_page: 10, pages: 0 });
          }
          return this.itemsService.getItems({ search: query, per_page: 10 });
        })
      )
      .subscribe((response) => {
        this.searchResults1.set(
          response.items.map((item) => ({
            wakfu_id: item.wakfu_id,
            name: item.title,
            level: item.level,
            rarity: item.rarity,
            icon_gfx_id: item.icon_gfx_id || 0,
            equipment_type_id: item.equipment_type_id,
          }))
        );
        this.showDropdown1.set(response.items.length > 0);
      });

    // Setup search pour item 2 - filtrer par type du premier item
    this.searchSubject2
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        switchMap((query) => {
          if (query.length < 2) {
            return of({ items: [], total: 0, page: 1, per_page: 10, pages: 0 });
          }
          const filters: any = { search: query, per_page: 10 };
          const item1 = this.selectedItem1();
          if (item1?.equipment_type_id) {
            filters.equipment_type_id = item1.equipment_type_id;
          }
          return this.itemsService.getItems(filters);
        })
      )
      .subscribe((response) => {
        this.searchResults2.set(
          response.items.map((item) => ({
            wakfu_id: item.wakfu_id,
            name: item.title,
            level: item.level,
            rarity: item.rarity,
            icon_gfx_id: item.icon_gfx_id || 0,
            equipment_type_id: item.equipment_type_id,
          }))
        );
        this.showDropdown2.set(response.items.length > 0);
      });
  }

  /**
   * Recherche item 1
   */
  onSearchInput1(): void {
    this.searchSubject1.next(this.searchQuery1);
  }

  /**
   * Recherche item 2
   */
  onSearchInput2(): void {
    this.searchSubject2.next(this.searchQuery2);
  }

  /**
   * Sélectionne item 1
   */
  selectItem1(item: ItemOption): void {
    this.selectedItem1.set(item);
    this.searchQuery1 = item.name;
    this.showDropdown1.set(false);
    // Réinitialiser item 2 si le type change
    const item2 = this.selectedItem2();
    if (item2 && item2.equipment_type_id !== item.equipment_type_id) {
      this.clearItem2();
    }
  }

  /**
   * Sélectionne item 2
   */
  selectItem2(item: ItemOption): void {
    this.selectedItem2.set(item);
    this.searchQuery2 = item.name;
    this.showDropdown2.set(false);
  }

  /**
   * Efface la sélection item 1
   */
  clearItem1(): void {
    this.selectedItem1.set(null);
    this.searchQuery1 = '';
    this.searchResults1.set([]);
    this.showDropdown1.set(false);
  }

  /**
   * Efface la sélection item 2
   */
  clearItem2(): void {
    this.selectedItem2.set(null);
    this.searchQuery2 = '';
    this.searchResults2.set([]);
    this.showDropdown2.set(false);
  }

  /**
   * Lance la comparaison
   */
  async compare(): Promise<void> {
    const item1 = this.selectedItem1();
    const item2 = this.selectedItem2();

    if (!item1 || !item2) {
      this.error.set('Veuillez sélectionner 2 items à comparer');
      return;
    }

    const ids = [item1.wakfu_id, item2.wakfu_id];

    this.loading.set(true);
    this.error.set(null);
    this.result.set(null);

    this.compareService.compareItems(ids).subscribe({
      next: (response) => {
        this.result.set(response);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.error || 'Erreur lors de la comparaison');
        this.loading.set(false);
      },
    });
  }

  /**
   * Réinitialise le formulaire
   */
  reset(): void {
    this.clearItem1();
    this.clearItem2();
    this.result.set(null);
    this.error.set(null);
  }

  /**
   * Obtient la classe CSS pour une valeur de stat
   */
  getStatClass(values: (number | null)[], index: number): string {
    return this.compareService.getStatColorClass(values, index);
  }

  /**
   * Formatte une valeur de stat
   */
  formatValue(value: number | null): string {
    return this.compareService.formatStatValue(value);
  }

  /**
   * Obtient les noms de stats triés
   */
  getStatNames(): string[] {
    const result = this.result();
    if (!result) return [];
    return Object.keys(result.stats).sort();
  }

  /**
   * Obtient l'URL de l'icône via le proxy
   */
  getItemIconUrl(iconGfxId: number): string {
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  /**
   * Nettoie le texte Wakfu (enlève les balises et placeholders)
   */
  cleanText(text: string | null | undefined): string {
    return cleanWakfuText(text);
  }

  /**
   * Nettoie les descriptions de stats
   */
  cleanStatLabel(label: string | null | undefined): string {
    return cleanWakfuStatDescription(label);
  }

  /**
   * Retourne la classe CSS pour une rareté donnée
   */
  getRarityClass(rarity: number): string {
    const rarities = [
      'common', // 0 - Ancien objet
      'unusual', // 1 - Inhabituel
      'rare', // 2 - Rare
      'mythical', // 3 - Mythique
      'legendary', // 4 - Légendaire
      'relic', // 5 - Relique
      'souvenir', // 6 - Souvenir
      'epic', // 7 - Épique
    ];
    return rarities[rarity] || 'common';
  }

  /**
   * Retourne le label d'une rareté
   */
  getRarityLabel(rarity: number): string {
    const labels = [
      'Ancien objet', // 0
      'Inhabituel', // 1
      'Rare', // 2
      'Mythique', // 3
      'Légendaire', // 4
      'Relique', // 5
      'Souvenir', // 6
      'Épique', // 7
    ];
    return labels[rarity] || 'Commun';
  }

  /**
   * Calcule le score global d'un item (somme des stats positives)
   */
  getItemScore(itemIndex: number): number {
    const result = this.result();
    if (!result) return 0;

    let score = 0;
    for (const statData of Object.values(result.stats)) {
      const value = statData.values[itemIndex];
      if (value !== null && value > 0) {
        score += value;
      }
    }
    return Math.round(score * 10) / 10;
  }

  /**
   * Trouve l'index de l'item avec le meilleur score
   */
  getBestItemIndex(): number {
    const result = this.result();
    if (!result) return -1;

    let bestIndex = 0;
    let bestScore = this.getItemScore(0);

    for (let i = 1; i < result.items.length; i++) {
      const score = this.getItemScore(i);
      if (score > bestScore) {
        bestScore = score;
        bestIndex = i;
      }
    }

    return bestIndex;
  }
}
