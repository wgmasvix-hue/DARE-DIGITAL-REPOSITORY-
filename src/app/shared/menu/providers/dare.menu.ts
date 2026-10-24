import { Injectable } from '@angular/core';
import {
  Observable,
  of,
} from 'rxjs';

import { MenuItemType } from '../menu-item-type.model';
import {
  AbstractMenuProvider,
  PartialMenuSection,
} from '../menu-provider.model';

/**
 * Menu provider adding the "Publications" item to the public navbar.
 * Resolves to the repository search scoped to research publications.
 */
@Injectable()
export class PublicationsMenuProvider extends AbstractMenuProvider {
  public getSections(): Observable<PartialMenuSection[]> {
    return of([
      {
        visible: true,
        model: {
          type: MenuItemType.LINK,
          text: 'menu.section.dare_publications',
          link: '/search',
          queryParams: { query: 'publication' },
        },
        icon: 'book',
      },
    ] as PartialMenuSection[]);
  }
}

/**
 * Menu provider adding the "Datasets" item to the public navbar.
 */
@Injectable()
export class DatasetsMenuProvider extends AbstractMenuProvider {
  public getSections(): Observable<PartialMenuSection[]> {
    return of([
      {
        visible: true,
        model: {
          type: MenuItemType.LINK,
          text: 'menu.section.dare_datasets',
          link: '/search',
          queryParams: { query: 'dataset' },
        },
        icon: 'database',
      },
    ] as PartialMenuSection[]);
  }
}

/**
 * Menu provider adding the "About DARE" item to the public navbar.
 */
@Injectable()
export class AboutMenuProvider extends AbstractMenuProvider {
  public getSections(): Observable<PartialMenuSection[]> {
    return of([
      {
        visible: true,
        model: {
          type: MenuItemType.LINK,
          text: 'menu.section.dare_about',
          link: '/info/about',
        },
        icon: 'circle-info',
      },
    ] as PartialMenuSection[]);
  }
}
