# DSpace Gutenberg Ingest Guide

Complete guide for ingesting Project Gutenberg books into your DSpace instance at repo.dare.co.zw.

## Quick Start

### Step 1: Get Authentication Token

```bash
# Login to DSpace and get authentication token
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{
    "user": "admin@example.com",
    "password": "your_password"
  }' \
  -c cookies.txt

# Extract token from response (look for "token" in JSON response)
# Or extract from cookies
grep "DSPACE-XSRF-TOKEN" cookies.txt
```

### Step 2: Create Gutenberg Collection (Optional)

If you don't already have a Gutenberg collection, create one:

```bash
# Use DSpace Admin UI or API
curl -X POST https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Gutenberg",
    "metadata": {
      "dc.description": ["70,000+ public domain books from Project Gutenberg"],
      "dc.title": ["Project Gutenberg Books"]
    }
  }'
```

Note the returned `handle` (e.g., `123456789/10`)

### Step 3: Ingest Gutenberg Books

```bash
# Make the script executable
chmod +x deploy/dspace_gutenberg_ingest.py

# Ingest from JSON
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token YOUR_AUTH_TOKEN \
  --collection 123456789/10 \
  --json gutenberg_data/gutenberg_books_latest.json

# Or ingest from CSV
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token YOUR_AUTH_TOKEN \
  --collection 123456789/10 \
  --csv gutenberg_data/gutenberg_books_latest.csv
```

---

## Detailed Steps

### 1. Authentication

#### Option A: Using REST API

```bash
# Send login request
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{
    "user": "admin@example.com",
    "password": "admin_password"
  }' | jq .

# Example response:
# {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "name": "Administrator"
# }

# Save the token for later use
export DSPACE_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Option B: Using Web Interface

1. Go to https://repo.dare.co.zw/admin/access-control
2. Login with admin credentials
3. Generate or copy your API token from settings

### 2. Collection Setup

#### Option A: Using REST API

```bash
# Create collection via API
curl -X POST https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Gutenberg",
    "metadata": {
      "dc.title": ["Project Gutenberg Books"],
      "dc.description": ["Digital collection of 70,000+ public domain books"],
      "dc.rights": ["Public Domain"]
    }
  }' | jq .

# Save the handle from response (usually looks like: 123456789/10)
export COLLECTION_HANDLE="123456789/10"
```

#### Option B: Using Web Interface

1. Go to https://repo.dare.co.zw/admin/workspace
2. Click "Create Collection"
3. Fill in metadata:
   - Name: Project Gutenberg
   - Description: 70,000+ public domain books from Project Gutenberg
4. Note the collection handle

#### Option C: Using Existing Collection

If you already have a collection for Gutenberg:

```bash
# Find collection handle
curl -s https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '.[] | select(.name | contains("Gutenberg")) | .handle'

# Save the handle
export COLLECTION_HANDLE="123456789/10"
```

### 3. Ingest Books

#### Prepare Data Files

Ensure you have the Gutenberg data files:

```bash
ls -lah gutenberg_data/
# Should show:
# - gutenberg_books_latest.json (or .csv)
# - gutenberg_books_sample.json (for testing)
```

#### Test Ingest (Recommended)

Test with sample data first:

```bash
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token $DSPACE_TOKEN \
  --collection $COLLECTION_HANDLE \
  --json gutenberg_data/gutenberg_books_sample.json
```

#### Full Ingest

After testing, ingest all books:

```bash
# Progress will be shown as books are ingested
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token $DSPACE_TOKEN \
  --collection $COLLECTION_HANDLE \
  --json gutenberg_data/gutenberg_books_latest.json

# Or from CSV
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token $DSPACE_TOKEN \
  --collection $COLLECTION_HANDLE \
  --csv gutenberg_data/gutenberg_books_latest.csv
```

---

## Ingest Script Details

### Script: `dspace_gutenberg_ingest.py`

**What it does:**
1. Reads Gutenberg books from JSON or CSV
2. Maps Gutenberg metadata to Dublin Core
3. Creates items in your DSpace collection
4. Reports success/failure rate

**Metadata Mapping:**

| Gutenberg Field | Dublin Core Field |
|-----------------|-------------------|
| id | gutenberg.id |
| title | dc.title |
| authors | dc.creator |
| languages | dc.language |
| subjects | dc.subject |
| url | dc.identifier.uri |
| publication_date | dc.date.issued |
| download_count | gutenberg.downloads |
| cover_image | dc.relation.isPartOf |
| (implicit) | dc.rights: Public Domain |
| (implicit) | dc.type: Book |

### Usage Examples

#### Ingest from JSON with custom path

```bash
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... \
  --collection 123456789/10 \
  --json /path/to/custom/books.json
```

#### Ingest from CSV with environment variables

```bash
export DSPACE_URL="https://repo.dare.co.zw"
export DSPACE_TOKEN="your_token_here"
export COLLECTION_HANDLE="123456789/10"

python3 deploy/dspace_gutenberg_ingest.py \
  --url $DSPACE_URL \
  --token $DSPACE_TOKEN \
  --collection $COLLECTION_HANDLE \
  --csv gutenberg_data/gutenberg_books_latest.csv
