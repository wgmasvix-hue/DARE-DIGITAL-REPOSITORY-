import { provideHttpClient } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';

import {
  DareLibrarianComponent,
  LibrarianAnswer,
} from './dare-librarian.component';

/** A grounded answer fixture. */
function makeAnswer(overrides: Partial<LibrarianAnswer> = {}): LibrarianAnswer {
  return {
    question: 'climate',
    answer: 'Here is what I found.',
    grounded: true,
    insufficient: false,
    citations: [{
      n: 1,
      sourceId: 'uuid-1',
      title: 'Climate and Agriculture',
      authors: ['Yadav, Neeru'],
      year: 2018,
      publisher: 'Zenodo',
      url: 'https://library.dare.co.zw/items/uuid-1',
      page: null,
      hasFulltext: false,
    }],
    provider: { name: 'extractive', mode: 'extractive' },
    disclaimer: 'Verify against the source.',
    ...overrides,
  };
}

describe('DareLibrarianComponent', () => {
  let component: DareLibrarianComponent;
  let fixture: ComponentFixture<DareLibrarianComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DareLibrarianComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();

    fixture = TestBed.createComponent(DareLibrarianComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('shows a welcome message initially', () => {
    expect(component.messages().length).toBe(1);
    expect(component.messages()[0].role).toBe('bot');
  });

  it('ignores empty questions', async () => {
    await component.ask();
    httpMock.expectNone('/librarian/api/ask');
    expect(component.messages().length).toBe(1);
  });

  it('posts the question and appends the grounded answer with citations', async () => {
    component.question.set('climate');
    const promise = component.ask();

    const req = httpMock.expectOne('/librarian/api/ask');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ question: 'climate' });
    req.flush(makeAnswer());
    await promise;

    const msgs = component.messages();
    const user = msgs[msgs.length - 2];
    expect(user.role).toBe('user');
    expect(user.text).toBe('climate');
    const bot = msgs[msgs.length - 1];
    expect(bot.role).toBe('bot');
    expect(bot.citations?.length).toBe(1);
    expect(bot.citations?.[0].title).toBe('Climate and Agriculture');
  });

  it('clears the input after asking', async () => {
    component.question.set('maize');
    const promise = component.ask();
    httpMock.expectOne('/librarian/api/ask').flush(makeAnswer());
    await promise;
    expect(component.question()).toBe('');
  });

  it('shows a friendly message when the service fails', async () => {
    component.question.set('anything');
    const promise = component.ask();
    httpMock.expectOne('/librarian/api/ask').error(new ErrorEvent('network'));
    await promise;
    expect(component.error()).not.toBe('');
    expect(component.messages()[component.messages().length - 1].text)
      .toContain('unavailable');
  });

  it('marks insufficient answers', async () => {
    component.question.set('obscure');
    const promise = component.ask();
    httpMock.expectOne('/librarian/api/ask').flush(
      makeAnswer({ grounded: false, insufficient: true, citations: [] }));
    await promise;
    const bot = component.messages()[component.messages().length - 1];
    expect(bot.insufficient).toBe(true);
  });

  it('sends a suggestion preset', async () => {
    const promise = component.ask('public health');
    const req = httpMock.expectOne('/librarian/api/ask');
    expect(req.request.body).toEqual({ question: 'public health' });
    req.flush(makeAnswer());
    await promise;
  });

  it('formats author lines', () => {
    const base = makeAnswer().citations[0];
    expect(component.authorLine({ ...base, authors: [] })).toBe('Unknown author');
    expect(component.authorLine({ ...base, authors: ['A'] })).toBe('A');
    expect(component.authorLine({ ...base, authors: ['A', 'B'] })).toBe('A and B');
    expect(component.authorLine({ ...base, authors: ['A', 'B', 'C'] })).toBe('A et al.');
  });

  it('renders the composer and suggestions', () => {
    const el: HTMLElement = fixture.nativeElement;
    expect(el.querySelector('#dare-librarian')).toBeTruthy();
    expect(el.querySelectorAll('.dare-librarian__chip').length)
      .toBe(component.suggestions.length);
    expect(el.querySelector('#dare-librarian-input')).toBeTruthy();
  });
});
