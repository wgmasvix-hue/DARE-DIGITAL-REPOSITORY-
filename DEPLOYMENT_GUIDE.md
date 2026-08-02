# Gutenberg Deployment Guide

Complete guide for deploying Project Gutenberg data to the DARE server.

## Quick Start

### Option 1: Bash Script (Simple)
```bash
cd deploy/
chmod +x deploy_gutenberg.sh
./deploy_gutenberg.sh production
```

### Option 2: Kubernetes (Scalable)
```bash
kubectl apply -f deploy/gutenberg-deployment.yaml
```

---

## Deployment Methods

### Method 1: Direct Server Deployment (Bash)

**Best for**: Single server, simple setup, manual control

#### Prerequisites
- SSH access to server
- Python 3.7+ on server
- ~500GB free disk space
- Write permissions to `/opt/dspace/data/`

#### Step-by-Step

##### 1. Prepare Deployment
```bash
cd /home/user/DARE-DIGITAL-REPOSITORY-
chmod +x deploy/deploy_gutenberg.sh
```

##### 2. Deploy to Production
```bash
deploy/deploy_gutenberg.sh production
```

Or staging:
```bash
deploy/deploy_gutenberg.sh staging
```

##### 3. Verify Deployment
```bash
# Check files are in place
ssh dspace@dspace.dare.co.zw ls -lah /opt/dspace/data/gutenberg

# Check API endpoint
curl https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_sample.json

# Check cron job
ssh dspace@dspace.dare.co.zw crontab -l | grep gutenberg
```

#### Deployment Locations

| Item | Location |
|------|----------|
| Data Files | `/opt/dspace/data/gutenberg/` |
| Harvester Script | `/opt/dspace/data/gutenberg/harvest_gutenberg.py` |
| Documentation | `/opt/dspace/data/gutenberg/GUTENBERG_DATASET.md` |
| Web Access | `/var/www/dspace/data/gutenberg/` (symlink) |
| Logs | `/var/log/dspace/gutenberg_harvest.log` |
| Cron Job | User crontab, runs daily at 2 AM |

#### Manual Operations

**Trigger harvest immediately:**
```bash
ssh dspace@dspace.dare.co.zw /opt/dspace/scripts/harvest_gutenberg_daily.sh
```

**View harvest logs:**
```bash
ssh dspace@dspace.dare.co.zw tail -f /var/log/dspace/gutenberg_harvest.log
```

**Stop cron job:**
```bash
ssh dspace@dspace.dare.co.zw crontab -e
# Remove the gutenberg_harvest line
```

**Restart cron job:**
```bash
ssh dspace@dspace.dare.co.zw
(crontab -l 2>/dev/null | grep -v "harvest_gutenberg"; echo "0 2 * * * /opt/dspace/scripts/harvest_gutenberg_daily.sh") | crontab -
```

---

### Method 2: Kubernetes Deployment (Recommended)

**Best for**: Cloud infrastructure, GKE, high availability, scaling

#### Prerequisites
- Kubernetes cluster (1.18+)
- kubectl configured
- 500GB PersistentVolume available
- cert-manager for HTTPS
- nginx-ingress controller

#### Step-by-Step

##### 1. Create Namespace and Resources
```bash
kubectl apply -f deploy/gutenberg-deployment.yaml
```

##### 2. Verify Deployment
```bash
# Check namespace
kubectl get namespace dare-data

# Check PersistentVolumeClaim
kubectl get pvc -n dare-data

# Check CronJob
kubectl get cronjob -n dare-data

# Check Deployment
kubectl get deployment -n dare-data

# Check Service
kubectl get service -n dare-data
```

##### 3. Monitor Deployment
```bash
# Watch logs
kubectl logs -n dare-data -l app=dare,component=gutenberg-api -f

# Check CronJob history
kubectl get jobs -n dare-data -l app=dare,component=gutenberg

# View recent job logs
kubectl logs -n dare-data $(kubectl get pods -n dare-data --sort-by=.metadata.creationTimestamp -l batch.kubernetes.io/controller-uid -o jsonpath='{.items[-1].metadata.name}')
```

##### 4. Manual Harvest Trigger (Kubernetes)
```bash
# Create one-off job
kubectl create job --from=cronjob/gutenberg-harvest gutenberg-harvest-manual-$(date +%s) -n dare-data

# Check job status
kubectl get job -n dare-data

# View logs
kubectl logs -n dare-data job/gutenberg-harvest-manual-*
```

#### Kubernetes Architecture

