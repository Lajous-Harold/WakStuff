import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { ImportsService } from '../../../core/services/imports.service';
import { ImportResult } from '../../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../../shared/components';

@Component({
  selector: 'app-imports-dashboard',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent],
  templateUrl: './imports-dashboard.component.html',
  styleUrl: './imports-dashboard.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImportsDashboardComponent implements OnInit {
  importing = signal(false);
  importResult = signal<ImportResult | null>(null);
  error = signal<string | null>(null);

  constructor(private importsService: ImportsService) {}

  ngOnInit(): void {}

  startImport(): void {
    if (this.importing()) return;

    this.importing.set(true);
    this.error.set(null);
    this.importResult.set(null);

    this.importsService.importAll().subscribe({
      next: (result) => {
        this.importResult.set(result);
        this.importing.set(false);
      },
      error: (err) => {
        this.error.set("Erreur lors de l'importation");
        this.importing.set(false);
        console.error(err);
      },
    });
  }

  getPhaseStatus(phase: string): string {
    const result = this.importResult();
    if (!result) return 'pending';
    return result.success ? 'success' : 'pending';
  }

  getPhaseIcon(phase: string): string {
    const status = this.getPhaseStatus(phase);
    return status === 'success' ? '✓' : status === 'pending' ? '○' : '✗';
  }
}
