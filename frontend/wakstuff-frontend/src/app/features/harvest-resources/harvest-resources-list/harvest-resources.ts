import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  HarvestResourcesService,
  HarvestResource,
} from '../../../core/services/harvest-resources.service';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-harvest-resources',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './harvest-resources.html',
  styleUrl: './harvest-resources.scss',
})
export class HarvestResourcesComponent implements OnInit {
  private harvestService = inject(HarvestResourcesService);

  resources: HarvestResource[] = [];
  groupedResources: Array<{ key: string; value: HarvestResource[] }> = [];
  loading = true;
  error: string | null = null;
  totalResources = 0;

  ngOnInit() {
    this.loadResources();

    // Timeout de sécurité après 10 secondes
    setTimeout(() => {
      if (this.loading) {
        console.error('Loading timeout - forcing error state');
        this.loading = false;
        this.error = 'Timeout lors du chargement des ressources';
      }
    }, 10000);
  }

  loadResources() {
    this.loading = true;
    this.error = null;
    console.log('Starting to load harvest resources...');

    this.harvestService.getHarvestResources().subscribe({
      next: (response) => {
        console.log('Received response:', response);
        this.resources = response.resources;
        this.totalResources = response.total;
        this.groupResourcesByRarity();
        console.log('Grouped resources:', this.groupedResources);
        this.loading = false;
      },
      error: (err) => {
        console.error('Error loading harvest resources:', err);
        this.error = 'Erreur lors du chargement des ressources de récolte';
        this.loading = false;
      },
    });
  }

  groupResourcesByRarity() {
    // Les ressources n'ont pas de rareté car elles ne sont pas dans items.json
    // On les groupe par plage d'ID pour faciliter la navigation
    const groupMap = new Map<string, HarvestResource[]>();

    this.resources.forEach((resource) => {
      // Grouper par millier d'ID
      const idRange = Math.floor(resource.item_id / 1000) * 1000;
      const rangeLabel = `ID ${idRange} - ${idRange + 999}`;

      if (!groupMap.has(rangeLabel)) {
        groupMap.set(rangeLabel, []);
      }
      groupMap.get(rangeLabel)!.push(resource);
    });

    console.log('ID range groups:', Array.from(groupMap.keys()));

    // Trier chaque groupe par ID
    groupMap.forEach((group) => {
      group.sort((a, b) => a.item_id - b.item_id);
    });

    // Convertir en array triée par plage d'ID
    this.groupedResources = Array.from(groupMap.entries())
      .map(([key, value]) => ({ key, value }))
      .sort((a, b) => {
        const idA = parseInt(a.key.split(' ')[1]);
        const idB = parseInt(b.key.split(' ')[1]);
        return idA - idB;
      });
  }

  getIconUrl(iconGfxId: number | null): string {
    if (!iconGfxId) return '';
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  getRarityClass(rarity: string | null): string {
    if (!rarity) return 'rarity-unknown';
    return `rarity-${rarity.toLowerCase().replace('é', 'e').replace('è', 'e')}`;
  }

  getDropRatePercentage(dropRate: number): string {
    return `${(dropRate * 100).toFixed(0)}%`;
  }

  getQuantityDisplay(min: number, max: number): string {
    if (min === max) return `${min}`;
    return `${min}-${max}`;
  }
}
