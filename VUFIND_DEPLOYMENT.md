# VuFind-DSpace Integration Deployment Guide

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- DSpace running at `repo.dare.co.zw`
- Domain configured for `vufind.dare.co.zw`
- SSL certificates (or use Let's Encrypt)

### 1. Prepare Environment

```bash
# Clone/navigate to repository
cd /path/to/DARE-DIGITAL-REPOSITORY-

# Create necessary directories
mkdir -p config/vufind config/nginx config/solr certs logs

# Create .env file
cat > .env << 'EOF'
# ORCID Configuration
ORCID_CLIENT_ID=your_client_id
ORCID_CLIENT_SECRET=your_client_secret

# ChengetAi Configuration (optional)
CHENGETAI_API_KEY=your_api_key

# Environment
ENVIRONMENT=production
EOF

chmod 600 .env
```

### 2. SSL Certificates

**Option A: Let's Encrypt (Recommended)**

```bash
# Using Certbot
sudo certbot certonly --standalone \
  -d vufind.dare.co.zw \
  -d repo.dare.co.zw

# Copy to certs directory
sudo cp /etc/letsencrypt/live/vufind.dare.co.zw/fullchain.pem certs/
sudo cp /etc/letsencrypt/live/vufind.dare.co.zw/privkey.pem certs/
sudo chown $(whoami):$(whoami) certs/*
```

**Option B: Self-Signed (Development Only)**

```bash
openssl req -x509 -newkey rsa:4096 -keyout certs/privkey.pem \
  -out certs/fullchain.pem -days 365 -nodes \
  -subj "/CN=vufind.dare.co.zw"
```

### 3. Deploy with Docker Compose

```bash
# Start services
docker-compose -f docker-compose.vufind.yml up -d

# Check status
docker-compose -f docker-compose.vufind.yml ps

# View logs
docker-compose -f docker-compose.vufind.yml logs -f vufind
```

### 4. Initial Configuration

```bash
# Enter VuFind container
docker-compose -f docker-compose.vufind.yml exec vufind bash

# Create Solr core
curl -X POST http://solr:8983/solr/admin/cores?action=CREATE&name=biblio&configSet=_default

# Initialize harvest
php harvest_oai.php --skip-checks --from-date="2024-01-01"

# Exit container
exit
```

### 5. Verify Installation

```bash
# Test VuFind
curl -H "Host: vufind.dare.co.zw" http://localhost

# Test OAI-PMH from DSpace
curl "http://repo.dare.co.zw/oai/request?verb=Identify"

# Test Solr
curl "http://localhost:8983/solr/biblio/select?q=*:*&rows=0"
```

---

## Production Deployment

### 1. Configure Domain DNS

```bash
# Point to your server
vufind.dare.co.zw A 1.2.3.4
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp    # HTTPS

# Restrict Solr admin to internal only
sudo ufw deny from any to any port 8983
sudo ufw allow from 172.16.0.0/12 to any port 8983  # Docker network
```

### 3. Set Up Automated Harvesting

```bash
# Create cron job
sudo tee /etc/cron.d/vufind-harvest > /dev/null << 'EOF'
# Daily harvest at 2 AM
0 2 * * * docker-compose -f /path/to/docker-compose.vufind.yml exec -T vufind php harvest_oai.php --skip-checks >> /var/log/vufind-harvest.log 2>&1

# Weekly Solr optimization on Sunday at 3 AM
0 3 * * 0 curl "http://localhost:8983/solr/biblio/update?optimize=true" >> /var/log/vufind-optimize.log 2>&1

# Daily monitoring at 4 AM
0 4 * * * /path/to/scripts/check-harvest-status.sh >> /var/log/vufind-monitor.log 2>&1
EOF

sudo chmod 644 /etc/cron.d/vufind-harvest
```

### 4. Monitoring & Alerts

Create `scripts/check-harvest-status.sh`:

```bash
#!/bin/bash

LAST_HARVEST=$(stat -c %y /var/lib/docker/volumes/dare-vufind_vufind-logs/_data/harvest_oai.log 2>/dev/null || echo "Never")
DOC_COUNT=$(curl -s "http://localhost:8983/solr/biblio/select?q=*:*&rows=0" | grep -o '"numFound":[0-9]*' | cut -d: -f2)

echo "=== VuFind Harvest Status ==="
echo "Last Harvest: $LAST_HARVEST"
echo "Documents Indexed: $DOC_COUNT"

# Alert if stale (>48 hours)
LAST_MODIFIED=$(stat -c %Y /var/lib/docker/volumes/dare-vufind_vufind-logs/_data/harvest_oai.log 2>/dev/null || echo 0)
CURRENT_TIME=$(date +%s)
DIFF=$((CURRENT_TIME - LAST_MODIFIED))

if [ $DIFF -gt 172800 ]; then
    echo "⚠️  ALERT: Harvest stale ($(($DIFF / 3600)) hours old)"
    # Send alert email
    echo "Harvest is stale" | mail -s "DARE VuFind Alert" admin@dare.co.zw
fi
```

Make it executable:
```bash
chmod +x scripts/check-harvest-status.sh
```

### 5. Backup Strategy

```bash
# Backup Solr index and harvest logs
sudo tee /etc/cron.d/vufind-backup > /dev/null << 'EOF'
# Weekly backup on Saturday at 1 AM
0 1 * * 6 tar -czf /backup/vufind-$(date +\%Y\%m\%d).tar.gz \
  /var/lib/docker/volumes/dare-vufind_solr-data/_data \
  /var/lib/docker/volumes/dare-vufind_vufind-logs/_data
EOF
```

---

## Troubleshooting

### Issue: OAI-PMH Connection Fails

```bash
# Check DSpace OAI endpoint
curl -v "http://repo.dare.co.zw/oai/request?verb=Identify"

# Check firewall
telnet repo.dare.co.zw 80

# Check logs
docker-compose -f docker-compose.vufind.yml logs vufind | grep -i oai
```

### Issue: Solr Not Indexing

```bash
# Check Solr health
curl http://localhost:8983/solr/admin/cores

# Check if core exists
curl "http://localhost:8983/solr/admin/cores?action=STATUS&core=biblio"

# Re-index
docker-compose -f docker-compose.vufind.yml exec vufind \
  php harvest_oai.php --skip-checks --force
```

### Issue: VuFind Returns 502 Bad Gateway

```bash
# Check upstream
docker-compose -f docker-compose.vufind.yml ps

# Restart VuFind
docker-compose -f docker-compose.vufind.yml restart vufind

# Check logs
docker-compose -f docker-compose.vufind.yml logs vufind
```

### Issue: High Memory Usage

```bash
# Check container stats
docker stats

# Reduce Solr heap (edit docker-compose.yml)
# SOLR_HEAP=1g  # Reduce from 2g

# Restart
docker-compose -f docker-compose.vufind.yml restart solr
```

---

## Performance Optimization

### 1. Solr Configuration

```bash
# Increase cache sizes
docker-compose -f docker-compose.vufind.yml exec solr \
  curl "http://localhost:8983/solr/biblio/config?action=set-cache-sizes&max_default_cache_size=512&max_warming_searches=10"
```

### 2. VuFind Caching

```bash
# Enable Redis caching (optional)
# Add to docker-compose.vufind.yml:
# redis:
#   image: redis:7-alpine
#   ports:
#     - "6379:6379"

# Update VuFind config:
# [Caching]
# type = redis
# host = redis
# port = 6379
```

### 3. CDN Configuration

```nginx
# In nginx config, set cache headers for static files
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

---

## Security Hardening

### 1. Restrict Administrative Access

```nginx
# In nginx config, restrict /admin and /config
location ~ /admin/ {
    allow 10.0.0.0/8;      # Internal network only
    deny all;
}
```

### 2. Enable Security Headers

Already configured in `config/nginx/vufind.conf`

### 3. Regular Updates

```bash
# Check for updates
docker pull vufind/vufind:latest

# Update docker-compose.yml with new version
# Redeploy
docker-compose -f docker-compose.vufind.yml pull
docker-compose -f docker-compose.vufind.yml up -d
```

---

## Integration with Matomo Analytics

See `docs/integration-guides/matomo-setup.md` for analytics integration.

---

## Integration with ChengetAi Labs

Add to `config/vufind/config.ini`:

```ini
[ChengetAi]
enabled = true
api_url = https://api.chengetai.com
api_key = ${CHENGETAI_API_KEY}
search_enhancement = true
recommendations = true
auto_tagging = true
```

---

## Support & Resources

- [VuFind Documentation](https://vufind.org/wiki/start)
- [DSpace OAI-PMH Guide](https://wiki.lyrasis.org/display/DSPACE/OAI-PMH)
- [Solr Documentation](https://solr.apache.org/guide/)
- [ORCID Integration](https://github.com/ORCID/orcid-integration-examples)

---

## Next Steps

1. ✅ VuFind installed and running
2. ⬜ Add Matomo Analytics
3. ⬜ Integrate ChengetAi AI features
4. ⬜ Configure custom branding
5. ⬜ Set up user authentication
6. ⬜ Add search facets
7. ⬜ Configure recommended results
8. ⬜ Performance optimization
