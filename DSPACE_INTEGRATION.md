# rosersg × DSpace Integration Guide

Complete guide to integrate rosersg AI with your live DSpace instance at `repo.dare.co.zw`

## 🔗 Integration Architecture

```
┌─────────────────────────────────────┐
│     User Browsers                   │
│  (Access via repo.dare.co.zw)    │
└────────────────┬────────────────────┘
                 │
        ┌────────▼──────────┐
        │  DSpace Frontend   │  (Angular/Vue)
        │  repo.dare.co.zw│
        └────────┬──────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌──────────────┐
│DSpace  │  │rosersg │  │ Nginx Proxy  │
│REST    │  │ AI API │  │(Optional)    │
│API     │  │:5000   │  │              │
└────────┘  └────────┘  └──────────────┘
    │            ▲
    └────────────┘
      (REST Calls)
```

## ✅ Prerequisites

- ✓ DSpace instance running at `repo.dare.co.zw`
- ✓ DSpace REST API enabled
- ✓ Docker & Docker Compose installed
- ✓ Network access between rosersg and DSpace

## 📋 Step 1: Configure DSpace Connection

### Update `.env` file

```bash
# Edit your .env file
nano .env
```

**Add/Update these settings:**

```env
# DSpace Configuration - IMPORTANT!
DSPACE_ENDPOINT=https://repo.dare.co.zw
DSPACE_REST_API_URL=https://repo.dare.co.zw/server/api

# If DSpace uses authentication (optional)
DSPACE_API_TOKEN=your-token-here  # Leave empty if not needed

# rosersg Configuration
OLLAMA_ENDPOINT=http://ollama:11434
OLLAMA_MODEL=mistral

# Security
ROSERSG_API_KEY=your-secure-key-here
```

### Update `rosersg-config.json`

```bash
nano rosersg-config.json
```

**Modify the `dspace` section:**

```json
{
  "dspace": {
    "endpoint": "https://repo.dare.co.zw",
    "rest_api": "/server/api",
    "search_limit": 50,
    "timeout": 30000,
    "collections": {
      "enabled": true,
      "cache_ttl": 3600
    }
  }
}
```

## 🧪 Step 2: Test DSpace Connection

### Test REST API Access

```bash
# Test basic connectivity
curl https://repo.dare.co.zw/server/api/core/collections

# If behind authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://repo.dare.co.zw/server/api/core/collections
```

### Test from rosersg Container

```bash
# Start services first
docker-compose up -d

# Test from API container
docker-compose exec rosersg-api curl \
  https://repo.dare.co.zw/server/api/core/collections

# Check logs
docker-compose logs -f rosersg-api
```

## 🚀 Step 3: Deploy rosersg

### Option A: Local Development (Testing)

```bash
# 1. Update configuration files
nano .env
nano rosersg-config.json

# 2. Start services
docker-compose up -d

# 3. Verify connection
curl -H "X-API-Key: your-api-key" \
  http://localhost:5000/api/status

# 4. Test DSpace search through rosersg
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -X POST http://localhost:5000/api/search/intelligent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"query": "your search term"}'
```

### Option B: Production Deployment (Server)

#### On your server/VM:

```bash
# 1. Clone repository
git clone https://github.com/wgmasvix-hue/dare-digital-repository-.git
cd dare-digital-repository-

# 2. Check out rosersg branch
git checkout claude/rosersg-ollama-dspace-ai-b9tvxu

# 3. Setup environment
cp .env.example .env

# 4. Edit with your settings
nano .env  # Update DSpace endpoint, API key

# 5. Start services
docker-compose up -d

# 6. Verify running
docker-compose ps
docker-compose logs rosersg-api
```

## 🌐 Step 4: Expose rosersg to DSpace Users

### Option A: Reverse Proxy (Recommended)

If you're using Nginx as reverse proxy for DSpace, add rosersg:

**Nginx Configuration** (`/etc/nginx/sites-enabled/dspace`):

```nginx
# Add this to your existing DSpace server block

upstream rosersg_backend {
    server localhost:5000;
}

upstream rosersg_ui {
    server localhost:3000;
}

server {
    listen 443 ssl http2;
    server_name repo.dare.co.zw;

    # ... existing DSpace SSL config ...

    # rosersg API route
    location /ai-api/ {
        proxy_pass http://rosersg_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Content-Type, X-API-Key';
    }

    # rosersg UI route
    location /ai/ {
        proxy_pass http://rosersg_ui/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Restart Nginx:**
```bash
sudo systemctl restart nginx
```

**Access rosersg at:**
- Frontend: `https://repo.dare.co.zw/ai/`
- API: `https://repo.dare.co.zw/ai-api/`

