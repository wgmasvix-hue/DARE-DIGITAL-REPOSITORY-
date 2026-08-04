# DSpace 9 Integration Checklist for rosersg

Complete this checklist to integrate rosersg seamlessly into your DSpace 9 installation at **repo.dare.co.zw**.

## 🚀 Phase 1: Deploy rosersg Backend (on your server)

### Step 1.1: SSH to Your Server
```bash
# SSH to your DSpace server
ssh root@repo.dare.co.zw
# or your actual SSH endpoint
```

### Step 1.2: Clone Repository
```bash
# Create deployment directory
sudo mkdir -p /opt/rosersg
cd /opt/rosersg

# Clone the rosersg repository
sudo git clone -b claude/rosersg-ollama-dspace-ai-b9tvxu \
  https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git .
```

### Step 1.3: Verify Prerequisites
```bash
# Check Docker
docker --version

# Check Docker Compose (v2)
docker compose version

# Verify docker-compose can be invoked
docker compose config > /dev/null && echo "✓ Docker Compose works"
```

### Step 1.4: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Generate a STRONG API key (keep this safe!)
API_KEY=$(openssl rand -hex 32)
echo "Your API Key: $API_KEY"

# Update .env file
sudo sed -i "s|ROSERSG_API_KEY=.*|ROSERSG_API_KEY=$API_KEY|" .env

# Verify configuration
cat .env
```

### Step 1.5: Start Services
```bash
# Build Docker images
docker compose build --no-cache

# Start all services (Ollama, API, UI)
docker compose up -d

# Wait 2-3 minutes for services to fully initialize
sleep 30

# Check service status
docker compose ps
```

### Step 1.6: Verify Services Are Running
```bash
# Check if Ollama is responding
curl -s http://localhost:11434/api/tags | head -20

# Check if API is responding
curl -s http://localhost:5000/health

# Check if you can authenticate
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" http://localhost:5000/api/status
```

### Step 1.7: Pull Ollama Models
```bash
# Access the Ollama container
docker compose exec ollama ollama list

# Pull the default model (mistral)
docker compose exec ollama ollama pull mistral

# (Optional) Pull neural-chat for better conversations
docker compose exec ollama ollama pull neural-chat
```

**✅ Backend Phase Complete** - Services are running on:
- API: http://localhost:5000
- Frontend: http://localhost:3000
- Ollama: http://localhost:11434

---

## 📡 Phase 2: Configure Nginx Routing

This makes rosersg accessible through your main DSpace domain.

### Step 2.1: Add Nginx Configuration

Edit your Nginx config for `repo.dare.co.zw`:

```bash
# Backup existing config
sudo cp /etc/nginx/sites-enabled/default \
  /etc/nginx/sites-enabled/default.backup

# Edit Nginx config
sudo nano /etc/nginx/sites-enabled/default
```

### Step 2.2: Add rosersg Routes

Add these location blocks to your server block:

```nginx
# Route API requests to rosersg backend
location /ai-api/ {
    proxy_pass http://localhost:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_buffering off;
    proxy_request_buffering off;
}

# Route UI (if running standalone)
location /ai/ {
    proxy_pass http://localhost:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Step 2.3: Restart Nginx

```bash
# Test configuration
sudo nginx -t

# Restart if valid
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

**✅ Routing Complete** - Now accessible at:
- API: https://repo.dare.co.zw/ai-api/
- UI: https://repo.dare.co.zw/ai/

---

## 🔧 Phase 3: Integrate with DSpace Angular Frontend

This embeds rosersg components directly in your DSpace interface.

### Step 3.1: Locate DSpace Angular Directory

```bash
# Find your DSpace Angular installation
# Common locations:
ls -la /opt/dspace-angular
ls -la /opt/dspace/src/app
# or wherever you have it installed
```

### Step 3.2: Create Component Directories

```bash
# Create directories for rosersg components
mkdir -p /opt/dspace-angular/src/app/shared/components/{rosersg-chat,rosersg-search-enhance,rosersg-metadata-suggestions,rosersg-recommendations}
```

### Step 3.3: Copy Component Files

The complete component code is in **EMBED_IN_DSPACE.md**. Copy these files:

#### Chat Component
- `rosersg-chat.component.ts` → `src/app/shared/components/rosersg-chat/`
- `rosersg-chat.component.html` → `src/app/shared/components/rosersg-chat/`
- `rosersg-chat.component.scss` → `src/app/shared/components/rosersg-chat/`

#### Search Enhancement Component
- `rosersg-search-enhance.component.ts` → `src/app/shared/components/rosersg-search-enhance/`
- `rosersg-search-enhance.component.html` → `src/app/shared/components/rosersg-search-enhance/`
- `rosersg-search-enhance.component.scss` → `src/app/shared/components/rosersg-search-enhance/`

#### Metadata Suggestions Component
- `rosersg-metadata-suggestions.component.ts` → `src/app/shared/components/rosersg-metadata-suggestions/`
- `rosersg-metadata-suggestions.component.html` → `src/app/shared/components/rosersg-metadata-suggestions/`
- `rosersg-metadata-suggestions.component.scss` → `src/app/shared/components/rosersg-metadata-suggestions/`

#### Recommendations Component
- `rosersg-recommendations.component.ts` → `src/app/shared/components/rosersg-recommendations/`
- `rosersg-recommendations.component.html` → `src/app/shared/components/rosersg-recommendations/`
- `rosersg-recommendations.component.scss` → `src/app/shared/components/rosersg-recommendations/`

### Step 3.4: Update SharedModule

Edit `src/app/shared/shared.module.ts`:

```typescript
// Add imports
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

### Step 3.5: Add Chat to Every Page

Edit `src/app/app.component.html` - add at the bottom:

```html
<!-- rosersg Chat (appears on all pages) -->
<app-rosersg-chat 
  placeholder="Ask rosersg about this research..."
></app-rosersg-chat>
```

### Step 3.6: Add to Item Detail Page

Edit `src/app/item-page/full/item-detail.component.html` - add after item info:

```html
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

### Step 3.7: Add to Search Page

Edit `src/app/search-page/search.component.html` - add before results:

```html
<!-- Smart Search with AI -->
<app-rosersg-search-enhance
  [(ngModel)]="query"
  (enhancedQuery)="performSearch($event)"
></app-rosersg-search-enhance>

<!-- Existing search results -->
```

### Step 3.8: Configure Environment

Edit `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  // ... other config ...
  rosersg: {
    apiUrl: '/ai-api',
    apiKey: 'your-rosersg-api-key-here'  // From your .env file
  }
};
```

### Step 3.9: Build DSpace Angular

```bash
cd /opt/dspace-angular

