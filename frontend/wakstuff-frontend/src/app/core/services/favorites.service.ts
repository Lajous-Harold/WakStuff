import { Injectable, signal, computed } from '@angular/core';
import { Favorite, FavoriteType, FavoritesCollection } from '../models/favorite.model';

@Injectable({
  providedIn: 'root',
})
export class FavoritesService {
  private readonly STORAGE_KEY = 'wakstuff_favorites';

  // Signals pour réactivité
  private favoritesSignal = signal<Favorite[]>([]);

  // Computed signals
  favorites = computed(() => this.favoritesSignal());
  itemFavorites = computed(() => this.favoritesSignal().filter((f) => f.type === 'item'));
  resourceFavorites = computed(() => this.favoritesSignal().filter((f) => f.type === 'resource'));
  recipeFavorites = computed(() => this.favoritesSignal().filter((f) => f.type === 'recipe'));

  count = computed(() => this.favoritesSignal().length);

  constructor() {
    this.loadFromStorage();
  }

  private loadFromStorage(): void {
    const stored = localStorage.getItem(this.STORAGE_KEY);
    if (stored) {
      try {
        const favorites = JSON.parse(stored) as Favorite[];
        this.favoritesSignal.set(favorites);
      } catch (e) {
        console.error('Erreur lors du chargement des favoris', e);
      }
    }
  }

  private saveToStorage(): void {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.favoritesSignal()));
  }

  add(type: FavoriteType, wakfu_id: number, title: string): void {
    const existing = this.favoritesSignal().find((f) => f.type === type && f.wakfu_id === wakfu_id);

    if (!existing) {
      const newFavorite: Favorite = {
        type,
        wakfu_id,
        title,
        added_at: new Date().toISOString(),
      };

      this.favoritesSignal.update((favs) => [...favs, newFavorite]);
      this.saveToStorage();
    }
  }

  remove(type: FavoriteType, wakfu_id: number): void {
    this.favoritesSignal.update((favs) =>
      favs.filter((f) => !(f.type === type && f.wakfu_id === wakfu_id))
    );
    this.saveToStorage();
  }

  isFavorite(type: FavoriteType, wakfu_id: number): boolean {
    return this.favoritesSignal().some((f) => f.type === type && f.wakfu_id === wakfu_id);
  }

  clearAll(): void {
    this.favoritesSignal.set([]);
    this.saveToStorage();
  }

  exportToJSON(): string {
    const collection: FavoritesCollection = {
      items: this.itemFavorites().map((f) => f.wakfu_id),
      resources: this.resourceFavorites().map((f) => f.wakfu_id),
      recipes: this.recipeFavorites().map((f) => f.wakfu_id),
      version: '1.0',
    };

    return JSON.stringify(collection, null, 2);
  }

  importFromJSON(json: string): void {
    try {
      const collection = JSON.parse(json) as FavoritesCollection;

      // Pour simplifier, on remplace tout
      // Dans une vraie app, on pourrait merger
      this.clearAll();

      console.log('Import de', collection);
      // TODO: Re-fetch les détails depuis l'API et ajouter
    } catch (e) {
      console.error("Erreur lors de l'import", e);
      throw new Error('Format JSON invalide');
    }
  }
}
