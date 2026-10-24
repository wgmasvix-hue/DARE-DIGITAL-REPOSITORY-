import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { fadeIn } from 'src/app/shared/animations/fade';
import { ErrorComponent } from 'src/app/shared/error/error.component';
import { ObjectCollectionComponent } from 'src/app/shared/object-collection/object-collection.component';
import { SearchExportCsvComponent } from 'src/app/shared/search/search-export-csv/search-export-csv.component';
import { SearchResultsSkeletonComponent } from 'src/app/shared/search/search-results/search-results-skeleton/search-results-skeleton.component';

import { SearchResultsComponent as BaseComponent } from '../../../../../../app/shared/search/search-results/search-results.component';

/**
 * DARE override of the search results component.
 *
 * Extends the stock component (all behaviour, inputs, outputs and CSV export
 * are inherited unchanged) and improves the presentation of the results header
 * and the "no results" state so it is clearer and accessible to screen readers.
 */
@Component({
  selector: 'ds-themed-search-results',
  templateUrl: './search-results.component.html',
  styleUrls: ['./search-results.component.scss'],
  animations: [
    fadeIn,
  ],
  imports: [
    AsyncPipe,
    ErrorComponent,
    NgxSkeletonLoaderModule,
    ObjectCollectionComponent,
    RouterLink,
    SearchExportCsvComponent,
    SearchResultsSkeletonComponent,
    TranslateModule,
  ],
})
export class SearchResultsComponent extends BaseComponent {
}
