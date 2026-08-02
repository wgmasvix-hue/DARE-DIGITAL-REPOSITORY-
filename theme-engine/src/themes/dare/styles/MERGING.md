# Merging this layer into the theme on the server

Your theme at `/opt/dspace9/theme-engine/src/themes/dare/` already owns three
files with names DSpace reserves:

```
styles/_theme_css_variable_overrides.scss
styles/_theme_sass_variable_overrides.scss
styles/theme.scss
```

Nothing in this directory shares those names. Every file here is prefixed
`_dare-*` and is new, so copying this folder in cannot overwrite your work.

## Adopting it

**One line**, at the end of your existing `styles/theme.scss`:

```scss
@import 'dare-index';
```

Last, so the accessibility rules in `_dare-accessibility.scss` win where
specificity ties.

Then copy these files into `styles/`:

```
_dare-index.scss
_dare-tokens.scss
_dare-library.scss
_dare-orcid.scss
_dare-accessibility.scss
```

## The one file that must be merged by hand

`_dare-bootstrap-overrides.scss` **is not imported by `_dare-index.scss`** and
must not be. Bootstrap reads SCSS variables at compile time, before any import
in `theme.scss` is reached, so these have to live in the file DSpace already
loads for that purpose: `_theme_sass_variable_overrides.scss`.

Open both files side by side and copy across only what you want. The values
that matter most, in order:

```scss
// Contrast fixes — the reason this layer exists
$primary:              #516ce7;   // was #667eea at 3.66:1, now 4.52:1
$link-color:           #516ce7;
$link-hover-color:     #2144e1;   // 7.05:1
$link-decoration:      underline; // colour alone must not signal a link
$input-border-color:   #868e96;   // Bootstrap default is 2.07:1, fails 1.4.11

// Focus visibility
$focus-ring-width:     3px;
$focus-ring-color:     #2144e1;
$btn-focus-width:      3px;
$input-btn-focus-width: 3px;
```

Take the typography and spacing blocks too if you want the full scale, but they
are optional — the list above is the accessibility-critical set.

### Check what you already have first

`_theme_sass_variable_overrides.scss.bak` sits beside the live file on the
server, which suggests it has been edited by hand before. Diff them before
merging so you know which values are deliberate:

```bash
cd /opt/dspace9/theme-engine/src/themes/dare/styles
diff _theme_sass_variable_overrides.scss _theme_sass_variable_overrides.scss.bak
```

## Verifying after the build

The `ds-*` selectors in `_dare-library.scss` and `_dare-orcid.scss` are DSpace 9
component element names. **A selector that does not match fails silently** —
nothing errors, the rule simply never applies. After the first build, open the
running site and confirm in devtools that the elements you expect are present.

The `.dare-*` classes are ours and apply only where you add them to component
templates. Your theme already overrides:

```
app/header/header.component.html
app/header-nav-wrapper/header-navbar-wrapper.component.html
app/home-page/home-news/home-news.component.html
```

Those are the three templates where the `.dare-hero`, `.dare-search`,
`.dare-stat` and `.dare-collections` classes belong.

## Hero images

The theme carries four hero images:

```
assets/images/hero/dare-open.jpg
assets/images/hero/dare-knowledge.jpg
assets/images/hero/dare-universities.jpg
assets/images/hero/dare-theses.jpg
```

`.dare-hero` currently paints the brand gradient with a dot lattice over it. If
those images are meant to rotate behind the hero, the gradient should become an
overlay on top of the photograph rather than the background itself — otherwise
the images are never seen. Text contrast over a photograph also has to be
re-measured; a gradient scrim is the usual fix, and the ratios in
`_dare-tokens.scss` assume a white or gradient ground, not a photo.

Send the contents of `home-news.component.html` and I will wire the hero to
those images with a scrim that keeps the headline above 4.5:1.
