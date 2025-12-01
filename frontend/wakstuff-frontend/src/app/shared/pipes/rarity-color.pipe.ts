import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'rarityColor',
  standalone: true,
})
export class RarityColorPipe implements PipeTransform {
  transform(rarity: string | null): string {
    if (!rarity) return 'rarity-common';
    return `rarity-${rarity.toLowerCase()}`;
  }
}
