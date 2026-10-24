import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

/**
 * Static "About DARE" information page.
 *
 * Presents the mission of the DARE African Knowledge Repository. Content is
 * intentionally conservative: it describes the repository's purpose and does
 * not assert research metrics or institutional claims that are not verifiable.
 */
@Component({
  selector: 'ds-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss'],
  imports: [
    RouterLink,
    TranslateModule,
  ],
})
export class AboutComponent {
}
