import {
  DOCUMENT,
  Inject,
  Injectable,
} from '@angular/core';
import {
  Meta,
  MetaDefinition,
  Title,
} from '@angular/platform-browser';
import {
  ActivatedRoute,
  NavigationEnd,
  Router,
} from '@angular/router';
import {
  APP_CONFIG,
  AppConfig,
} from '@dspace/config/app-config.interface';
import {
  hasNoValue,
  hasValue,
  isNotEmpty,
} from '@dspace/shared/utils/empty.util';
import {
  createSelector,
  select,
  Store,
} from '@ngrx/store';
import { TranslateService } from '@ngx-translate/core';
import {
  BehaviorSubject,
  combineLatest,
  concat as observableConcat,
  EMPTY,
  Observable,
  of,
} from 'rxjs';
import {
  filter,
  map,
  mergeMap,
  switchMap,
  take,
} from 'rxjs/operators';

import { DSONameService } from '../breadcrumbs/dso-name.service';
import { coreSelector } from '../core.selectors';
import { CoreState } from '../core-state.model';
import { BundleDataService } from '../data/bundle-data.service';
import { AuthorizationDataService } from '../data/feature-authorization/authorization-data.service';
import { FindListOptions } from '../data/find-list-options.model';
import { PaginatedList } from '../data/paginated-list.model';
import { RemoteData } from '../data/remote-data';
import { RootDataService } from '../data/root-data.service';
import {
  getBitstreamDownloadRoute,
  getDSORoute,
} from '../router/utils/dso-route.utils';
import { HardRedirectService } from '../services/hard-redirect.service';
import { LinkHeadService } from '../services/link-head.service';
import { Bitstream } from '../shared/bitstream.model';
import { getDownloadableBitstream } from '../shared/bitstream.operators';
import { BitstreamFormat } from '../shared/bitstream-format.model';
import { Bundle } from '../shared/bundle.model';
import { Collection } from '../shared/collection.model';
import { Community } from '../shared/community.model';
import { DSpaceObject } from '../shared/dspace-object.model';
import { followLink } from '../shared/follow-link-config.model';
import { Item } from '../shared/item.model';
import {
  getFirstCompletedRemoteData,
  getFirstSucceededRemoteDataPayload,
} from '../shared/operators';
import { URLCombiner } from '../url-combiner/url-combiner';
import {
  AddMetaTagAction,
  ClearMetaTagAction,
} from './meta-tag.actions';
import { MetaTagState } from './meta-tag.reducer';

/**
 * The base selector function to select the metaTag section in the store
 */
const metaTagSelector = createSelector(
  coreSelector,
  (state: CoreState) => state.metaTag,
);

/**
 * Selector function to select the tags in use from the MetaTagState
 */
const tagsInUseSelector =
  createSelector(
    metaTagSelector,
    (state: MetaTagState) => state.tagsInUse,
  );

@Injectable({
  providedIn: 'root',
})
export class HeadTagService {

  private currentObject: BehaviorSubject<DSpaceObject> = new BehaviorSubject<DSpaceObject>(undefined);

  /**
   * The route (path + query) for which head tags were last rendered. Used to
   * ignore redundant NavigationEnd events emitted for the same URL.
   */
  private lastProcessedRoute: string;

  /**
   * When generating the citation_pdf_url meta tag for Items with more than one Bitstream (and no primary Bitstream),
   * the first Bitstream to match one of the following MIME types is selected.
   * See {@linkcode getFirstAllowedFormatBitstreamLink}
   * @private
   */
  private readonly CITATION_PDF_URL_MIMETYPES = [
    'application/pdf',                                                          // .pdf
    'application/postscript',                                                   // .ps
    'application/msword',                                                       // .doc
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  // .docx
    'application/rtf',                                                          // .rtf
    'application/epub+zip',                                                     // .epub
  ];

  /**
   * Site-wide fallback description used when a route does not define its own and
   * the current page is not a repository object (home, browse, search, info pages).
   * Deliberately states only what the repository is — no invented statistics.
   */
  private readonly SITE_DESCRIPTION =
    'DARE African Knowledge Repository (Digital Academic Repository & Education) is an '
    + 'open-access repository of African scholarship, research, theses, datasets and '
    + 'heritage materials — preserving African knowledge for present and future generations.';

