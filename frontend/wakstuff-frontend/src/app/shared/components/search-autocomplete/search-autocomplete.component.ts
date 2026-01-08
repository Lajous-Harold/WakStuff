import {
  Component,
  input,
  output,
  signal,
  computed,
  effect,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import {
  GlobalSearchService,
  SearchSuggestion,
} from '../../../core/services/global-search.service';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-search-autocomplete',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search-autocomplete.component.html',
  styleUrl: './search-autocomplete.component.scss',
})
export class SearchAutocompleteComponent {
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

  // Inputs
  placeholder = input<string>('Rechercher items, recettes, ressources...');
  showIcons = input<boolean>(true);
  maxSuggestions = input<number>(5);
  minChars = input<number>(2);

  // Outputs
  search = output<string>();
  suggestionSelected = output<SearchSuggestion>();

  // State
  searchQuery = signal<string>('');
  suggestions = signal<SearchSuggestion[]>([]);
  showSuggestions = signal<boolean>(false);
  selectedIndex = signal<number>(-1);
  isLoading = signal<boolean>(false);

  // Observable pour debounce
  private searchSubject = new Subject<string>();

  constructor(private searchService: GlobalSearchService, private router: Router) {
    // Subscribe aux suggestions avec debounce
    this.searchService.getAutocompleteSuggestions(this.searchSubject.asObservable()).subscribe({
      next: (results) => {
        this.suggestions.set(results.slice(0, this.maxSuggestions()));
        this.isLoading.set(false);
        this.showSuggestions.set(results.length > 0);
      },
      error: () => {
        this.isLoading.set(false);
        this.suggestions.set([]);
        this.showSuggestions.set(false);
      },
    });
  }

  onInput(): void {
    const query = this.searchQuery();
    this.selectedIndex.set(-1);

    if (query.length < this.minChars()) {
      this.suggestions.set([]);
      this.showSuggestions.set(false);
      this.isLoading.set(false);
      return;
    }

    this.isLoading.set(true);
    this.searchSubject.next(query);
  }

  onKeyDown(event: KeyboardEvent): void {
    const suggestionsCount = this.suggestions().length;

    if (!this.showSuggestions() || suggestionsCount === 0) {
      if (event.key === 'Enter') {
        this.performSearch();
      }
      return;
    }

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.selectedIndex.update((i) => Math.min(i + 1, suggestionsCount - 1));
        break;

      case 'ArrowUp':
        event.preventDefault();
        this.selectedIndex.update((i) => Math.max(i - 1, -1));
        break;

      case 'Enter':
        event.preventDefault();
        const idx = this.selectedIndex();
        if (idx >= 0 && idx < suggestionsCount) {
          this.selectSuggestion(this.suggestions()[idx]);
        } else {
          this.performSearch();
        }
        break;

      case 'Escape':
        event.preventDefault();
        this.closeSuggestions();
        break;
    }
  }

  selectSuggestion(suggestion: SearchSuggestion): void {
    this.searchQuery.set(suggestion.title);
    this.closeSuggestions();
    this.suggestionSelected.emit(suggestion);

    // Navigate basé sur le type
    if (suggestion.type === 'item') {
      this.router.navigate(['/items', suggestion.wakfu_id]);
    } else if (suggestion.type === 'recipe') {
      this.router.navigate(['/craft/recipe', suggestion.wakfu_id]);
    } else if (suggestion.type === 'resource') {
      this.router.navigate(['/resources', suggestion.wakfu_id]);
    }
  }

  performSearch(): void {
    const query = this.searchQuery().trim();
    if (query) {
      this.closeSuggestions();
      this.search.emit(query);
    }
  }

  clearSearch(): void {
    this.searchQuery.set('');
    this.suggestions.set([]);
    this.showSuggestions.set(false);
    this.selectedIndex.set(-1);
    this.search.emit('');
    this.searchInput?.nativeElement.focus();
  }

  closeSuggestions(): void {
    this.showSuggestions.set(false);
    this.selectedIndex.set(-1);
  }

  getIconUrl(wakfuId: number): string {
    return `${environment.apiUrl}/proxy/icon/${wakfuId}`;
  }

  getTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      item: 'Item',
      recipe: 'Recette',
      resource: 'Ressource',
    };
    return labels[type] || type;
  }

  getTypeColor(type: string): string {
    const colors: Record<string, string> = {
      item: '#3b82f6',
      recipe: '#f59e0b',
      resource: '#10b981',
    };
    return colors[type] || '#6b7280';
  }

  highlightMatch(text: string): string {
    const query = this.searchQuery();
    if (!query) return text;
    return this.searchService.highlightMatch(text, query);
  }
}
