# rosersg Embedded in DSpace - Quick Start

Get rosersg seamlessly integrated into your DSpace UI in 30 minutes.

## 🎯 What You Get

```
DSpace Repository (repo.dare.co.zw)
├── Search Page
│   └── 🤖 AI Smart Search Suggestions
├── Item Detail Page
│   ├── 💬 Floating AI Chat
│   ├── 📝 AI Metadata Suggestions
│   └── ⭐ AI Recommendations
└── Every Page
    └── 🤖 Chat Button (floating)
```

## 📝 Step-by-Step Implementation

### Step 1: Prepare rosersg Backend

```bash
# SSH to your server and ensure rosersg is running
ssh root@your-server
cd /opt/rosersg

# Start services
sudo docker-compose up -d

# Verify API is accessible
curl -s http://localhost:5000/health
```

### Step 2: Copy Angular Components

Assuming your DSpace Angular is at `/opt/dspace-angular`:

```bash
# Create component directories
mkdir -p /opt/dspace-angular/src/app/shared/components/{rosersg-chat,rosersg-search-enhance,rosersg-metadata-suggestions,rosersg-recommendations}

# Copy the component files from EMBED_IN_DSPACE.md
# Create each .ts, .html, and .scss file in their respective folders
```

**Quick file structure:**
```
src/app/shared/components/
├── rosersg-chat/
│   ├── rosersg-chat.component.ts
│   ├── rosersg-chat.component.html
│   └── rosersg-chat.component.scss
├── rosersg-search-enhance/
│   ├── rosersg-search-enhance.component.ts
│   ├── rosersg-search-enhance.component.html
│   └── rosersg-search-enhance.component.scss
├── rosersg-metadata-suggestions/
│   ├── rosersg-metadata-suggestions.component.ts
│   ├── rosersg-metadata-suggestions.component.html
│   └── rosersg-metadata-suggestions.component.scss
└── rosersg-recommendations/
    ├── rosersg-recommendations.component.ts
    ├── rosersg-recommendations.component.html
    └── rosersg-recommendations.component.scss
```

### Step 3: Update SharedModule

**File:** `src/app/shared/shared.module.ts`

Add imports and declarations:

```typescript
import { RosersqChatComponent } from './components/rosersg-chat/rosersg-chat.component';
import { RosersqSearchEnhanceComponent } from './components/rosersg-search-enhance/rosersg-search-enhance.component';
import { RosersqMetadataSuggestionsComponent } from './components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component';
import { RosersqRecommendationsComponent } from './components/rosersg-recommendations/rosersg-recommendations.component';

@NgModule({
  declarations: [
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent
  ],
  imports: [CommonModule, HttpClientModule, FormsModule],
  exports: [
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent
  ]
})
export class SharedModule { }
```

### Step 4: Add Chat to Every Page

**File:** `src/app/app.component.html`

Add at the bottom of your app:

```html
<!-- Existing app content -->

<!-- rosersg Chat (appears on all pages) -->
<app-rosersg-chat 
  placeholder="Ask rosersg about this research..."
></app-rosersg-chat>
```

### Step 5: Add to Item Detail Page

**File:** `src/app/item-page/full/item-detail.component.html`

Add after existing item information:

```html
<!-- Existing item content -->

<!-- AI Metadata Suggestions -->
<app-rosersg-metadata-suggestions
  [itemTitle]="item?.name"
  [itemDescription]="getDescription()"
></app-rosersg-metadata-suggestions>

<!-- AI Recommendations -->
<app-rosersg-recommendations
  [itemId]="itemId"
  [searchQuery]="item?.name"
></app-rosersg-recommendations>
```

### Step 6: Add to Search Page

**File:** `src/app/search-page/search.component.html`

Add above search results:

```html
<!-- Smart Search with AI -->
<app-rosersg-search-enhance
  [(ngModel)]="query"
  (enhancedQuery)="performSearch($event)"
></app-rosersg-search-enhance>

<!-- Existing search results -->
```

### Step 7: Setup Nginx Routing

**File:** `/etc/nginx/sites-enabled/repo.dare.co.zw`

Add to your server block:

```nginx
server {
    listen 443 ssl http2;
    server_name repo.dare.co.zw;

    # ... existing SSL/DSpace config ...

    # Route rosersg API
    location /ai-api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

### Step 8: Configure API Key in DSpace

Add to your DSpace theme HTML (e.g., in header.html or environment file):

```typescript
// src/environments/environment.prod.ts

