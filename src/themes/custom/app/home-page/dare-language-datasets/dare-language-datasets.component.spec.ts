import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { TranslateModule } from '@ngx-translate/core';

import { DareLanguageDatasetsComponent } from './dare-language-datasets.component';
import {
  DareLanguageDataset,
  DarePublicationState,
} from './dare-language-datasets.model';

/** Build a dataset fixture with sensible defaults. */
function makeDataset(overrides: Partial<DareLanguageDataset> = {}): DareLanguageDataset {
  return {
    id: 'sample',
    title: 'Sample Dataset',
    task: 'named-entity-recognition',
    languages: [{ code: 'sn', name: 'chiShona' }],
    licence: {
      spdx: 'CC-BY-NC-4.0',
      name: 'Creative Commons Attribution-NonCommercial 4.0 International',
      url: 'https://creativecommons.org/licenses/by-nc/4.0/',
      commercialUse: false,
      requiresAttribution: true,
      status: 'RESOLVED_NONCOMMERCIAL',
    },
    attribution: { curator: null, citation: null },
    provenance: {
      sourceUrl: 'https://example.org/sample',
      repository: 'https://example.org/sample',
      revision: 'abc123',
      retrieved: null,
      validationStatus: 'not_validated',
      notes: 'sample note',
    },
    publicationState: 'metadata-only',
    lifecycleState: 'VALIDATED',
    downloadPermitted: false,
    reportLinks: ['final-project-report.md'],
    ...overrides,
  };
}

const SAMPLE: DareLanguageDataset[] = [
  makeDataset({ id: 'shona-ner', title: 'Shona NER', languages: [{ code: 'sn', name: 'chiShona' }] }),
  makeDataset({
    id: 'ndebele-pos', title: 'Ndebele POS', task: 'part-of-speech',
    languages: [{ code: 'nd', name: 'isiNdebele' }],
    publicationState: 'awaiting-licence-review',
    licence: { spdx: null, name: null, url: null, commercialUse: null, requiresAttribution: null, status: 'UNRESOLVED' },
  }),
  makeDataset({
    id: 'multi', title: 'Multilingual Corpus',
    languages: [{ code: 'sn', name: 'chiShona' }, { code: 'nd', name: 'isiNdebele' }],
    publicationState: 'approved-for-redistribution',
    downloadPermitted: true,
  }),
];

describe('DareLanguageDatasetsComponent', () => {
  let component: DareLanguageDatasetsComponent;
  let fixture: ComponentFixture<DareLanguageDatasetsComponent>;

  const cards = (): NodeListOf<Element> =>
    fixture.nativeElement.querySelectorAll('.dare-lang-card');

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        DareLanguageDatasetsComponent,
        TranslateModule.forRoot(),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DareLanguageDatasetsComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('datasets', SAMPLE);
    fixture.detectChanges();
  });

  it('renders one card per dataset', () => {
    expect(cards().length).toBe(3);
  });

  it('derives unique language options with counts', () => {
    const options = component.languageOptions();
    expect(options.length).toBe(2);
    expect(options.find((o) => o.code === 'sn').count).toBe(2);
    expect(options.find((o) => o.code === 'nd').count).toBe(2);
  });

  it('derives publication-state options with counts', () => {
    const options = component.stateOptions();
    const countOf = (key: DarePublicationState) =>
      options.find((o) => o.key === key)?.count ?? 0;
    expect(countOf('metadata-only')).toBe(1);
    expect(countOf('awaiting-licence-review')).toBe(1);
    expect(countOf('approved-for-redistribution')).toBe(1);
  });

  it('filters by free-text search', () => {
    component.onSearch({ target: { value: 'ndebele' } } as unknown as Event);
    fixture.detectChanges();
    expect(component.filtered().length).toBe(1);
    expect(component.filtered()[0].id).toBe('ndebele-pos');
    expect(cards().length).toBe(1);
  });

  it('filters by language', () => {
    component.toggleLanguage('nd');
    fixture.detectChanges();
    expect(component.filtered().map((d) => d.id).sort()).toEqual(['multi', 'ndebele-pos']);
    // toggling again clears the filter
    component.toggleLanguage('nd');
    expect(component.filtered().length).toBe(3);
  });

  it('filters by publication state', () => {
    component.toggleState('awaiting-licence-review');
    fixture.detectChanges();
    expect(component.filtered().map((d) => d.id)).toEqual(['ndebele-pos']);
  });

  it('clears all filters', () => {
    component.onSearch({ target: { value: 'shona' } } as unknown as Event);
    component.toggleLanguage('sn');
    component.toggleState('metadata-only');
    expect(component.filtered().length).toBeLessThan(3);
    component.clearFilters();
    expect(component.filtered().length).toBe(3);
    expect(component.hasFilters()).toBeFalse();
  });

  it('shows the empty state when nothing matches', () => {
    component.onSearch({ target: { value: 'zzzzz-no-match' } } as unknown as Event);
    fixture.detectChanges();
    expect(cards().length).toBe(0);
    expect(fixture.nativeElement.querySelector('.dare-empty-state')).toBeTruthy();
  });

  it('never renders an unauthorized download affordance', () => {
    // Dataset is metadata-only and not download-permitted.
    const metadataOnly = SAMPLE[0];
    expect(metadataOnly.downloadPermitted).toBeFalse();
    const gates = fixture.nativeElement.querySelectorAll('.dare-lang-card__gate');
    expect(gates.length).toBe(3);
    // Exactly one dataset is download-permitted (the approved one).
    const okGates = fixture.nativeElement.querySelectorAll('.dare-lang-card__gate--ok');
    expect(okGates.length).toBe(1);
  });

  it('exposes only approved report links via a public asset path', () => {
    expect(component.reportUrl('final-project-report.md'))
      .toBe('assets/custom/reports/final-project-report.md');
  });

  it('maps publication states to translation keys', () => {
    expect(component.stateLabelKey('metadata-only'))
      .toBe('home.dare-language-datasets.state.metadata-only');
  });
});
