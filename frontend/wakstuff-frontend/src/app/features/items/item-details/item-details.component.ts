import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ItemsService } from '../../../core/services/items.service';
import { ImportStatusService } from '../../../core/services/import-status.service';
import { ItemDetail } from '../../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../../shared/components';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-item-details',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent, EmptyStateComponent],
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
      next: (item) => {
        this.item.set(item);
        this.hasData.set(true);
        this.loading.set(false);
      },
      error: (err) => {
        // Ne pas logger les 404, c'est juste un item introuvable
        if (err.status === 404) {
          this.error.set('Item non trouvé');
        } else {
          console.error('Erreur lors du chargement de l\'item', err);
          this.error.set('Erreur lors du chargement de l\'item');
        }
        this.loading.set(false);
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/items']);
  }

  getRarityClass(rarity: number): string {
    const rarities = [
      'common',
      'common',
      'unusual',
      'rare',
      'mythical',
      'legendary',
      'relic',
      'souvenir',
    ];
    return rarities[rarity] || 'common';
  }

  getRarityLabel(rarity: number): string {
    const labels = [
      'Commun',
      'Commun',
      'Inhabituel',
      'Rare',
      'Mythique',
      'Légendaire',
      'Relique',
      'Souvenir',
    ];
    return labels[rarity] || 'Commun';
  }
}