### Option B: Subdomain

If you can create a DNS subdomain:

```nginx
server {
    listen 443 ssl http2;
    server_name ai.dare.co.zw;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api-ai.dare.co.zw;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🎨 Step 5: Integrate with DSpace UI

### Option A: Embed in DSpace Theme

Add rosersg widget to your DSpace Angular theme:

**File:** `dspace-angular/src/app/shared/components/rosersg-widget.component.ts`

```typescript
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-rosersg-widget',
  template: `
    <div class="rosersg-widget">
      <h3>🤖 Ask rosersg</h3>
      <input 
        [(ngModel)]="query" 
        placeholder="Ask about this item..."
        (keyup.enter)="search()"
      />
      <button (click)="search()">Search</button>
      <div *ngIf="results" class="results">
        {{ results }}
      </div>
    </div>
  `,
  styles: [`
    .rosersg-widget {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
    }
  `]
})
export class RosersqWidgetComponent implements OnInit {
  query = '';
  results = '';

  constructor(private http: HttpClient) {}

  ngOnInit() {}

  search() {
    const apiKey = localStorage.getItem('rosersg-api-key');
    this.http.post('/ai-api/api/search/intelligent', 
      { query: this.query },
      { headers: { 'X-API-Key': apiKey } }
    ).subscribe(
      (response: any) => {
        this.results = response.ai_suggestions;
      }
    );
  }
}
```

### Option B: DSpace Plugin (Advanced)

Create a DSpace plugin for deeper integration:

**File:** `dspace-server/src/main/java/org/dspace/rosersg/RosersqPlugin.java`

```java
@RestController
@RequestMapping("/api/rosersg")
public class RosersqPlugin {
    
    @Autowired
    private ItemService itemService;
    
    @GetMapping("/item/{id}/ai-summary")
    public ResponseEntity<?> getAISummary(@PathVariable String id) {
        // Get item from DSpace
        Item item = itemService.find(context, UUID.fromString(id));
        
        // Call rosersg API
        // Return enhanced metadata
        
        return ResponseEntity.ok(aiSummary);
    }
    
    @PostMapping("/search/enhanced")
    public ResponseEntity<?> enhancedSearch(@RequestBody SearchRequest req) {
        // Call rosersg intelligent search
        // Combine with DSpace results
        
        return ResponseEntity.ok(combinedResults);
    }
}
```

## 🔄 Step 6: Sync DSpace Data with rosersg

### Create Cron Job for Indexing

**File:** `index-collections.sh`

```bash
#!/bin/bash

API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
DSPACE_API="https://repo.dare.co.zw/server/api"

# Get all collections
COLLECTIONS=$(curl -s "$DSPACE_API/core/collections" | \
  jq -r '.page.content[] | .id')

# Update collection insights
for COLLECTION_ID in $COLLECTIONS; do
  echo "Updating insights for collection: $COLLECTION_ID"
  
  curl -X GET "http://localhost:5000/api/collections/insights" \
    -H "X-API-Key: $API_KEY"
done

echo "Collection indexing complete"
```

**Schedule with cron:**

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * /path/to/index-collections.sh >> /var/log/rosersg-index.log 2>&1
```

## 📊 Step 7: Monitor Integration

### Check Service Status

```bash
# API health
curl https://repo.dare.co.zw/ai-api/health

# Full status
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
  https://repo.dare.co.zw/ai-api/api/status
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f rosersg-api

# Specific time range
docker-compose logs --since 1h rosersg-api

# Save logs to file
docker-compose logs > rosersg.log
```

### Monitor Performance

```bash
# Check container stats
docker stats rosersg-api rosersg-ui rosersg-ollama

# Check disk usage
du -sh /var/lib/docker/volumes/ollama_data
```

## 🔐 Step 8: Security Configuration

### Enable HTTPS

Ensure your `.env` uses HTTPS:

```env
DSPACE_ENDPOINT=https://repo.dare.co.zw
```

### Secure API Key

```bash
# Generate strong random key
openssl rand -hex 32

# Update in .env
ROSERSG_API_KEY=your-new-generated-key
```

### Configure Firewall

```bash
# Only allow rosersg API to be accessed through DSpace
sudo ufw allow from localhost to localhost port 5000
sudo ufw allow from localhost to localhost port 3000
sudo ufw allow from localhost to localhost port 11434
```

### DSpace Authentication (Optional)

If DSpace requires API token:

```bash
# Get DSpace API token
curl -X POST "https://repo.dare.co.zw/server/api/authn/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"your-password"}'

# Update .env with token
DSPACE_API_TOKEN=your-token-here

# Update rosersg.py to use token:
# headers = {"Authorization": f"Bearer {DSPACE_API_TOKEN}"}
```

## 🚀 Step 9: Deploy to Production

### Systemd Service (Alternative to Docker)

**File:** `/etc/systemd/system/rosersg.service`

```ini
[Unit]
Description=rosersg AI Service
After=network.target
Requires=ollama.service

[Service]
Type=notify
User=rosersg
WorkingDirectory=/opt/rosersg
Environment="PATH=/opt/rosersg/venv/bin"
ExecStart=/opt/rosersg/venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --timeout 120 \
    rosersg:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl enable rosersg
sudo systemctl start rosersg
sudo systemctl status rosersg
```

### Kubernetes Deployment (Optional)

**File:** `k8s/rosersg-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rosersg-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rosersg
  template:
    metadata:
      labels:
        app: rosersg
    spec:
      containers:
      - name: rosersg
        image: rosersg:latest
        ports:
        - containerPort: 5000
        env:
        - name: DSPACE_ENDPOINT
          value: "https://repo.dare.co.zw"
        - name: OLLAMA_ENDPOINT
          value: "http://ollama:11434"
        - name: ROSERSG_API_KEY
          valueFrom:
            secretKeyRef:
              name: rosersg-secrets
              key: api-key
```

## 🧩 Step 10: Custom Integration Examples

### Add rosersg Search to DSpace Header

**DSpace Angular:** Add to search bar component

```typescript
// In search.service.ts
searchWithAI(query: string) {
  const apiKey = this.configService.get('rosersg.apiKey');
  
  return this.http.post('/ai-api/api/search/intelligent',
    { query },
    { headers: { 'X-API-Key': apiKey } }
  ).pipe(
    switchMap(aiSuggestions => 
      this.dspaceSearch.search(query, aiSuggestions)
    )
  );
}
```

### Add AI Metadata to Item Detail Page

```typescript
// In item-detail.component.ts
ngOnInit() {
  this.item$.subscribe(item => {
    this.getAISummary(item.id);
  });
}

getAISummary(itemId: string) {
  const apiKey = this.configService.get('rosersg.apiKey');
  
  this.http.get(`/ai-api/api/item/${itemId}/summarize`,
    { headers: { 'X-API-Key': apiKey } }
  ).subscribe(summary => {
    this.aiSummary = summary;
  });
}
```

## ✅ Verification Checklist

- [ ] Updated `.env` with correct DSpace endpoint
- [ ] Updated `rosersg-config.json` with DSpace settings
- [ ] Tested DSpace API connectivity
- [ ] Started rosersg with `docker-compose up -d`
- [ ] Verified rosersg API responds at `/health`
- [ ] Tested search functionality through rosersg
- [ ] Configured Nginx reverse proxy (if applicable)
- [ ] Set up SSL/HTTPS
- [ ] Secured API key in production
- [ ] Configured firewall rules
- [ ] Set up monitoring and logging
- [ ] Tested with actual DSpace data

## 🔧 Troubleshooting

### "Cannot connect to DSpace"
```bash
# Check network connectivity
docker-compose exec rosersg-api \
  curl -v https://repo.dare.co.zw/server/api/core/collections

# Check firewall
sudo ufw status
```

### "API Key rejected"
```bash
# Verify key in .env
grep ROSERSG_API_KEY .env

# Restart services
docker-compose restart rosersg-api
```

### "Ollama not responding"
```bash
# Check Ollama health
curl http://localhost:11434/api/tags

# Restart Ollama
docker-compose restart ollama

# Check logs
docker logs rosersg-ollama
```

### "DSpace search not working"
```bash
# Test DSpace REST API directly
curl "https://repo.dare.co.zw/server/api/discover/search?query=test"

# Check DSpace API documentation
# Usually at: https://repo.dare.co.zw/server/docs
```

## 📚 Additional Resources

- DSpace REST API Docs: `https://repo.dare.co.zw/server/docs`
- Ollama Documentation: `https://ollama.ai`
- rosersg Backend Docs: See `ROSERSG.md`
- rosersg Frontend Docs: See `QUICKSTART.md`

## 🎉 Success!

Once integrated, your users can:

✅ Search your DSpace repository with AI assistance
✅ Get automatic metadata suggestions
✅ Discover related research automatically
✅ Chat with an AI about your collections
✅ Get intelligent insights about your data

---

**Questions?** Check the logs, review the troubleshooting guide, or refer to the main documentation files.

**Ready to deploy?** Follow the steps above in order and test at each stage!