export const environment = {
  production: true,
  // ... other config ...
  rosersg: {
    apiUrl: '/ai-api',
    apiKey: 'your-rosersg-api-key-here'  // From .env on server
  }
};
```

Or inject at runtime:

```html
<!-- In theme header template -->
<script>
  window.ROSERSG_API_KEY = '{{ rosersg_api_key }}';
</script>
```

### Step 9: Build DSpace

```bash
cd /opt/dspace-angular

# Install dependencies
npm install

# Build for production
npm run build

# Or for development with live reload
npm start
```

### Step 10: Deploy

```bash
# If using DSpace's default setup:
cd /opt/dspace/
./restart-dspace.sh

# Or if Angular is served separately:
# Copy dist/ to your web server
sudo cp -r dist/* /var/www/dspace-ui/
```

## 🧪 Testing

### 1. Check rosersg API
```bash
# From server
curl http://localhost:5000/health

# Through Nginx
curl https://repo.dare.co.zw/ai-api/health
```

### 2. Open DSpace in browser
```
https://repo.dare.co.zw
```

### 3. Look for rosersg features:

✅ **Chat button** (bottom-right corner) 🤖
✅ **AI search** (on search page)
✅ **Metadata suggestions** (on item pages)
✅ **Recommendations** (on item pages)

## 🐛 Troubleshooting

### "API not found" errors

Check Nginx routing:
```bash
sudo nginx -t  # Test config
sudo systemctl restart nginx
```

### "Components not displaying"

Make sure SharedModule is imported:
```typescript
// In app.module.ts or your module
import { SharedModule } from './shared/shared.module';

@NgModule({
  imports: [SharedModule, ...]
})
```

### "API key not working"

Verify API key:
```bash
# On server
grep ROSERSG_API_KEY /opt/rosersg/.env

# Test with curl
API_KEY="your-key-here"
curl -H "X-API-Key: $API_KEY" https://repo.dare.co.zw/ai-api/api/status
```

### "Chat button not appearing"

1. Check browser console for errors
2. Verify components are in SharedModule
3. Check app.component.html has the component tag
4. Verify FormsModule is imported

## 📊 File Checklist

- [ ] All 4 rosersg components created (ts, html, scss)
- [ ] SharedModule updated with components
- [ ] app.component.html includes `<app-rosersg-chat>`
- [ ] item-detail.component.html has metadata & recommendations
- [ ] search.component.html has smart search
- [ ] environment.prod.ts has rosersg config
- [ ] Nginx configured with /ai-api/ route
- [ ] rosersg backend running (docker-compose)
- [ ] DSpace Angular built
- [ ] API key set in environment

## 🎯 Expected Result

When users visit repo.dare.co.zw:

```
┌─────────────────────────────────────┐
│    DSpace Repository                │
│                                     │
│  [Search with AI suggestions]       │
│                                     │
│  Search Results:                    │
│  - Item 1                           │
│  - Item 2                           │
│  - Item 3                           │
│                       [🤖 Chat]     │ ← Floating button
└─────────────────────────────────────┘

Click 🤖 → Chat opens asking "Ask rosersg about this research..."
```

**On Item Page:**

```
┌─────────────────────────────────────┐
│  Item Title                         │
│  Author: ...                        │
│  Date: ...                          │
│                                     │
│  🤖 AI Metadata Suggestions         │ ← Shows improvements
│  ┌────────────────────────────────┐ │
│  │ Try adding these keywords...   │ │
│  └────────────────────────────────┘ │
│                                     │
│  🤖 AI-Powered Recommendations     │ ← Shows related items
│  ┌────────────────────────────────┐ │
│  │ Related Research:              │ │
│  │ - Paper A (related to this)    │ │
│  │ - Paper B (similar topic)      │ │
│  └────────────────────────────────┘ │
│                       [🤖 Chat]     │ ← Floating
└─────────────────────────────────────┘
```

## 📚 Reference

- Full guide: `EMBED_IN_DSPACE.md`
- Deployment: `DEPLOY_DSPACE_LIVE.md`
- API docs: `ROSERSG.md`
- Component code: All code in `EMBED_IN_DSPACE.md`

## 🚀 You're Done!

rosersg is now seamlessly embedded in DSpace. Users get AI assistance:
- While searching
- While browsing items
- For metadata improvement
- For discovering related research

All without leaving the repo.dare.co.zw domain! 🎉

---

**Questions?** See `EMBED_IN_DSPACE.md` for complete component code and detailed explanations.
