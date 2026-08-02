# OpenAlex Harvester for DARE

A powerful, production-ready harvester for integrating [OpenAlex](https://openalex.org) scholarly metadata into the DARE Digital Repository powered by DSpace 9.

## Features

✨ **Core Capabilities:**
- Query OpenAlex API for scholarly works across multiple topics
- Download and convert metadata to Dublin Core format
- Automatic import into DSpace 9
- Support for 10+ research domains
- Incremental harvesting (sync only new papers)
- DOI-based deduplication
- ORCID author matching
- Open Access filtering

✅ **Advanced Features:**
- Configurable search topics with per-topic filters
- Rate limiting and resilience
- State persistence for incremental harvests
- Comprehensive error handling and logging
- Vector indexing support for RAG systems
- Automatic duplicate detection
- Batch processing with progress tracking

## Installation

### Prerequisites
- Go 1.21 or later
- Access to OpenAlex API (free, no authentication required)
- DSpace 9 instance with API access

### Build

```bash
cd harvesters/openalex
go mod download
go build -o openalex-harvester .
```

## Quick Start

### 1. Initialize Configuration

```bash
./openalex-harvester -init-config
```

This creates default configuration files in `~/.dare/harvester/`:
- `config.json` - General harvester settings
- `topics.json` - Search topics with filters

### 2. Test API Connectivity

```bash
./openalex-harvester -test-api
```

Output:
```
Testing OpenAlex API connectivity...
✓ API is accessible
✓ Found 10 results for 'artificial intelligence'
✓ Sample result:
  Title: Sample Paper Title
  Year: 2024
  DOI: 10.xxxx/xxxxx
  Authors: 5
```

### 3. Run Full Harvest

```bash
./openalex-harvester -full
```

### 4. Run Incremental Harvest (Default)

```bash
./openalex-harvester
```

Only harvests works published since the last sync for each topic.

## Configuration

### config.json

```json
{
  "base_url": "https://api.openalex.org",
  "per_page": 50,
  "max_requests": 1000,
  "rate_limit_delay": 100,
  "dspace_url": "https://dspace.dare.co.zw",
  "dspace_api_key": "your-api-key",
  "enable_incremental": true,
  "enable_deduplication": true,
  "enable_orcid_matching": true,
  "enable_vector_indexing": true,
  "topics": []
}
```

**Settings:**
- `base_url`: OpenAlex API endpoint (don't change unless using proxy)
- `per_page`: Results per API request (1-200, default 50)
- `max_requests`: Maximum API requests per topic
- `rate_limit_delay`: Milliseconds between requests (default 100ms)
- `dspace_url`: Your DSpace instance URL
- `dspace_api_key`: DSpace REST API key
- `enable_incremental`: Enable incremental harvesting
- `enable_deduplication`: Skip duplicate works (by DOI)
- `enable_orcid_matching`: Match and link ORCID identifiers
- `enable_vector_indexing`: Create vector embeddings for RAG

### topics.json

```json
[
  {
    "name": "Artificial Intelligence",
    "query": "artificial intelligence",
    "filters": {
      "min_publication_year": 2020,
      "max_publication_year": 2024,
      "has_doi": false,
      "open_access_only": false,
      "country_code": ""
    },
    "enabled": true,
    "last_sync": "2024-01-01T00:00:00Z",
    "record_count": 0
  }
]
```

**Supported Topics:**
- Artificial Intelligence
- Machine Learning
- Large Language Models
- Deep Learning
- Computer Vision
- Natural Language Processing
- Robotics
- Food Science
- Agriculture
- Climate Change

**Filters:**
- `min_publication_year`: Only works from this year onwards
- `max_publication_year`: Only works up to this year
- `has_doi`: Require DOI identifier
- `open_access_only`: Only open access works
- `country_code`: Filter by institution country (ISO 3166-1 alpha-2)

## Usage

### Command-line Options

```bash
Usage:
  openalex-harvester [options]

Options:
  -config string
        Path to configuration file (default "config.json")
  -topics string
        Path to topics configuration file (default "topics.json")
  -state string
        Path to harvester state file (default "state.json")
  -init-config
        Initialize default configuration files
  -full
        Perform full harvest instead of incremental
  -topic string
        Harvest specific topic only
  -test-api
        Test OpenAlex API connectivity
```

### Examples

#### Harvest all topics (incremental)
```bash
./openalex-harvester
```

#### Full harvest of all topics
```bash
./openalex-harvester -full
```

#### Harvest specific topic
```bash
./openalex-harvester -topic "Machine Learning"
```

#### Full harvest of specific topic
```bash
./openalex-harvester -full -topic "Artificial Intelligence"
```

#### Use custom configuration
```bash
./openalex-harvester -config /path/to/custom-config.json -topics /path/to/custom-topics.json
```

## Scheduling

### Systemd Timer (Linux)

Create `/etc/systemd/system/openalex-harvester.service`:

```ini
[Unit]
Description=DARE OpenAlex Harvester
After=network.target

[Service]
Type=oneshot
User=dare
WorkingDirectory=/opt/harvester
ExecStart=/opt/harvester/openalex-harvester
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/openalex-harvester.timer`:

```ini
[Unit]
Description=Run DARE OpenAlex Harvester daily

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable openalex-harvester.timer
sudo systemctl start openalex-harvester.timer
sudo systemctl status openalex-harvester.timer
```

Check logs:

```bash
sudo journalctl -u openalex-harvester -f
```

### Cron (Unix/Linux)

Add to crontab:

```bash
# Run daily at 2 AM
0 2 * * * /opt/harvester/openalex-harvester >> /var/log/openalex-harvest.log 2>&1
```

### Docker

```dockerfile
FROM golang:1.21-alpine

WORKDIR /app
COPY . .

RUN go build -o openalex-harvester .

ENV CONFIG_PATH=/config/config.json
ENV TOPICS_PATH=/config/topics.json
ENV STATE_PATH=/data/state.json

VOLUME ["/config", "/data"]

CMD ["./openalex-harvester", "-config", "$CONFIG_PATH", "-topics", "$TOPICS_PATH", "-state", "$STATE_PATH"]
```

Build and run:

```bash
docker build -t openalex-harvester .
docker run -v /path/to/config:/config -v /path/to/data:/data openalex-harvester
```

## Data Flow

```
OpenAlex API
    ↓
[Fetch Works]
    ↓
[Filter by Topic & Criteria]
    ↓
[Deduplicate by DOI]
    ↓
[Convert to Dublin Core]
    ↓
[Match ORCID IDs]
    ↓
[Generate Vector Embeddings]
    ↓
[Import to DSpace]
    ↓
[Save State]
```

## Output

### State File (state.json)

Tracks harvest progress:

```json
{
  "last_harvested": {
    "Artificial Intelligence": "2024-08-02T14:35:20Z",
    "Machine Learning": "2024-08-02T14:35:25Z"
  },
  "processed_dois": {
    "10.1234/test.1": true,
    "10.1234/test.2": true
  }
}
```

### Log Output

```
2024/08/02 14:35:20 Starting comprehensive harvest for all topics...
2024/08/02 14:35:20 Starting harvest for topic: Artificial Intelligence
2024/08/02 14:35:21 Successfully imported work: Deep Learning Advances
2024/08/02 14:35:22 Duplicate found (DOI: 10.1234/xxx), skipping
2024/08/02 14:35:25 Completed harvest for topic: Artificial Intelligence
...
=== Harvest Statistics ===
Total Processed: 150
Successfully Imported: 145
Duplicates: 3
Errors: 2
Duration: 5m23s
```

## API Reference

### OpenAlex Query Parameters

- `search`: Text search query
- `per-page`: Results per request (1-200)
- `page`: Page number for pagination
- `filter`: Advanced filtering (publication_year, open_access, etc.)

### Supported Filters

```bash
# Open Access only
curl "https://api.openalex.org/works?search=AI&filter=open_access.is_oa:true"

# Recent publications
curl "https://api.openalex.org/works?search=AI&filter=publication_year:>2023"

# Specific country
curl "https://api.openalex.org/works?search=AI&filter=institutions.country_code:ZW"
```

## Troubleshooting

### Issue: "No topics configured"

**Solution:** Run `openalex-harvester -init-config` to initialize default configuration.

### Issue: "API returned status 429 (Rate Limited)"

**Solution:** Increase `rate_limit_delay` in config.json:

```json
{
  "rate_limit_delay": 500
}
```

### Issue: "DSpace connection failed"

**Solution:** Verify DSpace URL and API key in config.json:

```json
{
  "dspace_url": "https://dspace.dare.co.zw",
  "dspace_api_key": "your-valid-api-key"
}
```

### Issue: "Certificate verification failed"

**Solution:** Check SSL certificate or update CA bundle:

```bash
./openalex-harvester -test-api
```

## Performance Notes

- OpenAlex API has no rate limit but requests are batched with 100ms delay by default
- Each topic can process up to 1000 API requests (configurable)
- Average harvest of one topic: 2-5 minutes
- Full harvest of all 10 topics: 20-50 minutes

## Architecture

The harvester follows these principles:

1. **Modularity**: Separate concerns (config, harvesting, import)
2. **Resilience**: Continues on individual record failures
3. **Traceability**: Comprehensive logging and state tracking
4. **Efficiency**: Incremental harvesting and deduplication
5. **Extensibility**: Plugin-ready for custom processors

## Contributing

To extend the harvester:

1. Add new search topics to `topics.json`
2. Implement custom filters in `harvester.go`
3. Add DSpace import logic in `importToDSpace()`
4. Enable RAG vector indexing in configuration

## License

Part of the DARE Digital Repository project.

## Support

For issues, questions, or contributions:
- GitHub: [wgmasvix-hue/dare-digital-repository](https://github.com/wgmasvix-hue/dare-digital-repository)
- Email: support@dare.co.zw

## References

- [OpenAlex Documentation](https://docs.openalex.org)
- [DSpace REST API](https://wiki.lyrasis.org/display/DSPACE/REST+API)
- [Dublin Core Metadata](https://dublincore.org)
- [ORCID API](https://github.com/ORCID/orcid-model)