```
┌─────────────────────────────────────────────────────┐
│ dare-data Namespace                                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ┌──────────────────────────────────────────────┐  │
│ │ CronJob: gutenberg-harvest                   │  │
│ │ Schedule: 0 2 * * * (Daily at 2 AM UTC)     │  │
│ │ Creates: Pod with harvest_gutenberg.py       │  │
│ └──────────────────────────────────────────────┘  │
│                          │                         │
│                          ↓                         │
│ ┌──────────────────────────────────────────────┐  │
│ │ PersistentVolumeClaim: gutenberg-data-pvc   │  │
│ │ Size: 500Gi                                  │  │
│ │ Access: ReadWriteOnce                        │  │
│ └──────────────────────────────────────────────┘  │
│                          │                         │
│                          ↓                         │
│ ┌──────────────────────────────────────────────┐  │
│ │ Deployment: gutenberg-api (2 replicas)       │  │
│ │ Container: nginx:alpine                      │  │
│ │ Serves: JSON/CSV data, API endpoints         │  │
│ └──────────────────────────────────────────────┘  │
│                          │                         │
│                          ↓                         │
│ ┌──────────────────────────────────────────────┐  │
│ │ Service: gutenberg-api-service               │  │
│ │ Type: LoadBalancer                           │  │
│ │ Port: 80 → 8080                              │  │
│ └──────────────────────────────────────────────┘  │
│                          │                         │
│                          ↓                         │
│ ┌──────────────────────────────────────────────┐  │
│ │ Ingress: gutenberg-ingress                   │  │
│ │ Host: dspace.dare.co.zw                      │  │
│ │ TLS: Enabled (cert-manager)                  │  │
│ │ Paths:                                       │  │
│ │   /data/gutenberg → API Service              │  │
│ │   /api/gutenberg → API Service               │  │
│ └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Kubernetes ConfigMaps

**gutenberg-config**: Environment and scheduling settings
```yaml
harvest_schedule: "0 2 * * *"
api_url: "https://dspace.dare.co.zw"
data_path: "/data/gutenberg"
```

**nginx-config**: Web server configuration with CORS
```yaml
- Directory listing on /data/gutenberg/
- API routing for /api/gutenberg/
- CORS headers for browser requests
- 1-day caching for data files
- Health check endpoint
```

**gutenberg-scripts**: Harvester script content

#### Scaling in Kubernetes

**Increase API replicas:**
```bash
kubectl scale deployment gutenberg-api --replicas=5 -n dare-data
```

**Increase storage:**
```bash
kubectl patch pvc gutenberg-data-pvc -p '{"spec":{"resources":{"requests":{"storage":"1Ti"}}}}' -n dare-data
```

**Change harvest schedule:**
```bash
kubectl patch cronjob gutenberg-harvest -p '{"spec":{"schedule":"0 0 * * *"}}' -n dare-data
```

---

## API Endpoints (After Deployment)

### Data Files
```bash
# Full JSON dataset
https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_latest.json

# Full CSV dataset
https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_latest.csv

# Sample data
https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_sample.json
https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_sample.csv

# Documentation
https://dspace.dare.co.zw/data/gutenberg/GUTENBERG_DATASET.md

# Directory listing
https://dspace.dare.co.zw/data/gutenberg/
```

### API Endpoints
```bash
# Latest books (redirects to JSON)
https://dspace.dare.co.zw/api/gutenberg/books

# Sample books
https://dspace.dare.co.zw/api/gutenberg/sample
```

### Example Usage
```bash
# Get all books
curl https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_latest.json | jq length

# Get CSV
curl https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_latest.csv | head -10

# Stream and process
curl https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_latest.json \
  | jq '.[] | select(.languages[] == "en") | .title' | head -20
```

---

## Monitoring & Maintenance

### Automated Monitoring (Kubernetes)
```bash
# PrometheusRule alerts:
# - GutenbergHarvestFailed: Triggers if harvest fails
# - GutenbergDataMissing: Triggers if no books in storage
```

### Manual Monitoring

**Check harvest status:**
```bash
# Bash method
ssh dspace@dspace.dare.co.zw ls -lah /opt/dspace/data/gutenberg/

# Kubernetes method
kubectl get pvc -n dare-data
kubectl get pod -n dare-data -l batch.kubernetes.io/controller-uid
```

**Monitor harvest logs:**
```bash
# Bash method
ssh dspace@dspace.dare.co.zw tail -f /var/log/dspace/gutenberg_harvest.log

