import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'categoryBadge',
  standalone: true,
})
export class CategoryBadgePipe implements PipeTransform {
  transform(category: string | null): string {
    if (!category) return 'N/A';
    const parts = category.split('.');
    return parts[parts.length - 1] || category;
  }
}
