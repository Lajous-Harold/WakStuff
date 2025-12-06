import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-error-message',
  standalone: true,
  template: `
    <div class="error-container" [class]="type()">
      <div class="error-icon">
        @if (type() === 'error') { ❌ } @else if (type() === 'warning') { ⚠️ } @else { ℹ️ }
      </div>

      <div class="error-content">
        @if (title()) {
        <h3 class="error-title">{{ title() }}</h3>
        }
        <p class="error-message">{{ message() }}</p>

        @if (details()) {
        <details class="error-details">
          <summary>Détails techniques</summary>
          <pre>{{ details() }}</pre>
        </details>
        }
      </div>

      @if (dismissible()) {
      <button class="error-close" (click)="dismiss.emit()" aria-label="Fermer">✕</button>
      }
    </div>
  `,
  styles: [
    `
      .error-container {
        display: flex;
        gap: 1rem;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        position: relative;

        &.error {
          background: #fee;
          border-left: 4px solid #c33;
          color: #c33;
        }

        &.warning {
          background: #fffbea;
          border-left: 4px solid #f39c12;
          color: #856404;
        }

        &.info {
          background: #e7f3ff;
          border-left: 4px solid #3498db;
          color: #004085;
        }
      }

      .error-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
      }

      .error-content {
        flex: 1;
      }

      .error-title {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
      }

      .error-message {
        margin: 0;
        line-height: 1.5;
      }

      .error-details {
        margin-top: 0.5rem;

        summary {
          cursor: pointer;
          font-size: 0.9rem;
          color: inherit;
          opacity: 0.8;

          &:hover {
            opacity: 1;
          }
        }

        pre {
          margin-top: 0.5rem;
          padding: 0.5rem;
          background: rgba(0, 0, 0, 0.05);
          border-radius: 4px;
          font-size: 0.85rem;
          overflow-x: auto;
        }
      }

      .error-close {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0.5;
        transition: opacity 0.2s;

        &:hover {
          opacity: 1;
        }
      }
    `,
  ],
})
export class ErrorMessageComponent {
  type = input<'error' | 'warning' | 'info'>('error');
  title = input<string>('');
  message = input.required<string>();
  details = input<string>('');
  dismissible = input<boolean>(false);

  dismiss = output<void>();
}
