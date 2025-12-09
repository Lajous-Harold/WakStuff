import { Component, Input, Output, EventEmitter, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CraftTreeNode } from '../../../core/models';
import { environment } from '../../../core/config';

@Component({
  selector: 'app-craft-tree-node',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './craft-tree-node.component.html',
  styleUrl: './craft-tree-node.component.scss',
})
export class CraftTreeNodeComponent {
  @Input() node!: CraftTreeNode;
  @Input() ownedItems: Set<number> = new Set();
  @Output() toggleOwned = new EventEmitter<number>();

  collapsed = signal(false);

  get isOwned(): boolean {
    return this.ownedItems.has(this.node.item_wakfu_id);
  }

  toggleCollapse(): void {
    if (this.node.children && this.node.children.length > 0) {
      this.collapsed.set(!this.collapsed());
    }
  }

  onToggleOwned(event: Event): void {
    event.stopPropagation();
    this.toggleOwned.emit(this.node.item_wakfu_id);
  }

  getItemIconUrl(itemId: number): string {
    return `${environment.apiUrl}/proxy/icon/${itemId}`;
  }
}
