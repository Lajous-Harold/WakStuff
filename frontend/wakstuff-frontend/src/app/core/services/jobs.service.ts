import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Job, JobDetail, XPCalculatorData } from '../models/job.model';

export interface JobRecipesFilters {
  level_min?: number;
  level_max?: number;
}

@Injectable({
  providedIn: 'root',
})
export class JobsService {
  private apiUrl = 'http://localhost:5000/api/jobs';

  jobs = signal<Job[]>([]);

  constructor(private http: HttpClient) {}

  getJobs(): Observable<{ jobs: Job[] }> {
    return this.http.get<{ jobs: Job[] }>(this.apiUrl);
  }

  getJobDetail(categoryId: number): Observable<JobDetail> {
    return this.http.get<JobDetail>(`${this.apiUrl}/${categoryId}`);
  }

  getJobRecipes(categoryId: number, filters: JobRecipesFilters = {}): Observable<any> {
    let params = new HttpParams();

    if (filters.level_min !== undefined) {
      params = params.set('level_min', filters.level_min.toString());
    }
    if (filters.level_max !== undefined) {
      params = params.set('level_max', filters.level_max.toString());
    }

    return this.http.get(`${this.apiUrl}/${categoryId}/recipes`, { params });
  }

  getXPCalculator(categoryId: number): Observable<XPCalculatorData> {
    return this.http.get<XPCalculatorData>(`${this.apiUrl}/${categoryId}/xp-calculator`);
  }

  // Méthode helper pour calculer combien de craft nécessaires
  calculateCraftsNeeded(
    currentLevel: number,
    targetLevel: number,
    xpData: XPCalculatorData,
    selectedRecipeLevel: number
  ): number {
    const currentXP = xpData.xp_per_level.find((x) => x.level === currentLevel)?.cumulative_xp || 0;
    const targetXP = xpData.xp_per_level.find((x) => x.level === targetLevel)?.cumulative_xp || 0;
    const xpNeeded = targetXP - currentXP;

    const recipeXP =
      xpData.recipes_xp.find((r) => r.recipe_level === selectedRecipeLevel)?.xp_granted || 1;

    return Math.ceil(xpNeeded / recipeXP);
  }
}
