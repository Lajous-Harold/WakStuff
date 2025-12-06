import { Component, input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  template: `
    <div class="spinner-container" [class.inline]="inline()">
      <div class="spinner" [style.width.px]="size()" [style.height.px]="size()"></div>
      @if (message()) {
      <p class="spinner-message">{{ message() }}</p>
      }
    </div>
  `,
  styles: [
    `
      .spinner-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;

        &.inline {
          padding: 0.5rem;
          display: inline-flex;
        }
      }

      .spinner {
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top-color: #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }

      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }

      .spinner-message {
        margin-top: 1rem;
        color: #666;
        font-size: 0.9rem;
      }
    `,
  ],
})
export class LoadingSpinnerComponent {
  size = input<number>(40);
  message = input<string>('');
  inline = input<boolean>(false);
}
