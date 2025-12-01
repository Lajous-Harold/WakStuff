import { Pipe, PipeTransform } from '@angular/core';

/**
 * Pipe pour afficher le label d'une rareté en fonction de la langue
 *
 * Usage:
 * {{ 'common' | rarityLabel:'fr' }} -> "Commun"
 * {{ 'legendary' | rarityLabel:'en' }} -> "Legendary"
 */
@Pipe({
  name: 'rarityLabel',
  standalone: true,
})
export class RarityLabelPipe implements PipeTransform {
  private readonly labels: Record<string, { fr: string; en: string }> = {
    common: { fr: 'Commun', en: 'Common' },
    unusual: { fr: 'Inhabituel', en: 'Unusual' },
    rare: { fr: 'Rare', en: 'Rare' },
    mythical: { fr: 'Mythique', en: 'Mythical' },
    legendary: { fr: 'Légendaire', en: 'Legendary' },
    relic: { fr: 'Relique', en: 'Relic' },
    souvenir: { fr: 'Souvenir', en: 'Souvenir' },
    epic: { fr: 'Épique', en: 'Epic' },
  };

  transform(rarity: string, lang: 'fr' | 'en' = 'fr'): string {
    const label = this.labels[rarity?.toLowerCase()];
    if (label) {
      return label[lang];
    }

    // Fallback: capitaliser la première lettre
    return rarity ? rarity.charAt(0).toUpperCase() + rarity.slice(1).toLowerCase() : '';
  }
}
