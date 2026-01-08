import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { RecipesService } from '../../../core/services/recipes.service';
import { RecipeCategory } from '../../../core/models/recipe.model';
import { LoadingSpinnerComponent } from '../../../shared/components/loading-spinner/loading-spinner.component';
import { ErrorMessageComponent } from '../../../shared/components/error-message/error-message.component';

@Component({
  selector: 'app-craft-jobs',
  standalone: true,
  imports: [CommonModule, RouterLink, LoadingSpinnerComponent, ErrorMessageComponent],
  templateUrl: './craft-jobs.component.html',
  styleUrl: './craft-jobs.component.scss',
})
export class CraftJobsComponent implements OnInit {
  loading = signal(false);
  error = signal<string | null>(null);
  craftJobs = signal<RecipeCategory[]>([]);

  // Icônes personnalisées par métier
  jobIcons: Record<string, string> = {
    Boulanger: '🍞',
    Trappeur: '🪤',
    Cuisinier: '🍳',
    Armurier: '⚔️',
    Bijoutier: '💎',
    Tailleur: '🧵',
    Maroquinier: '👜',
    Ébéniste: '🪑',
    "Maitre d'Armes": '⚒️',
  };

  constructor(private recipesService: RecipesService, private router: Router) {}

  ngOnInit(): void {
    this.loadCraftJobs();
  }

  loadCraftJobs(): void {
    this.loading.set(true);
    this.error.set(null);

    // Ajouter le paramètre category_type=craft pour filtrer côté backend
    this.recipesService.getCategories('craft').subscribe({
      next: (response) => {
        this.craftJobs.set(response.categories);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Erreur lors du chargement des métiers de craft');
        this.loading.set(false);
        console.error(err);
      },
    });
  }

  getJobIcon(name: string): string {
    return this.jobIcons[name] || '🛠️';
  }

  navigateToJob(categoryId: number): void {
    this.router.navigate(['/craft/job', categoryId]);
  }
}
