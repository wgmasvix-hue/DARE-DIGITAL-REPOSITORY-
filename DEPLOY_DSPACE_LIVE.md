# 🚀 Deploy rosersg LIVE on DSpace in 5 Minutes

Quick reference for getting rosersg running on your DSpace instance at `repo.dare.co.zw`

## Option A: Automated Deployment (Recommended)

```bash
# Run the automated deployment script
chmod +x deploy-to-dspace.sh
sudo ./deploy-to-dspace.sh

# Follow the prompts - it handles everything!
```

**What the script does:**
- ✅ Checks Docker/Compose installation
- ✅ Verifies DSpace connectivity
- ✅ Clones/updates the repository
- ✅ Generates secure API key
- ✅ Builds Docker images
- ✅ Starts all services
- ✅ Runs health checks
- ✅ Optionally configures Nginx

**Time needed:** ~5-10 minutes

---

## Option B: Manual Deployment (Step-by-step)

### 1. Prerequisites

```bash
# Check Docker
docker --version
docker-compose --version

# Check git
git --version
```

### 2. Clone Repository

```bash
# Create directory
sudo mkdir -p /opt/rosersg
cd /opt/rosersg

# Clone rosersg branch
sudo git clone -b claude/rosersg-ollama-dspace-ai-b9tvxu \
  https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git .
```

### 3. Configure for DSpace

```bash
# Copy environment template
cp .env.example .env

# Edit .env
nano .env
```

**Must update:**
```env
DSPACE_ENDPOINT=https://repo.dare.co.zw
ROSERSG_API_KEY=your-secure-key-here
```

### 4. Start Services

```bash
# Build and start
docker-compose up -d

# Wait 60 seconds for services to initialize...

# Verify running
docker-compose ps
docker-compose logs -f rosersg-api
```

### 5. Test Connection

```bash
# Health check
curl http://localhost:5000/health

# Test DSpace integration
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -H "X-API-Key: $API_KEY" \
  http://localhost:5000/api/dspace/health
```

**Expected response:** Shows `"status":"online"` if DSpace is reachable

### 6. Access rosersg

- **Frontend UI:** http://localhost:3000
- **API:** http://localhost:5000
- **Ollama:** http://localhost:11434

---

## Exposing to DSpace Users

### Option 1: Nginx Reverse Proxy (Production)

Add to your DSpace Nginx config (`/etc/nginx/sites-enabled/dspace`):

```nginx
# rosersg AI API
location /ai-api/ {
    proxy_pass http://localhost:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# rosersg UI
location /ai/ {
    proxy_pass http://localhost:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Then restart Nginx:
```bash
sudo systemctl restart nginx
```

**Users access at:**
- http://repo.dare.co.zw/ai/ (UI)
- http://repo.dare.co.zw/ai-api/ (API)

### Option 2: Direct Access (Development)

If firewall permits:
- UI: http://server-ip:3000
- API: http://server-ip:5000

### Option 3: SSH Tunnel (Remote Testing)

```bash
ssh -L 3000:localhost:3000 -L 5000:localhost:5000 user@server

# Then access locally:
# http://localhost:3000
# http://localhost:5000
```

---

## Verification Checklist

- [ ] Services running: `docker-compose ps`
- [ ] API healthy: `curl http://localhost:5000/health`
- [ ] DSpace connected: Check `/api/dspace/health`
- [ ] Frontend accessible: Open http://localhost:3000
- [ ] Can chat with AI: Try asking a question
- [ ] Can search DSpace: Try searching for something
- [ ] Can use recommendations: Try the recommendations tab
- [ ] Nginx configured: If using reverse proxy
- [ ] SSL/HTTPS enabled: For production
- [ ] API key secured: Check `.env`

---

## API Key Management

```bash
# View current API key
grep ROSERSG_API_KEY .env

# Generate new key (when needed)
openssl rand -hex 32

# Update .env and restart
# Then: docker-compose restart rosersg-api
```

**Use in requests:**
```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:5000/api/status
```

---

## Monitoring & Logs

```bash
# Real-time logs
docker-compose logs -f rosersg-api

# Specific service
docker-compose logs -f ollama
docker-compose logs -f rosersg-ui

# Container stats
docker stats rosersg-api

# Disk usage
du -sh /var/lib/docker/volumes/ollama_data
```

---

## Troubleshooting

### "Cannot connect to DSpace"
```bash
# Test DSpace API directly
curl https://repo.dare.co.zw/server/api/core/collections

# Check .env has correct endpoint
grep DSPACE_ENDPOINT .env
```

### "Ollama not responding"
```bash
# Check if running
docker-compose ps | grep ollama

# View logs
docker-compose logs ollama

# Restart
docker-compose restart ollama
```

