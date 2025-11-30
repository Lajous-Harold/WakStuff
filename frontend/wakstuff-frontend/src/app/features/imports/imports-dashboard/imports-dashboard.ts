import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { finalize } from 'rxjs';
import { ImportsService, ImportBatchDto } from '../../../core/services/imports.service';

@Component({
  selector: 'app-imports-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './imports-dashboard.html',
  styleUrls: ['./imports-dashboard.scss'],
})
export class ImportsDashboard implements OnInit {
  batches: ImportBatchDto[] = [];
  loading = false;
  reloading = false;
  lastRunMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private importsService: ImportsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.data.subscribe({
      next: (data) => {
        const resolved = data['batches'];
        this.batches = Array.isArray(resolved) ? resolved : [];
      },
      error: (err) => {
        this.batches = [];
      },
    });
  }

  loadBatches(): void {
    this.reloading = true;
    this.cdr.detectChanges();

    this.importsService
      .list()
      .pipe(
        finalize(() => {
          this.reloading = false;
          this.loading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (batches) => {
          this.batches = Array.isArray(batches) ? batches : [];
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.lastRunMessage = `Erreur de chargement: ${err?.message ?? err}`;
          this.batches = [];
          this.cdr.detectChanges();
        },
      });
  }

  runImport(): void {
    this.loading = true;
    this.lastRunMessage = null;

    this.importsService.run().subscribe({
      next: (res) => {
        const versionLabel = res.game_version ?? 'version inconnue';
        this.lastRunMessage = `Import #${res.batch_id} (${versionLabel}) – statut : ${res.status}, items : ${res.total_items}, erreurs : ${res.error_count}`;
        this.loadBatches();
      },
      error: (err) => {
        this.lastRunMessage = `Erreur: ${err?.message ?? err}`;
        this.loading = false;
      },
    });
  }
}
