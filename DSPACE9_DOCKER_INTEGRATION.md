# 🐳 DSpace 9 Docker Integration - rosersg

Since your DSpace 9 Angular runs in Docker, we'll create a custom image with rosersg integrated.

## 📋 What You Have

- **Container:** `dspace-angular` running `dare/dspace-angular:9.3-unified`
- **Working Dir:** `/app` (inside container)
- **Config:** `/opt/dspace9/config.yml` (mounted, read-only)
- **Status:** Running for 30+ hours ✅

## 🎯 Integration Strategy

We'll create a new Docker image that:
1. Extends the official `dare/dspace-angular:9.3-unified` image
2. Adds rosersg components
3. Modifies necessary files (SharedModule, templates, environment)
4. Rebuilds the Angular app
5. Ready to replace your current container

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Build Directory

On your server, create a build directory:

```bash
mkdir -p /opt/dspace9-rosersg-build
cd /opt/dspace9-rosersg-build
```

### Step 2: Clone rosersg Repository

```bash
cd /opt/dspace9-rosersg-build
git clone -b claude/rosersg-ollama-dspace-ai-b9tvxu \
  https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git rosersg-repo

# Copy the Dockerfile and components
cp rosersg-repo/Dockerfile.dspace9-rosersg ./
```

### Step 3: Prepare Component Files

Create the component directory structure:

```bash
mkdir -p components/{rosersg-chat,rosersg-search-enhance,rosersg-metadata-suggestions,rosersg-recommendations}
mkdir -p patches
```

### Step 4: Copy Component Files

The rosersg repo includes all component files. Copy them:

```bash
# Copy component code (from EMBED_IN_DSPACE.md or use this structure)
# This assumes you have the component files extracted

# Or manually copy from rosersg-repo/components/ if they exist
cp -r rosersg-repo/components/* components/
```

### Step 5: Create Modified Files (patches)

Create `patches/` directory with modified files:

#### patches/shared.module.ts

```typescript
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

// Import rosersg components
import { RosersqChatComponent } from './components/rosersg-chat/rosersg-chat.component';
import { RosersqSearchEnhanceComponent } from './components/rosersg-search-enhance/rosersg-search-enhance.component';
import { RosersqMetadataSuggestionsComponent } from './components/rosersg-metadata-suggestions/rosersg-metadata-suggestions.component';
import { RosersqRecommendationsComponent } from './components/rosersg-recommendations/rosersg-recommendations.component';

// ... import existing shared components ...

@NgModule({
  declarations: [
    // ... existing components ...
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent,
  ],
  imports: [
    CommonModule,
    HttpClientModule,
    FormsModule,
    // ... other imports ...
  ],
  exports: [
    // ... existing exports ...
    RosersqChatComponent,
    RosersqSearchEnhanceComponent,
    RosersqMetadataSuggestionsComponent,
    RosersqRecommendationsComponent,
  ]
})
export class SharedModule { }
```

#### patches/app.component.html

Add at the end of your existing app.component.html:

```html
<!-- rosersg Chat Widget - appears on all pages -->
<app-rosersg-chat 
  placeholder="Ask rosersg about this research..."
></app-rosersg-chat>
```

#### patches/item-detail.component.html

Add after item metadata section:

```html
<!-- rosersg AI Components -->
<div class="rosersg-section">
  <app-rosersg-metadata-suggestions
    [itemTitle]="item?.name"
    [itemDescription]="getItemDescription()"
  ></app-rosersg-metadata-suggestions>

  <app-rosersg-recommendations
    [itemId]="itemId"
    [searchQuery]="item?.name"
  ></app-rosersg-recommendations>
</div>
```

#### patches/search.component.html

Add before search results:

```html
<!-- rosersg Smart Search Enhancement -->
<div class="rosersg-search-wrapper">
  <app-rosersg-search-enhance
    [(ngModel)]="query"
    (enhancedQuery)="performSearch($event)"
  ></app-rosersg-search-enhance>
</div>
```

#### patches/environment.prod.ts

Add rosersg configuration:

```typescript
export const environment = {
  production: true,
  // ... existing config ...
  
  rosersg: {
    apiUrl: '/ai-api',  // Proxied through Caddy
    apiKey: '6411d796c1962ffe483147c0c7e211bc6f47cecbfc723f9c5957a73ee70b8bac'  // Your API key
  }
};
```

### Step 6: Build Docker Image

