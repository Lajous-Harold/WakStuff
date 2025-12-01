import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize, debounceTime, distinctUntilChanged, Subject } from 'rxjs';
import { ItemsService, WakstuffItem } from '../../core/services/items.service';
import {
  WakfuDataService,
  CraftCalculation,
  CraftTreeItem,
} from '../../core/services/wakfu-data.service';

@Component({
  selector: 'app-craft-calculator',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './craft-calculator.html',
  styleUrls: ['./craft-calculator.scss'],
})
export class CraftCalculator implements OnInit {
  // Recherche d'item
  searchQuery = '';
  searchResults: WakstuffItem[] = [];
  searching = false;
  showSearchResults = false;
  private searchSubject = new Subject<string>();

  // Item sélectionné et quantité
  selectedItem: WakstuffItem | null = null;
  quantity = 1;

  // Résultat du calcul
  calculation: CraftCalculation | null = null;
  calculating = false;
  error: string | null = null;

  // Affichage
  expandedNodes = new Set<string>();

  constructor(
    private itemsService: ItemsService,
    private wakfuDataService: WakfuDataService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Debounce pour la recherche
    this.searchSubject.pipe(debounceTime(300), distinctUntilChanged()).subscribe((query) => {
      this.performSearch(query);
    });
  }

  onSearchInput(): void {
    const query = this.searchQuery.trim();
    if (query.length < 2) {
      this.searchResults = [];
      this.showSearchResults = false;
      return;
    }
    this.searchSubject.next(query);
  }

  private performSearch(query: string): void {
    if (!query || query.length < 2) {
      return;
    }

    this.searching = true;
    this.error = null;

    this.itemsService
      .list({ search: query, limit: 10 })
      .pipe(
        finalize(() => {
          this.searching = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (response) => {
          this.searchResults = response.items;
          this.showSearchResults = true;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = 'Erreur lors de la recherche';
          this.searchResults = [];
          this.cdr.detectChanges();
        },
      });
  }

  selectItem(item: WakstuffItem): void {
    this.selectedItem = item;
    this.searchQuery = item.name;
    this.showSearchResults = false;
    this.searchResults = [];
    this.calculation = null;
    this.error = null;
  }

  clearSelection(): void {
    this.selectedItem = null;
    this.searchQuery = '';
    this.calculation = null;
    this.error = null;
  }

  calculateCraft(): void {
    if (!this.selectedItem || this.quantity < 1) {
      this.error = 'Veuillez sélectionner un item et une quantité valide';
      return;
    }

    this.calculating = true;
    this.error = null;

    this.wakfuDataService
      .calculateCraft(this.selectedItem.wakfu_id, this.quantity)
      .pipe(
        finalize(() => {
          this.calculating = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (result) => {
          this.calculation = result;
          this.expandedNodes.clear();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = err?.error?.error || 'Erreur lors du calcul du craft';
          this.calculation = null;
          this.cdr.detectChanges();
        },
      });
  }

  toggleNode(nodeId: string): void {
    if (this.expandedNodes.has(nodeId)) {
      this.expandedNodes.delete(nodeId);
    } else {
      this.expandedNodes.add(nodeId);
    }
  }

  isNodeExpanded(nodeId: string): boolean {
    return this.expandedNodes.has(nodeId);
  }

  getNodeId(node: CraftTreeItem, prefix: string = ''): string {
    return `${prefix}-${node.item_id}-${node.quantity_needed}`;
  }

  hasRecipe(node: CraftTreeItem): boolean {
    return !!node.recipe && node.recipe.ingredients && node.recipe.ingredients.length > 0;
  }

  viewItemDetails(itemId: number): void {
    this.router.navigate(['/items', itemId]);
  }

  getTotalResourcesList(): Array<{ name: string; quantity: number }> {
    if (!this.calculation || !this.calculation.total_base_resources) {
      return [];
    }

    return Object.entries(this.calculation.total_base_resources)
      .map(([name, data]) => ({
        name,
        quantity: data.quantity,
      }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }
}
