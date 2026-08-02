# MIT Papers Harvester for DSpace 9

A comprehensive Python-based tool for harvesting academic papers and metadata from MIT DSpace 9 repositories using the OAI-PMH (Open Archives Initiative Protocol for Metadata Harvesting) protocol.

## Features

- **OAI-PMH Compliant**: Full support for OAI-PMH protocol used by DSpace 9
- **Multiple Export Formats**: Save harvested data as JSON or CSV
- **Flexible Harvesting**: Harvest all records, specific collections, or date ranges
- **Robust Error Handling**: Automatic retry logic and comprehensive logging
- **Batch Processing**: Handles large datasets with resumption tokens
- **CLI Interface**: Easy-to-use command-line interface
- **Configuration File Support**: YAML-based configuration for advanced setups

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage (CLI)

Harvest all papers from an MIT DSpace instance:

```bash
python harvest_cli.py --url https://dspace.mit.edu
```

### List Available Collections

View all available collections before harvesting:

```bash
python harvest_cli.py --url https://dspace.mit.edu --list-sets
```

### Harvest Specific Collection

```bash
python harvest_cli.py --url https://dspace.mit.edu --set "com_123_456"
```

### Harvest Recent Papers (Last 30 Days)

```bash
python harvest_cli.py --url https://dspace.mit.edu --recent 30
```

### Harvest with Date Range

```bash
python harvest_cli.py --url https://dspace.mit.edu --from 2024-01-01 --until 2024-12-31
```

### Specify Output Format

```bash
# Save as JSON only
python harvest_cli.py --url https://dspace.mit.edu --format json

# Save as CSV only
python harvest_cli.py --url https://dspace.mit.edu --format csv

# Save as both (default)
python harvest_cli.py --url https://dspace.mit.edu --format both
```

## Command-Line Options

```
Usage: harvest_cli.py --url <dspace-url> [options]

Options:
  -u, --url URL                Base URL of DSpace repository (required)
  -o, --output DIR             Output directory (default: ./harvest_output)
  -s, --set SPEC               Specific collection/set to harvest
  -f, --format FORMAT          Output format: json, csv, or both (default: both)
  --from DATE                  Start date (format: YYYY-MM-DD)
  --until DATE                 End date (format: YYYY-MM-DD)
  --recent DAYS                Harvest records from last N days
  --metadata-prefix PREFIX     Metadata format (default: oai_dc)
  --list-sets                  List available sets and exit
  --timeout SECONDS            Request timeout (default: 30)
  --log-level LEVEL            Logging level: DEBUG, INFO, WARNING, ERROR
  --help                       Show help message
```

## Usage Examples

### Example 1: Full MIT DSpace Harvest

```bash
python harvest_cli.py \
  --url https://dspace.mit.edu \
  --output ./mit_papers \
  --format both \
  --log-level INFO
```

### Example 2: Harvest Theses and Dissertations

```bash
# First, list sets to find theses collection
python harvest_cli.py --url https://dspace.mit.edu --list-sets

# Then harvest specific collection
python harvest_cli.py \
  --url https://dspace.mit.edu \
  --set "com_1721.1_49604" \
  --format json
```

### Example 3: Monthly Harvest with Logging

```bash
python harvest_cli.py \
  --url https://dspace.mit.edu \
  --recent 30 \
  --log-level DEBUG \
  --output ./harvest_monthly
```

### Example 4: Programmatic Usage (Python)

```python
from harvest_mit_papers import DSpaceHarvester

# Initialize harvester
harvester = DSpaceHarvester('https://dspace.mit.edu', './output')

# Get available collections
sets = harvester.get_available_sets()
print(f"Found {len(sets)} collections")

# Harvest records
records = harvester.get_oai_records(
    set_spec='com_1721.1_49604',
    from_date='2024-01-01'
)

# Save to files
harvester.save_json(records, 'papers.json')
harvester.save_csv(records, 'papers.csv')

print(f"Harvested {len(records)} papers")
```

## Output Format

### JSON Output Structure

```json
[
  {
    "identifier": "http://hdl.handle.net/1721.1/...",
    "datestamp": "2024-08-01T12:00:00Z",
    "titles": ["Paper Title"],
    "creators": ["Author Name"],
    "subjects": ["Subject 1", "Subject 2"],
    "description": "Abstract text...",
    "date_issued": "2024-07-15",
    "type": "Article",
    "url": "https://dspace.mit.edu/handle/1721.1/...",
    "rights": "© 2024 Author"
  }
]
```

