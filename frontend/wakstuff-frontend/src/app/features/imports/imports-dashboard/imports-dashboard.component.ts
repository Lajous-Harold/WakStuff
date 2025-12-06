import {
  Component,
  OnInit,
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ImportsService } from '../../../core/services/imports.service';
import { ImportResult, ImportBatch } from '../../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../../shared/components';

@Component({
  selector: 'app-imports-dashboard',
  standalone: true,
  imports: [CommonModule, LoadingSpinnerComponent, ErrorMessageComponent],
  templateUrl: './imports-dashboard.component.html',
  styleUrl: './imports-dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImportsDashboardComponent implements OnInit {
  importing = signal(false);
  clearing = signal(false);
  loading = signal(true);
  importResult = signal<ImportResult | null>(null);
  error = signal<string | null>(null);
  batches = signal<ImportBatch[]>([]);
  stats = signal<any>(null);
  showDeleteConfirm = signal(false);
  showResetHistoryConfirm = signal(false);

  constructor(private importsService: ImportsService, private cdr: ChangeDetectorRef) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);

    // Charger les batches
    this.importsService.getImportBatches(20).subscribe({
      next: (response) => {
        this.batches.set(response.batches || []);
        this.loading.set(false);
        this.cdr.markForCheck(); // Forcer la détection de changement
      },
      error: (err) => {
        console.error('Erreur chargement batches:', err);
        this.loading.set(false);
        this.cdr.markForCheck();
      },
    });

    // Charger les stats
    this.importsService.getImportStats().subscribe({
      next: (stats) => {
        this.stats.set(stats);
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Erreur chargement stats:', err);
      },
    });
  }

  startImport(): void {
    if (this.importing()) return;

    this.importing.set(true);
    this.error.set(null);
    this.importResult.set(null);

    // Toujours supprimer les données existantes avant un nouvel import
    // pour éviter les conflits de clés uniques (clear_before: true)
    // L'historique des imports est conservé dans ImportBatch
    this.importsService.importAll(true).subscribe({
      next: (result) => {
        this.importResult.set(result);
        this.importing.set(false);
        this.loadData(); // Recharger les données
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.error.set("Erreur lors de l'importation");
        this.importing.set(false);
        this.cdr.markForCheck();
        console.error(err);
      },
    });
  }

  confirmDelete(): void {
    this.showDeleteConfirm.set(true);
  }

  cancelDelete(): void {
    this.showDeleteConfirm.set(false);
  }

  clearAllData(): void {
    if (this.clearing()) return;

    this.clearing.set(true);
    this.error.set(null);

    this.importsService.clearAllData().subscribe({
      next: () => {
        this.clearing.set(false);
        this.showDeleteConfirm.set(false);
        this.loadData(); // Recharger les données
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.error.set('Erreur lors de la suppression');
        this.clearing.set(false);
        this.cdr.markForCheck();
        console.error(err);
      },
    });
  }

  confirmResetHistory(): void {
    this.showResetHistoryConfirm.set(true);
  }

  cancelResetHistory(): void {
    this.showResetHistoryConfirm.set(false);
  }

  resetImportHistory(): void {
    if (this.clearing()) return;

    this.clearing.set(true);
    this.error.set(null);

    this.importsService.clearImportHistory().subscribe({
      next: () => {
        this.clearing.set(false);
        this.showResetHistoryConfirm.set(false);
        this.loadData(); // Recharger les données
        this.cdr.markForCheck();
      },
      error: (err) => {
        this.error.set("Erreur lors de la réinitialisation de l'historique");
        this.clearing.set(false);
        this.cdr.markForCheck();
        console.error(err);
      },
    });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleString('fr-FR');
  }

  formatDuration(started: string, completed: string): string {
    const start = new Date(started).getTime();
    const end = new Date(completed).getTime();
    const duration = Math.round((end - start) / 1000);
    return `${duration}s`;
  }

  getStatusClass(status: string): string {
    return status === 'success'
      ? 'status-success'
      : status === 'error'
      ? 'status-error'
      : 'status-pending';
  }
}
