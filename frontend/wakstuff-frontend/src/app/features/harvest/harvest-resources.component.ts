import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HarvestService } from '../../core/services/harvest.service';
import { HarvestResource, HarvestJob } from '../../core/models/harvest.model';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../shared/components/error-message/error-message.component';

@Component({
  selector: 'app-harvest-resources',
  standalone: true,
  imports: [CommonModule, FormsModule, LoadingSpinnerComponent, ErrorMessageComponent],
  templateUrl: './harvest-resources.component.html',
  styleUrl: './harvest-resources.component.scss',
})
export class HarvestResourcesComponent implements OnInit {
  loading = signal(false);
  error = signal<string | null>(null);
  
  resources = signal<HarvestResource[]>([]);
  selectedSkillId = signal<number | null>(null);
  searchQuery = signal('');
  
  // Définition des métiers de récolte
  harvestJobs: HarvestJob[] = [
    { skill_id: 64, name: 'Paysan', icon: '🌾' },
    { skill_id: 71, name: 'Forestier', icon: '🪓' },
    { skill_id: 72, name: 'Herboriste', icon: '🌿' },
    { skill_id: 73, name: 'Mineur', icon: '⛏️' },
    { skill_id: 75, name: 'Pêcheur', icon: '🎣' },
  ];

  // Ressources filtrées
  filteredResources = computed(() => {
    let filtered = this.resources();
    
    // Filtre par métier
    if (this.selectedSkillId()) {
      filtered = filtered.filter(r => r.skill_id === this.selectedSkillId());
    }
    
    // Filtre par recherche
    const query = this.searchQuery().toLowerCase();
    if (query) {
      filtered = filtered.filter(r => r.name.toLowerCase().includes(query));
    }
    
    return filtered.sort((a, b) => a.level - b.level);
  });

  constructor(private harvestService: HarvestService) {}

  ngOnInit(): void {
    this.loadAllHarvestResources();
  }

  loadAllHarvestResources(): void {
    this.loading.set(true);
    this.error.set(null);

    this.harvestService.getHarvestResources().subscribe({
      next: (response) => {
        this.resources.set(response.resources);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Erreur lors du chargement des ressources récoltables');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  selectJob(skillId: number | null): void {
    this.selectedSkillId.set(skillId);
  }

  getJobName(skillId: number): string {
    return this.harvestJobs.find(j => j.skill_id === skillId)?.name || 'Inconnu';
  }

  getJobIcon(skillId: number): string {
    return this.harvestJobs.find(j => j.skill_id === skillId)?.icon || '❓';
  }

  getRarityClass(rarity: number): string {
    const rarityMap: Record<number, string> = {
      0: 'common',
      1: 'unusual',
      2: 'rare',
      3: 'mythical',
      4: 'legendary',
      5: 'relic',
      6: 'souvenir',
      7: 'epic',
    };
    return rarityMap[rarity] || 'common';
  }

  getIconUrl(iconId: number): string {
    return `https://wakfu.cdn.ankama.com/gamedata/1.88.2/gfx/items/${iconId}.png`;
  }

  formatDropRate(rate: number): string {
    return (rate * 100).toFixed(1) + '%';
  }
}
