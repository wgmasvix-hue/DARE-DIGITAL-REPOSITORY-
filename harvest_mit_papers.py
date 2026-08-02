#!/usr/bin/env python3
"""
MIT Papers Harvester for DSpace 9 Repositories
Harvests paper metadata using OAI-PMH protocol from MIT DSpace instances
"""

import requests
import logging
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('harvest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DSpaceHarvester:
    """Harvest metadata from DSpace 9 OAI-PMH endpoints"""

    # OAI-PMH namespaces
    NAMESPACES = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'dcterms': 'http://purl.org/dc/terms/'
    }

    def __init__(self, base_url: str, output_dir: str = './harvest_output'):
        """
        Initialize harvester with DSpace repository URL

        Args:
            base_url: Base URL of DSpace instance (e.g., https://dspace.mit.edu)
            output_dir: Directory for storing harvested data
        """
        self.base_url = base_url.rstrip('/')
        self.oai_url = urljoin(self.base_url, '/oai/request')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MIT-DSpace-Harvester/1.0'})

    def get_oai_records(self,
                       set_spec: Optional[str] = None,
                       metadata_prefix: str = 'oai_dc',
                       from_date: Optional[str] = None,
                       until_date: Optional[str] = None) -> List[Dict]:
        """
        Harvest records from OAI-PMH endpoint

        Args:
            set_spec: Specific set to harvest (collection)
            metadata_prefix: Metadata format (default: oai_dc)
            from_date: Start date (YYYY-MM-DD format)
            until_date: End date (YYYY-MM-DD format)

        Returns:
            List of parsed record dictionaries
        """
        records = []
        resume_token = None

        logger.info(f"Starting harvest from {self.base_url}")
        logger.info(f"Set: {set_spec or 'All'}, Format: {metadata_prefix}")

        while True:
            try:
                params = {
                    'verb': 'ListRecords',
                    'metadataPrefix': metadata_prefix,
                }

                if set_spec:
                    params['set'] = set_spec
                if from_date:
                    params['from'] = from_date
                if until_date:
                    params['until'] = until_date
                if resume_token:
                    params['resumptionToken'] = resume_token

                response = self.session.get(self.oai_url, params=params, timeout=30)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                # Extract records
                record_elements = root.findall('.//oai:record', self.NAMESPACES)
                logger.info(f"Retrieved {len(record_elements)} records in this batch")

                for record_elem in record_elements:
                    record = self._parse_record(record_elem)
                    if record:
                        records.append(record)

                # Check for resumption token
                resumption = root.find('.//oai:resumptionToken', self.NAMESPACES)
                if resumption is not None and resumption.text:
                    resume_token = resumption.text
                    cursor = root.find('.//oai:resumptionToken', self.NAMESPACES).get('cursor')
                    complete = root.find('.//oai:resumptionToken', self.NAMESPACES).get('completeListSize')
                    logger.info(f"Resumption token found. Progress: {cursor}/{complete}")
                else:
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                break
            except ET.ParseError as e:
                logger.error(f"XML parsing error: {e}")
                break

        logger.info(f"Total records harvested: {len(records)}")
        return records

    def _parse_record(self, record_elem: ET.Element) -> Optional[Dict]:
        """Parse OAI record element into dictionary"""
        try:
            header = record_elem.find('oai:header', self.NAMESPACES)
            if header is None:
                return None

            # Check if record is deleted
            if header.get('status') == 'deleted':
                return None

            identifier = header.findtext('oai:identifier', '', self.NAMESPACES)
            datestamp = header.findtext('oai:datestamp', '', self.NAMESPACES)

            # Extract metadata
            metadata_elem = record_elem.find('.//oai_dc:dc', self.NAMESPACES)
            if metadata_elem is None:
                return None

            record = {
                'identifier': identifier,
                'datestamp': datestamp,
                'titles': [],
                'creators': [],
                'subjects': [],
                'description': '',
                'date_issued': '',
                'type': '',
                'url': '',
                'rights': '',
            }

            # Extract DC elements
            for title_elem in metadata_elem.findall('dc:title', self.NAMESPACES):
                if title_elem.text:
                    record['titles'].append(title_elem.text)

            for creator_elem in metadata_elem.findall('dc:creator', self.NAMESPACES):
                if creator_elem.text:
                    record['creators'].append(creator_elem.text)

            for subject_elem in metadata_elem.findall('dc:subject', self.NAMESPACES):
                if subject_elem.text:
                    record['subjects'].append(subject_elem.text)

            desc = metadata_elem.findtext('dc:description', '', self.NAMESPACES)
            if desc:
                record['description'] = desc

            date_issued = metadata_elem.findtext('dc:issued', '', self.NAMESPACES)
            if not date_issued:
                date_issued = metadata_elem.findtext('dcterms:issued', '', self.NAMESPACES)
            record['date_issued'] = date_issued

            type_elem = metadata_elem.findtext('dc:type', '', self.NAMESPACES)
            record['type'] = type_elem

            # Extract URL (typically the most common identifier)
            for identifier_elem in metadata_elem.findall('dc:identifier', self.NAMESPACES):
                if identifier_elem.text and identifier_elem.text.startswith('http'):
                    record['url'] = identifier_elem.text
                    break

            rights = metadata_elem.findtext('dc:rights', '', self.NAMESPACES)
            record['rights'] = rights

            return record

        except Exception as e:
            logger.warning(f"Error parsing record: {e}")
            return None

    def save_json(self, records: List[Dict], filename: str = 'harvested_papers.json'):
        """Save records to JSON file"""
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(records)} records to {output_path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")

    def save_csv(self, records: List[Dict], filename: str = 'harvested_papers.csv'):
        """Save records to CSV file"""
        output_path = self.output_dir / filename
        try:
            if not records:
                logger.warning("No records to save")
                return

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                fieldnames = [
                    'identifier', 'datestamp', 'title', 'creators',
                    'subjects', 'description', 'date_issued', 'type', 'url', 'rights'
                ]
                writer.writerow(fieldnames)

                # Data rows
                for record in records:
                    writer.writerow([
                        record.get('identifier', ''),
                        record.get('datestamp', ''),
                        '; '.join(record.get('titles', [])),
                        '; '.join(record.get('creators', [])),
                        '; '.join(record.get('subjects', [])),
                        record.get('description', '')[:500],  # Truncate for CSV
                        record.get('date_issued', ''),
                        record.get('type', ''),
                        record.get('url', ''),
                        record.get('rights', ''),
                    ])

            logger.info(f"Saved {len(records)} records to {output_path}")
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")

    def get_available_sets(self) -> List[Dict[str, str]]:
        """Get list of available sets (collections) from repository"""
        sets = []
        resume_token = None

        logger.info("Fetching available sets...")

        while True:
            try:
                params = {'verb': 'ListSets'}
                if resume_token:
                    params['resumptionToken'] = resume_token

                response = self.session.get(self.oai_url, params=params, timeout=30)
                response.raise_for_status()

                root = ET.fromstring(response.content)

                set_elements = root.findall('.//oai:set', self.NAMESPACES)

                for set_elem in set_elements:
                    set_spec = set_elem.findtext('oai:setSpec', '', self.NAMESPACES)
                    set_name = set_elem.findtext('oai:setName', '', self.NAMESPACES)
                    sets.append({'spec': set_spec, 'name': set_name})

                # Check for resumption token
                resumption = root.find('.//oai:resumptionToken', self.NAMESPACES)
                if resumption is not None and resumption.text:
                    resume_token = resumption.text
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching sets: {e}")
                break

        logger.info(f"Found {len(sets)} sets")
        for s in sets[:10]:  # Show first 10
            logger.info(f"  - {s['spec']}: {s['name']}")

        return sets


def main():
    """Example usage"""

    # Configuration
    MIT_DSPACE_URL = "https://dspace.mit.edu"  # Replace with actual MIT DSpace URL
    OUTPUT_DIR = "./harvest_output"

    # Initialize harvester
    harvester = DSpaceHarvester(MIT_DSPACE_URL, OUTPUT_DIR)

    # Option 1: Get available sets
    logger.info("\n=== Available Collections ===")
    sets = harvester.get_available_sets()

    # Option 2: Harvest all records (may take time)
    logger.info("\n=== Harvesting All Papers ===")
    all_records = harvester.get_oai_records()
    harvester.save_json(all_records, 'all_papers.json')
    harvester.save_csv(all_records, 'all_papers.csv')

    # Option 3: Harvest specific set/collection
    if sets:
        logger.info("\n=== Harvesting Specific Collection ===")
        specific_set = sets[0]['spec']
        logger.info(f"Harvesting set: {specific_set}")
        collection_records = harvester.get_oai_records(set_spec=specific_set)
        harvester.save_json(collection_records, f'{specific_set.replace("/", "_")}.json')
        harvester.save_csv(collection_records, f'{specific_set.replace("/", "_")}.csv')

    # Option 4: Harvest records from last 30 days
    logger.info("\n=== Harvesting Recent Papers ===")
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_records = harvester.get_oai_records(from_date=from_date)
    harvester.save_json(recent_records, 'recent_papers.json')
    harvester.save_csv(recent_records, 'recent_papers.csv')

    logger.info("\n=== Harvest Complete ===")
    logger.info(f"Output saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
