import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { environment } from '../config';

/**
 * Service qui vérifie si des données ont été importées dans la base de données.
 * Permet d'éviter les appels API inutiles quand aucun import n'a été fait.
 */
@Injectable({
  providedIn: 'root',
})
export class ImportStatusService {
  private readonly API_URL = environment.apiUrl;

  // Signal qui indique si des données sont présentes
  hasImportedData = signal<boolean | null>(null); // null = non vérifié, true = données présentes, false = pas de données

  constructor(private http: HttpClient) {}

  /**
   * Vérifie si des données ont été importées en appelant l'endpoint stats/overview
   * Cet endpoint est léger et donne un aperçu rapide de l'état de la base
   */
  checkImportStatus(): Observable<boolean> {
    // Si déjà vérifié et positif, on retourne directement
    if (this.hasImportedData() === true) {
      return of(true);
    }

    return this.http.get<any>(`${this.API_URL}/stats/overview`).pipe(
      map((stats) => {
        // Si au moins un type de données existe, considérer que des imports ont été faits
        const hasData =
          stats.total_items > 0 || stats.total_resources > 0 || stats.total_recipes > 0;
        this.hasImportedData.set(hasData);
        return hasData;
      }),
      catchError(() => {
        // En cas d'erreur (500 ou autre), considérer qu'il n'y a pas de données
        this.hasImportedData.set(false);
        return of(false);
      })
    );
  }

  /**
   * Force la revérification du statut d'import (utile après un import)
   */
  refresh(): Observable<boolean> {
    this.hasImportedData.set(null);
    return this.checkImportStatus();
  }

  /**
   * Réinitialise le statut (utile pour forcer une nouvelle vérification)
   */
  reset(): void {
    this.hasImportedData.set(null);
  }
}