# Install dependencies
npm install

# Build for production
npm run build

# Wait for build to complete (5-15 minutes)
```

### Step 3.10: Deploy DSpace

```bash
# Copy built files to web root
sudo cp -r dist/* /var/www/dspace-ui/
# OR if using DSpace's default:
sudo cp -r dist/* /opt/dspace/src/app/

# Restart DSpace (if applicable)
cd /opt/dspace/
./restart-dspace.sh
```

**✅ Integration Complete** - DSpace now has rosersg embedded!

---

## ✅ Phase 4: Verification

### Test 1: Check Backend API
```bash
curl -s https://repo.dare.co.zw/ai-api/health
# Should return: {"status": "healthy"}

# Test with API key
API_KEY=$(grep ROSERSG_API_KEY /opt/rosersg/.env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" https://repo.dare.co.zw/ai-api/api/status
```

### Test 2: Open DSpace in Browser
1. Go to **https://repo.dare.co.zw**
2. Look for **Chat button** (bottom-right) 🤖
3. Click to open chat and type a question

### Test 3: Check Search Page
1. Go to search page
2. Should see **AI Search Enhance** component
3. Type a query - should see AI suggestions

### Test 4: Check Item Page
1. Open any item
2. Should see **AI Metadata Suggestions** section
3. Should see **AI Recommendations** section

---

## 🐛 Troubleshooting

### Issue: "API not found" errors
```bash
# Check Nginx configuration
sudo nginx -t

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test API directly
curl -v http://localhost:5000/health
```

### Issue: "Components not displaying" in DSpace
```bash
# Check browser console for errors
# Look for: Failed to load rosersg components

# Verify components are in SharedModule
grep -r "RosersqChatComponent" /opt/dspace-angular/src/app/

# Check that component files exist
ls -la /opt/dspace-angular/src/app/shared/components/rosersg-chat/
```

### Issue: API key not working
```bash
# Verify API key is correct
cat /opt/rosersg/.env | grep ROSERSG_API_KEY

# Test with curl
API_KEY=$(grep ROSERSG_API_KEY /opt/rosersg/.env | cut -d= -f2)
curl -v -H "X-API-Key: $API_KEY" http://localhost:5000/api/status
```

### Issue: Ollama container unhealthy
```bash
# Check Ollama logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama

# Wait 2+ minutes, then check status
docker compose ps

# Verify Ollama is initialized
curl http://localhost:11434/api/tags
```

### Issue: DSpace build fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf /opt/dspace-angular/node_modules package-lock.json

# Reinstall
cd /opt/dspace-angular
npm install

# Retry build
npm run build
```

---

## 📊 File Checklist

Complete this checklist as you go:

- [ ] Backend services running (`docker compose ps`)
- [ ] API responding to health check
- [ ] Nginx routing configured
- [ ] Ollama models pulled (`docker compose exec ollama ollama list`)
- [ ] rosersg component directories created
- [ ] All 4 components' files copied
- [ ] SharedModule updated with component declarations
- [ ] `app.component.html` includes `<app-rosersg-chat>`
- [ ] `item-detail.component.html` has metadata & recommendations
- [ ] `search.component.html` has search enhance component
- [ ] `environment.prod.ts` has rosersg config
- [ ] DSpace Angular built successfully
- [ ] Built files deployed
- [ ] DSpace restarted
- [ ] Chat button visible on all pages
- [ ] Search page shows AI suggestions
- [ ] Item pages show metadata suggestions
- [ ] Item pages show recommendations

---

## 🎯 Expected Result

When complete, users visiting **https://repo.dare.co.zw** will see:

✅ **Chat Button** (bottom-right, all pages) - Click to ask rosersg questions  
✅ **AI Search** (search page) - Get AI-enhanced search suggestions  
✅ **Metadata Suggestions** (item pages) - Improve metadata with AI  
✅ **Recommendations** (item pages) - Discover related research  

All without leaving the DSpace domain! 🎉

---

## 📞 Support & References

- **Full Documentation**: See `ROSERSG.md`
- **Component Code**: See `EMBED_IN_DSPACE.md`
- **Quick Start**: See `QUICKSTART.md`
- **Deployment Guide**: See `DEPLOY_DSPACE_LIVE.md`

---

**Ready to deploy? Start with Phase 1 on your production server!**
