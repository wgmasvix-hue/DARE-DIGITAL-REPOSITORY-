#!/usr/bin/env python3
"""
Project Gutenberg Harvester - Harvest all books from Gutendex API
Saves metadata for 9000+ public domain books to JSON and CSV formats
"""

import json
import csv
import requests
from datetime import datetime
from pathlib import Path
import sys

class GutenbergHarvester:
    def __init__(self, output_dir="./gutenberg_data"):
        self.api_url = "https://gutendex.com/books"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DARE-Gutenberg-Harvester/1.0'
        })

    def harvest_all(self):
        """Harvest all books from Gutendex API"""
        print("Starting Gutenberg harvest from Gutendex API...")
        print(f"Output directory: {self.output_dir.absolute()}")
        print()

        books = []
        page = 1
        total_pages = 1

        try:
            while page <= total_pages:
                print(f"Fetching page {page}/{total_pages}...", end=" ")

                try:
                    params = {'page': page}
                    response = self.session.get(self.api_url, params=params, timeout=30)
                    response.raise_for_status()

                    data = response.json()
                    results = data.get('results', [])

                    if not results:
                        print("No more results")
                        break

                    # Extract book metadata
                    for book in results:
                        book_data = {
                            'id': book.get('id'),
                            'title': book.get('title', ''),
                            'authors': [
                                author.get('name', '')
                                for author in book.get('authors', [])
                            ],
                            'cover_image': book.get('cover_image'),
                            'languages': book.get('languages', []),
                            'download_count': book.get('download_count', 0),
                            'url': f"https://www.gutenberg.org/ebooks/{book.get('id')}",
                            'formats': book.get('formats', {}),
                            'subjects': book.get('subjects', []),
                            'copyright': book.get('copyright'),
                            'publication_date': book.get('publication_date')
                        }
                        books.append(book_data)

                    print(f"Added {len(results)} books (Total: {len(books)})")

                    # Update total pages for progress tracking
                    total_pages = (data.get('count', 0) + 31) // 32  # 32 books per page

                    # Save checkpoint every 1000 books
                    if len(books) % 1000 == 0:
                        checkpoint_file = self.output_dir / f"checkpoint_books_{len(books)}.json"
                        with open(checkpoint_file, 'w', encoding='utf-8') as f:
                            json.dump(books, f, ensure_ascii=False, indent=2)
                        print(f"  → Checkpoint saved: {len(books)} books")

                    page += 1

                except requests.exceptions.RequestException as e:
                    print(f"Error on page {page}: {e}")
                    if len(books) > 0:
                        print(f"Continuing with {len(books)} books harvested so far...")
                    continue

        except KeyboardInterrupt:
            print("\nHarvest interrupted by user")
        except Exception as e:
            print(f"Error during harvest: {e}")

        if books:
            print(f"\n✓ Harvest complete: {len(books)} books collected")
            self.save_data(books)
            return books
        else:
            print("No books harvested")
            return []

    def save_data(self, books):
        """Save harvested data to JSON and CSV"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save JSON
        json_file = self.output_dir / f"gutenberg_books_{timestamp}.json"
        print(f"\nSaving JSON to {json_file}...")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON saved: {json_file}")

        # Also save as latest
        latest_json = self.output_dir / "gutenberg_books_latest.json"
        with open(latest_json, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)

        # Save CSV
        csv_file = self.output_dir / f"gutenberg_books_{timestamp}.csv"
        print(f"Saving CSV to {csv_file}...")

        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'title', 'authors', 'languages', 'download_count',
                'cover_image', 'url', 'subjects', 'copyright', 'publication_date'
            ])

            for book in books:
                writer.writerow([
                    book['id'],
                    book['title'],
                    '; '.join(book['authors']),
                    '; '.join(book['languages']),
                    book['download_count'],
                    book['cover_image'] or '',
                    book['url'],
                    '; '.join(book['subjects']),
                    'Yes' if book['copyright'] else 'No',
                    book['publication_date'] or ''
                ])

        print(f"✓ CSV saved: {csv_file}")

        # Also save as latest
        latest_csv = self.output_dir / "gutenberg_books_latest.csv"
        with open(latest_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'title', 'authors', 'languages', 'download_count',
                'cover_image', 'url', 'subjects', 'copyright', 'publication_date'
            ])

            for book in books:
                writer.writerow([
                    book['id'],
                    book['title'],
                    '; '.join(book['authors']),
                    '; '.join(book['languages']),
                    book['download_count'],
                    book['cover_image'] or '',
                    book['url'],
                    '; '.join(book['subjects']),
                    'Yes' if book['copyright'] else 'No',
                    book['publication_date'] or ''
                ])

        # Print summary
        print(f"\n{'='*60}")
        print(f"Gutenberg Harvest Summary")
        print(f"{'='*60}")
        print(f"Total books: {len(books)}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Files created:")
        print(f"  - {json_file.name}")
        print(f"  - {latest_json.name} (latest version)")
        print(f"  - {csv_file.name}")
        print(f"  - {latest_csv.name} (latest version)")
        print(f"{'='*60}\n")

def main():
    harvester = GutenbergHarvester("./gutenberg_data")
    books = harvester.harvest_all()

    if books:
        print(f"Successfully harvested {len(books)} books!")
        sys.exit(0)
    else:
        print("Harvest failed - no books collected")
        sys.exit(1)

if __name__ == '__main__':
    main()