```

---

## Monitoring Ingest

### Real-time Progress

The script displays progress as it ingests:

```
[1/18] Ingesting 'The United States Bill of Rights'... ✓ 123456789/1
[2/18] Ingesting 'Alice's Adventures in Wonderland'... ✓ 123456789/2
[3/18] Ingesting 'Frankenstein'... ✓ 123456789/3
...
============================================================
Ingest Summary
============================================================
Successful: 18
Failed: 0
Total: 18
Success rate: 100.0%
============================================================
```

### Check DSpace Web UI

After ingest:

1. Go to https://repo.dare.co.zw/
2. Search for "Gutenberg" or book titles
3. Browse collection: Project Gutenberg
4. Verify metadata in item details

### DSpace Admin Monitor

```bash
# Check collection item count
curl -s https://repo.dare.co.zw/server/api/core/collections/123456789/10 \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '.items, .itemsCount'

# List recently added items
curl -s 'https://repo.dare.co.zw/server/api/core/items?page=0&size=10&sort=dc.date.accessioned,desc' \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '.[] | {handle, title: .metadata."dc.title"[0]}'
```

---

## Troubleshooting

### "Authentication failed"

**Problem**: Invalid token or expired session  
**Solution**:
```bash
# Get a fresh token
curl -X POST https://repo.dare.co.zw/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin@example.com","password":"password"}'
```

### "Collection not found"

**Problem**: Invalid collection handle  
**Solution**:
```bash
# List all collections
curl -s https://repo.dare.co.zw/server/api/core/collections \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '.[] | {name, handle}'

# Use correct handle in ingest command
```

### "File not found"

**Problem**: Path to JSON/CSV file is incorrect  
**Solution**:
```bash
# Check file exists
ls -la gutenberg_data/gutenberg_books_latest.json

# Use full path if needed
python3 deploy/dspace_gutenberg_ingest.py \
  --url https://repo.dare.co.zw \
  --token $DSPACE_TOKEN \
  --collection $COLLECTION_HANDLE \
  --json /home/user/DARE-DIGITAL-REPOSITORY-/gutenberg_data/gutenberg_books_latest.json
```

### "Connection refused"

**Problem**: DSpace server is down or unreachable  
**Solution**:
```bash
# Test connection
curl -I https://repo.dare.co.zw/

# Check DSpace status
curl https://repo.dare.co.zw/server/api/system/info

# Verify network/firewall
ping repo.dare.co.zw
```

### Slow ingest speed

**Problem**: Ingesting is taking a long time  
**Solution**:
- Normal: ~0.5-1 item per second (rate limited by script)
- For 18 books: ~30 seconds to 1 minute
- For full dataset: ~10-15 hours

To speed up (not recommended for production):
```python
# Edit dspace_gutenberg_ingest.py, change sleep time
time.sleep(0.1)  # Reduce from 0.5 (use with caution)
```

---

## Post-Ingest

### Index Rebuild

After ingesting many items, rebuild the search index:

```bash
# Via DSpace CLI (on server)
/dspace/bin/dspace index-discovery -b

# Or via REST API
curl -X POST https://repo.dare.co.zw/server/api/core/items/search/reindex \
  -H "Authorization: Bearer $DSPACE_TOKEN"
```

### Verify in Search

```bash
# Search for Gutenberg books
curl -s 'https://repo.dare.co.zw/server/api/discover/search?query=gutenberg' \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '.results | length'

# Should show your ingested count
```

### Generate Statistics

```bash
# Count books by language
curl -s 'https://repo.dare.co.zw/server/api/discover/search?query=collection:PROJECT_GUTENBERG' \
  -H "Authorization: Bearer $DSPACE_TOKEN" \
  | jq '[.results[] | .metadata."dc.language"[]] | group_by(.) | map({language: .[0], count: length})'
```

---

## Automated Ingest Schedule

### Daily Ingest (Cron)

```bash
# Create script: /opt/dspace/scripts/ingest_gutenberg_daily.sh
#!/bin/bash

# Configuration
DSPACE_URL="https://repo.dare.co.zw"
DSPACE_USER="admin@example.com"
DSPACE_PASS="password"
COLLECTION_HANDLE="123456789/10"
DATA_FILE="/home/dspace/gutenberg_books_latest.json"

# Get fresh token
TOKEN=$(curl -s -X POST $DSPACE_URL/server/api/authn/login \
  -H "Content-Type: application/json" \
  -d "{\"user\":\"$DSPACE_USER\",\"password\":\"$DSPACE_PASS\"}" \
  | jq -r '.token')

# Ingest
python3 /opt/dspace/scripts/dspace_gutenberg_ingest.py \
  --url $DSPACE_URL \
  --token $TOKEN \
  --collection $COLLECTION_HANDLE \
  --json $DATA_FILE \
  >> /var/log/dspace/gutenberg_ingest.log 2>&1

# Make executable
chmod +x /opt/dspace/scripts/ingest_gutenberg_daily.sh

# Add to crontab (runs daily at 3 AM)
# 0 3 * * * /opt/dspace/scripts/ingest_gutenberg_daily.sh
```

---

## Support & Resources

- **DSpace REST API**: https://wiki.lyrasis.org/display/DSPACE/REST+API
- **DSpace Documentation**: https://wiki.lyrasis.org/display/DSPACE
- **Gutenberg Dataset**: See `GUTENBERG_DATASET.md`
- **Repository**: https://github.com/wgmasvix-hue/dare-digital-repository-

---

**Last Updated**: August 2, 2026  
**Version**: 1.0  
**Server**: repo.dare.co.zw