### CSV Output Columns

- identifier: Handle/DOI of the paper
- datestamp: Date harvested in OAI-PMH
- title: Paper title
- creators: Author names (semicolon-separated)
- subjects: Keywords/subjects (semicolon-separated)
- description: Abstract or description (first 500 chars)
- date_issued: Publication date
- type: Resource type (Article, Thesis, etc.)
- url: Direct URL to paper
- rights: Copyright/license information

## Configuration File (Advanced)

Use `harvest_config.yaml` for advanced configuration:

```yaml
repositories:
  mit_main:
    url: "https://dspace.mit.edu"
    enabled: true

harvest:
  metadata_prefix: "oai_dc"
  timeout: 30

output:
  directory: "./harvest_output"
  formats: ["json", "csv"]
```

## OAI-PMH Metadata Formats

Common metadata prefixes supported by DSpace:

- **oai_dc**: Dublin Core (default, most compatible)
- **mets**: METS (Metadata Encoding & Transmission Standard)
- **rdf**: RDF/XML
- **marc**: MARC format (if supported)

## Troubleshooting

### Connection Issues

**Error**: `Connection timeout`
- **Solution**: Increase timeout: `--timeout 60`
- **Check**: Verify DSpace URL is accessible

### Empty Results

**Issue**: Harvester returns 0 records
- **Check**: Verify collection/set specifier is correct with `--list-sets`
- **Try**: Harvest all records first: remove `--set` parameter
- **Check**: Date range might be too restrictive

### Memory Issues (Large Harvests)

For very large datasets:
- Harvest by date ranges in smaller chunks
- Use `--recent` to harvest incrementally
- Process CSV output in streaming mode

### XML Parse Errors

**Error**: `XML parsing error`
- **Cause**: Malformed response from server
- **Solution**: Increase `--timeout` and retry
- **Report**: Check DSpace server logs

## Performance Tips

1. **Incremental Harvesting**: Use `--recent 1` for daily harvests
2. **Parallel Processing**: Run multiple commands with different date ranges
3. **CSV for Analysis**: CSV is lighter for data analysis than JSON
4. **Batch Mode**: Schedule harvests during off-peak hours

## Logging

Logs are saved to `harvest.log` with timestamp and detailed information. Use `--log-level DEBUG` for troubleshooting:

```bash
python harvest_cli.py --url https://dspace.mit.edu --log-level DEBUG
```

## MIT DSpace Instances

Common MIT DSpace URLs:
- Main repository: https://dspace.mit.edu
- HDLR: https://hdl.handle.net (Handle Resolution System)
- Theses: Collection-specific endpoints

To find specific collections, use: `python harvest_cli.py --url <url> --list-sets`

## Output Files

All harvested data is saved to the output directory with timestamp:
- `mit_papers_20240801_120000.json` - Full metadata in JSON
- `mit_papers_20240801_120000.csv` - Tabular data in CSV

## Advanced Features

### Filtering Records (Python)

```python
records = harvester.get_oai_records()

# Filter by year
papers_2024 = [r for r in records if r['date_issued'].startswith('2024')]

# Filter by type
articles = [r for r in records if r['type'] == 'Article']

# Filter by subject
cs_papers = [r for r in records if 'Computer Science' in r['subjects']]
```

### Custom Processing

```python
import json

with open('mit_papers.json') as f:
    papers = json.load(f)

# Process each paper
for paper in papers:
    # Download full text, extract citations, etc.
    print(f"{paper['titles'][0]} by {paper['creators'][0]}")
```

## Rate Limiting

DSpace OAI-PMH has built-in rate limiting. The harvester:
- Respects server resumption tokens
- Uses exponential backoff on failures
- Maintains reasonable request intervals

For large-scale harvests, consider:
- Distributing requests over time
- Using `--recent` for incremental updates
- Contacting repository administrators for bulk export options

## License

This harvester is provided as-is for harvesting public MIT research data.

## Support

For issues:
1. Check `harvest.log` for error details
2. Verify DSpace URL and connectivity
3. Review examples in this README
4. Report repository access issues to MIT DSpace support

## References

- OAI-PMH Protocol: https://www.openarchives.org/pmh/
- DSpace Documentation: https://wiki.lyrasis.org/display/DSPACE
- Dublin Core Metadata: https://purl.org/dc/documents/dc-best-practices-20060711.pdf