```bash
cd /opt/dspace9-rosersg-build

# Build the new image
docker build -f Dockerfile.dspace9-rosersg -t dare/dspace-angular:9.3-rosersg .

# This will take 10-20 minutes (rebuilds Angular app)
```

### Step 7: Test New Image

Before replacing, test it:

```bash
# Run the new image on a different port
docker run -d \
  --name dspace-angular-test \
  -p 4001:4000 \
  -v /opt/dspace9/config.yml:/app/config/config.yml:ro \
  dare/dspace-angular:9.3-rosersg

# Wait 30 seconds
sleep 30

# Test it
curl http://localhost:4001

# Check logs
docker logs dspace-angular-test

# If good, stop the test
docker stop dspace-angular-test
docker rm dspace-angular-test
```

### Step 8: Update Running Container

Once tested, update your production container:

```bash
# Stop current container
docker stop dspace-angular

# Backup current image (optional)
docker tag dare/dspace-angular:9.3-unified dare/dspace-angular:9.3-unified.backup

# Run new image with same config
docker run -d \
  --name dspace-angular \
  -p 4000:4000 \
  -v /opt/dspace9/config.yml:/app/config/config.yml:ro \
  dare/dspace-angular:9.3-rosersg

# Wait for startup
sleep 30

# Verify it's running
docker ps | grep dspace-angular
```

### Step 9: Verify through Caddy

Test through your domain:

```bash
# Health check
curl https://repo.dare.co.zw/

# Should see your DSpace UI with rosersg components

# Check chat button appears (bottom-right in browser)
# Check search page for AI enhancement
# Check item pages for metadata suggestions
```

## ✅ Verification Checklist

After deployment:

- [ ] Container is running: `docker ps | grep dspace-angular`
- [ ] Accessible at: https://repo.dare.co.zw
- [ ] Chat button visible (bottom-right)
- [ ] Chat responds to messages
- [ ] Search page shows AI suggestions
- [ ] Item pages show metadata suggestions
- [ ] Item pages show recommendations
- [ ] No errors in browser console (F12)

## 🐛 Troubleshooting

### Build fails

```bash
# Check build logs
docker build -f Dockerfile.dspace9-rosersg -t dare/dspace-angular:9.3-rosersg . 2>&1 | tail -50

# Clear and retry
docker system prune -a
docker build -f Dockerfile.dspace9-rosersg -t dare/dspace-angular:9.3-rosersg --no-cache .
```

### Container won't start

```bash
# Check logs
docker logs dspace-angular

# Check if port is in use
lsof -i :4000

# Restart
docker restart dspace-angular
```

### Components don't appear

```bash
# Check if they compiled
docker exec dspace-angular ls -la /app/dist/ | grep -i rosersg

# Check browser console for errors (F12)
# Errors will show if components didn't load
```

### API returns 401

```bash
# Verify API key is correct in environment.prod.ts
# Should be: 6411d796c1962ffe483147c0c7e211bc6f47cecbfc723f9c5957a73ee70b8bac

# Test API directly
curl -H "X-API-Key: 6411d796c1962ffe483147c0c7e211bc6f47cecbfc723f9c5957a73ee70b8bac" \
  https://repo.dare.co.zw/ai-api/health
```

## 📊 Time Estimates

- Prepare directories: 5 min
- Copy files: 5 min
- Build Docker image: 10-20 min
- Test: 5 min
- Deploy: 2 min
- Verify: 5 min
- **Total: 30-40 minutes**

## 🎉 Result

Your DSpace 9 will now have:
- ✅ Floating chat button (all pages)
- ✅ AI-powered search (search page)
- ✅ Metadata suggestions (item pages)
- ✅ Smart recommendations (item pages)

All seamlessly integrated into the official DSpace 9 image! 🚀

## 📝 Quick Commands Reference

```bash
# Build
docker build -f Dockerfile.dspace9-rosersg -t dare/dspace-angular:9.3-rosersg .

# Test
docker run -d --name test -p 4001:4000 -v /opt/dspace9/config.yml:/app/config/config.yml:ro dare/dspace-angular:9.3-rosersg
docker logs test
docker stop test && docker rm test

# Deploy
docker stop dspace-angular
docker run -d --name dspace-angular -p 4000:4000 -v /opt/dspace9/config.yml:/app/config/config.yml:ro dare/dspace-angular:9.3-rosersg

# Verify
curl https://repo.dare.co.zw/
```

---

**Next:** Run the build and deployment steps above! 🚀