### "UI shows blank page"
```bash
# Check UI logs
docker-compose logs rosersg-ui

# Verify frontend URL
curl http://localhost:3000

# Check API connectivity
curl http://localhost:5000/health
```

### "API key rejected"
```bash
# Verify key matches
KEY_IN_ENV=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
echo "Key: $KEY_IN_ENV"

# Restart API with new config
docker-compose restart rosersg-api

# Test again with correct key
curl -H "X-API-Key: $KEY_IN_ENV" http://localhost:5000/api/status
```

---

## Production Deployment

### Enable SSL/HTTPS

1. **Update Nginx config** to use existing DSpace SSL certificates
2. **Ensure .env uses HTTPS**: `DSPACE_ENDPOINT=https://repo.dare.co.zw`
3. **Restart services** after changes

### Secure the Server

```bash
# Firewall rules
sudo ufw allow 22/tcp  # SSH only
sudo ufw allow 80/tcp  # HTTP (for reverse proxy)
sudo ufw allow 443/tcp # HTTPS (for reverse proxy)
sudo ufw enable

# Close direct access to rosersg
sudo ufw deny 3000/tcp
sudo ufw deny 5000/tcp
sudo ufw deny 11434/tcp
```

### Set up Auto-restart

```bash
# Systemd service that manages Docker Compose
sudo tee /etc/systemd/system/rosersg.service > /dev/null <<EOF
[Unit]
Description=rosersg Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/rosersg
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable rosersg
sudo systemctl start rosersg
sudo systemctl status rosersg
```

---

## Useful Commands

```bash
# View status
docker-compose ps

# Stop all
docker-compose down

# Stop and remove volumes (BE CAREFUL!)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Pull latest code
git pull origin claude/rosersg-ollama-dspace-ai-b9tvxu
docker-compose up -d

# Test DSpace search via rosersg
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
curl -X POST http://localhost:5000/api/search/intelligent \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"query": "machine learning"}'

# Get recommendations
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"query": "artificial intelligence"}'

# Optimize metadata
curl -X POST http://localhost:5000/api/metadata/optimize \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"title": "My Research", "description": "About AI"}'
```

---

## File Locations

| File | Purpose |
|------|---------|
| `/opt/rosersg/.env` | Configuration & secrets |
| `/opt/rosersg/rosersg-config.json` | Feature & API settings |
| `/opt/rosersg/docker-compose.yml` | Service orchestration |
| `/opt/rosersg/ROSERSG.md` | Full documentation |
| `/opt/rosersg/DSPACE_INTEGRATION.md` | Integration guide |

---

## Support & Documentation

- **Main Docs:** See `ROSERSG.md` (400+ lines)
- **Integration Guide:** See `DSPACE_INTEGRATION.md` (600+ lines)
- **API Reference:** Run `curl http://localhost:5000/api/status`
- **DSpace API Docs:** https://repo.dare.co.zw/server/docs

---

## Success Indicators

✅ **You're good when:**

```bash
# All containers running
$ docker-compose ps
NAME                      STATUS
rosersg-api               Up
rosersg-ui                Up
rosersg-ollama            Up

# API responds
$ curl http://localhost:5000/health
{"status":"healthy",...}

# DSpace connected
$ curl -H "X-API-Key: KEY" http://localhost:5000/api/dspace/health
{"dspace_status":{"status":"online",...}

# Frontend loads
$ curl http://localhost:3000
<!DOCTYPE html>...
```

---

## Next Steps

1. ✅ Deploy using automated or manual method
2. ✅ Verify all services running
3. ✅ Configure Nginx reverse proxy
4. ✅ Test DSpace integration
5. ✅ Users access via http://repo.dare.co.zw/ai/
6. ✅ Monitor logs and performance
7. ✅ Keep updated: `git pull && docker-compose up -d`

---

## Common Workflows

### Workflow 1: First-Time Setup
```bash
sudo ./deploy-to-dspace.sh  # 5 mins
# -> Done! Access at http://localhost:3000
```

### Workflow 2: Manual Setup
```bash
mkdir -p /opt/rosersg && cd /opt/rosersg
git clone ... .
cp .env.example .env && nano .env  # Edit DSPACE_ENDPOINT
docker-compose up -d && sleep 60
curl http://localhost:5000/health
```

### Workflow 3: Update Existing
```bash
cd /opt/rosersg
git pull origin claude/rosersg-ollama-dspace-ai-b9tvxu
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

🎉 **That's it! rosersg is now live on your DSpace!**

Questions? See the detailed guides:
- DSPACE_INTEGRATION.md - Deep dive
- ROSERSG.md - Complete reference
- QUICKSTART.md - Interactive features
