# DARE Theme Files Reference

Quick reference guide to all theme files and their purposes.

## Theme Directory Structure

```
themes/dare/
├── README.md
└── styles/
    ├── _dare-index.scss
    ├── _dare-tokens.scss
    ├── _dare-variables.scss
    ├── _dare-bootstrap-overrides.scss
    ├── _dare-hero-patch.scss
    ├── _dare-library.scss
    ├── _dare-orcid.scss
    └── _dare-accessibility.scss
```

## File Purposes

### `themes/dare/README.md` (70 lines)
**Purpose**: Theme overview and documentation  
**Contains**:
- Theme features list
- Theme structure explanation
- Installation instructions
- Customization guide
- Browser support information
- Version history

### `themes/dare/styles/_dare-index.scss` (380 lines)
**Purpose**: Main theme entry point  
**Imports**: All other SCSS files in correct order  
**Contains**:
- Global theme styles
- HTML and body styling
- Typography styles (headings, paragraphs, links)
- Button styles
- Form styles
- Card styles
- Navigation/header styles
- Footer styles
- Table styles
- Badge styles
- Loading spinner animation
- Utility classes

**Key Features**:
- Applies all design tokens
- Sets up base styling for all elements
- Defines default animations and transitions

### `themes/dare/styles/_dare-tokens.scss` (120 lines)
**Purpose**: Design system tokens (single source of truth)  
**Contains**:
- **Colors**: 20+ color variables with shades
  - Primary (purple): #667eea, light, dark
  - Secondary (dark purple): #764ba2
  - Success (green): #16a085
  - Gray scale: 9 levels
  - Text/accent colors
- **Typography**: 
  - Font families (primary, monospace)
  - Font sizes (8 levels)
  - Line heights (3 options)
  - Font weights (4 levels)
- **Spacing**: 7 spacing levels (xs → 3xl)
- **Borders**: Radius values and width
- **Shadows**: 4 shadow levels
- **Transitions**: 3 transition speeds
- **Breakpoints**: 6 responsive breakpoints
- **Z-index**: Standard z-index scale
- **Gradients**: Primary and secondary gradients

**Usage**: All other files import and use these tokens

### `themes/dare/styles/_dare-variables.scss` (60 lines)
**Purpose**: SCSS variables for Bootstrap compatibility  
**Contains**:
- Bootstrap color overrides ($primary, $secondary, etc.)
- Bootstrap typography variables
- Bootstrap spacing configuration
- Bootstrap border and shadow overrides
- Component-specific Bootstrap variables
- Navbar, card, modal, input sizing

**Purpose**: Ensures Bootstrap components use DARE theme colors/fonts

### `themes/dare/styles/_dare-bootstrap-overrides.scss` (450 lines)
**Purpose**: Bootstrap component customizations  
**Contains**:
- **Buttons**: Primary, outline, large, small variants
- **Forms**: Input, select, checkbox, radio styling
- **Navbar**: Navigation and brand styling
- **Cards**: Card layout, header, body, footer
- **Badges**: Badge colors and sizes
- **Alerts**: Info, success, warning, danger variants
- **Pagination**: Page link styling
- **Modals**: Modal layout and header/footer styling
- **Tooltips/Popovers**: Hover text styling
- **Dropdowns**: Dropdown menu styling
- **List Groups**: List styling
- **Tables**: Table head, body, striped styling
- **Breadcrumbs**: Navigation breadcrumb styling

**Key Features**:
- All transitions and hover states
- Gradient backgrounds where appropriate
- Shadow effects
- Focus states for accessibility

### `themes/dare/styles/_dare-hero-patch.scss` (350 lines)
**Purpose**: Large visual sections (hero, banners, CTAs)  
**Contains**:
- **Hero Sections**: Full-width hero banners with gradients
- **Banners**: Primary, success, secondary, light variants
- **Feature Highlights**: Card-based feature showcase
- **Section Headers**: Centered section titles with underline
- **Jumbotron**: Large prominent sections
- **CTA Sections**: Call-to-action with buttons
- **Dividers**: Visual section separators
- **Media Sections**: Text + image grid layouts
- **Testimonials**: Quote/testimonial styling
- **Stats Sections**: Number/metric displays

**Key Features**:
- Responsive grid layouts
- Pattern overlays on gradients
- Hover animations
- Icon styling
- Text shadows for readability

### `themes/dare/styles/_dare-library.scss` (420 lines)
**Purpose**: DSpace discovery, search, and collection browsing  
**Contains**:
- **Search Interface**: Search bar and input styling
- **Search Results**: Result item cards with metadata
- **Result Pagination**: Pagination controls
- **Faceted Search**: Filter sections and checkboxes
- **Collections Grid**: Collection cards with stats
- **Item Detail Views**: Metadata display
- **Alphabetical Browsing**: Letter navigation and lists
- **Empty States**: Helpful messaging when no results

**Key Features**:
- Hover effects on interactive elements
- Compact metadata display
- Tag/badge styling
- Statistics cards
- Responsive grid layouts

