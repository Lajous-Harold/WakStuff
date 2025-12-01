import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'levelDisplay',
  standalone: true,
})
export class LevelDisplayPipe implements PipeTransform {
  transform(level: number | null): string {
    if (level === null || level === undefined) return 'N/A';
    return `Niv. ${level}`;
  }
}
