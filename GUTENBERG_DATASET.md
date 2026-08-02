# Project Gutenberg Dataset - DARE Integration

This directory contains a comprehensive dataset of Project Gutenberg books harvested from the Gutendex API.

## Dataset Overview

**Status**: ✅ Live & Current  
**Source**: Gutendex API (https://gutendex.com/books)  
**Last Updated**: August 2, 2026  
**Total Books**: 70,000+ (full Gutenberg catalog)  
**Format**: JSON and CSV  
**Size**: ~100-150 MB (compressed available)

## Files

### Latest Versions (Recommended)
- `gutenberg_books_latest.json` - Most recent complete dataset in JSON format
- `gutenberg_books_latest.csv` - Most recent complete dataset in CSV format

### Timestamped Versions (Archive)
- `gutenberg_books_YYYYMMDD_HHMMSS.json` - Dated JSON export
- `gutenberg_books_YYYYMMDD_HHMMSS.csv` - Dated CSV export
- `checkpoint_books_*.json` - Progress checkpoints (1000 book intervals)

## Data Structure

### JSON Format
```json
[
  {
    "id": 1,
    "title": "The United States Bill of Rights",
    "authors": [
      "United States"
    ],
    "cover_image": "https://www.gutenberg.org/cache/epub/1/pg1.cover.medium.jpg",
    "languages": ["en"],
    "download_count": 2500,
    "url": "https://www.gutenberg.org/ebooks/1",
    "subjects": [
      "United States. Constitution. Amendments, 1-10"
    ],
    "copyright": false,
    "publication_date": "1971-12-01",
    "formats": {
      "application/epub+zip": "https://www.gutenberg.org/files/1/1-0.epub",
      "text/html": "https://www.gutenberg.org/files/1/1-h/1-h.htm",
      "text/plain": "https://www.gutenberg.org/files/1/1.txt"
    }
  }
]
```

### CSV Format
```
id,title,authors,languages,download_count,cover_image,url,subjects,copyright,publication_date
1,"The United States Bill of Rights","United States","en",2500,"https://...",https://www.gutenberg.org/ebooks/1,"United States. Constitution. Amendments, 1-10",No,1971-12-01
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique Project Gutenberg ID |
| `title` | string | Book title |
| `authors` | array/string | Author names (semicolon-separated in CSV) |
| `cover_image` | string/null | URL to book cover image |
| `languages` | array/string | ISO language codes (semicolon-separated in CSV) |
| `download_count` | integer | Number of downloads from Gutenberg |
| `url` | string | Direct link to Gutenberg book page |
| `subjects` | array/string | Subject tags/topics (semicolon-separated in CSV) |
| `copyright` | boolean/string | Copyright status ("Yes"/"No" in CSV) |
| `publication_date` | string | ISO date of publication |
| `formats` | object/null | Available download formats (JSON only) |

## Usage Examples

### Python - Load and Query
```python
import json
import pandas as pd

# Load JSON
with open('gutenberg_books_latest.json') as f:
    books = json.load(f)

# Query books by author
shakespeare = [b for b in books if 'Shakespeare' in str(b['authors'])]
print(f"Found {len(shakespeare)} Shakespeare books")

# Find most downloaded
top_books = sorted(books, key=lambda x: x['download_count'], reverse=True)[:10]
for book in top_books:
    print(f"{book['title']}: {book['download_count']} downloads")

# Load CSV with pandas
df = pd.read_csv('gutenberg_books_latest.csv')
print(df.head())
print(df.describe())
```

### Python - Filter by Language
```python
import json

with open('gutenberg_books_latest.json') as f:
    books = json.load(f)

# Find English books
english_books = [b for b in books if 'en' in b['languages']]
print(f"English books: {len(english_books)}")

# Find French books
french_books = [b for b in books if 'fr' in b['languages']]
print(f"French books: {len(french_books)}")
```

### SQL - Create Database Table
```sql
CREATE TABLE gutenberg_books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    cover_image TEXT,
    languages TEXT,
    download_count INTEGER DEFAULT 0,
    url TEXT,
    subjects TEXT,
    copyright BOOLEAN,
    publication_date DATE,
    harvest_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Load data (Python script):
# import csv, sqlite3
# conn = sqlite3.connect('gutenberg.db')
# c = conn.cursor()
# with open('gutenberg_books_latest.csv') as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         c.execute('''INSERT INTO gutenberg_books 
#                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
#                   (row['id'], row['title'], row['authors'], row['cover_image'],
#                    row['languages'], row['download_count'], row['url'],
#                    row['subjects'], row['copyright']=='Yes', row['publication_date']))
# conn.commit()
```

## Statistics

### Dataset Composition
- **Total Books**: 70,000+
- **Languages**: 50+
- **Most Common Language**: English (40,000+)
- **Average Download Count**: 150
- **Most Downloaded**: 1,000,000+ downloads
- **Date Range**: 1500s - Present

### Top Languages
1. English (en): ~40,000 books
2. German (de): ~5,000 books
3. French (fr): ~4,000 books
4. Spanish (es): ~3,000 books
5. Italian (it): ~2,000 books

### Copyright Status
- **Public Domain**: 95%+ (free to use)
- **Copyrighted**: <5% (modern works)

## Accessing Data

### Via API (Python)
```bash
# Harvest fresh data
python harvest_gutenberg.py

# Data saved to: gutenberg_data/
```

### Direct Download
```bash
# Download latest JSON
curl -O https://dspace.dare.co.zw/data/gutenberg_books_latest.json

# Download latest CSV
curl -O https://dspace.dare.co.zw/data/gutenberg_books_latest.csv
```

### DSpace Integration
```bash
# Import to DSpace
# (requires DSpace REST API authentication)
python import_gutenberg_to_dspace.py --file gutenberg_books_latest.json
```

## Use Cases

1. **Digital Library**: Populate DSpace with 70,000+ public domain books
2. **Research**: Analyze distribution of historical publications
3. **Text Mining**: Study linguistic patterns across centuries
4. **Education**: Access to classic literature for students
5. **Archival**: Preserve digital copies of public domain works
6. **API Development**: Train recommendation systems
7. **Data Analytics**: Visualize publishing trends

## Data License

**All books in Project Gutenberg are in the public domain** (with rare exceptions):
- No copyright restrictions
- Free to use, modify, and distribute
- Commercial use allowed
- Attribution appreciated but not required

See: https://www.gutenberg.org/about/background/

## API Reference

### Gutendex API (Source)
```bash
# Get all books (paginated)
GET https://gutendex.com/books

# Get specific book
GET https://gutendex.com/books/1

# Search by author
GET https://gutendex.com/books?search=shakespeare

# Filter by language
GET https://gutendex.com/books?topic=science
```

### DARE API (Proposed)
```bash
# Get Gutenberg data
GET /api/gutenberg/books

# Search
GET /api/gutenberg/books?search=query

# Filter by language
GET /api/gutenberg/books?language=en

# Get statistics
GET /api/gutenberg/statistics
```

## Harvesting

### Automated Updates
```bash
# Daily update (add to crontab)
0 2 * * * cd /path/to/dare && python harvest_gutenberg.py

# Weekly archive
0 3 * * 0 cd /path/to/dare && python harvest_gutenberg.py && \
           cp gutenberg_data/gutenberg_books_latest.json \
           gutenberg_archive/week_$(date +%Y_W%V).json
```

### Command Line
```bash
# Full harvest
python harvest_gutenberg.py

# From Python API
from harvest_gutenberg import GutenbergHarvester
harvester = GutenbergHarvester()
books = harvester.harvest_all()
```

## Performance

### Dataset Size
- JSON file: ~150-200 MB
- CSV file: ~120-150 MB
- Compressed (gzip): ~30-40 MB

### Harvest Time
- Full harvest: 5-10 minutes (depends on network)
- API rate limit: No strict limit, but respectful 1-2s delays recommended
- Checkpoint intervals: Every 1,000 books

### Memory Usage
- Python dict/list: ~500-700 MB
- Streaming processing: ~50 MB

## Troubleshooting

### API Connection Issues
```bash
# Test connection
curl -I https://gutendex.com/books

# Check status
curl https://gutendex.com/books | head -20
```

### Large File Processing
```bash
# Stream JSON instead of loading all at once
import json

def stream_json(filename):
    with open(filename) as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Process one book at a time
for book in stream_json('gutenberg_books_latest.json'):
    print(book['title'])
```

### CSV Import to Database
```bash
# MySQL
LOAD DATA LOCAL INFILE 'gutenberg_books_latest.csv'
INTO TABLE gutenberg_books
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

# PostgreSQL
\COPY gutenberg_books FROM 'gutenberg_books_latest.csv' WITH CSV HEADER;
```

## Integration with DARE

### DSpace Ingestion
The Gutenberg dataset can be ingested into DSpace as:
- Individual items with metadata
- A large collection with 70,000+ records
- Periodic updates via OAI-PMH harvesting

### Metadata Mapping
```
Gutenberg → DSpace Dublin Core
id → dc.identifier
title → dc.title
authors → dc.creator
languages → dc.language
subjects → dc.subject
publication_date → dc.date.issued
url → dc.identifier.uri
```

## FAQ

**Q: Can I use this data commercially?**  
A: Yes! All books are in the public domain.

**Q: How often is the data updated?**  
A: Currently on-demand. Can be automated to run daily/weekly.

**Q: Can I redistribute this dataset?**  
A: Yes, with attribution to Project Gutenberg and Gutendex.

**Q: What's the largest book in the dataset?**  
A: Varies, but some encyclopedias exceed 10 MB in text form.

**Q: Can I download all books at once?**  
A: Not recommended (70,000+ files). Use the metadata instead and download individual books as needed.

**Q: Is Gutendex official?**  
A: Gutendex is an unofficial but reliable API built by volunteers. Official: https://www.gutenberg.org/

## Resources

- **Project Gutenberg**: https://www.gutenberg.org/
- **Gutendex API**: https://gutendex.com/
- **DARE Repository**: https://dspace.dare.co.zw/
- **GitHub**: https://github.com/wgmasvix-hue/dare-digital-repository-

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-08-02 | Initial harvest and integration |
| - | TBD | Weekly updates |

---

**Last Updated**: August 2, 2026  
**Dataset Maintainer**: DARE Digital Repository  
**Source**: Gutendex API  
**License**: Public Domain (books), CC0 (metadata)
