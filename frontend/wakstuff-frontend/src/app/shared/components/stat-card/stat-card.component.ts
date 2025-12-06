import { Component, input } from '@angular/core';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  template: `
    <div class="stat-card" [class]="variant()">
      @if (icon()) {
      <div class="stat-icon">{{ icon() }}</div>
      }

      <div class="stat-content">
        <div class="stat-label">{{ label() }}</div>
        <div class="stat-value">
          {{ value() }}
          @if (unit()) {
          <span class="stat-unit">{{ unit() }}</span>
          }
        </div>

        @if (subtitle()) {
        <div class="stat-subtitle">{{ subtitle() }}</div>
        } @if (trend() !== undefined) {
        <div class="stat-trend" [class.positive]="trend()! > 0" [class.negative]="trend()! < 0">
          {{ trend()! > 0 ? '↑' : '↓' }} {{ Math.abs(trend()!) }}%
        </div>
        }
      </div>
    </div>
  `,
  styles: [
    `
      .stat-card {
        display: flex;
        gap: 1rem;
        padding: 1.5rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        &.primary {
          border-left: 4px solid #3498db;
        }

        &.success {
          border-left: 4px solid #2ecc71;
        }

        &.warning {
          border-left: 4px solid #f39c12;
        }

        &.danger {
          border-left: 4px solid #e74c3c;
        }

        &.info {
          border-left: 4px solid #9b59b6;
        }
      }

      .stat-icon {
        font-size: 2.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        flex-shrink: 0;
      }

      .stat-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }

      .stat-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #333;
        line-height: 1;
      }

      .stat-unit {
        font-size: 1rem;
        font-weight: 400;
        color: #999;
        margin-left: 0.25rem;
      }

      .stat-subtitle {
        font-size: 0.85rem;
        color: #999;
        margin-top: 0.25rem;
      }

      .stat-trend {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;

        &.positive {
          color: #2ecc71;
        }

        &.negative {
          color: #e74c3c;
        }
      }
    `,
  ],
})
export class StatCardComponent {
  label = input.required<string>();
  value = input.required<string | number>();
  unit = input<string>('');
  subtitle = input<string>('');
  icon = input<string>('');
  variant = input<'primary' | 'success' | 'warning' | 'danger' | 'info'>('primary');
  trend = input<number>();

  // Pour le template
  Math = Math;
}