### `themes/dare/styles/_dare-orcid.scss` (280 lines)
**Purpose**: ORCID authentication and profile integration  
**Contains**:
- **ORCID Sections**: Information boxes with ORCID styling
- **Login Buttons**: Green gradient ORCID buttons
- **Benefits Grid**: Benefits of ORCID connection
- **Profile Cards**: User profile display
- **Auth Prompts**: Call-to-action for ORCID login
- **Connection Status**: Connected/disconnected indicators
- **ORCID Widgets**: Embedded ORCID elements
- **Identity Linking**: Account linking interface
- **Trust Badges**: Verification badges

**Key Features**:
- ORCID green color (#a6ce39) usage
- Profile avatar styling
- Statistics display
- Action buttons
- Status indicators

### `themes/dare/styles/_dare-accessibility.scss` (380 lines)
**Purpose**: WCAG 2.1 AA compliance and accessible styling  
**Contains**:
- **Focus Indicators**: Visible keyboard navigation (2px outlines)
- **Focus-Visible**: Modern browser focus support
- **Skip Links**: Skip to content functionality
- **Link Enhancement**: Underlines + color for better visibility
- **Form Accessibility**: Label styling, error messages, required indicators
- **Color Contrast**: Enhanced contrast ratios (4.5:1+)
- **Motion Preferences**: Respects `prefers-reduced-motion`
- **Dark Mode**: `prefers-color-scheme` support
- **High Contrast**: Support for high-contrast mode users
- **Print Styles**: Printer-friendly styling
- **Screen Reader**: SR-only content and ARIA support
- **Semantic HTML**: Heading spacing, structure
- **Touch Targets**: 48x48px minimum size
- **Reduced Motion**: Disables animations for vestibular disorders

**Testing**: WCAG 2.1 Level AA compliant (testable with Lighthouse)

## Import Order

```scss
// Order matters for cascade:
@import 'dare-tokens';              // 1. Design tokens (no dependencies)
@import 'dare-variables';           // 2. Bootstrap variables
@import 'dare-bootstrap-overrides'; // 3. Bootstrap overrides
@import 'dare-hero-patch';          // 4. Hero/banner components
@import 'dare-library';             // 5. Discovery/search components
@import 'dare-orcid';               // 6. ORCID integration
@import 'dare-accessibility';       // 7. Accessibility (overrides others)
```

## File Sizes (Lines of Code)

| File | Lines | Type |
|------|-------|------|
| _dare-index.scss | 380 | Entry point & global |
| _dare-bootstrap-overrides.scss | 450 | Component overrides |
| _dare-hero-patch.scss | 350 | Large sections |
| _dare-library.scss | 420 | Discovery UI |
| _dare-accessibility.scss | 380 | A11y features |
| _dare-orcid.scss | 280 | ORCID integration |
| _dare-tokens.scss | 120 | Design tokens |
| _dare-variables.scss | 60 | Bootstrap vars |
| README.md | 70 | Documentation |
| **Total** | **2,110** | |

## How to Use These Files

### To Customize Colors
Edit: `themes/dare/styles/_dare-tokens.scss`
```scss
$dare-primary: #667eea;  // Change this
```

### To Customize Typography
Edit: `themes/dare/styles/_dare-tokens.scss`
```scss
$dare-font-primary: 'Your Font', sans-serif;  // Change this
```

### To Add Custom Components
Create: `themes/dare/styles/_dare-custom.scss`  
Then add to `_dare-index.scss`: `@import 'dare-custom';`

### To Override Bootstrap
Edit: `themes/dare/styles/_dare-bootstrap-overrides.scss`

### To Add Accessibility Features
Edit: `themes/dare/styles/_dare-accessibility.scss`

## Building the Theme

```bash
# Development
ng build --configuration development --theme dare --watch

# Production
ng build --configuration production --theme dare

# Serve locally
ng serve --theme dare
```

## File Dependencies

```
_dare-index.scss
  ├─ _dare-tokens.scss (colors, fonts, spacing)
  ├─ _dare-variables.scss (Bootstrap overrides)
  ├─ _dare-bootstrap-overrides.scss (component styling)
  ├─ _dare-hero-patch.scss (hero/banner sections)
  ├─ _dare-library.scss (discovery/search)
  ├─ _dare-orcid.scss (ORCID integration)
  └─ _dare-accessibility.scss (WCAG compliance)
```

## Key SCSS Mixins & Functions

```scss
// All using tokens from _dare-tokens.scss

// Colors
$dare-primary: #667eea
$dare-gradient-primary: linear-gradient(135deg, $dare-primary 0%, $dare-secondary 100%)

// Spacing
$dare-spacing-md: 1rem
$dare-spacing-lg: 1.5rem

// Shadows
$dare-shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)

// Transitions
$dare-transition-base: all 0.3s ease-in-out

// Breakpoints (for media queries)
@media (max-width: $dare-breakpoint-md) { }
```

## Responsive Breakpoints

```scss
$dare-breakpoint-xs: 0         // Extra small
$dare-breakpoint-sm: 576px     // Small
$dare-breakpoint-md: 768px     // Medium
$dare-breakpoint-lg: 992px     // Large
$dare-breakpoint-xl: 1200px    // Extra large
$dare-breakpoint-xxl: 1400px   // Double XL
```

Usage:
```scss
.responsive-element {
  @media (max-width: $dare-breakpoint-md) {
    // Mobile styles
  }
}
```

---

For complete documentation, see:
- `themes/dare/README.md` - Theme overview
- `THEME_IMPLEMENTATION.md` - Integration guide
- `THEME_STATUS.md` - Development status
