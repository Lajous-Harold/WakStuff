import { Pipe, PipeTransform } from '@angular/core';

/**
 * Pipe pour afficher le label d'une catégorie en fonction de la langue
 *
 * Usage:
 * {{ 'equipments.belt' | categoryLabel:'fr' }} -> "Ceintures"
 * {{ 'equipments.belt' | categoryLabel:'en' }} -> "Belts"
 */
@Pipe({
  name: 'categoryLabel',
  standalone: true,
})
export class CategoryLabelPipe implements PipeTransform {
  private readonly labels: Record<string, { fr: string; en: string }> = {
    // Équipements
    equipments: { fr: 'Équipements', en: 'Equipment' },
    'equipments.helmets': { fr: 'Casques', en: 'Helmets' },
    'equipments.chest': { fr: 'Plastrons', en: 'Breastplates' },
    'equipments.shoulders': { fr: 'Épaulettes', en: 'Epaulettes' },
    'equipments.legs': { fr: 'Jambes', en: 'Legs' },
    'equipments.back': { fr: 'Capes', en: 'Cloaks' },
    'equipments.belt': { fr: 'Ceintures', en: 'Belts' },
    'equipments.boots': { fr: 'Bottes', en: 'Boots' },
    'equipments.amulet': { fr: 'Amulettes', en: 'Amulets' },
    'equipments.ring': { fr: 'Anneaux', en: 'Rings' },
    'equipments.shield': { fr: 'Boucliers', en: 'Shields' },
    'equipments.weapons.one_handed': { fr: 'Armes 1 main', en: 'One-Handed Weapons' },
    'equipments.weapons.two_handed': { fr: 'Armes 2 mains', en: 'Two-Handed Weapons' },
    'equipments.pet': { fr: 'Familiers', en: 'Pets' },
    'equipments.mount': { fr: 'Montures', en: 'Mounts' },
    'equipments.costume': { fr: 'Cosmétiques', en: 'Cosmetics' },
    'equipments.emblem': { fr: 'Emblèmes', en: 'Emblems' },

    // Consommables
    consumables: { fr: 'Consommables', en: 'Consumables' },
    'consumables.food': { fr: 'Nourriture', en: 'Food' },
    'consumables.potions': { fr: 'Potions', en: 'Potions' },
    'consumables.buffs': { fr: 'Buffs', en: 'Buffs' },

    // Autres
    quest_items: { fr: 'Objets de quête', en: 'Quest Items' },
    bags: { fr: 'Sacs', en: 'Bags' },
    keys: { fr: 'Clés', en: 'Keys' },
    runes: { fr: 'Enchantements', en: 'Enchantments' },
    sublimations: { fr: 'Sublimations', en: 'Sublimations' },
    tokens: { fr: 'Jetons', en: 'Tokens' },
    recipes: { fr: 'Recettes', en: 'Recipes' },
    improvements: { fr: 'Améliorations', en: 'Improvements' },
    relics: { fr: 'Reliques', en: 'Relics' },
    sets: { fr: 'Panoplies', en: 'Sets' },
    tools: { fr: 'Outils', en: 'Tools' },
    furniture: { fr: 'Mobilier', en: 'Furniture' },
    teleportation: { fr: 'Téléportation', en: 'Teleportation' },
    transformations: { fr: 'Transformations', en: 'Transformations' },
    events: { fr: 'Événements', en: 'Events' },
    misc: { fr: 'Divers', en: 'Miscellaneous' },
  };

  transform(categoryName: string, lang: 'fr' | 'en' = 'fr'): string {
    const label = this.labels[categoryName];
    if (label) {
      return label[lang];
    }

    // Fallback: formatter le nom technique
    return this.formatTechnicalName(categoryName);
  }

  private formatTechnicalName(name: string): string {
    // Prendre la dernière partie après le point
    const parts = name.split('.');
    const last = parts[parts.length - 1];

    // Remplacer underscores par espaces et capitaliser
    return last
      .replace(/_/g, ' ')
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
}
