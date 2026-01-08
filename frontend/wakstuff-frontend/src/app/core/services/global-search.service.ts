import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, catchError, debounceTime, distinctUntilChanged, switchMap } from 'rxjs';
import { environment } from '../config';

/**
 * Suggestion de recherche avec type
 */
export interface SearchSuggestion {
  id: number;
  wakfu_id: number;
  icon_gfx_id?: number;
  title: string;
  type: 'item' | 'recipe' | 'resource';
  level?: number;
  rarity?: number;
  category?: string;
}

/**
 * Résultats de recherche globale
 */
export interface GlobalSearchResults {
  items: any[];
  recipes: any[];
  resources: any[];
  total: number;
  page: number;
  per_page: number;
}

/**
 * Filtres de recherche avancée
 */
export interface AdvancedSearchFilters {
  query?: string;
  types?: ('item' | 'recipe' | 'resource')[];
  minLevel?: number;
  maxLevel?: number;
  rarity?: number[];
  categories?: number[];
  sortBy?: 'name' | 'level' | 'rarity' | 'date';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
}

/**
 * Service de recherche globale avec auto-complete
 */
@Injectable({
  providedIn: 'root',
})
export class GlobalSearchService {
  private apiUrl = `${environment.apiUrl}/stats/global`;

  constructor(private http: HttpClient) {}

  /**
   * Recherche globale avec filtres avancés
   */
  search(filters: AdvancedSearchFilters): Observable<GlobalSearchResults> {
    let params = new HttpParams();

    if (filters.query) {
      params = params.set('query', filters.query);
    }
    if (filters.minLevel !== undefined) {
      params = params.set('min_level', filters.minLevel.toString());
    }
    if (filters.maxLevel !== undefined) {
      params = params.set('max_level', filters.maxLevel.toString());
    }
    if (filters.page) {
      params = params.set('page', filters.page.toString());
    }
    if (filters.per_page) {
      params = params.set('limit', filters.per_page.toString());
    }

    return this.http.get<GlobalSearchResults>(this.apiUrl, { params });
  }

  /**
   * Obtenir des suggestions pour l'auto-complete (max 5 résultats)
   */
  getSuggestions(query: string): Observable<SearchSuggestion[]> {
    if (!query || query.trim().length < 2) {
      return of([]);
    }

    return this.search({ query: query.trim(), per_page: 5 }).pipe(
      switchMap((results) => {
        const suggestions: SearchSuggestion[] = [];

        // Ajouter items
        results.items.slice(0, 3).forEach((item) => {
          suggestions.push({
            id: item.id,
            wakfu_id: item.wakfu_id,
            icon_gfx_id: item.icon_gfx_id,
            title: item.title,
            type: 'item',
            level: item.level,
            rarity: item.rarity,
          });
        });

        // Ajouter recettes
        results.recipes?.slice(0, 2).forEach((recipe: any) => {
          suggestions.push({
            id: recipe.id,
            wakfu_id: recipe.wakfu_id,
            icon_gfx_id: recipe.icon_gfx_id,
            title: recipe.title,
            type: 'recipe',
            level: recipe.level,
          });
        });

        // Limiter à 5 suggestions max
        return of(suggestions.slice(0, 5));
      }),
      catchError(() => of([]))
    );
  }

  /**
   * Recherche rapide pour auto-complete avec debounce
   */
  getAutocompleteSuggestions(queryObservable: Observable<string>): Observable<SearchSuggestion[]> {
    return queryObservable.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap((query) => this.getSuggestions(query))
    );
  }

  /**
   * Filtrer les suggestions par type
   */
  filterSuggestionsByType(
    suggestions: SearchSuggestion[],
    types: ('item' | 'recipe' | 'resource')[]
  ): SearchSuggestion[] {
    if (!types || types.length === 0) {
      return suggestions;
    }
    return suggestions.filter((s) => types.includes(s.type));
  }

  /**
   * Highlight le texte de recherche dans les résultats
   */
  highlightMatch(text: string, query: string): string {
    if (!query || !text) {
      return text;
    }

    const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  private escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}
