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
  pagedBatches: ImportBatchDto[] = [];
  loading = false;
  reloading = false;
  error: string | null = null;
  lastRunMessage: string | null = null;

  pageIndex = 0;
  pageSize = 10;
  pageSizeOptions = [10, 25, 50];

  get totalBatches(): number {
    return this.batches.length;
  }

  get totalPages(): number {
    if (this.pageSize <= 0) return 1;
    const pages = Math.ceil(this.totalBatches / this.pageSize);
    return pages > 0 ? pages : 1;
  }

  get pageStartIndex(): number {
    if (this.totalBatches === 0) return 0;
    return this.pageIndex * this.pageSize + 1;
  }

  get pageEndIndex(): number {
    return Math.min(this.totalBatches, (this.pageIndex + 1) * this.pageSize);
  }

  constructor(
    private route: ActivatedRoute,
    private importsService: ImportsService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loading = true;

    this.route.data.subscribe({
      next: (data) => {
        const resolved = data['batches'];
        this.batches = Array.isArray(resolved) ? resolved : [];
        this.pageIndex = 0;
        this.updatePagedBatches();
        this.loading = false;
        this.error = null;
      },
      error: (err) => {
        this.error = err?.message ?? 'Erreur lors du chargement des imports';
        this.batches = [];
        this.pagedBatches = [];
        this.loading = false;
      },
    });
  }

  private updatePagedBatches(): void {
    const start = this.pageIndex * this.pageSize;
    const end = start + this.pageSize;
    this.pagedBatches = this.batches.slice(start, end);
  }

  loadBatches(): void {
    this.reloading = true;
    this.error = null;
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
          this.pageIndex = 0;
          this.updatePagedBatches();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = err?.message ?? 'Erreur lors du rechargement des imports';
          this.batches = [];
          this.cdr.detectChanges();
        },
      });
  }

  changePageSize(rawValue: string | number): void {
    const size = typeof rawValue === 'string' ? parseInt(rawValue, 10) : rawValue;

    if (!Number.isFinite(size) || size <= 0) {
      return;
    }

    this.pageSize = size;
    this.pageIndex = 0;
    this.updatePagedBatches();
  }

  goToFirstPage(): void {
    if (this.pageIndex === 0) return;
    this.pageIndex = 0;
    this.updatePagedBatches();
  }

  goToLastPage(): void {
    if (this.pageIndex >= this.totalPages - 1) return;
    this.pageIndex = this.totalPages - 1;
    this.updatePagedBatches();
  }

  goToPreviousPage(): void {
    if (this.pageIndex === 0) return;
    this.pageIndex--;
    this.updatePagedBatches();
  }

  goToNextPage(): void {
    if (this.pageIndex >= this.totalPages - 1) return;
    this.pageIndex++;
    this.updatePagedBatches();
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
