import { Component, computed, input, signal } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

import { DARE_LANGUAGE_DATASETS } from './dare-language-datasets.data';
import {
  DareLanguageDataset,
  DarePublicationState,
} from './dare-language-datasets.model';

/** A language filter option with the number of matching datasets. */
interface LanguageOption {
  code: string;
  name: string;
  count: number;
}

/** A publication-state filter option. */
interface StateOption {
  key: DarePublicationState;
  count: number;
}

/**
 * DARE "African Language Datasets" interface.
 *
 * A self-contained, metadata-only discovery panel rendered from the verified
 * catalogue export (`dare-language-datasets.data.ts`). It provides:
 *  - full-text dataset search (title, task, language, licence),
 *  - language filters,
 *  - task / licence / attribution / provenance / validation display,
 *  - approved research-report links,
 *  - clear separation of metadata-only, approved-for-redistribution and
 *    awaiting-licence-review datasets.
 *
 * It never offers an unauthorized download: a download affordance is rendered
 * only when a dataset's `downloadPermitted` flag is true, which the catalogue
 * sets only for `APPROVED_FOR_RESEARCH`/`APPROVED_FOR_REDISTRIBUTION` states.
 */
@Component({
  selector: 'ds-dare-language-datasets',
  templateUrl: './dare-language-datasets.component.html',
  styleUrls: ['./dare-language-datasets.component.scss'],
  imports: [
    TranslateModule,
  ],
})
export class DareLanguageDatasetsComponent {

  /** Dataset source; overridable for testing and for later REST wiring. */
  readonly datasets = input<DareLanguageDataset[]>(DARE_LANGUAGE_DATASETS);

  /** Free-text search term. */
  readonly searchTerm = signal('');

  /** Active language filter (ISO code) or null for "all". */
  readonly activeLanguage = signal<string | null>(null);

  /** Active publication-state filter or null for "all". */
  readonly activeState = signal<DarePublicationState | null>(null);

  /** Language filters derived from the datasets, with counts. */
  readonly languageOptions = computed<LanguageOption[]>(() => {
    const options = new Map<string, LanguageOption>();
    for (const dataset of this.datasets()) {
      for (const language of dataset.languages) {
        const existing = options.get(language.code);
        if (existing) {
          existing.count += 1;
        } else {
          options.set(language.code, {
            code: language.code,
            name: language.name,
            count: 1,
          });
        }
      }
    }
    return Array.from(options.values()).sort((a, b) => a.name.localeCompare(b.name));
  });

  /** Publication-state filter options, with counts. */
  readonly stateOptions = computed<StateOption[]>(() => {
    const order: DarePublicationState[] = [
      'metadata-only',
      'approved-for-redistribution',
      'awaiting-licence-review',
    ];
    return order
      .map((key) => ({
        key,
        count: this.datasets().filter((d) => d.publicationState === key).length,
      }))
      .filter((option) => option.count > 0);
  });

  /** Datasets matching the current search and filters. */
  readonly filtered = computed<DareLanguageDataset[]>(() => {
    const term = this.searchTerm().trim().toLowerCase();
    const language = this.activeLanguage();
    const state = this.activeState();
    return this.datasets().filter((dataset) => {
      if (language && !dataset.languages.some((l) => l.code === language)) {
        return false;
      }
      if (state && dataset.publicationState !== state) {
        return false;
      }
      return term === '' || this.matchesTerm(dataset, term);
    });
  });

  /** True when at least one filter or the search box is active. */
  readonly hasFilters = computed<boolean>(() =>
    this.searchTerm().trim() !== '' ||
    this.activeLanguage() !== null ||
    this.activeState() !== null);

  /** Update the search term from the input event. */
  onSearch(event: Event): void {
    this.searchTerm.set((event.target as HTMLInputElement).value);
  }

  /** Toggle a language filter (clicking the active one clears it). */
  toggleLanguage(code: string): void {
    this.activeLanguage.set(this.activeLanguage() === code ? null : code);
  }

  /** Toggle a publication-state filter. */
  toggleState(key: DarePublicationState): void {
    this.activeState.set(this.activeState() === key ? null : key);
  }

  /** Reset every filter. */
  clearFilters(): void {
    this.searchTerm.set('');
    this.activeLanguage.set(null);
    this.activeState.set(null);
  }

  /** Translate key for a publication state. */
  stateLabelKey(state: DarePublicationState): string {
    return 'home.dare-language-datasets.state.' + state;
  }

  /** Public URL for an approved report asset. */
  reportUrl(name: string): string {
    return 'assets/custom/reports/' + name;
  }

  private matchesTerm(dataset: DareLanguageDataset, term: string): boolean {
    const haystack = [
      dataset.title,
      dataset.task,
      dataset.licence.spdx,
      dataset.licence.name,
      dataset.attribution.curator,
      dataset.provenance.notes,
      ...dataset.languages.map((l) => l.code),
      ...dataset.languages.map((l) => l.name),
    ];
    return haystack.some((value) =>
      typeof value === 'string' && value.toLowerCase().includes(term));
  }
}
