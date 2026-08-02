# DARE Theme Implementation Guide

This guide explains how to integrate the DARE DSpace Angular theme with a DSpace 7+ instance.

## Overview

The DARE theme is a comprehensive DSpace Angular theme featuring:
- Purple gradient branding (#667eea to #764ba2)
- WCAG 2.1 AA accessibility compliance
- Responsive mobile-first design
- ORCID authentication integration
- Dark mode support
- Comprehensive component styling

## Prerequisites

- DSpace 7.0 or higher
- Angular 12 or higher
- Node.js 14+ and npm 6+
- Git (for version control)

## Installation Steps

### 1. Clone DSpace Angular Repository

```bash
# Clone the DSpace Angular repository
git clone https://github.com/DSpace/dspace-angular.git
cd dspace-angular

# Or if you already have it
cd /path/to/dspace-angular
```

### 2. Add DARE Theme

```bash
# Copy the DARE theme to the appropriate location
cp -r /path/to/DARE-DIGITAL-REPOSITORY-/themes/dare src/themes/dare

# Or create a git submodule for easy updates
git submodule add https://github.com/wgmasvix-hue/dare-digital-repository-.git themes-dare
```

### 3. Update Angular Theme Configuration

Edit `angular.json` to register the DARE theme:

```json
{
  "projects": {
    "dspace-angular": {
      "architect": {
        "build": {
          "configurations": {
            "dare": {
              "theme": "src/themes/dare"
            }
          }
        }
      }
    }
  }
}
```

### 4. Update DSpace Configuration

Edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  
  // Theme configuration
  theme: {
    name: 'dare',
    path: 'src/themes/dare'
  },
  
  // REST API configuration
  rest: {
    baseUrl: 'http://localhost:8080/server/api',
    timeout: 15000
  },
  
  // ORCID configuration
  orcid: {
    enabled: true,
    clientId: 'YOUR_ORCID_CLIENT_ID',
    redirectUrl: 'http://localhost:4200/orcid-callback'
  }
};
```

### 5. Build with DARE Theme

```bash
# Build for development with DARE theme
ng build --configuration development --theme dare

# Or build for production
ng build --configuration production --theme dare

# Serve locally with DARE theme
ng serve --theme dare
```

## Theme Structure

```
themes/dare/
├── README.md                          # Theme documentation
├── styles/
│   ├── _dare-index.scss              # Main import file
│   ├── _dare-tokens.scss             # Design tokens (colors, fonts, spacing)
│   ├── _dare-variables.scss          # SCSS variables for Bootstrap
│   ├── _dare-bootstrap-overrides.scss # Bootstrap component customizations
│   ├── _dare-hero-patch.scss         # Hero and banner styling
│   ├── _dare-library.scss            # Discovery/search styling
│   ├── _dare-orcid.scss              # ORCID integration styling
│   └── _dare-accessibility.scss      # Accessibility features (WCAG 2.1 AA)
├── images/                            # Theme images and assets
└── fonts/                             # Custom fonts (optional)
```

## Customization

### Modify Colors

Edit `themes/dare/styles/_dare-tokens.scss`:

```scss
// Change primary color
$dare-primary: #667eea;      // Your color here
$dare-secondary: #764ba2;    // Your color here

// These are used throughout the theme
```

### Change Fonts

In `_dare-tokens.scss`:

```scss
$dare-font-primary: 'Your Font Family', sans-serif;
$dare-font-monospace: 'Courier New', monospace;
```

### Add Custom Components

Create a new file in `themes/dare/styles/`:

```scss
// _dare-custom.scss
.my-component {
  color: $dare-primary;
  background: $dare-gradient-primary;
  
  &:hover {
    box-shadow: $dare-shadow-lg;
  }
}
```

Then import it in `_dare-index.scss`:

```scss
@import 'dare-custom';
```

### Override Theme Components

Create custom component templates:

```
themes/dare/
├── app/
│   ├── header/
│   │   └── header.component.html    # Custom header
│   ├── footer/
│   │   └── footer.component.html    # Custom footer
│   └── search/
│       └── search-results.component.html
└── styles/
```

## ORCID Integration

The theme includes ORCID authentication styling. Configure in your DSpace:

### 1. Register ORCID Application

Visit https://orcid.org/developers and create an application:
- Name: DARE Digital Repository
- Redirect URIs: `https://dspace.dare.co.zw/orcid-callback`

### 2. Configure DSpace REST API

In DSpace configuration:

