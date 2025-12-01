/**
 * Formatte un nombre en ajoutant des espaces comme séparateurs de milliers
 * @param value - Le nombre à formatter
 * @returns Le nombre formatté avec des espaces
 * @example
 * formatNumber(1234567) // "1 234 567"
 */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0';
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

/**
 * Calcule le pourcentage d'une valeur par rapport à un total
 * @param value - La valeur
 * @param total - Le total
 * @param decimals - Nombre de décimales (défaut: 1)
 * @returns Le pourcentage formatté
 * @example
 * calculatePercentage(25, 100) // "25.0%"
 */
export function calculatePercentage(value: number, total: number, decimals: number = 1): string {
  if (total === 0) return '0%';
  const percentage = (value / total) * 100;
  return `${percentage.toFixed(decimals)}%`;
}

/**
 * Tronque un texte à une longueur maximale et ajoute "..."
 * @param text - Le texte à tronquer
 * @param maxLength - Longueur maximale
 * @returns Le texte tronqué
 * @example
 * truncateText("Lorem ipsum dolor sit amet", 10) // "Lorem ipsu..."
 */
export function truncateText(text: string, maxLength: number): string {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Formate une date en format français lisible
 * @param date - La date à formatter (string ISO ou Date)
 * @returns La date formatée
 * @example
 * formatDate("2025-01-15T10:30:00") // "15/01/2025 à 10:30"
 */
export function formatDate(date: string | Date | null): string {
  if (!date) return 'N/A';

  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) return 'Date invalide';

  const day = d.getDate().toString().padStart(2, '0');
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const year = d.getFullYear();
  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');

  return `${day}/${month}/${year} à ${hours}:${minutes}`;
}

/**
 * Retourne la couleur CSS associée à une rareté
 * @param rarity - La rareté
 * @returns La classe CSS de couleur
 */
export function getRarityColorClass(rarity: string | null): string {
  if (!rarity) return 'rarity-common';
  return `rarity-${rarity.toLowerCase()}`;
}

/**
 * Extrait le dernier segment d'une catégorie (après le dernier point)
 * @param category - La catégorie complète
 * @returns Le nom court de la catégorie
 * @example
 * getCategoryShortName("equipments.weapons.swords") // "swords"
 */
export function getCategoryShortName(category: string | null): string {
  if (!category) return 'N/A';
  const parts = category.split('.');
  return parts[parts.length - 1] || category;
}

/**
 * Détermine si une date est récente (moins de 24h)
 * @param date - La date à vérifier
 * @returns true si la date est récente
 */
export function isRecentDate(date: string | Date | null): boolean {
  if (!date) return false;

  const d = typeof date === 'string' ? new Date(date) : date;
  if (isNaN(d.getTime())) return false;

  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const hoursDiff = diff / (1000 * 60 * 60);

  return hoursDiff < 24;
}

/**
 * Formate une durée en secondes en format lisible
 * @param seconds - Durée en secondes
 * @returns La durée formatée
 * @example
 * formatDuration(3661) // "1h 1m 1s"
 */
export function formatDuration(seconds: number | null): string {
  if (seconds === null || seconds === undefined || seconds < 0) return 'N/A';

  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  const parts: string[] = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(' ');
}