  /** Open Graph keys this service manages, cleared on every route change. */
  private readonly OG_KEYS = [
    'og:site_name', 'og:type', 'og:title', 'og:description', 'og:url', 'og:image',
  ];

  /** Twitter/X card keys this service manages, cleared on every route change. */
  private readonly TWITTER_KEYS = [
    'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image',
  ];


  constructor(
    protected router: Router,
    protected translate: TranslateService,
    protected meta: Meta,
    protected title: Title,
    protected dsoNameService: DSONameService,
    protected bundleDataService: BundleDataService,
    protected rootService: RootDataService,
    protected store: Store<CoreState>,
    protected hardRedirectService: HardRedirectService,
    @Inject(APP_CONFIG) protected appConfig: AppConfig,
    protected authorizationService: AuthorizationDataService,
    protected linkHeadService: LinkHeadService,
    @Inject(DOCUMENT) protected document: Document,
  ) {
  }

  public listenForRouteChange(): void {
    // This never changes, set it only once
    this.setGenerator();

    this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => this.router.routerState.root),
      map((route: ActivatedRoute) => {
        route = this.getCurrentRoute(route);
        return { params: route.params, data: route.data };
      })).subscribe((routeInfo: any) => {
      this.processRouteChange(routeInfo);
    });
  }

  protected processRouteChange(routeInfo: any): void {
    const routeTitle = routeInfo.data.value.title;
    const isNotFound = routeTitle === '404.page-not-found';
    const hasDso = hasValue(routeInfo.data.value.dso) && hasValue(routeInfo.data.value.dso.payload);
    const currentRoute = this.hardRedirectService.getCurrentRoute();

    // Angular can emit additional NavigationEnd events for the same URL while
    // nested resolvers finish. Those follow-up events typically carry no DSO
    // payload, and processing them would wipe the tags already rendered for the
    // page. Skip them so per-resource tags survive until the URL really changes.
    if (!hasDso && !isNotFound && hasValue(this.lastProcessedRoute) && currentRoute === this.lastProcessedRoute) {
      return;
    }

    this.clearMetaTags();
    this.clearSocialMetaTags();

    if (hasDso) {
      this.currentObject.next(routeInfo.data.value.dso.payload);
      this.setDSOMetaTags();
    } else {
      this.currentObject.next(undefined);
    }

    if (isNotFound) {
      // A missing page must not advertise a canonical URL, and should be kept
      // out of the search index.
      this.clearCanonicalTag();
      this.clearStructuredDataTag();
      this.addMetaTag('robots', 'noindex');
    } else {
      this.setCanonicalTag();
      this.setStructuredDataTag();
    }

    this.lastProcessedRoute = currentRoute;

    if (routeTitle) {
      const titlePrefix = this.translate.get('repository.title.prefix');
      const title = this.translate.get(routeTitle, routeInfo.data.value);
      combineLatest([titlePrefix, title]).pipe(take(1)).subscribe(([translatedTitlePrefix, translatedTitle]: [string, string]) => {
        const fullTitle = translatedTitlePrefix + translatedTitle;
        this.addMetaTag('title', fullTitle);
        this.title.setTitle(fullTitle);

        // Missing pages are marked noindex and must not be advertised to social
        // scrapers either.
        if (!isNotFound) {
          const description = this.ensureMetaDescription(routeInfo);
          this.setSocialMetaTags(fullTitle, description);
        }
      });
    } else if (!isNotFound) {
      // DSO pages (items, communities, collections) take their document title
      // straight from the object above, so advertise that same title to social
      // scrapers — a shared item link should read as the item, not the site.
      const dsoTitle = this.currentObject.value?.name;
      const fullTitle = isNotEmpty(dsoTitle)
        ? dsoTitle
        : this.translate.instant('repository.title');
      if (isNotEmpty(fullTitle) && fullTitle !== 'repository.title') {
        this.setSocialMetaTags(fullTitle, this.ensureMetaDescription(routeInfo));
      }
    }
    if (routeInfo.data.value.description) {
      this.translate.get(routeInfo.data.value.description).pipe(take(1)).subscribe((translatedDescription: string) => {
        this.addMetaTag('description', translatedDescription);
      });
    }
  }

  protected getCurrentRoute(route: ActivatedRoute): ActivatedRoute {
    while (route.firstChild) {
      route = route.firstChild;
    }
    return route;
  }

  protected setDSOMetaTags(): void {

    this.setNoIndexTag();

    this.setTitleTag();
    this.setDescriptionTag();

    this.setCitationTitleTag();
    this.setCitationAuthorTags();
    this.setCitationPublicationDateTag();
    this.setCitationISSNTag();
    this.setCitationISBNTag();

    this.setCitationLanguageTag();
    this.setCitationKeywordsTag();

    this.setCitationAbstractUrlTag();
    this.setCitationDoiTag();
    this.setCitationPdfUrlTag();
    this.setCitationPublisherTag();

    if (this.isDissertation()) {
      this.setCitationDissertationNameTag();
    }

    // this.setCitationJournalTitleTag();
    // this.setCitationVolumeTag();
    // this.setCitationIssueTag();
    // this.setCitationFirstPageTag();
    // this.setCitationLastPageTag();
    // this.setCitationPMIDTag();

    // this.setCitationFullTextTag();

    // this.setCitationConferenceTag();

    // this.setCitationPatentCountryTag();
    // this.setCitationPatentNumberTag();

  }

  /**
   * Add <meta name="robots" content="noindex">  to the <head> if non-discoverable item
   */
  protected setNoIndexTag(): void {
    if (this.currentObject.value instanceof Item && this.currentObject.value.isDiscoverable === false) {
      this.addMetaTag('robots', 'noindex');
    }
  }

  /**
   * Add <meta name="title" ... >  to the <head>
   */
  protected setTitleTag(): void {
    const value = this.dsoNameService.getName(this.currentObject.getValue());
    this.addMetaTag('title', value);
    this.title.setTitle(value);
  }

  /**
   * Add <meta name="description" ... >  to the <head>
   */
  protected setDescriptionTag(): void {
    const value = this.buildDescription();
    this.addMetaTag('description', value);
  }

  /**
   * Determine the best available description for the current object.
   * Prefers a real abstract, falls back to other description fields and a
   * generated summary so that every public resource exposes a meta description.
   */
  protected buildDescription(): string {
    const raw = this.getMetaTagValue('dc.description.abstract')
      || this.getMetaTagValue('dc.description');
    const truncated = this.truncateText(raw, 300);
    if (hasValue(truncated)) {
      return truncated;
    }

    // Fallback: generate a summary from the metadata we do have
    const title = this.dsoNameService.getName(this.currentObject.value);
    const author = this.getFirstMetaTagValue(['dc.contributor.author', 'dc.creator', 'dc.author']);
    const type = this.getMetaTagValue('dc.type');

    const parts: string[] = [];
    if (hasValue(title)) {
      parts.push(title);
    }
    if (hasValue(author)) {
      parts.push(`by ${author}`);
    }
    if (hasValue(type)) {
      parts.push(`(${type})`);
    }
    parts.push('Available in the DARE African Knowledge Repository.');

    return this.truncateText(parts.join(' '), 300);
  }

  /**
   * Normalize whitespace, strip any HTML markup and truncate the given text to
   * a search-engine friendly length.
   */
  protected truncateText(text: string, maxLength: number): string {
    if (hasNoValue(text)) {
      return '';
    }
    const normalized = text.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    if (normalized.length <= maxLength) {
      return normalized;
    }
    return normalized.substring(0, maxLength - 1).trimEnd() + '…';
  }

  /**
   * Make sure a <meta name="description"> is always present for the current
   * route. DSpace object pages set theirs via {@linkcode setDescriptionTag};
   * routes such as home/browse/search do not, so fall back to the route's own
   * description or the site-wide description.
   *
   * @returns the description that is now on the page (or '' if none)
   */
  protected ensureMetaDescription(routeInfo: any): string {
    const existing = this.meta.getTag('name="description"');
    if (hasValue(existing) && isNotEmpty(existing.content)) {
      return existing.content;
    }

    const resolved = this.resolveRouteDescription(routeInfo);
    this.addMetaTag('description', resolved);
    return resolved;
  }

  /**
   * Resolve a description for a non-DSO route: prefer the route's own
   * translated description, otherwise the site-wide fallback description.
   */
  protected resolveRouteDescription(routeInfo: any): string {
    const key = routeInfo?.data?.value?.description;
    if (isNotEmpty(key)) {
      const translated = this.translate.instant(key);
      if (isNotEmpty(translated) && translated !== key) {
        return this.truncateText(translated, 300);
      }
    }
    return this.truncateText(this.getSiteDescription(), 300);
  }

  /**
   * The site-wide fallback description, preferring an i18n value when one is
   * available and falling back to the built-in English description.
   */
  protected getSiteDescription(): string {
    const translated = this.translate.instant('repository.description');
    if (isNotEmpty(translated) && translated !== 'repository.description') {
      return translated;
    }
    return this.SITE_DESCRIPTION;
  }

  /**
   * Add or refresh the Open Graph and Twitter/X card tags for the current page.
   * These are what social platforms and messaging previews read.
   */
  protected setSocialMetaTags(title: string, description: string): void {
    const baseUrl = this.hardRedirectService.getBaseUrl();
    if (hasNoValue(baseUrl)) {
      return;
    }

    const url = this.resolveCanonicalUrl();
    const isItem = this.currentObject.value instanceof Item;
    const type = isItem ? 'article' : 'website';

    // Open Graph (property=...)
    this.upsertTag({ property: 'og:site_name', content: 'DARE African Knowledge Repository' }, 'og:site_name');
    this.upsertTag({ property: 'og:type', content: type }, 'og:type');
    if (isNotEmpty(title)) {
      this.upsertTag({ property: 'og:title', content: title }, 'og:title');
    }
    if (isNotEmpty(description)) {
      this.upsertTag({ property: 'og:description', content: this.truncateText(description, 300) }, 'og:description');
    }
    if (hasValue(url)) {
      this.upsertTag({ property: 'og:url', content: url }, 'og:url');
    }
    this.upsertTag({ property: 'og:image', content: `${baseUrl}/assets/custom/images/dare-logo.png` }, 'og:image');

    // Twitter / X (name=...)
    this.upsertTag({ name: 'twitter:card', content: 'summary' }, 'twitter:card');
    if (isNotEmpty(title)) {
      this.upsertTag({ name: 'twitter:title', content: title }, 'twitter:title');
    }
    if (isNotEmpty(description)) {
      this.upsertTag({ name: 'twitter:description', content: this.truncateText(description, 300) }, 'twitter:description');
    }
    this.upsertTag({ name: 'twitter:image', content: `${baseUrl}/assets/custom/images/dare-logo.png` }, 'twitter:image');
  }

  /**
   * Insert or update a meta tag. Angular's {@link Meta.updateTag} only rewrites
   * an existing tag, so check first and add when the tag is new.
   *
   * @param tag     the tag to write
   * @param key     the value of the attribute that identifies it (name or property)
   */
  protected upsertTag(tag: MetaDefinition, key: string): void {
    const attr = tag.property !== undefined ? 'property' : 'name';
    const selector = `${attr}="${key}"`;
    if (hasValue(this.meta.getTag(selector))) {
      this.meta.updateTag(tag);
    } else {
      this.meta.addTag(tag);
    }
  }

  /**
   * Remove every Open Graph and Twitter tag this service manages. Open Graph
   * tags carry a `property` attribute and therefore are not tracked in the
   * metaTag store, so they must be cleared explicitly.
   */
  protected clearSocialMetaTags(): void {
    for (const key of this.OG_KEYS) {
      this.meta.removeTag(`property="${key}"`);
    }
    for (const key of this.TWITTER_KEYS) {
      this.meta.removeTag(`name="${key}"`);
    }
  }

  /**
   * Add a <link rel="canonical" ... > tag to the <head>.
   *
   * Uses the object's canonical route (honouring custom URLs) when the current
   * page represents a DSpace object. Otherwise it falls back to the current
   * route with any query string and fragment removed, so that faceted or
   * paginated URLs point search engines at a single canonical resource.
   */
  protected setCanonicalTag(): void {
    this.clearCanonicalTag();

    const href = this.resolveCanonicalUrl();
    if (hasNoValue(href)) {
      return;
    }

    this.linkHeadService.addTag({ rel: 'canonical', href });
  }

  /**
   * Resolve the absolute canonical URL for the current route (or DSO), with any
   * query string and fragment removed so faceted/paginated URLs collapse onto a
   * single canonical resource. Returns undefined when no base URL is available.
   */
  protected resolveCanonicalUrl(): string | undefined {
    const baseUrl = this.hardRedirectService.getBaseUrl();
    if (hasNoValue(baseUrl)) {
      return undefined;
    }

    let path: string;
    const dso = this.currentObject.value;
    if (hasValue(dso)) {
      path = getDSORoute(dso);
    }
    if (hasNoValue(path)) {
      path = this.hardRedirectService.getCurrentRoute().split(/[?#]/)[0];
    }
    if (hasNoValue(path)) {
      return undefined;
    }

    return new URLCombiner(baseUrl, path).toString();
  }

  /**
   * Remove any existing <link rel="canonical" ... > tags from the <head>.
   */
  protected clearCanonicalTag(): void {
    this.linkHeadService.removeTag('rel="canonical"');
  }

  /**
   * Build and inject a Schema.org JSON-LD <script> block for the current route.
   *
   * Emits a detailed {@link https://schema.org/CreativeWork} style block for
   * Items, a {@link https://schema.org/CollectionPage} block for Communities and
   * Collections, and a {@link https://schema.org/WebSite} block (with a
   * SearchAction) on the home route.
   */
  protected setStructuredDataTag(): void {
    this.clearStructuredDataTag();

    const json = this.buildStructuredData();
    if (hasNoValue(json)) {
      return;
    }

    const head = this.document.head;
    if (hasNoValue(head)) {
      return;
    }

    const script = this.document.createElement('script');
    script.setAttribute('type', 'application/ld+json');
    script.setAttribute('data-seo', 'jsonld');
    script.textContent = JSON.stringify(json);
    head.appendChild(script);
  }

  /**
   * Remove any previously injected JSON-LD <script> blocks from the <head>.
   */
  protected clearStructuredDataTag(): void {
    const head = this.document.head;
    if (hasNoValue(head)) {
      return;
    }
    const existing = head.querySelectorAll('script[data-seo="jsonld"]');
    for (let i = existing.length - 1; i >= 0; i--) {
      existing[i].remove();
    }
  }

  /**
   * Produce the Schema.org structured data object that best describes the
   * current route, or undefined when no appropriate mapping exists.
   */
  protected buildStructuredData(): any {
    const dso = this.currentObject.value;
    if (dso instanceof Item) {
      return this.buildItemStructuredData(dso);
    }
    if (dso instanceof Community || dso instanceof Collection) {
      return this.buildCollectionPageStructuredData(dso);
    }

    const route = this.hardRedirectService.getCurrentRoute().split(/[?#]/)[0];
    if (route === '' || route === '/' || route === '/home') {
      return this.buildWebsiteStructuredData();
    }
    return undefined;
  }

  /**
   * Map the repository's own `dc.type` values onto the closest Schema.org type.
   */
  protected getSchemaType(dso: DSpaceObject): string {
    const type = (dso.firstMetadataValue('dc.type') || '').toLowerCase();
    if (type.includes('thesis') || type.includes('dissertation')) {
      return 'Thesis';
    }
    if (type.includes('dataset')) {
      return 'Dataset';
    }
    if (type.includes('book')) {
      return 'Book';
    }
    if (type.includes('article') || type.includes('journal') || type.includes('paper')) {
      return 'ScholarlyArticle';
    }
    return 'CreativeWork';
  }

  /**
   * Build a {@link https://schema.org/CreativeWork} JSON-LD object for an Item.
   */
  protected buildItemStructuredData(item: Item): any {
    const title = this.dsoNameService.getName(item);
    const authors = this.getMetaTagValues(['dc.contributor.author', 'dc.creator', 'dc.author']);
    const datePublished = this.getFirstMetaTagValue(['dc.date.issued', 'dc.date.copyright', 'dc.date.available', 'dc.date']);
    const language = this.getFirstMetaTagValue(['dc.language.iso', 'dc.language']);
    const keywords = this.getMetaTagValues(['dc.subject']);
    const license = this.getMetaTagValue('dc.rights.uri');
    const url = this.buildCanonicalUrl(item);
    const identifier = item.firstMetadataValue('dc.identifier.uri');

    const data: any = {
      '@context': 'https://schema.org',
      '@type': this.getSchemaType(item),
      'name': title,
      'headline': title,
    };

    if (hasValue(url)) {
      data.url = url;
    }
    if (isNotEmpty(authors)) {
      data.author = authors.map((name: string) => ({ '@type': 'Person', 'name': name }));
    }
    if (hasValue(datePublished)) {
      data.datePublished = datePublished;
    }
    if (hasValue(language)) {
      data.inLanguage = language;
    }
    if (isNotEmpty(keywords)) {
      data.keywords = keywords.join(', ');
    }
    if (hasValue(license)) {
      data.license = license;
    }
    if (hasValue(identifier)) {
      data.identifier = identifier;
    }

    const description = this.buildDescription();
    if (isNotEmpty(description)) {
      data.description = description;
    }

    data.publisher = {
      '@type': 'Organization',
      'name': 'DARE African Knowledge Repository',
      'url': this.hardRedirectService.getBaseUrl(),
    };

    return data;
  }

  /**
   * Build a {@link https://schema.org/CollectionPage} JSON-LD object for a
   * Community or Collection.
   */
  protected buildCollectionPageStructuredData(dso: DSpaceObject): any {
    const data: any = {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      'name': this.dsoNameService.getName(dso),
    };

    const url = this.buildCanonicalUrl(dso);
    if (hasValue(url)) {
      data.url = url;
    }

    const description = this.truncateText(
      dso.firstMetadataValue(['dc.description.abstract', 'dc.description']), 300,
    );
    if (isNotEmpty(description)) {
      data.description = description;
    }

    return data;
  }

  /**
   * Build a {@link https://schema.org/WebSite} JSON-LD object for the home route,
   * including a SearchAction describing the repository search endpoint.
   */
  protected buildWebsiteStructuredData(): any {
    const baseUrl = this.hardRedirectService.getBaseUrl();
    return {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      'name': 'DARE African Knowledge Repository',
      'url': baseUrl,
      'potentialAction': {
        '@type': 'SearchAction',
        'target': {
          '@type': 'EntryPoint',
          'urlTemplate': `${baseUrl}/search?query={search_term_string}`,
        },
        'query-input': 'required name=search_term_string',
      },
    };
  }

  /**
   * Resolve the absolute canonical URL for the given DSpace object.
   */
  protected buildCanonicalUrl(dso: DSpaceObject): string {
    const baseUrl = this.hardRedirectService.getBaseUrl();
    const path = getDSORoute(dso);
    if (hasNoValue(baseUrl) || hasNoValue(path)) {
      return '';
    }
    return new URLCombiner(baseUrl, path).toString();
  }

  /**
   * Add <meta name="citation_title" ... >  to the <head>
   */
  protected setCitationTitleTag(): void {
    const value = this.getMetaTagValue('dc.title');
    this.addMetaTag('citation_title', value);
  }

  /**
   * Add <meta name="citation_author" ... >  to the <head>
   */
  protected setCitationAuthorTags(): void {
    const values: string[] = this.getMetaTagValues(['dc.author', 'dc.contributor.author', 'dc.creator']);
    this.addMetaTags('citation_author', values);
  }

  /**
   * Add <meta name="citation_publication_date" ... >  to the <head>
   */
  protected setCitationPublicationDateTag(): void {
    const value = this.getFirstMetaTagValue(['dc.date.copyright', 'dc.date.issued', 'dc.date.available', 'dc.date.accessioned']);
    this.addMetaTag('citation_publication_date', value);
  }

  /**
   * Add <meta name="citation_issn" ... >  to the <head>
   */
  protected setCitationISSNTag(): void {
    const value = this.getMetaTagValue('dc.identifier.issn');
    this.addMetaTag('citation_issn', value);
  }

  /**
   * Add <meta name="citation_isbn" ... >  to the <head>
   */
  protected setCitationISBNTag(): void {
    const value = this.getMetaTagValue('dc.identifier.isbn');
    this.addMetaTag('citation_isbn', value);
  }

  /**
   * Add <meta name="citation_language" ... >  to the <head>
   */
  protected setCitationLanguageTag(): void {
    const value = this.getFirstMetaTagValue(['dc.language', 'dc.language.iso']);
    this.addMetaTag('citation_language', value);
  }

  /**
   * Add <meta name="citation_dissertation_name" ... >  to the <head>
   */
  protected setCitationDissertationNameTag(): void {
    const value = this.getMetaTagValue('dc.title');
    this.addMetaTag('citation_dissertation_name', value);
  }

  /**
   * Add dc.publisher to the <head>. The tag name depends on the item type.
   */
  protected setCitationPublisherTag(): void {
    const value = this.getMetaTagValue('dc.publisher');
    if (this.isDissertation()) {
      this.addMetaTag('citation_dissertation_institution', value);
    } else if (this.isTechReport()) {
      this.addMetaTag('citation_technical_report_institution', value);
    } else {
      this.addMetaTag('citation_publisher', value);
    }
  }

  /**
   * Add <meta name="citation_keywords" ... >  to the <head>
   */
  protected setCitationKeywordsTag(): void {
    const value = this.getMetaTagValuesAndCombine('dc.subject');
    this.addMetaTag('citation_keywords', value);
  }

  /**
   * Add <meta name="citation_abstract_html_url" ... >  to the <head>
   */
  protected setCitationAbstractUrlTag(): void {
    if (this.currentObject.value instanceof Item) {
      let url = this.getMetaTagValue('dc.identifier.uri');
      if (hasNoValue(url)) {
        url = new URLCombiner(this.hardRedirectService.getBaseUrl(), this.router.url).toString();
      }
      this.addMetaTag('citation_abstract_html_url', url);
    }
  }

  /**
   * Add <meta name="citation_doi" ... >  to the <head>
   */
  protected setCitationDoiTag(): void {
    if (this.currentObject.value instanceof Item) {
      const doi = this.getMetaTagValue('dc.identifier.doi');
      if (hasValue(doi)) {
        this.addMetaTag('citation_doi', doi);
      }
    }
  }

  /**
   * Add <meta name="citation_pdf_url" ... >  to the <head>
   */
  protected setCitationPdfUrlTag(): void {
    if (this.currentObject.value instanceof Item) {
      const item = this.currentObject.value as Item;

      // Retrieve the ORIGINAL bundle for the item
      this.bundleDataService.findByItemAndName(
        item,
        'ORIGINAL',
        true,
        true,
        new FindListOptions(),
        followLink('primaryBitstream'),
        followLink('bitstreams', {
          findListOptions: {
            // limit the number of bitstreams used to find the citation pdf url to the number
            // shown by default on an item page
            elementsPerPage: this.appConfig.item.bitstream.pageSize,
          },
        }, followLink('format')),
      ).pipe(
        getFirstSucceededRemoteDataPayload(),
        switchMap((bundle: Bundle) =>
          // First try the primary bitstream
          bundle.primaryBitstream.pipe(
            getFirstCompletedRemoteData(),
            map((rd: RemoteData<Bitstream>) => {
              if (hasValue(rd.payload)) {
                return rd.payload;
              } else {
                return null;
              }
            }),
            getDownloadableBitstream(this.authorizationService),
            // return the bundle as well so we can use it again if there's no primary bitstream
            map((bitstream: Bitstream) => [bundle, bitstream]),
          ),
        ),
        switchMap(([bundle, primaryBitstream]: [Bundle, Bitstream]) => {
          if (hasValue(primaryBitstream)) {
            // If there was a downloadable primary bitstream, emit its link
            return [getBitstreamDownloadRoute(primaryBitstream)];
          } else {
            // Otherwise consider the regular bitstreams in the bundle
            return bundle.bitstreams.pipe(
              getFirstCompletedRemoteData(),
              switchMap((bitstreamRd: RemoteData<PaginatedList<Bitstream>>) => {
                if (hasValue(bitstreamRd.payload) && bitstreamRd.payload.totalElements === 1) {
                  // If there's only one bitstream in the bundle, emit its link if its downloadable
                  return this.getBitLinkIfDownloadable(bitstreamRd.payload.page[0], bitstreamRd);
                } else {
                  // Otherwise check all bitstreams to see if one matches the format whitelist
                  return this.getFirstAllowedFormatBitstreamLink(bitstreamRd);
                }
              }),
            );
          }
        }),
        take(1),
      ).subscribe((link: string) => {
        // Use the found link to set the <meta> tag
        this.addMetaTag(
          'citation_pdf_url',
          new URLCombiner(this.hardRedirectService.getBaseUrl(), link).toString(),
        );
      });
    }
  }

  getBitLinkIfDownloadable(bitstream: Bitstream, bitstreamRd: RemoteData<PaginatedList<Bitstream>>): Observable<string> {
    return of(bitstream).pipe(
      getDownloadableBitstream(this.authorizationService),
      switchMap((bit: Bitstream) => {
        if (hasValue(bit)) {
          return [getBitstreamDownloadRoute(bit)];
        } else {
          // Otherwise check all bitstreams to see if one matches the format whitelist
          return this.getFirstAllowedFormatBitstreamLink(bitstreamRd);
        }
      }),
    );
  }

  /**
   * For Items with more than one Bitstream (and no primary Bitstream), link to the first Bitstream
   * with a MIME type.
   *
   * Note this will only check the current page (page size determined item.bitstream.pageSize in the
   * config) of bitstreams for performance reasons.
   * See https://github.com/DSpace/DSpace/issues/8648 for more info
   *
   * included in {@linkcode CITATION_PDF_URL_MIMETYPES}
   * @param bitstreamRd
   * @private
   */
  protected getFirstAllowedFormatBitstreamLink(bitstreamRd: RemoteData<PaginatedList<Bitstream>>): Observable<string> {
    if (hasValue(bitstreamRd.payload) && isNotEmpty(bitstreamRd.payload.page)) {
      // Retrieve the formats of all bitstreams in the page sequentially
      return observableConcat(
        ...bitstreamRd.payload.page.map((bitstream: Bitstream) => bitstream.format.pipe(
          getFirstSucceededRemoteDataPayload(),
          // Keep the original bitstream, because it, not the format, is what we'll need
          // for the link at the end
          map((format: BitstreamFormat) => [bitstream, format]),
        )),
      ).pipe(
        // Verify that the bitstream is downloadable
        mergeMap(([bitstream, format]: [Bitstream, BitstreamFormat]) => of(bitstream).pipe(
          getDownloadableBitstream(this.authorizationService),
          map((bit: Bitstream) => [bit, format]),
        )),
        // Filter out only pairs with whitelisted formats and non-null bitstreams, null from download check
        filter(([bitstream, format]: [Bitstream, BitstreamFormat]) =>
          hasValue(format) && hasValue(bitstream) && this.CITATION_PDF_URL_MIMETYPES.includes(format.mimetype)),
        // We only need 1
        take(1),
        // Emit the link of the match
        // tap((v) => console.log('result', v)),
        map(([bitstream, format]: [Bitstream, BitstreamFormat]) => getBitstreamDownloadRoute(bitstream)),
      );
    } else {
      return EMPTY;
    }
  }

  /**
   * Add <meta name="Generator" ... >  to the <head> containing the repository brand
   */
  protected setGenerator(): void {
    this.rootService.findRoot().pipe(getFirstSucceededRemoteDataPayload()).subscribe(() => {
      this.meta.addTag({ name: 'Generator', content: 'DARE African Knowledge Repository' });
    });
  }

  protected hasType(value: string): boolean {
    return this.currentObject.value.hasMetadata('dc.type', { value: value, ignoreCase: true });
  }

  /**
   * Returns true if this._item is a dissertation
   *
   * @returns {boolean}
   *      true if this._item has a dc.type equal to 'Thesis'
   */
  protected isDissertation(): boolean {
    return this.hasType('thesis');
  }

  /**
   * Returns true if this._item is a technical report
   *
   * @returns {boolean}
   *      true if this._item has a dc.type equal to 'Technical Report'
   */
  protected isTechReport(): boolean {
    return this.hasType('technical report');
  }

  protected getMetaTagValue(key: string): string {
    return this.currentObject.value.firstMetadataValue(key);
  }

  protected getFirstMetaTagValue(keys: string[]): string {
    return this.currentObject.value.firstMetadataValue(keys);
  }

  protected getMetaTagValuesAndCombine(key: string): string {
    return this.getMetaTagValues([key]).join('; ');
  }

  protected getMetaTagValues(keys: string[]): string[] {
    return this.currentObject.value.allMetadataValues(keys);
  }

  protected addMetaTag(name: string, content: string): void {
    if (content) {
      const tag = { name, content } as MetaDefinition;
      this.meta.addTag(tag);
      this.storeTag(name);
    }
  }

  protected addMetaTags(name: string, content: string[]): void {
    for (const value of content) {
      this.addMetaTag(name, value);
    }
  }

  protected storeTag(key: string): void {
    this.store.dispatch(new AddMetaTagAction(key));
  }

  protected clearMetaTags(): void {
    this.store.pipe(
      select(tagsInUseSelector),
      take(1),
    ).subscribe((tagsInUse: string[]) => {
      for (const name of tagsInUse) {
        this.meta.removeTag('name=\'' + name + '\'');
      }
      this.store.dispatch(new ClearMetaTagAction());
    });
  }


}
