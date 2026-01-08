import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SearchAutocompleteComponent } from '../../shared/components/search-autocomplete/search-autocomplete.component';
import {
  GlobalSearchService,
  SearchSuggestion,
  GlobalSearchResults,
} from '../../core/services/global-search.service';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { environment } from '../../core/config';

@Component({
  selector: 'app-search-page',
  standalone: true,
  imports: [CommonModule, SearchAutocompleteComponent, LoadingSpinnerComponent],
  templateUrl: './search-page.component.html',
  styleUrl: './search-page.component.scss',
})
export class SearchPageComponent {
  isLoading = signal(false);
  searchQuery = signal('');
  results = signal<GlobalSearchResults | null>(null);

  constructor(private searchService: GlobalSearchService, private router: Router) {}

  onSearch(query: string): void {
    if (!query || query.trim().length < 2) {
      this.results.set(null);
      return;
    }

    this.searchQuery.set(query);
    this.isLoading.set(true);

    this.searchService.search({ query: query.trim(), per_page: 20 }).subscribe({
      next: (data) => {
        this.results.set(data);
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Search error:', error);
        this.isLoading.set(false);
      },
    });
  }

  onSuggestionSelected(suggestion: SearchSuggestion): void {
    // Navigation is handled by the autocomplete component
    console.log('Selected:', suggestion);
  }

  viewItem(wakfuId: number, type: string): void {
    if (type === 'item' || type === 'items') {
      this.router.navigate(['/items', wakfuId]);
    } else if (type === 'recipe' || type === 'recipes') {
      this.router.navigate(['/craft/recipe', wakfuId]);
    } else if (type === 'resource' || type === 'resources') {
      this.router.navigate(['/resources', wakfuId]);
    }
  }

  getIconUrl(wakfuId: number): string {
    return `${environment.apiUrl}/proxy/icon/${wakfuId}`;
  }

  highlightMatch(text: string): string {
    return this.searchService.highlightMatch(text, this.searchQuery());
  }

  getTotalResults(): number {
    const res = this.results();
    if (!res) return 0;
    return (res.items?.length || 0) + (res.recipes?.length || 0) + (res.resources?.length || 0);
  }
}
