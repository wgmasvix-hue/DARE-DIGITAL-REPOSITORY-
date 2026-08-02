# DARE DSpace Angular Theme

A custom DSpace Angular theme for the DARE Digital Repository with modern styling and enhanced user experience.

## Theme Features

- **Purple Gradient Branding**: Consistent with DARE corporate identity
- **Enhanced Typography**: Improved readability and visual hierarchy
- **Responsive Design**: Mobile-first approach for all screen sizes
- **Accessibility**: WCAG 2.1 AA compliant styling
- **Component Customization**: Tailored DSpace components
- **ORCID Integration**: Streamlined ORCID login experience
- **ChengetAi Labs Integration**: Partnership branding elements

## Theme Structure

```
dare/
├── README.md                          # This file
├── styles/
│   ├── _dare-index.scss              # Main entry point
│   ├── _dare-tokens.scss             # Design tokens (colors, fonts, spacing)
│   ├── _dare-accessibility.scss      # Accessibility overrides
│   ├── _dare-bootstrap-overrides.scss # Bootstrap customizations
│   ├── _dare-hero-patch.scss         # Hero section styling
│   ├── _dare-library.scss            # Library/discovery styling
│   ├── _dare-orcid.scss              # ORCID integration styling
│   └── _dare-variables.scss          # SCSS variables
├── images/
│   ├── dare-logo.svg
│   ├── dare-logo-dark.svg
│   └── orcid-logo.svg
└── fonts/
    └── (Custom fonts if needed)
```

## Installation

1. Place this directory in your DSpace Angular theme directory:
   ```
   dspace-angular/src/themes/dare/
   ```

2. Update your DSpace configuration to use the DARE theme

3. Import DARE theme styles in your main theme file

## Customization

### Color Palette

- **Primary Purple**: `#667eea` - Main brand color
- **Secondary Purple**: `#764ba2` - Accent color
- **Green (Success)**: `#16a085` - Call-to-action elements
- **Dark Gray**: `#333` - Text color
- **Light Gray**: `#f8f9fa` - Background

### Font Family

- Primary: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- Monospace: Courier New (for code/metadata display)

## Development

### Using SCSS Variables

```scss
// Define custom variables
$dare-primary: #667eea;
$dare-secondary: #764ba2;
$dare-success: #16a085;

// Use in components
.dare-header {
  background: linear-gradient(135deg, $dare-primary 0%, $dare-secondary 100%);
}
```

## Building the Theme

To build and deploy the theme with DSpace Angular:

```bash
# Build DSpace Angular with DARE theme
ng build --configuration production

# Or with custom theme
ng build --configuration production --theme=dare
```

## Testing the Theme

1. Test responsive design on all screen sizes
2. Verify color contrast (WCAG AA minimum)
3. Test with screen readers
4. Validate with CSS linters
5. Check performance metrics

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS 12+, Android 8+

## Documentation

For DSpace Angular theming documentation, see:
- [DSpace Angular Documentation](https://wiki.lyrasis.org/display/DSPACE/DSpace+7+Angular+Application)
- [Angular Theming Guide](https://angular.io/guide/theming)

## Version History

- **1.0.0** (2026-08-02) - Initial DARE theme creation