# Kubernetes method
kubectl logs -n dare-data -l app=dare,component=gutenberg -f
```

**Check API availability:**
```bash
curl -I https://dspace.dare.co.zw/data/gutenberg/gutenberg_books_sample.json
```

### Maintenance Tasks

#### Backup Data
```bash
# Bash
ssh dspace@dspace.dare.co.zw \
  tar -czf /backup/gutenberg_$(date +%Y%m%d).tar.gz \
  /opt/dspace/data/gutenberg/

# Kubernetes
kubectl exec -n dare-data $(kubectl get pod -n dare-data -o jsonpath='{.items[0].metadata.name}') \
  -- tar -czf /backup/gutenberg_$(date +%Y%m%d).tar.gz /data/gutenberg/
```

#### Update Harvester Script
```bash
# Download latest
curl https://raw.githubusercontent.com/wgmasvix-hue/dare-digital-repository-/main/harvest_gutenberg.py \
  > /tmp/harvest_gutenberg.py

# Backup old version
ssh dspace@dspace.dare.co.zw \
  cp /opt/dspace/data/gutenberg/harvest_gutenberg.py \
  /opt/dspace/data/gutenberg/harvest_gutenberg.py.bak

# Deploy new version
scp /tmp/harvest_gutenberg.py dspace@dspace.dare.co.zw:/opt/dspace/data/gutenberg/
ssh dspace@dspace.dare.co.zw chmod 755 /opt/dspace/data/gutenberg/harvest_gutenberg.py
```

#### Clean Old Backups
```bash
# Keep last 30 days of data
find /opt/dspace/data/gutenberg/gutenberg_books_*.json -mtime +30 -delete
find /opt/dspace/data/gutenberg/checkpoint_books_*.json -mtime +30 -delete
```

---

## Troubleshooting

### "Connection refused" when accessing API
**Problem**: API endpoint returns connection refused  
**Solution**:
```bash
# Bash: Check if web server is running
ssh dspace@dspace.dare.co.zw sudo systemctl status nginx

# Kubernetes: Check if pod is running
kubectl get pod -n dare-data -l app=dare,component=gutenberg-api
```

### "Permission denied" when harvesting
**Problem**: Harvest script fails with permission error  
**Solution**:
```bash
# Fix permissions
chmod 755 /opt/dspace/data/gutenberg/harvest_gutenberg.py
chmod 755 /opt/dspace/data/gutenberg/
chown dspace:dspace -R /opt/dspace/data/gutenberg/
```

### Harvest takes too long
**Problem**: Harvest job times out or takes hours  
**Solution**:
```bash
# Increase timeout in CronJob
kubectl patch cronjob gutenberg-harvest -n dare-data \
  -p '{"spec":{"jobTemplate":{"spec":{"activeDeadlineSeconds":86400}}}}'

# Reduce API calls with filters
# Edit harvest_gutenberg.py to harvest specific language only
```

### "No space left on device"
**Problem**: Storage is full  
**Solution**:
```bash
# Clean old checkpoints
rm /opt/dspace/data/gutenberg/checkpoint_books_*.json

# Archive old exports
tar -czf /backup/gutenberg_archive_$(date +%Y%m).tar.gz \
  /opt/dspace/data/gutenberg/gutenberg_books_2024*.json

# Extend PV size (Kubernetes)
kubectl patch pvc gutenberg-data-pvc -n dare-data \
  -p '{"spec":{"resources":{"requests":{"storage":"1Ti"}}}}'
```

---

## Rollback

### Bash Deployment
```bash
# Remove deployed files
ssh dspace@dspace.dare.co.zw rm -rf /opt/dspace/data/gutenberg

# Remove cron job
ssh dspace@dspace.dare.co.zw crontab -e
# Remove gutenberg line

# Restore from backup
tar -xzf /backup/gutenberg_backup.tar.gz -C /
```

### Kubernetes Deployment
```bash
# Delete everything
kubectl delete namespace dare-data

# Restore from PVC backup
kubectl apply -f gutenberg-deployment.yaml
kubectl exec -n dare-data <pod-name> -- tar -xzf /backup/gutenberg_backup.tar.gz
```

---

## Support & Documentation

- **Deployment Guide**: This file
- **Dataset Docs**: `GUTENBERG_DATASET.md`
- **Harvester Script**: `harvest_gutenberg.py`
- **Repository**: https://github.com/wgmasvix-hue/dare-digital-repository-
- **Issues**: https://github.com/wgmasvix-hue/dare-digital-repository-/issues

---

**Last Updated**: August 2, 2026  
**Version**: 1.0  
**Maintained By**: DARE Team
