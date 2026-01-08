import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { RecipesService, RecipeFilters } from '../../../core/services/recipes.service';
import { RecipeModel, RecipeCategory } from '../../../core/models';
import { environment } from '../../../core/config';
import {
  LoadingSpinnerComponent,
  ErrorMessageComponent,
  PaginationComponent,
  PaginationConfig,
  SearchBarComponent,
} from '../../../shared/components';

@Component({
  selector: 'app-craft-recipes-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    LoadingSpinnerComponent,
    ErrorMessageComponent,
    PaginationComponent,
    SearchBarComponent,
  ],
  templateUrl: './craft-recipes-list.component.html',
  styleUrl: './craft-recipes-list.component.scss',
})
export class CraftRecipesListComponent implements OnInit {
  loading = signal(false);
  error = signal<string | null>(null);

  recipes = signal<RecipeModel[]>([]);
  category = signal<RecipeCategory | null>(null);
  categoryId = signal<number>(0);

  filters = signal<RecipeFilters>({
    page: 1,
    per_page: 50,
    category_id: 0,
  });

  totalItems = signal(0);
  totalPages = signal(0);

  // Filtres niveau
  minLevel = signal<number | null>(null);
  maxLevel = signal<number | null>(null);

  paginationConfig = computed<PaginationConfig>(() => ({
    currentPage: this.filters().page || 1,
    totalPages: this.totalPages(),
    pageSize: this.filters().per_page || 50,
    totalItems: this.totalItems(),
  }));

  constructor(
    private recipesService: RecipesService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const catId = +params['categoryId'];
      this.categoryId.set(catId);
      this.filters.update((f) => ({ ...f, category_id: catId }));
      this.loadCategory(catId);
      this.loadRecipes();
    });
  }

  loadCategory(categoryId: number): void {
    // Récupérer les infos de la catégorie depuis l'API categories
    this.recipesService.getCategories().subscribe({
      next: (response: any) => {
        const cat = response.categories.find((c: RecipeCategory) => c.id === categoryId);
        if (cat) {
          this.category.set(cat);
        }
      },
      error: (err: any) => {
        console.error('Erreur chargement catégorie', err);
      },
    });
  }

  loadRecipes(): void {
    this.loading.set(true);
    this.error.set(null);

    const filterParams: RecipeFilters = {
      ...this.filters(),
      level_min: this.minLevel() || undefined,
      level_max: this.maxLevel() || undefined,
    };

    this.recipesService.getRecipes(filterParams).subscribe({
      next: (response: any) => {
        this.recipes.set(response.recipes);
        this.totalItems.set(response.total);
        this.totalPages.set(response.pages);
        this.loading.set(false);
      },
      error: (err: any) => {
        this.error.set('Erreur lors du chargement des recettes');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  onSearch(query: string): void {
    this.filters.update((f) => ({ ...f, search: query, page: 1 }));
    this.loadRecipes();
  }

  onLevelFilterChange(): void {
    this.filters.update((f) => ({ ...f, page: 1 }));
    this.loadRecipes();
  }

  clearLevelFilters(): void {
    this.minLevel.set(null);
    this.maxLevel.set(null);
    this.onLevelFilterChange();
  }

  hasActiveFilters(): boolean {
    const f = this.filters();
    return !!(
      f.search ||
      this.minLevel() ||
      this.maxLevel() ||
      (f.sort_by && f.sort_by !== 'level') ||
      (f.sort_order && f.sort_order !== 'desc')
    );
  }

  clearAllFilters(): void {
    this.minLevel.set(null);
    this.maxLevel.set(null);
    this.filters.update((f) => ({
      page: 1,
      per_page: 50,
      category_id: f.category_id, // Garder la catégorie
      sort_by: 'level',
      sort_order: 'desc',
    }));
    this.loadRecipes();
  }

  onPageChange(page: number): void {
    this.filters.update((f) => ({ ...f, page }));
    this.loadRecipes();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  onPageSizeChange(pageSize: number): void {
    this.filters.update((f) => ({ ...f, per_page: pageSize, page: 1 }));
    this.loadRecipes();
  }

  viewRecipeDetail(wakfuId: number): void {
    this.router.navigate(['/craft/recipe', wakfuId]);
  }

  openCalculator(wakfuId: number, event: Event): void {
    event.stopPropagation();
    this.router.navigate(['/craft/calculator', wakfuId]);
  }

  goBack(): void {
    this.router.navigate(['/craft']);
  }

  onSortByChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.filters.update((f) => ({ ...f, sort_by: select.value as any, page: 1 }));
    this.loadRecipes();
  }

  onSortOrderChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    this.filters.update((f) => ({ ...f, sort_order: select.value as any, page: 1 }));
    this.loadRecipes();
  }

  getItemIconUrl(iconGfxId: number): string {
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }
}
