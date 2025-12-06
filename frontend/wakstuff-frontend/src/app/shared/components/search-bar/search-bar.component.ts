import { Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [FormsModule],
  template: `
    <div class="search-bar">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          class="search-input"
          [placeholder]="placeholder()"
          [(ngModel)]="searchQuery"
          (input)="onSearchInput()"
          (keyup.enter)="onSearch()"
        />
        @if (searchQuery()) {
        <button class="search-clear" (click)="clearSearch()" aria-label="Effacer">✕</button>
        }
      </div>

      @if (showSearchButton()) {
      <button class="search-button" (click)="onSearch()">Rechercher</button>
      }
    </div>
  `,
  styles: [
    `
      .search-bar {
        display: flex;
        gap: 0.5rem;
        width: 100%;
      }

      .search-input-wrapper {
        position: relative;
        flex: 1;
        display: flex;
        align-items: center;
      }

      .search-icon {
        position: absolute;
        left: 1rem;
        font-size: 1.2rem;
        pointer-events: none;
        opacity: 0.5;
      }

      .search-input {
        width: 100%;
        padding: 0.75rem 3rem 0.75rem 3rem;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 1rem;
        transition: border-color 0.2s;

        &:focus {
          outline: none;
          border-color: #3498db;
        }

        &::placeholder {
          color: #999;
        }
      }

      .search-clear {
        position: absolute;
        right: 1rem;
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.5;
        transition: opacity 0.2s;
        padding: 0.25rem;

        &:hover {
          opacity: 1;
        }
      }

      .search-button {
        padding: 0.75rem 1.5rem;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1rem;
        font-weight: 500;
        transition: background 0.2s;
        white-space: nowrap;

        &:hover {
          background: #2980b9;
        }
      }
    `,
  ],
})
export class SearchBarComponent {
  placeholder = input<string>('Rechercher...');
  debounceTime = input<number>(300);
  showSearchButton = input<boolean>(false);

  search = output<string>();

  searchQuery = signal<string>('');
  private debounceTimeout: any;

  onSearchInput(): void {
    if (this.debounceTime() > 0) {
      clearTimeout(this.debounceTimeout);
      this.debounceTimeout = setTimeout(() => {
        this.search.emit(this.searchQuery());
      }, this.debounceTime());
    }
  }

  onSearch(): void {
    clearTimeout(this.debounceTimeout);
    this.search.emit(this.searchQuery());
  }

  clearSearch(): void {
    this.searchQuery.set('');
    this.search.emit('');
  }
}
