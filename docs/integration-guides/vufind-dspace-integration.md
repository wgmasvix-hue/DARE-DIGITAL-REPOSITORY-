# VuFind-DSpace Integration Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [OAI-PMH Configuration](#oai-pmh-configuration)
5. [VuFind Setup](#vufind-setup)
6. [Solr Indexing](#solr-indexing)
7. [Metadata Mapping](#metadata-mapping)
8. [Authentication](#authentication)
9. [Deployment](#deployment)
10. [Testing & Troubleshooting](#testing--troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Users/Browsers                        │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │       VuFind Discovery Layer   │
        │  (Search Interface & UI)       │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Solr Search Index             │
        │  (Indexed DSpace Content)      │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  OAI-PMH Harvester            │
        │  (Syncs metadata from DSpace) │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  DSpace Repository             │
        │  (repo.dare.co.zw)            │
        └────────────────────────────────┘
```

### Data Flow
1. **DSpace** stores digital objects and metadata
2. **OAI-PMH Harvester** (in VuFind) periodically harvests metadata from DSpace
3. **Solr** indexes the harvested metadata for fast searching
4. **VuFind** queries Solr to display search results to users
5. **Deep Links** point back to DSpace for full item access

---

## Prerequisites

### System Requirements
- **VuFind**: 8.0+ (recommends 9.0+)
- **DSpace**: 6.0+ (supports up to 7.x)
- **Solr**: 8.0+ (bundled with VuFind)
- **PHP**: 7.4+
- **Java**: 11+
- **Linux Server**: Ubuntu 20.04+ or similar

### Disk Space
- VuFind: ~2-3 GB
- Solr Index: Depends on content volume (estimate 1.5x raw data size)
- DSpace: Existing deployment

### Network Access
- VuFind server must access DSpace's OAI-PMH endpoint
- DSpace must be accessible at `http://repo.dare.co.zw` or IP address

---

## Installation

### Option 1: Docker Compose (Recommended for DARE)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # DSpace (already running at repo.dare.co.zw)
  # Assuming DSpace is already deployed

  # Solr for VuFind
  solr:
    image: solr:8.11
    container_name: dare-solr
    ports:
      - "8983:8983"
    environment:
      - SOLR_HEAP=2g
    volumes:
      - solr-data:/var/solr
    networks:
      - dare-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8983/solr/"]
      interval: 10s
      timeout: 5s
      retries: 5

  # VuFind
  vufind:
    image: vufind/vufind:9.0
    container_name: dare-vufind
    ports:
      - "8080:80"
    environment:
      - VUFIND_URL=http://vufind.dare.co.zw
      - VUFIND_CONFIG_PATH=/usr/local/vufind/config
      - SOLR_HOSTNAME=solr
      - SOLR_PORT=8983
    volumes:
      - ./config/vufind:/usr/local/vufind/local
      - vufind-data:/usr/local/vufind/harvest
    depends_on:
      solr:
        condition: service_healthy
    networks:
      - dare-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/index.php/"]
      interval: 15s
      timeout: 5s
      retries: 5

volumes:
  solr-data:
  vufind-data:

networks:
  dare-network:
    driver: bridge
```

### Option 2: Traditional Installation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y php php-cli php-curl php-dom php-gd \
  php-json php-mbstring php-mysql php-xml php-zip \
  openjdk-11-jre-headless git curl wget

# Download VuFind
cd /opt
sudo wget https://github.com/vufind-org/vufind/releases/download/v9.0/vufind-9.0.tar.gz
sudo tar xzf vufind-9.0.tar.gz
sudo ln -s vufind-9.0 vufind

# Setup VuFind
cd /opt/vufind
sudo ./install.sh
```

---

## OAI-PMH Configuration

### 1. Enable OAI-PMH in DSpace

Edit DSpace configuration: `dspace.cfg`

```properties
# Enable OAI-PMH
oai.url = http://repo.dare.co.zw/oai/request

# OAI-PMH settings
oai.implClassname = org.dspace.app.oai.OAIManager
oai.request.log = true

# Set crosswalk for Dublin Core
oai.metadataformats.dc.namespace = http://purl.org/dc/elements/1.1/
oai.metadataformats.dc.schemaLocation = http://purl.org/dc/xml/simpledc_schema.xsd
```

### 2. Verify OAI-PMH Endpoint

Test the OAI-PMH endpoint:

```bash
# List available metadata formats
curl "http://repo.dare.co.zw/oai/request?verb=ListMetadataFormats"

# List sets (collections)
curl "http://repo.dare.co.zw/oai/request?verb=ListSets"

# Harvest records
curl "http://repo.dare.co.zw/oai/request?verb=ListRecords&metadataPrefix=oai_dc"
```

---

## VuFind Setup

### 1. Create VuFind Local Config Directory

```bash
mkdir -p /usr/local/vufind/local
cp -r /usr/local/vufind/config/* /usr/local/vufind/local/
```

### 2. Configure OAI Harvester (`config/vufind/oai.ini`)

```ini
; OAI-PMH Harvester Configuration for DSpace

[General]
; Base URL for harvesting
url = http://repo.dare.co.zw/oai/request
; Set name to harvest (use 'all' for all sets)
set = 
; Metadata format to harvest
metadataPrefix = oai_dc
; Resumption token (for resuming interrupted harvests)
resumptionToken = 

[DSpace]
; OAI URL for DSpace instance
repository = http://repo.dare.co.zw
; Repository name
name = DARE DSpace Repository
; Namespace prefix
prefix = oai_dspace

[Harvesting]
; How often to re-harvest (in seconds)
; 604800 = weekly, 2592000 = monthly
interval = 604800
; Max records to harvest per run
batchSize = 100
; Enable incremental harvesting (only new/modified records)
incremental = true
```

### 3. Configure Search (`config/vufind/config.ini`)

Add to `[Index]` section:

```ini
[Index]
engine = Solr
url = http://solr:8983/solr/biblio
; Use Solr 8+
version = 8

[OAI]
; Enable OAI harvesting
enabled = true
; Index OAI records
indexing = true
```

### 4. Configure Search Results Display

Edit `config/vufind/searches.ini`:

```ini
[General]
; Default search type
default_type = AllFields

[Basic]
; Basic search fields
AllFields = adv_search_basic
Title = title
Author = author_display
Subject = subject
ISBN = isbn

[Advanced]
; Advanced search operators
Title_sub = title
Creator_sub = creator
Subject_sub = subject
Publisher_sub = publisher
Date_sub = date
```

---

## Solr Indexing

### 1. Configure Solr Core for VuFind

```bash
# Create Solr core
cd /opt/solr
./bin/solr create_core -c biblio -d /opt/vufind/solr/biblio

# Copy VuFind schema
cp /opt/vufind/solr/biblio/conf/schema.xml \
   /opt/solr/solr/biblio/conf/

# Restart Solr
./bin/solr restart
```

### 2. Create Solr Core Configuration (`solr/biblio/conf/solrconfig.xml`)

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<config>
  <luceneMatchVersion>8.0.0</luceneMatchVersion>
  
  <!-- Data directory -->
  <dataDir>${solr.data.home:}</dataDir>
  
  <!-- Request handlers -->
  <requestHandler name="/select" class="solr.SearchHandler">
    <lst name="defaults">
      <str name="echoParams">explicit</str>
      <int name="rows">20</int>
      <str name="df">text</str>
    </lst>
  </requestHandler>
  
  <!-- Update handler for indexing -->
  <requestHandler name="/update" class="solr.UpdateRequestHandler" />
  
  <!-- Query response writer -->
  <queryResponseWriter name="json" class="solr.JSONResponseWriter" />
</config>
```

### 3. Index DSpace Records

```bash
# Run VuFind harvest and index
cd /opt/vufind
php harvest_oai.php --skip-checks --from-date="2024-01-01"

# Monitor indexing progress
tail -f harvest_oai.log
```

---

## Metadata Mapping

### Map DSpace Dublin Core to VuFind Fields

Create `local/harvest/oai/oaiDublinCore.php`:

```php
<?php
/**
 * OAI Mapper for Dublin Core to VuFind fields
 */

// Map Dublin Core fields to Solr fields
$mappings = [
    'dc:title' => 'title',
    'dc:creator' => 'author_display',
    'dc:subject' => 'subject',
    'dc:description' => 'description',
    'dc:publisher' => 'publisher',
    'dc:date' => 'date',
    'dc:type' => 'resourcetype',
    'dc:format' => 'format',
    'dc:identifier' => 'id',
    'dc:language' => 'language',
    'dc:rights' => 'rights',
    'dc:coverage' => 'coverage',
    'dc:relation' => 'related_records_id',
    'dc:source' => 'source',
];

return $mappings;
```

### Custom Field Mapping for DARE

Create `local/harvest/oai/dareDublinCore.php`:

```php
<?php
/**
 * DARE-specific metadata mapping
 */

return [
    // Basic fields
    'title' => ['dc:title'],
    'author_display' => ['dc:creator'],
    'subject' => ['dc:subject'],
    'description' => ['dc:description'],
    'publisher' => ['dc:publisher'],
    'publishDate' => ['dc:issued', 'dc:date'],
    
    // DARE-specific fields
    'institution' => ['dc:source', 'dspace:institution'],
    'collection' => ['dc:coverage'],
    'handle' => ['dc:identifier'],  // DSpace Handle ID
    'orcid' => ['dc:creator.orcid'],  // If ORCID in metadata
    
    // Rights and licensing
    'rights' => ['dc:rights'],
    'access_restriction' => ['dc:accessRights'],
    
    // Content type
    'content_type' => ['dc:type'],
    'format' => ['dc:format'],
    'language' => ['dc:language'],
];
```

---

## Authentication

### Enable ORCID Authentication in VuFind

Edit `config/vufind/Authentication.php`:

```php
<?php
/**
 * ORCID Authentication Configuration
 */

return [
    'ORCID' => [
        'enabled' => true,
        'client_id' => 'YOUR_ORCID_CLIENT_ID',
        'client_secret' => 'YOUR_ORCID_CLIENT_SECRET',
        'redirect_uri' => 'http://vufind.dare.co.zw/Auth/ORCID/Callback',
        'api_url' => 'https://pub.orcid.org',
        // For sandbox: 'https://sandbox.orcid.org'
    ],
    
    'DSpace' => [
        'enabled' => true,
        'url' => 'http://repo.dare.co.zw',
        'rest_api' => 'http://repo.dare.co.zw/rest',
    ],
];
```

### Link ORCID to DSpace User Profiles

Create bridge script: `local/orcid-bridge.php`

```php
<?php
/**
 * Link ORCID profiles to DSpace user accounts
 */

class OrcidBridge {
    private $dspaceUrl;
    
    public function __construct($dspaceUrl) {
        $this->dspaceUrl = $dspaceUrl;
    }
    
    public function linkOrcid($email, $orcidId) {
        // Send to DSpace REST API
        $endpoint = $this->dspaceUrl . '/rest/users/' . urlencode($email);
        
        $data = [
            'metadata' => [
                [
                    'key' => 'dc.identifier.orcid',
                    'value' => $orcidId
                ]
            ]
        ];
        
        return $this->makeRequest('PUT', $endpoint, $data);
    }
    
    private function makeRequest($method, $url, $data = null) {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        }
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
}
```

---

## Deployment

### 1. Set Up Cron Jobs

Edit `/etc/cron.d/vufind-dare`:

```bash
# Harvest OAI records daily at 2 AM
0 2 * * * root cd /opt/vufind && php harvest_oai.php --skip-checks >> /var/log/vufind-harvest.log 2>&1

# Optimize Solr index weekly
0 3 * * 0 root curl "http://localhost:8983/solr/biblio/update?optimize=true"

# Clean up logs weekly
0 4 * * 0 root find /opt/vufind/logs -name "*.log" -mtime +30 -delete
```

### 2. Configure Web Server (Nginx)

Create `/etc/nginx/sites-available/vufind.dare.co.zw`:

```nginx
server {
    listen 80;
    server_name vufind.dare.co.zw;
    root /opt/vufind/public;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vufind.dare.co.zw;
    root /opt/vufind/public;
    
    ssl_certificate /etc/letsencrypt/live/vufind.dare.co.zw/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vufind.dare.co.zw/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # VuFind rewrite rules
    location / {
        try_files $uri $uri/ @rewrite;
    }
    
    location @rewrite {
        rewrite ^/(.*)$ /index.php?url=$1 last;
    }
    
    location ~ \.php$ {
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
    
    # Solr proxy (optional, for direct API access)
    location /solr/ {
        proxy_pass http://localhost:8983/solr/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/vufind.dare.co.zw \
           /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL Certificate

```bash
# Use Let's Encrypt
sudo certbot certonly --nginx -d vufind.dare.co.zw

# Setup auto-renewal
sudo systemctl enable certbot.timer
```

---

## Testing & Troubleshooting

### 1. Test OAI-PMH Connection

```bash
# Check DSpace OAI endpoint
curl -v "http://repo.dare.co.zw/oai/request?verb=Identify"

# Check if OAI returns records
curl "http://repo.dare.co.zw/oai/request?verb=ListRecords&metadataPrefix=oai_dc&from=2024-01-01" | head -50
```

### 2. Test Solr Indexing

```bash
# Check if Solr is running
curl http://localhost:8983/solr/admin/cores

# Count indexed documents
curl "http://localhost:8983/solr/biblio/select?q=*:*&rows=0"

# Search for specific field
curl "http://localhost:8983/solr/biblio/select?q=title:test"
```

### 3. Test VuFind

```bash
# Check VuFind status
curl http://localhost:8080/index.php/

# Check harvester logs
tail -f /opt/vufind/logs/harvest_oai.log

# Test search
curl "http://localhost:8080/index.php/Search/Results?lookfor=test"
```

### 4. Common Issues

**Issue**: Harvester times out
```
Solution: Increase timeout in harvest_oai.php
ini_set('default_socket_timeout', 300);
```

**Issue**: Solr index not updating
```
Solution: Restart Solr and clear cache
curl "http://localhost:8983/solr/biblio/update?commit=true"
```

**Issue**: ORCID authentication not working
```
Solution: Verify client ID and secret in config
Check firewall allows outbound to orcid.org
```

### 5. Monitor Harvesting

Create monitoring script: `scripts/check-harvest-status.sh`

```bash
#!/bin/bash

# Check harvest status
LAST_HARVEST=$(stat -c %y /opt/vufind/logs/harvest_oai.log)
DOC_COUNT=$(curl -s "http://localhost:8983/solr/biblio/select?q=*:*&rows=0" | grep -o '"numFound":[0-9]*' | cut -d: -f2)

echo "Last Harvest: $LAST_HARVEST"
echo "Documents Indexed: $DOC_COUNT"

# Alert if harvest is stale (>24 hours)
LAST_MODIFIED=$(stat -c %Y /opt/vufind/logs/harvest_oai.log)
CURRENT_TIME=$(date +%s)
DIFF=$((CURRENT_TIME - LAST_MODIFIED))

if [ $DIFF -gt 86400 ]; then
    echo "⚠️  WARNING: Harvest stale ($(($DIFF / 3600)) hours old)"
fi
```

---

## Next Steps

1. ✅ Prepare DSpace OAI-PMH endpoint
2. ✅ Install and configure VuFind
3. ✅ Set up Solr indexing
4. ✅ Map metadata fields
5. ✅ Configure authentication (ORCID)
6. ✅ Deploy and secure with SSL
7. ✅ Set up automated harvesting
8. ✅ Configure analytics (Matomo)
9. ✅ Add AI features (ChengetAi integration)

---

## Resources

- [VuFind Documentation](https://vufind.org/wiki/start)
- [DSpace OAI-PMH Guide](https://wiki.lyrasis.org/display/DSPACE/OAI-PMH)
- [Solr Documentation](https://solr.apache.org/guide/)
- [ORCID Integration Guide](https://github.com/ORCID/orcid-integration-examples)
