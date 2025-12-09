import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { RecipesService } from '../../../core/services/recipes.service';
import { RecipeDetail, RecipeIngredient, RecipeResult } from '../../../core/models';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../shared/components/error-message/error-message.component';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-craft-recipe-detail',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent, ErrorMessageComponent],
  templateUrl: './craft-recipe-detail.component.html',
  styleUrl: './craft-recipe-detail.component.scss',
})
export class CraftRecipeDetailComponent implements OnInit {
  loading = signal(false);
  error = signal<string | null>(null);

  recipeDetail = signal<RecipeDetail | null>(null);
  wakfuId = signal<number>(0);

  constructor(
    private recipesService: RecipesService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const id = +params['wakfuId'];
      this.wakfuId.set(id);
      this.loadRecipeDetail(id);
    });
  }

  loadRecipeDetail(wakfuId: number): void {
    this.loading.set(true);
    this.error.set(null);

    this.recipesService.getRecipeDetail(wakfuId).subscribe({
      next: (response: RecipeDetail) => {
        this.recipeDetail.set(response);
        this.loading.set(false);
      },
      error: (err: any) => {
        this.error.set('Erreur lors du chargement de la recette');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  getItemIconUrl(iconGfxId: number): string {
    return `${environment.apiUrl}/proxy/icon/${iconGfxId}`;
  }

  openCalculator(): void {
    const detail = this.recipeDetail();
    if (!detail || detail.results.length === 0) {
      console.error('Aucun résultat disponible pour ouvrir le calculateur');
      return;
    }

    const itemWakfuId = detail.results[0].produced_item_wakfu_id;
    if (!itemWakfuId) {
      console.error('produced_item_wakfu_id manquant dans le résultat');
      return;
    }

    this.router.navigate(['/craft/calculator', itemWakfuId]);
  }

  goBack(): void {
    window.history.back();
  }

  viewItem(wakfuId: number): void {
    this.router.navigate(['/items', wakfuId]);
  }
}
