import { Injectable, signal, computed } from '@angular/core';

/**
 * Interface pour une craft list sauvegardée
 */
export interface SavedCraftList {
  id: string;
  name: string;
  recipeId: number;
  recipeName: string;
  recipeIconGfxId?: number; // Icon du résultat de la recette
  quantity: number;
  maxDepth: number;
  skipOwnedItems: boolean;
  createdAt: string;
  updatedAt: string;
  materials?: {
    itemId: number;
    itemName: string;
    quantity: number;
  }[];
}

/**
 * Service pour gérer les craft lists favorites avec localStorage
 */
@Injectable({
  providedIn: 'root',
})
export class CraftFavoritesService {
  private readonly STORAGE_KEY = 'wakstuff_craft_favorites';

  // Signal pour stocker toutes les craft lists
  private craftListsSignal = signal<SavedCraftList[]>([]);

  // Computed pour exposer les craft lists
  craftLists = this.craftListsSignal.asReadonly();

  // Computed pour compter le nombre de favoris
  favoritesCount = computed(() => this.craftListsSignal().length);

  constructor() {
    this.loadFromLocalStorage();
  }

  /**
   * Charger les craft lists depuis localStorage
   */
  private loadFromLocalStorage(): void {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as SavedCraftList[];
        this.craftListsSignal.set(parsed);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des favoris:', error);
      this.craftListsSignal.set([]);
    }
  }

  /**
   * Sauvegarder les craft lists dans localStorage
   */
  private saveToLocalStorage(): void {
    try {
      const data = JSON.stringify(this.craftListsSignal());
      localStorage.setItem(this.STORAGE_KEY, data);
    } catch (error) {
      console.error('Erreur lors de la sauvegarde des favoris:', error);
    }
  }

  /**
   * Ajouter une nouvelle craft list aux favoris
   */
  addCraftList(craftList: Omit<SavedCraftList, 'id' | 'createdAt' | 'updatedAt'>): SavedCraftList {
    const newCraftList: SavedCraftList = {
      ...craftList,
      id: this.generateId(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const current = this.craftListsSignal();
    this.craftListsSignal.set([...current, newCraftList]);
    this.saveToLocalStorage();

    return newCraftList;
  }

  /**
   * Mettre à jour une craft list existante
   */
  updateCraftList(id: string, updates: Partial<SavedCraftList>): void {
    const current = this.craftListsSignal();
    const index = current.findIndex((list) => list.id === id);

    if (index !== -1) {
      const updated = {
        ...current[index],
        ...updates,
        id: current[index].id, // Préserver l'ID
        createdAt: current[index].createdAt, // Préserver la date de création
        updatedAt: new Date().toISOString(),
      };

      const newList = [...current];
      newList[index] = updated;
      this.craftListsSignal.set(newList);
      this.saveToLocalStorage();
    }
  }

  /**
   * Renommer une craft list
   */
  renameCraftList(id: string, newName: string): void {
    this.updateCraftList(id, { name: newName });
  }

  /**
   * Supprimer une craft list
   */
  deleteCraftList(id: string): void {
    const current = this.craftListsSignal();
    const filtered = current.filter((list) => list.id !== id);
    this.craftListsSignal.set(filtered);
    this.saveToLocalStorage();
  }

  /**
   * Dupliquer une craft list
   */
  duplicateCraftList(id: string): SavedCraftList | null {
    const current = this.craftListsSignal();
    const original = current.find((list) => list.id === id);

    if (!original) {
      return null;
    }

    const duplicate: Omit<SavedCraftList, 'id' | 'createdAt' | 'updatedAt'> = {
      ...original,
      name: `${original.name} (copie)`,
    };

    return this.addCraftList(duplicate);
  }

  /**
   * Récupérer une craft list par son ID
   */
  getCraftList(id: string): SavedCraftList | undefined {
    return this.craftListsSignal().find((list) => list.id === id);
  }

  /**
   * Exporter toutes les craft lists en JSON
   */
  exportToJSON(): string {
    return JSON.stringify(this.craftListsSignal(), null, 2);
  }

  /**
   * Importer des craft lists depuis JSON
   */
  importFromJSON(jsonString: string): { success: boolean; imported: number; errors: string[] } {
    const errors: string[] = [];
    let imported = 0;

    try {
      const data = JSON.parse(jsonString) as SavedCraftList[];

      if (!Array.isArray(data)) {
        return { success: false, imported: 0, errors: ['Le JSON doit contenir un tableau'] };
      }

      const validLists: SavedCraftList[] = [];

      for (const item of data) {
        if (this.isValidCraftList(item)) {
          // Générer un nouvel ID pour éviter les doublons
          validLists.push({
            ...item,
            id: this.generateId(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
          imported++;
        } else {
          errors.push(`Craft list invalide ignorée: ${(item as any).name || 'sans nom'}`);
        }
      }

      if (validLists.length > 0) {
        const current = this.craftListsSignal();
        this.craftListsSignal.set([...current, ...validLists]);
        this.saveToLocalStorage();
      }

      return { success: imported > 0, imported, errors };
    } catch (error) {
      return {
        success: false,
        imported: 0,
        errors: [`Erreur de parsing JSON: ${error}`],
      };
    }
  }

  /**
   * Supprimer toutes les craft lists
   */
  clearAll(): void {
    this.craftListsSignal.set([]);
    this.saveToLocalStorage();
  }

  /**
   * Valider qu'un objet est une craft list valide
   */
  private isValidCraftList(obj: any): obj is SavedCraftList {
    return (
      typeof obj === 'object' &&
      typeof obj.name === 'string' &&
      typeof obj.recipeId === 'number' &&
      typeof obj.recipeName === 'string' &&
      typeof obj.quantity === 'number'
    );
  }

  /**
   * Générer un ID unique
   */
  private generateId(): string {
    return `craft_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
