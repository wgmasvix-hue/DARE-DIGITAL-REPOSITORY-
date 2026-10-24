import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import {
  Params,
  RouterLink,
} from '@angular/router';
import { CollectionDataService } from '@dspace/core/data/collection-data.service';
import { PaginatedList } from '@dspace/core/data/paginated-list.model';
import { RemoteData } from '@dspace/core/data/remote-data';
import { Collection } from '@dspace/core/shared/collection.model';
import { followLink } from '@dspace/core/shared/follow-link-config.model';
import { getDSORoute } from '@dspace/core/router/utils/dso-route.utils';
import {
  getFirstSucceededRemoteData,
  getRemoteDataPayload,
} from '@dspace/core/shared/operators';
import { FacetValues } from '@dspace/core/shared/search/models/facet-values.model';
import { SearchFilterConfig } from '@dspace/core/shared/search/models/search-filter-config.model';
import { TranslateModule } from '@ngx-translate/core';
import { Observable } from 'rxjs';
import {
  filter,
  map,
  switchMap,
} from 'rxjs/operators';
import { SearchConfigurationService } from 'src/app/shared/search/search-configuration.service';
import { SearchService } from 'src/app/shared/search/search.service';

/**
 * DARE home page discovery band.
 *
 * Renders two live, REST-driven discovery aids for the repository:
 *  - "Explore by subject": the most-used subject facet values (with real counts),
 *    each linking into a filtered search.
 *  - "Featured collections": a sample of real collections.
 *
 * All values are read from the existing DSpace REST API. Nothing here is
 * fabricated or hard-coded: if the repository has no data, the section renders
 * an accessible empty state instead.
 */
@Component({
  selector: 'ds-dare-home-discovery',
  templateUrl: './dare-home-discovery.component.html',
  styleUrls: ['./dare-home-discovery.component.scss'],
  imports: [
    AsyncPipe,
    RouterLink,
    TranslateModule,
  ],
})
export class DareHomeDiscoveryComponent {

  /**
   * The most-used subject facet values, with their real result counts
   */
  subjects$: Observable<RemoteData<FacetValues>>;

  /**
   * A sample of collections in the repository
   */
  collections$: Observable<RemoteData<PaginatedList<Collection>>>;

  constructor(
    private searchConfigurationService: SearchConfigurationService,
    private searchService: SearchService,
    private collectionDataService: CollectionDataService,
  ) {
    this.subjects$ = this.searchConfigurationService.getConfig().pipe(
      getFirstSucceededRemoteData(),
      getRemoteDataPayload(),
      map((filters: SearchFilterConfig[]) => filters.find((config: SearchFilterConfig) => config.name === 'subject')),
      filter((subjectFilter: SearchFilterConfig) => subjectFilter !== undefined),
      switchMap((subjectFilter: SearchFilterConfig) => this.searchService.getFacetValuesFor(
        Object.assign(new SearchFilterConfig(), subjectFilter, { pageSize: 18 }),
        1,
      )),
    );

    this.collections$ = this.collectionDataService.findAll(
      { elementsPerPage: 6, currentPage: 1 },
      false,
      true,
      followLink('logo'),
    );
  }

  /**
   * Build the query parameters that apply a subject filter on the search page
   */
  subjectQueryParams(value: string): Params {
    return { 'f.subject': [`${value},equals`] };
  }

  /**
   * Resolve the client route for a collection
   */
  collectionRoute(collection: Collection): string {
    return getDSORoute(collection);
  }
}
