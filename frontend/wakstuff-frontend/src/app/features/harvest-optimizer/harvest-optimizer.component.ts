import { Component, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  HarvestService,
  HarvestZone,
  RecommendedZone,
  OptimizeResponse,
} from '../../core/services/harvest.service';

interface ResourceInput {
  id: number;
  name: string;
  quantity: number;
}

@Component({
  selector: 'app-harvest-optimizer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './harvest-optimizer.component.html',
  styleUrls: ['./harvest-optimizer.component.scss'],
})
export class HarvestOptimizerComponent {
  // Inputs
  resourceInput = signal<string>('');
  playerLevel = signal<number>(50);
  maxZones = signal<number>(5);

  // State
  selectedResources = signal<ResourceInput[]>([]);
  loading = signal<boolean>(false);
  error = signal<string | null>(null);

  // Results
  optimizationResult = signal<OptimizeResponse | null>(null);

  constructor(private harvestService: HarvestService) {}

  addResource(): void {
    const input = this.resourceInput().trim();
    if (!input) return;

    // Parse format: "nom:quantité" ou juste "nom"
    const parts = input.split(':');
    const name = parts[0].trim();
    const quantity = parts.length > 1 ? parseInt(parts[1], 10) || 1 : 1;

    // Ajouter à la liste (ID fictif pour l'instant)
    const newResource: ResourceInput = {
      id: Date.now(), // Temporaire
      name,
      quantity,
    };

    this.selectedResources.update((resources) => [...resources, newResource]);
    this.resourceInput.set('');
  }

  removeResource(index: number): void {
    this.selectedResources.update((resources) => resources.filter((_, i) => i !== index));
  }

  clearAll(): void {
    this.selectedResources.set([]);
    this.optimizationResult.set(null);
    this.error.set(null);
  }

  optimize(): void {
    const resources = this.selectedResources();
    if (resources.length === 0) {
      this.error.set('Veuillez ajouter au moins une ressource');
      return;
    }

    this.loading.set(true);
    this.error.set(null);

    // Utiliser les IDs des ressources (ici fictifs, à mapper avec vraies données)
    const resourceIds = resources.map((r) => r.id);

    this.harvestService
      .optimizeRoute({
        resource_ids: resourceIds,
        player_level: this.playerLevel(),
        max_zones: this.maxZones(),
      })
      .subscribe({
        next: (result: OptimizeResponse) => {
          this.optimizationResult.set(result);
          this.loading.set(false);
        },
        error: (err: any) => {
          this.error.set("Erreur lors de l'optimisation: " + err.message);
          this.loading.set(false);
        },
      });
  }

  exportItinerary(): void {
    const result = this.optimizationResult();
    if (!result) return;

    let text = '=== ITINÉRAIRE DE RÉCOLTE ===\n\n';
    text += `Niveau du joueur: ${this.playerLevel()}\n`;
    text += `Ressources demandées: ${result.resources_requested}\n`;
    text += `Ressources couvertes: ${result.resources_covered}\n`;
    text += `Distance totale: ${result.total_distance.toFixed(2)} unités\n\n`;
    text += `Parcours: ${result.itinerary}\n\n`;
    text += '=== ZONES RECOMMANDÉES ===\n\n';

    result.recommended_zones.forEach((rz: RecommendedZone, index: number) => {
      text += `${index + 1}. ${rz.zone.name}\n`;
      text += `   Niveau: ${rz.zone.level_range[0]}-${rz.zone.level_range[1]}\n`;
      text += `   Efficacité: ${(rz.efficiency * 100).toFixed(0)}%\n`;
      text += `   Ressources: ${rz.matched_resources.length}\n`;
      if (rz.zone.description) {
        text += `   Description: ${rz.zone.description}\n`;
      }
      if (rz.distance_to_next) {
        text += `   Distance vers suivant: ${rz.distance_to_next.toFixed(2)} unités\n`;
      }
      text += '\n';
    });

    // Télécharger le fichier
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `itineraire-recolte-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  getEfficiencyClass(efficiency: number): string {
    if (efficiency >= 0.8) return 'high';
    if (efficiency >= 0.5) return 'medium';
    return 'low';
  }

  getJobIcon(skillId: number): string {
    const icons: { [key: number]: string } = {
      64: '🌾', // Paysan
      71: '🪵', // Forestier
      72: '🌿', // Herboriste
      73: '⛏️', // Mineur
      75: '🎣', // Pêcheur
    };
    return icons[skillId] || '❓';
  }
}
