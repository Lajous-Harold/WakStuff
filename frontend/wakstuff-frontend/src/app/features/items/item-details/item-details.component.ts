import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { ItemsService } from '../../../core/services/items.service';
import { ImportStatusService } from '../../../core/services/import-status.service';
import { ItemDetail } from '../../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../../shared/components';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';
import {
  cleanWakfuText,
  cleanWakfuStatDescription,
  getRarityColorClass,
} from '../../../shared/utils';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-item-details',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    EmptyStateComponent,
  ],
  templateUrl: './item-details.component.html',
  styleUrl: './item-details.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ItemDetailsComponent implements OnInit {
  item = signal<ItemDetail | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);
  hasData = signal(true);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private location: Location,
    private itemsService: ItemsService,
    private importStatusService: ImportStatusService
  ) {}

  ngOnInit(): void {
    // Vérifier d'abord si des données ont été importées
    this.importStatusService.checkImportStatus().subscribe({
      next: (hasData) => {
        if (!hasData) {
          // Pas de données importées
          this.hasData.set(false);
          this.loading.set(false);
          return;
        }

        // Des données existent, charger normalement
        this.route.params.subscribe((params) => {
          const wakfuId = Number(params['wakfuId']);
          if (wakfuId) {
            this.loadItem(wakfuId);
          }
        });
      },
      error: () => {
        this.hasData.set(false);
        this.loading.set(false);
      },
    });
  }

  loadItem(wakfuId: number): void {
    this.loading.set(true);
    this.error.set(null);

    this.itemsService.getItemDetail(wakfuId).subscribe({
      next: (response) => {
        this.item.set(response.item);
        this.hasData.set(true);
        this.loading.set(false);
      },
      error: (err) => {
        // Ne pas logger les 404, c'est juste un item introuvable
        if (err.status === 404) {
          this.error.set('Item non trouvé');
        } else {
          console.error("Erreur lors du chargement de l'item", err);
          this.error.set("Erreur lors du chargement de l'item");
        }
        this.loading.set(false);
      },
    });
  }

  goBack(): void {
    // Utiliser location.back() pour retourner à la page précédente avec son état
    this.location.back();
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

  getItemImageUrl(iconGfxId: number | undefined): string {
    if (!iconGfxId) return '';
    // Utiliser le proxy backend pour éviter les problèmes CORS avec le CDN Ankama
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  cleanText(text: string | null | undefined): string {
    return cleanWakfuText(text);
  }

  cleanStatLabel(label: string | null | undefined): string {
    return cleanWakfuStatDescription(label);
  }

  isExclusiveProperty(wakfuId: number): boolean {
    // Properties 8 et 12 sont les propriétés exclusives (Relique/Épique)
    return wakfuId === 8 || wakfuId === 12;
  }

  getExclusivePropertyLabel(wakfuId: number): string {
    if (wakfuId === 8) return 'Item Relique Exclusif';
    if (wakfuId === 12) return 'Item Épique Exclusif';
    return '';
  }

  getExclusivePropertyDescription(): string {
    return "Il ne peut y avoir qu'un seul item ayant cette propriété équipé à la fois.";
  }

  getStatisticsArray(): {
    key: string;
    stat: { label: string; value: number; action_id: number };
  }[] {
    const item = this.item();
    if (!item?.statistics) return [];

    return Object.entries(item.statistics).map(([key, stat]) => ({ key, stat }));
  }

  formatStatValue(stat: { value: number; action_id: number }): string {
    // Formater simplement la valeur (le label contient déjà l'unité si nécessaire)
    if (stat.value > 0) {
      return `+${stat.value}`;
    }
    return `${stat.value}`;
  }

  getJobTypeName(jobItem: any): string {
    if (jobItem.harvest_skill_id) {
      const skills: { [key: number]: string } = {
        64: 'Paysan',
        71: 'Forestier',
        72: 'Herboriste',
        73: 'Mineur',
        75: 'Pêcheur',
      };
      return skills[jobItem.harvest_skill_id] || 'Métier de récolte';
    }
    if (jobItem.craft_skill_id) {
      return 'Métier de craft';
    }
    return 'Item de métier';
  }
}
