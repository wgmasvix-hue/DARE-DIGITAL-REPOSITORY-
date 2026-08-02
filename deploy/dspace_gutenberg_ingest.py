#!/usr/bin/env python3
"""
DSpace Gutenberg Ingest Tool
Ingests Project Gutenberg books into DSpace via REST API
"""

import json
import csv
import requests
import argparse
from pathlib import Path
from datetime import datetime
import time

class DSpaceGutenbergIngest:
    def __init__(self, dspace_url, auth_token, collection_handle):
        """
        Initialize DSpace ingester

        Args:
            dspace_url: Base URL of DSpace instance (e.g., https://repo.dare.co.zw)
            auth_token: DSpace REST API authentication token
            collection_handle: Handle of target collection (e.g., 123456789/10)
        """
        self.dspace_url = dspace_url.rstrip('/')
        self.auth_token = auth_token
        self.collection_handle = collection_handle
        self.api_url = f"{self.dspace_url}/server/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })

    def create_collection(self):
        """Create a new Gutenberg collection if it doesn't exist"""
        print("Creating Gutenberg collection...")

        # Prepare collection metadata
        collection_data = {
            "name": "Project Gutenberg",
            "metadata": {
                "dc.description": ["Digital collection of 70,000+ public domain books from Project Gutenberg"],
                "dc.title": ["Project Gutenberg Books"],
                "dc.rights": ["Public Domain"]
            }
        }

        try:
            # Create collection
            response = self.session.post(
                f"{self.api_url}/core/collections",
                json=collection_data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            handle = result.get('handle')
            print(f"✓ Collection created: {handle}")
            return handle
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating collection: {e}")
            return None

    def ingest_book(self, book_data):
        """
        Ingest a single book into DSpace

        Args:
            book_data: Dictionary with book metadata

        Returns:
            Item handle if successful, None otherwise
        """
        # Map Gutenberg metadata to Dublin Core
        item_metadata = {
            "dc.title": [book_data['title']],
            "dc.creator": book_data['authors'],
            "dc.language": book_data['languages'],
            "dc.subject": book_data.get('subjects', []),
            "dc.identifier.uri": [book_data['url']],
            "dc.date.issued": [book_data['publication_date']] if book_data.get('publication_date') else [],
            "dc.rights": ["Public Domain"],
            "dc.type": ["Book"],
            "gutenberg.id": [str(book_data['id'])],
            "gutenberg.downloads": [str(book_data.get('download_count', 0))],
        }

        # Add cover image if available
        if book_data.get('cover_image'):
            item_metadata["dc.relation.isPartOf"] = [book_data['cover_image']]

        item_json = {
            "metadata": item_metadata,
            "inArchive": True,
            "discoverable": True,
            "withdrawn": False
        }

        try:
            # Create item in collection
            response = self.session.post(
                f"{self.api_url}/core/items",
                params={"owningCollection": self.collection_handle},
                json=item_json,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get('handle')
        except requests.exceptions.RequestException as e:
            print(f"✗ Error ingesting '{book_data['title']}': {e}")
            return None

    def ingest_from_json(self, json_file):
        """
        Ingest books from JSON file

        Args:
            json_file: Path to gutenberg_books_latest.json
        """
        print(f"Loading books from {json_file}...")

        with open(json_file) as f:
            books = json.load(f)

        print(f"Ingesting {len(books)} books into DSpace...")
        print()

        successful = 0
        failed = 0

        for i, book in enumerate(books, 1):
            print(f"[{i}/{len(books)}] Ingesting '{book['title']}'...", end=" ")

            handle = self.ingest_book(book)
            if handle:
                print(f"✓ {handle}")
                successful += 1
            else:
                print("✗ Failed")
                failed += 1

            # Rate limiting - be respectful to DSpace
            time.sleep(0.5)

        print()
        print(f"{'='*60}")
        print(f"Ingest Summary")
        print(f"{'='*60}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(books)}")
        print(f"Success rate: {(successful/len(books)*100):.1f}%")
        print(f"{'='*60}")

    def ingest_from_csv(self, csv_file):
        """
        Ingest books from CSV file

        Args:
            csv_file: Path to gutenberg_books_latest.csv
        """
        print(f"Loading books from {csv_file}...")

        books = []
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                book = {
                    'id': int(row['id']),
                    'title': row['title'],
                    'authors': [a.strip() for a in row['authors'].split(';')] if row['authors'] else [],
                    'languages': [l.strip() for l in row['languages'].split(';')] if row['languages'] else [],
                    'subjects': [s.strip() for s in row['subjects'].split(';')] if row['subjects'] else [],
                    'url': row['url'],
                    'publication_date': row.get('publication_date'),
                    'download_count': int(row['download_count']) if row['download_count'] else 0,
                    'cover_image': row.get('cover_image') if row.get('cover_image') else None,
                }
                books.append(book)

        print(f"Ingesting {len(books)} books into DSpace...")
        print()

        successful = 0
        failed = 0

        for i, book in enumerate(books, 1):
            print(f"[{i}/{len(books)}] Ingesting '{book['title']}'...", end=" ")

            handle = self.ingest_book(book)
            if handle:
                print(f"✓ {handle}")
                successful += 1
            else:
                print("✗ Failed")
                failed += 1

            time.sleep(0.5)

        print()
        print(f"{'='*60}")
        print(f"Ingest Summary")
        print(f"{'='*60}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total: {len(books)}")
        print(f"Success rate: {(successful/len(books)*100):.1f}%")
        print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(
        description='Ingest Project Gutenberg books into DSpace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get authentication token
  curl -X POST https://repo.dare.co.zw/server/api/authn/login \\
    -H "Content-Type: application/json" \\
    -d '{"user":"admin@example.com", "password":"password"}' \\
    -c cookies.txt

  # Extract token from cookies
  grep "DSPACE-XSRF-TOKEN" cookies.txt

  # Ingest from JSON
  %(prog)s \\
    --url https://repo.dare.co.zw \\
    --token YOUR_TOKEN \\
    --collection 123456789/10 \\
    --json gutenberg_books_latest.json

  # Ingest from CSV
  %(prog)s \\
    --url https://repo.dare.co.zw \\
    --token YOUR_TOKEN \\
    --collection 123456789/10 \\
    --csv gutenberg_books_latest.csv
        """
    )

    parser.add_argument(
        '--url',
        required=True,
        help='DSpace base URL (e.g., https://repo.dare.co.zw)'
    )

    parser.add_argument(
        '--token',
        required=True,
        help='DSpace REST API authentication token'
    )

    parser.add_argument(
        '--collection',
        required=True,
        help='Target collection handle (e.g., 123456789/10)'
    )

    parser.add_argument(
        '--json',
        help='Path to gutenberg_books_latest.json'
    )

    parser.add_argument(
        '--csv',
        help='Path to gutenberg_books_latest.csv'
    )

    args = parser.parse_args()

    if not args.json and not args.csv:
        parser.error("Specify either --json or --csv")

    # Initialize ingester
    ingester = DSpaceGutenbergIngest(args.url, args.token, args.collection)

    # Ingest books
    if args.json:
        ingester.ingest_from_json(args.json)
    else:
        ingester.ingest_from_csv(args.csv)

if __name__ == '__main__':
    main()
