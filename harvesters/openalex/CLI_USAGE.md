# OpenAlex Harvester - CLI Usage Guide

Complete guide to using the OpenAlex Harvester command-line interface.

## Quick Start

```bash
# Initialize configuration
./openalex-harvester -init-config

# Edit configuration
vi configs/config.yaml

# Run harvest
./openalex-harvester

# Test API connectivity
./openalex-harvester -test-api
```

## Command-Line Flags

### Configuration

#### `-config string`
Path to configuration file (default: `configs/config.yaml`)

```bash
./openalex-harvester -config /etc/harvester/config.yaml
```

#### `-init-config`
Initialize default configuration files and directory structure.

```bash
./openalex-harvester -init-config
```

Creates:
- `configs/config.yaml` - Main configuration file

### Testing & Diagnostics

#### `-test-api`
Test connectivity to the OpenAlex API.

```bash
./openalex-harvester -test-api
```

Output:
```
Testing OpenAlex API connectivity...
API URL: https://api.openalex.org
Email: harvester@dare.co.zw
✓ API is accessible and responsive
```

#### `-test-dspace`
Test connection to DSpace (if enabled).

```bash
./openalex-harvester -test-dspace
```

### Harvesting Options

#### `-topic string`
Harvest a specific topic only.

```bash
# Harvest single topic
./openalex-harvester -topic "artificial intelligence"

# Harvest specific topic with limit
./openalex-harvester -topic "machine learning" -limit 100
```

#### `-limit int`
Limit the number of results per topic (for testing).

```bash
# Harvest only 50 records per topic
./openalex-harvester -limit 50

# Harvest 10 records for testing
./openalex-harvester -topic "deep learning" -limit 10 -dry-run
```

Default: `0` (no limit)

### Export Options

#### `-export-json`
Export results as JSON only (default format).

```bash
./openalex-harvester -export-json
```

Output: `output/harvest.json`

#### `-export-csv`
Export results in CSV format.

```bash
./openalex-harvester -export-csv
```

Output: `output/harvest_20260802_145800.csv`

Columns:
- DOI
- Title
- Authors
- Year
- Journal
- URL
- OpenAccess
- Topics

#### `-export-dc`
Export results in Dublin Core XML format.

```bash
./openalex-harvester -export-dc
```

Output: `output/dc_*.xml` (one file per record)

### Import & Testing

#### `-import-dspace`
Import harvested records directly into DSpace.

Requires:
- DSpace enabled in `configs/config.yaml`
- Valid DSpace API credentials

```bash
./openalex-harvester -import-dspace
```

#### `-dry-run`
Run the harvest without saving or importing data.

```bash
# Test harvest without saving
./openalex-harvester -topic "robotics" -limit 10 -dry-run

# Test DSpace import without actually importing
./openalex-harvester -import-dspace -dry-run
```

## Usage Examples

### Example 1: Full Harvest (All Topics)

```bash
./openalex-harvester
```

- Harvests all configured topics from `config.yaml`
- Uses incremental mode (only new records)
- Exports to JSON
- Saves to `output/harvest.json`

### Example 2: Harvest Single Topic with Limit

```bash
./openalex-harvester -topic "machine learning" -limit 100
```

- Harvests only "machine learning" topic
- Limits results to 100 records
- Useful for testing and development

### Example 3: Export in Multiple Formats

```bash
# Export as JSON
./openalex-harvester -topic "climate change" -export-json

# Export as CSV
./openalex-harvester -topic "climate change" -export-csv

# Export as Dublin Core XML
./openalex-harvester -topic "climate change" -export-dc
```

### Example 4: Dry Run Before Import

```bash
# Test configuration without saving
./openalex-harvester -topic "food science" -limit 5 -dry-run

# If successful, run actual harvest and import
./openalex-harvester -topic "food science" -import-dspace
```

### Example 5: Development Workflow

```bash
# 1. Initialize configuration
./openalex-harvester -init-config

# 2. Test API connectivity
./openalex-harvester -test-api

# 3. Test with small limit
./openalex-harvester -topic "artificial intelligence" -limit 10 -dry-run

# 4. Review output
cat output/harvest.json | head -50

# 5. Full harvest if satisfied
./openalex-harvester -topic "artificial intelligence"
```

