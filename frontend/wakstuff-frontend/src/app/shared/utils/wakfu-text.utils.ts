/**
 * Utilities for cleaning Wakfu text formatting codes
 */

/**
 * Removes Wakfu pluralization codes from text
 * Example: "Casque{[~1]?s:}" -> "Casque"
 */
export function cleanWakfuText(text: string | null | undefined): string {
  if (!text) return '';
  // Removes patterns like {[~1]?s:}, {[~1]?x:}, {[~1]?ies:y}, etc.
  return text.replace(/\{[^}]*\}/g, '').trim();
}

/**
 * Extracts and cleans title from multilingual object
 * Priority: fr > en > es > pt
 */
export function getCleanTitle(
  titleObj: { fr?: string; en?: string; es?: string; pt?: string } | null | undefined
): string {
  if (!titleObj) return '';
  const text = titleObj.fr || titleObj.en || titleObj.es || titleObj.pt || '';
  return cleanWakfuText(text);
}
