import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import {
  CraftFavoritesService,
  SavedCraftList,
} from '../../../core/services/craft-favorites.service';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-my-crafts',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './my-crafts.component.html',
  styleUrl: './my-crafts.component.scss',
})
export class MyCraftsComponent {
  constructor(private craftFavorites: CraftFavoritesService, private router: Router) {}

  get craftLists() {
    return this.craftFavorites.craftLists;
  }

  viewCraft(craftList: SavedCraftList): void {
    this.router.navigate(['/craft/calculator', craftList.recipeId], {
      queryParams: {
        quantity: craftList.quantity,
        maxDepth: craftList.maxDepth,
      },
    });
  }

  renameCraft(craftList: SavedCraftList): void {
    const newName = prompt('Nouveau nom:', craftList.name);
    if (newName && newName.trim()) {
      this.craftFavorites.renameCraftList(craftList.id, newName.trim());
    }
  }

  duplicateCraft(craftList: SavedCraftList): void {
    const duplicate = this.craftFavorites.duplicateCraftList(craftList.id);
    if (duplicate) {
      alert(`✅ Craft list "${duplicate.name}" créée !`);
    }
  }

  deleteCraft(craftList: SavedCraftList): void {
    if (confirm(`Supprimer la craft list "${craftList.name}" ?`)) {
      this.craftFavorites.deleteCraftList(craftList.id);
    }
  }

  exportAll(): void {
    const json = this.craftFavorites.exportToJSON();
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'wakstuff-craft-lists.json';
    link.click();
    window.URL.revokeObjectURL(url);
  }

  importFromFile(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';

    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (event: any) => {
        const result = this.craftFavorites.importFromJSON(event.target.result);

        if (result.success) {
          alert(`✅ ${result.imported} craft list(s) importée(s) !`);
        } else {
          alert(`❌ Erreur lors de l'import:\n${result.errors.join('\n')}`);
        }
      };
      reader.readAsText(file);
    };

    input.click();
  }

  clearAll(): void {
    if (confirm('⚠️ Supprimer TOUTES les craft lists sauvegardées ?')) {
      this.craftFavorites.clearAll();
      alert('✅ Toutes les craft lists ont été supprimées');
    }
  }

  getItemIconUrl(itemId: number): string {
    return `${environment.apiUrl}/proxy/icon/${itemId}`;
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
