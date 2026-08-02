# OpenAlex Harvester - Deployment Guide

Complete guide for deploying the OpenAlex Harvester to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Linux Deployment](#linux-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Go 1.21+ (for building from source)
- DSpace 9 instance with REST API enabled
- OpenAlex API access (free, no authentication)
- Linux server (for systemd deployment)
- Docker & Docker Compose (for containerized deployment)

### System Requirements

- **CPU**: 1+ cores
- **RAM**: 512MB minimum, 2GB recommended
- **Storage**: 100MB for logs and state (depends on volume)
- **Network**: Outbound HTTPS access to OpenAlex API and DSpace

## Linux Deployment

### 1. Build the Harvester

```bash
cd harvesters/openalex
make all
```

This will create the `openalex-harvester` binary.

### 2. Create System User

```bash
sudo useradd -r -s /bin/false -d /var/lib/dare dare
```

### 3. Install Binary and Configuration

```bash
# Create directories
sudo mkdir -p /opt/dare/harvesters/openalex
sudo mkdir -p /etc/dare/harvester
sudo mkdir -p /var/lib/dare/harvester
sudo mkdir -p /var/log/dare/harvester

# Copy binary
sudo cp openalex-harvester /opt/dare/harvesters/openalex/
sudo chmod 755 /opt/dare/harvesters/openalex/openalex-harvester

# Copy configuration files
sudo cp config.json /etc/dare/harvester/
sudo cp topics.json /etc/dare/harvester/

# Set ownership
sudo chown -R dare:dare /opt/dare/harvesters/openalex
sudo chown -R dare:dare /etc/dare/harvester
sudo chown -R dare:dare /var/lib/dare/harvester
sudo chown -R dare:dare /var/log/dare/harvester

# Secure permissions
sudo chmod 750 /etc/dare/harvester
sudo chmod 640 /etc/dare/harvester/config.json
```

### 4. Configure DSpace API Access

Edit `/etc/dare/harvester/config.json`:

```json
{
  "base_url": "https://api.openalex.org",
  "per_page": 50,
  "max_requests": 1000,
  "rate_limit_delay": 100,
  "dspace_url": "https://dspace.dare.co.zw",
  "dspace_api_key": "your-dspace-api-key",
  "enable_incremental": true,
  "enable_deduplication": true,
  "enable_orcid_matching": true,
  "enable_vector_indexing": true,
  "topics": []
}
```

To get a DSpace API key:

```bash
# Login to your DSpace admin panel
# Go to Administration > API Keys
# Generate a new API key for the harvester
```

### 5. Install Systemd Service

```bash
# Copy systemd files
sudo cp systemd/openalex-harvester.service /etc/systemd/system/
sudo cp systemd/openalex-harvester.timer /etc/systemd/system/
sudo cp systemd/openalex-harvester.env /etc/dare/harvester/

# Reload systemd
sudo systemctl daemon-reload

# Enable the timer (starts automatically after reboot)
sudo systemctl enable openalex-harvester.timer

# Start the timer
sudo systemctl start openalex-harvester.timer
```

### 6. Verify Installation

```bash
# Check timer status
sudo systemctl status openalex-harvester.timer

# Check next run time
sudo systemctl list-timers openalex-harvester.timer

# View recent logs
sudo journalctl -u openalex-harvester -n 50

# Follow logs in real-time
sudo journalctl -u openalex-harvester -f
```

### 7. Run Manually (First Time)

```bash
# Test API connectivity
sudo -u dare /opt/dare/harvesters/openalex/openalex-harvester -test-api

# Run harvester manually
sudo -u dare /opt/dare/harvesters/openalex/openalex-harvester -full
```

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t dare/openalex-harvester:1.0 .
```

### 2. Create Configuration Volume

```bash
# Create configuration files
mkdir -p config data logs

# Copy default configs
cp config.json config/
cp topics.json config/

# Edit configuration
vi config/config.json
```

### 3. Run with Docker Compose

```bash
docker-compose up -d
```

### 4. Run Docker Manual Harvest

```bash
docker run --rm \
  -v $(pwd)/config:/config \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/logs \
  dare/openalex-harvester:1.0
```

### 5. Scheduled Runs with Docker

Use a scheduler service like:

**Option A: Host Cron**

```bash
# Add to system crontab
0 2 * * * docker run --rm \
  -v /path/to/config:/config \
  -v /path/to/data:/data \
  -v /path/to/logs:/logs \
  dare/openalex-harvester:1.0 >> /var/log/harvest.log 2>&1
```

**Option B: Docker Swarm Scheduled Tasks**

```bash
docker service create \
  --name openalex-harvester \
  --mode global \
  --restart-condition=on-failure \
  --restart-max-attempts=3 \
  -v config:/config \
  -v data:/data \
  -v logs:/logs \
  dare/openalex-harvester:1.0
```

**Option C: APScheduler Service**

See the `scheduler.py` script in the repository.

## Kubernetes Deployment

### 1. Create ConfigMap for Configuration

```bash
kubectl create configmap openalex-config \
  --from-file=config/config.json \
  --from-file=config/topics.json \
  -n dare
```

### 2. Create PersistentVolume and PersistentVolumeClaim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: harvester-data
  namespace: dare
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: harvester-logs
  namespace: dare
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
```

### 3. Create CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: openalex-harvester
  namespace: dare
spec:
  # Run daily at 2:00 AM UTC
  schedule: "0 2 * * *"
  
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: harvester
          
          containers:
          - name: harvester
            image: dare/openalex-harvester:1.0
            imagePullPolicy: IfNotPresent
            
            resources:
              requests:
                cpu: 100m
                memory: 256Mi
              limits:
                cpu: 1
                memory: 2Gi
            
            volumeMounts:
            - name: config
              mountPath: /config
              readOnly: true
            - name: data
              mountPath: /data
            - name: logs
              mountPath: /logs
            
            env:
            - name: CONFIG_PATH
              value: /config/config.json
            - name: TOPICS_PATH
              value: /config/topics.json
            - name: STATE_PATH
              value: /data/state.json
            - name: LOG_FILE
              value: /logs/harvest.log
          
          volumes:
          - name: config
            configMap:
              name: openalex-config
          - name: data
            persistentVolumeClaim:
              claimName: harvester-data
          - name: logs
            persistentVolumeClaim:
              claimName: harvester-logs
          
          restartPolicy: OnFailure
```

### 4. Deploy to Kubernetes

```bash
kubectl apply -f k8s/cronjob.yaml

# Verify deployment
kubectl get cronjobs -n dare
kubectl get pods -n dare

# View logs
kubectl logs -n dare -l job-name=openalex-harvester-<timestamp> -f
```

## Monitoring & Logging

### 1. Systemd Logging

```bash
# View recent logs
journalctl -u openalex-harvester -n 100

# Follow logs
journalctl -u openalex-harvester -f

# Logs for a specific date
journalctl -u openalex-harvester --since "2024-08-02 00:00:00"

# Export logs
journalctl -u openalex-harvester > harvester.log
```

### 2. Prometheus Monitoring

Add to Prometheus configuration:

```yaml
- job_name: 'openalex-harvester'
  metrics_path: '/metrics'
  static_configs:
    - targets: ['localhost:9090']
```

### 3. Log Aggregation (ELK Stack)

Filebeat configuration:

```yaml
filebeat.inputs:
- type: log
  paths:
    - /var/log/dare/harvester/harvest.log
  
  tags: ["dare", "openalex-harvester"]

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  
  indices:
    - index: "openalex-harvest-%{+yyyy.MM.dd}"
```

### 4. Alerts and Notifications

Set up alerts for:
- Service failures
- API errors
- High error rates
- Slow harvests

Example using AlertManager:

```yaml
groups:
- name: openalex-harvester
  rules:
  - alert: HarvesterServiceDown
    expr: up{job="openalex-harvester"} == 0
    for: 5m
    annotations:
      summary: "OpenAlex Harvester service is down"
  
  - alert: HighErrorRate
    expr: rate(harvester_errors_total[5m]) > 0.1
    for: 10m
    annotations:
      summary: "High error rate in OpenAlex Harvester"
```

## Troubleshooting

### Issue: Service fails to start

**Check service status:**
```bash
sudo systemctl status openalex-harvester.service
```

**View detailed errors:**
```bash
sudo journalctl -u openalex-harvester -n 50
```

### Issue: API connection timeout

**Increase timeout in config.json:**
```json
{
  "api_timeout": 60
}
```

**Check network connectivity:**
```bash
curl -v https://api.openalex.org/works?search=test&per-page=1
```

### Issue: DSpace import failures

**Verify DSpace API:**
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR-API-KEY" \
  https://dspace.dare.co.zw/server/api/discover/search
```

**Check API key permissions:**
- Must have collection creation rights
- Must have item creation rights
- Must have metadata editing rights

### Issue: Disk space errors

**Check disk usage:**
```bash
du -sh /var/log/dare/harvester/
du -sh /var/lib/dare/harvester/
```

**Clean old logs:**
```bash
sudo find /var/log/dare/harvester -name "*.log" -mtime +30 -delete
```

### Issue: Rate limiting errors

**Increase rate limit delay:**
```json
{
  "rate_limit_delay": 500
}
```

**Reduce per_page:**
```json
{
  "per_page": 25
}
```

## Performance Tuning

### Memory Usage

```bash
# Monitor memory
watch -n 1 'ps aux | grep openalex-harvester'

# Limit memory (systemd)
MemoryLimit=2G
```

### CPU Usage

```bash
# Limit CPU (systemd)
CPUQuota=50%
```

### Disk I/O

- Use SSD for better performance
- Enable compression for logs
- Implement log rotation

## Backup and Recovery

### Backup Configuration and State

```bash
tar -czf openalex-harvester-backup-$(date +%Y%m%d).tar.gz \
  /etc/dare/harvester \
  /var/lib/dare/harvester/state.json
```

### Restore from Backup

```bash
tar -xzf openalex-harvester-backup-20240802.tar.gz -C /
sudo chown -R dare:dare /etc/dare/harvester /var/lib/dare/harvester
sudo systemctl restart openalex-harvester.timer
```

## Uninstallation

### Remove Systemd Service

```bash
sudo systemctl stop openalex-harvester.timer
sudo systemctl disable openalex-harvester.timer
sudo rm /etc/systemd/system/openalex-harvester.*
sudo systemctl daemon-reload
```

### Remove Installed Files

```bash
sudo rm -rf /opt/dare/harvesters/openalex
sudo rm -rf /etc/dare/harvester
sudo rm -rf /var/lib/dare/harvester
sudo rm -rf /var/log/dare/harvester
```

### Remove System User

```bash
sudo userdel dare
```

## Support

For deployment issues, consult:
- [README.md](README.md) - Feature documentation
- [GitHub Issues](https://github.com/wgmasvix-hue/dare-digital-repository-/issues)
- OpenAlex Docs: https://docs.openalex.org
- DSpace REST API: https://wiki.lyrasis.org/display/DSPACE/REST+API
