import { HttpClient } from '@angular/common/http';
import {
  Component,
  inject,
  signal,
} from '@angular/core';
import { firstValueFrom } from 'rxjs';

/** One source cited in a librarian answer. */
export interface LibrarianCitation {
  n: number;
  sourceId: string;
  title: string;
  authors: string[];
  year: number | null;
  publisher?: string | null;
  url: string;
  page?: number | null;
  hasFulltext: boolean;
}

/** Which answer engine produced an answer. */
export interface LibrarianProvider {
  name: string;
  mode: string;
  fallback?: boolean;
  reason?: string;
}

/** One grounded answer as returned by the librarian API. */
export interface LibrarianAnswer {
  question: string;
  answer: string;
  grounded: boolean;
  insufficient: boolean;
  citations: LibrarianCitation[];
  provider?: LibrarianProvider;
  disclaimer?: string;
  error?: string;
}

/** A single message shown in the conversation log. */
export interface LibrarianMessage {
  role: 'user' | 'bot';
  text: string;
  citations?: LibrarianCitation[];
  insufficient?: boolean;
}

/**
 * DARE "AI Librarian" chat interface.
 *
 * A self-contained, accessible discovery assistant. It asks the DARE Local AI
 * Librarian service (proxied at `/librarian`) questions, renders grounded
 * answers and shows the catalogue records used as citations. It never invents
 * sources: the service returns an explicit "insufficient" answer when the
 * catalogue cannot support a response.
 *
 * The backend binds to loopback only; the DARE frontend proxies the read-only
 * JSON API (see `server.ts`).
 */
@Component({
  selector: 'ds-dare-librarian',
  templateUrl: './dare-librarian.component.html',
  styleUrls: ['./dare-librarian.component.scss'],
})
export class DareLibrarianComponent {

  /** Read-only API endpoint (proxied to the librarian service). */
  readonly endpoint = '/librarian/api/ask';

  /** Example prompts shown as chips. */
  readonly suggestions: string[] = [
    'agriculture and food security',
    'Zimbabwe research',
    'climate change adaptation',
    'public health',
  ];

  /** Conversation log. */
  readonly messages = signal<LibrarianMessage[]>([
    {
      role: 'bot',
      text: 'Hello. Ask me about books, articles, research or datasets in the '
        + 'DARE Digital Library. I answer using the catalogue and cite every '
        + 'source I use.',
    },
  ]);

  /** Current input value. */
  readonly question = signal('');

  /** True while a request is in flight. */
  readonly loading = signal(false);

  /** Last error message, if any. */
  readonly error = signal('');

  private readonly http = inject(HttpClient);

  /** Update the input value. */
  onInput(event: Event): void {
    this.question.set((event.target as HTMLTextAreaElement).value);
  }

  /** Enter submits; Shift+Enter inserts a newline. */
  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void this.ask();
    }
  }

  /** Form submit handler. */
  onSubmit(event: Event): void {
    event.preventDefault();
    void this.ask();
  }

  /** Ask a question (or a suggestion preset) and append the answer. */
  async ask(preset?: string): Promise<void> {
    const q = (preset ?? this.question()).trim();
    if (!q || this.loading()) {
      return;
    }
    this.error.set('');
    this.question.set('');
    this.messages.update((m) => [...m, { role: 'user', text: q }]);
    this.loading.set(true);
    try {
      const res = await firstValueFrom(
        this.http.post<LibrarianAnswer>(this.endpoint, { question: q }));
      if (res && res.answer) {
        this.messages.update((m) => [...m, {
          role: 'bot',
          text: res.answer,
          citations: res.citations || [],
          insufficient: res.insufficient,
        }]);
      } else {
        this.pushBot('The librarian did not return an answer. Please try again.');
      }
    } catch {
      this.error.set('The librarian is temporarily unavailable.');
      this.pushBot('Sorry, the librarian is temporarily unavailable. '
        + 'Please try again shortly.');
    } finally {
      this.loading.set(false);
    }
  }

  /** Format an author list for display. */
  authorLine(citation: LibrarianCitation): string {
    const authors = citation.authors || [];
    if (authors.length === 0) {
      return 'Unknown author';
    }
    if (authors.length === 1) {
      return authors[0];
    }
    if (authors.length === 2) {
      return `${authors[0]} and ${authors[1]}`;
    }
    return `${authors[0]} et al.`;
  }

  private pushBot(text: string): void {
    this.messages.update((m) => [...m, { role: 'bot', text }]);
  }
}
