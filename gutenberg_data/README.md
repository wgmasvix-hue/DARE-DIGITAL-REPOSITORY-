# Gutenberg Data Directory

This directory contains Project Gutenberg book metadata harvested from the Gutendex API.

## Files

### Sample Data
- `gutenberg_books_sample.json` - Sample of 10 classic books in JSON format
- `gutenberg_books_sample.csv` - Same data in CSV format for spreadsheet/database import

### Full Dataset (To be populated)
- `gutenberg_books_latest.json` - Complete Gutenberg catalog (when fully harvested)
- `gutenberg_books_latest.csv` - Complete Gutenberg catalog in CSV format
- `gutenberg_books_YYYYMMDD_HHMMSS.json` - Dated versions (archive)
- `checkpoint_books_*.json` - Progress checkpoints from harvest runs

## Data Format

### Fields
- **id**: Unique Gutenberg identifier
- **title**: Book title
- **authors**: Author names (array in JSON, semicolon-separated in CSV)
- **languages**: ISO language codes
- **download_count**: Number of times downloaded from Gutenberg
- **cover_image**: URL to book cover
- **url**: Direct link to Gutenberg book page
- **subjects**: Topic tags and categories
- **copyright**: Copyright status (boolean)
- **publication_date**: ISO date

## Usage

### Load JSON with Python
```python
import json

with open('gutenberg_books_sample.json') as f:
    books = json.load(f)

for book in books:
    print(f"{book['title']} by {', '.join(book['authors'])}")
```

### Load CSV with Pandas
```python
import pandas as pd

df = pd.read_csv('gutenberg_books_sample.csv')
print(df.head())
```

### Import to Database
```bash
# MySQL
mysql> LOAD DATA LOCAL INFILE 'gutenberg_books_sample.csv'
    INTO TABLE books
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 ROWS;

# PostgreSQL
psql# \COPY books FROM 'gutenberg_books_sample.csv' WITH CSV HEADER;
```

## Full Harvest

To harvest the complete Gutenberg dataset (~70,000 books):

```bash
cd ..
python harvest_gutenberg.py
```

Output will be saved to this directory as:
- `gutenberg_books_YYYYMMDD_HHMMSS.json`
- `gutenberg_books_YYYYMMDD_HHMMSS.csv`
- `gutenberg_books_latest.json` (symlink to latest)
- `gutenberg_books_latest.csv` (symlink to latest)

## License

All books in Project Gutenberg are in the public domain (with rare exceptions).

- No copyright restrictions
- Free to use, modify, and distribute
- Commercial use allowed
- Attribution appreciated

See: https://www.gutenberg.org/about/background/

## References

- Project Gutenberg: https://www.gutenberg.org/
- Gutendex API: https://gutendex.com/
- DARE Repository: https://repo.dare.co.zw/

---

For more information, see `../GUTENBERG_DATASET.md`