```properties
# dspace.cfg
orcid.enabled = true
orcid.clientId = YOUR_ORCID_CLIENT_ID
orcid.clientSecret = YOUR_ORCID_CLIENT_SECRET
orcid.redirectUrl = https://dspace.dare.co.zw/orcid-callback
```

### 3. Enable ORCID Login in Theme

The DARE theme automatically includes ORCID styling. The login button will be visible when ORCID is configured.

## Accessibility Features

The DARE theme includes comprehensive accessibility features:

- ✓ WCAG 2.1 AA compliant
- ✓ Enhanced keyboard navigation
- ✓ High contrast mode support
- ✓ Screen reader compatible
- ✓ Reduced motion preferences
- ✓ Dark mode support
- ✓ Proper heading structure
- ✓ Accessible form labels
- ✓ Focus indicators on interactive elements
- ✓ Sufficient touch target sizes (48x48px minimum)

### Testing Accessibility

```bash
# Run accessibility tests
npm run test:a11y

# Audit with Lighthouse
npm run audit
```

## Dark Mode Support

The theme automatically adapts to system dark mode preferences:

```scss
@media (prefers-color-scheme: dark) {
  // Dark mode styles automatically applied
}
```

Users can also manually toggle dark mode in the footer.

## Performance Optimization

The DARE theme uses:
- Efficient SCSS nesting
- Shared design tokens (no color duplication)
- Minimal external dependencies
- Optimized CSS output
- No unnecessary vendor prefixes

Build size: ~150KB gzipped

## Responsive Design Breakpoints

```scss
$dare-breakpoint-xs: 0;       // Extra small
$dare-breakpoint-sm: 576px;   // Small
$dare-breakpoint-md: 768px;   // Medium
$dare-breakpoint-lg: 992px;   // Large
$dare-breakpoint-xl: 1200px;  // Extra large
```

## Deployment

### Docker Deployment

Update your Dockerfile:

```dockerfile
# Build stage
FROM node:16 as builder
WORKDIR /app
COPY . .
RUN npm install
RUN ng build --configuration production --theme dare

# Runtime stage
FROM nginx:alpine
COPY --from=builder /app/dist/dspace-angular /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment

Update your deployment YAML:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dspace-angular
spec:
  template:
    spec:
      containers:
      - name: dspace-angular
        image: dspace-angular:dare-1.0
        env:
        - name: THEME
          value: dare
        - name: DSPACE_REST_URL
          value: https://dspace.dare.co.zw/server/api
```

## Testing

### Run Theme Tests

```bash
# Run all tests
npm test

# Run theme-specific tests
npm test -- --include='**/themes/dare/**'

# Run e2e tests
npm run e2e
```

### Visual Regression Testing

```bash
# Run visual regression tests
npm run test:visual

# Update baselines if changes are intentional
npm run test:visual -- --updateBaseline
```

## Browser Compatibility

- ✓ Chrome 90+
- ✓ Firefox 88+
- ✓ Safari 14+
- ✓ Edge 90+
- ✓ Mobile browsers (iOS Safari 12+, Chrome Android)

## Troubleshooting

### Theme Not Loading

```bash
# Clear cache and rebuild
rm -rf dist node_modules
npm install
ng build --configuration production --theme dare
```

### Styles Not Applied

```bash
# Check if SCSS import is correct
grep -r "_dare-index" src/

# Verify theme path in environment
cat src/environments/environment.ts | grep theme
```

### ORCID Button Not Showing

1. Check DSpace configuration: `dspace.cfg` has `orcid.enabled = true`
2. Verify ORCID client ID is set
3. Check browser console for errors
4. Ensure DSpace REST API is accessible

## Support & Documentation

- **Theme Issues**: https://github.com/wgmasvix-hue/dare-digital-repository-/issues
- **DSpace Documentation**: https://wiki.lyrasis.org/display/DSPACE
- **Angular Documentation**: https://angular.io/docs
- **ORCID API**: https://info.orcid.org/documentation/

## License

This theme is provided as part of the DARE Digital Repository project.

## Contributing

To contribute improvements to the DARE theme:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Commit: `git commit -am 'Add your feature'`
5. Push: `git push origin feature/your-feature`
6. Open a Pull Request

## Version History

### v1.0.0 (August 2, 2026)
- Initial DARE theme release
- Complete SCSS component library
- WCAG 2.1 AA accessibility
- ORCID integration
- Dark mode support
- 9 SCSS modules
- Bootstrap overrides
- Design token system

---

For the latest updates, visit: https://github.com/wgmasvix-hue/dare-digital-repository-
