import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="empty-state">
      <div class="empty-state-icon">{{ icon() }}</div>
      <h2 class="empty-state-title">{{ title() }}</h2>
      <p class="empty-state-message">{{ message() }}</p>
      @if (showImportLink()) {
      <a routerLink="/imports" class="empty-state-action">
        <span class="action-icon">⚙️</span>
        <span>Aller à la page d'imports</span>
      </a>
      }
    </div>
  `,
  styles: [
    `
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        text-align: center;
        min-height: 400px;
      }

      .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        opacity: 0.5;
      }

      .empty-state-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.75rem;
      }

      .empty-state-message {
        font-size: 1rem;
        color: #7f8c8d;
        max-width: 500px;
        line-height: 1.6;
        margin-bottom: 2rem;
      }

      .empty-state-action {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
      }

      .empty-state-action:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
      }

      .action-icon {
        font-size: 1.2rem;
      }
    `,
  ],
})
export class EmptyStateComponent {
  icon = input<string>('📦');
  title = input<string>('Aucune donnée disponible');
  message = input<string>(
    "Aucun import n'a encore été effectué. Veuillez importer les données depuis la page d'imports."
  );
  showImportLink = input<boolean>(true);
}
