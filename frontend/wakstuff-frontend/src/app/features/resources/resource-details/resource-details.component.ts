import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ResourcesService } from '../../../core/services/resources.service';
import { ImportStatusService } from '../../../core/services/import-status.service';
import { ResourceDetail } from '../../../core/models';
import { LoadingSpinnerComponent, ErrorMessageComponent } from '../../../shared/components';
import { EmptyStateComponent } from '../../../shared/components/empty-state/empty-state.component';

@Component({
  selector: 'app-resource-details',
  standalone: true,
  imports: [LoadingSpinnerComponent, ErrorMessageComponent, EmptyStateComponent],
  templateUrl: './resource-details.component.html',
  styleUrl: './resource-details.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResourceDetailsComponent implements OnInit {
  resource = signal<ResourceDetail | null>(null);
  loading = signal(true);
  error = signal<string | null>(null);
  hasData = signal(true);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private resourcesService: ResourcesService,
    private importStatusService: ImportStatusService
  ) {}

  ngOnInit(): void {
    // Vérifier d'abord si des données ont été importées
    this.importStatusService.checkImportStatus().subscribe({
      next: (hasData) => {
        if (!hasData) {
          // Pas de données importées
          this.hasData.set(false);
          this.loading.set(false);
          return;
        }

        // Des données existent, charger normalement
        this.route.params.subscribe((params) => {
          const wakfuId = Number(params['wakfuId']);
          if (wakfuId) {
            this.loadResource(wakfuId);
          }
        });
      },
      error: () => {
        this.hasData.set(false);
        this.loading.set(false);
      },
    });
  }

  loadResource(wakfuId: number): void {
    this.loading.set(true);
    this.error.set(null);

    this.resourcesService.getResourceDetail(wakfuId).subscribe({
      next: (resource) => {
        this.resource.set(resource);
        this.hasData.set(true);
        this.loading.set(false);
      },
      error: (err) => {
        // Ne pas logger les 404, c'est juste une ressource introuvable
        if (err.status === 404) {
          this.error.set('Ressource non trouvée');
        } else {
          console.error('Erreur lors du chargement de la ressource', err);
          this.error.set('Erreur lors du chargement de la ressource');
        }
        this.loading.set(false);
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/resources']);
  }
}