### Example 6: DSpace Integration

```bash
# 1. Enable DSpace in config
vi configs/config.yaml
# Set: dspace.enabled: true
# Set: dspace.url: https://dspace.dare.co.zw/server
# Set: dspace.api_key: YOUR_API_KEY

# 2. Test DSpace connection
./openalex-harvester -test-dspace

# 3. Dry run import
./openalex-harvester -import-dspace -dry-run

# 4. Import records
./openalex-harvester -import-dspace
```

## Configuration File

The configuration file (`configs/config.yaml`) controls harvester behavior:

```yaml
openalex:
  email: harvester@dare.co.zw          # Required for OpenAlex API
  base_url: https://api.openalex.org   # API endpoint
  per_page: 100                        # Results per request (1-200)
  max_requests: 1000                   # Max API requests per session
  rate_limit_delay: 100                # Milliseconds between requests
  request_timeout: 30                  # Request timeout in seconds
  min_publication_year: 2020           # Filter by year
  max_publication_year: 2024

dspace:
  url: https://dspace.dare.co.zw/server
  username: admin@example.com
  api_key: YOUR_API_KEY
  enabled: false                       # Set to true to enable import

output:
  directory: ./output                  # Where to save results
  format: json                         # json, csv, or dublin_core
  pretty: true                         # Pretty-print JSON

features:
  enable_incremental: true             # Only harvest new records
  enable_deduplication: true           # Skip duplicate DOIs
  enable_orcid_matching: true          # Match ORCID IDs
  enable_vector_indexing: false        # Generate embeddings

topics:
  - artificial intelligence
  - machine learning
  - deep learning
  - computer vision
  - natural language processing
  - robotics
  - food science
  - agriculture
  - climate change
```

## Output Directory Structure

```
output/
├── harvest.json                    # JSON export
├── harvest_20260802_145800.csv    # CSV export (if enabled)
└── dc_*.xml                        # Dublin Core XMLs (if enabled)
```

## Troubleshooting

### Issue: "Configuration file not found"

```bash
./openalex-harvester -init-config
```

### Issue: "API returned status 403"

- Check network connectivity
- Verify email in `configs/config.yaml`
- Check if OpenAlex API is accessible

### Issue: "No topics configured"

Edit `configs/config.yaml` and add topics:

```yaml
topics:
  - your-topic-here
```

### Issue: "DSpace connection failed"

```bash
# 1. Verify DSpace is running
curl https://dspace.dare.co.zw/server/api/

# 2. Check credentials in config
vi configs/config.yaml

# 3. Test connection
./openalex-harvester -test-dspace
```

## Environment Variables

Override configuration with environment variables:

```bash
# Override output directory
export OUTPUT_DIR=/tmp/harvester-output
./openalex-harvester

# Override config file
export CONFIG_PATH=/etc/harvester/config.yaml
./openalex-harvester
```

## Batch Processing

Process multiple topics sequentially:

```bash
#!/bin/bash
for topic in "AI" "ML" "LLM" "CV" "NLP"; do
  echo "Harvesting $topic..."
  ./openalex-harvester -topic "$topic" -limit 100
  sleep 5  # Rate limiting
done
```

## Scripting

Integrate into automation:

```bash
#!/bin/bash

# Daily harvest
0 2 * * * /opt/harvester/openalex-harvester -config /etc/harvester/config.yaml

# Weekly full harvest
0 3 * * 0 /opt/harvester/openalex-harvester -full -import-dspace

# Test on startup
@reboot /opt/harvester/openalex-harvester -test-api
```

## Performance Tips

1. **Use `-limit` for testing** before full harvest
2. **Enable `-dry-run`** to verify configuration
3. **Adjust `-rate-limit-delay`** if getting rate-limited
4. **Use specific `-topic`** instead of harvesting all topics at once
5. **Monitor output files** during long harvests

## Getting Help

```bash
./openalex-harvester -h
```

For more information, see:
- [README.md](README.md) - Feature documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [configs/config.yaml](configs/config.yaml) - Configuration reference
