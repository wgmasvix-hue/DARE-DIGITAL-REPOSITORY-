#!/usr/bin/env python3
"""
Example usage of MIT Papers Harvester library
Shows various ways to use the harvester programmatically
"""

import logging
from datetime import datetime, timedelta
from harvest_mit_papers import DSpaceHarvester

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_harvest():
    """Example 1: Basic harvest of all papers"""
    logger.info("\n=== Example 1: Basic Harvest ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example1_output')

    # Harvest all records
    records = harvester.get_oai_records()

    # Save results
    harvester.save_json(records, 'all_papers.json')
    harvester.save_csv(records, 'all_papers.csv')

    logger.info(f"Harvested {len(records)} papers")
    return records


def example_2_harvest_by_collection():
    """Example 2: Harvest from specific collection"""
    logger.info("\n=== Example 2: Harvest by Collection ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example2_output')

    # First, list available collections
    logger.info("Available collections:")
    sets = harvester.get_available_sets()
    for s in sets[:5]:  # Show first 5
        logger.info(f"  {s['spec']}: {s['name']}")

    if sets:
        # Harvest from first available collection
        set_spec = sets[0]['spec']
        logger.info(f"Harvesting from: {set_spec}")
        records = harvester.get_oai_records(set_spec=set_spec)
        harvester.save_json(records, f'{set_spec}.json')
        logger.info(f"Harvested {len(records)} papers from collection")

    return sets


def example_3_harvest_by_date():
    """Example 3: Harvest papers from specific date range"""
    logger.info("\n=== Example 3: Harvest by Date Range ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example3_output')

    # Harvest from last 30 days
    from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    logger.info(f"Harvesting records from: {from_date}")

    records = harvester.get_oai_records(from_date=from_date)

    harvester.save_json(records, 'recent_papers.json')
    harvester.save_csv(records, 'recent_papers.csv')

    logger.info(f"Harvested {len(records)} recent papers")
    return records


def example_4_custom_processing():
    """Example 4: Harvest and process data"""
    logger.info("\n=== Example 4: Custom Processing ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example4_output')

    # Harvest records
    records = harvester.get_oai_records()

    # Process data
    logger.info(f"Total papers: {len(records)}")

    # Group by type
    by_type = {}
    for record in records:
        rtype = record.get('type', 'Unknown')
        by_type[rtype] = by_type.get(rtype, 0) + 1

    logger.info("Papers by type:")
    for rtype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {rtype}: {count}")

    # Find papers with multiple authors
    multi_author = [r for r in records if len(r.get('creators', [])) > 1]
    logger.info(f"Papers with multiple authors: {len(multi_author)}")

    # Extract top subjects
    subjects = {}
    for record in records:
        for subject in record.get('subjects', []):
            subjects[subject] = subjects.get(subject, 0) + 1

    logger.info("Top 10 subjects:")
    for subject, count in sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  {subject}: {count}")

    return records


def example_5_incremental_harvest():
    """Example 5: Incremental daily harvest"""
    logger.info("\n=== Example 5: Incremental Harvest ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example5_output')

    # Harvest only today's papers
    today = datetime.now().strftime('%Y-%m-%d')
    logger.info(f"Harvesting papers from: {today}")

    records = harvester.get_oai_records(from_date=today)

    harvester.save_json(records, f'papers_{today}.json')

    logger.info(f"Harvested {len(records)} papers from today")
    return records


def example_6_metadata_exploration():
    """Example 6: Explore metadata structure"""
    logger.info("\n=== Example 6: Metadata Exploration ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example6_output')

    # Harvest small sample
    records = harvester.get_oai_records()

    if records:
        # Show first record
        logger.info("Sample record structure:")
        record = records[0]
        for key, value in record.items():
            if isinstance(value, list):
                logger.info(f"  {key}: {value}")
            else:
                value_str = str(value)[:100]  # Truncate long values
                logger.info(f"  {key}: {value_str}")

        # Statistics
        logger.info("\nMetadata field completeness:")
        fields = ['titles', 'creators', 'subjects', 'description', 'date_issued', 'url']
        for field in fields:
            filled = sum(1 for r in records if r.get(field))
            percentage = (filled / len(records)) * 100
            logger.info(f"  {field}: {percentage:.1f}% ({filled}/{len(records)})")

    return records


def example_7_export_formats():
    """Example 7: Export in different formats"""
    logger.info("\n=== Example 7: Export Formats ===")

    harvester = DSpaceHarvester('https://dspace.mit.edu', './example7_output')

    # Harvest small sample
    records = harvester.get_oai_records()[:50]  # Limit to first 50

    # Export as JSON
    harvester.save_json(records, 'papers.json')
    logger.info("Exported as JSON")

    # Export as CSV
    harvester.save_csv(records, 'papers.csv')
    logger.info("Exported as CSV")

    # Custom export as Tab-separated
    import csv
    with open('./example7_output/papers.tsv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['Title', 'Creator', 'Date', 'URL'])
        for record in records:
            writer.writerow([
                '; '.join(record.get('titles', [])),
                '; '.join(record.get('creators', [])),
                record.get('date_issued', ''),
                record.get('url', '')
            ])
    logger.info("Exported as TSV")

    return records


def example_8_error_handling():
    """Example 8: Robust error handling"""
    logger.info("\n=== Example 8: Error Handling ===")

    # Try with invalid URL (should handle gracefully)
    try:
        harvester = DSpaceHarvester('https://invalid.example.com', './example8_output')
        records = harvester.get_oai_records()
        logger.info(f"Harvested {len(records)} papers")
    except Exception as e:
        logger.error(f"Expected error with invalid URL: {type(e).__name__}")

    # Try with valid URL but invalid set
    try:
        harvester = DSpaceHarvester('https://dspace.mit.edu', './example8_output')
        records = harvester.get_oai_records(set_spec='invalid_set_12345')
        logger.info(f"Harvested {len(records)} papers")
        if not records:
            logger.info("No records found for invalid set (expected behavior)")
    except Exception as e:
        logger.error(f"Error: {e}")

    logger.info("Error handling demonstration complete")


def main():
    """Run all examples"""
    print("\n" + "="*50)
    print("MIT Papers Harvester - Usage Examples")
    print("="*50)

    # Uncomment examples to run (some may require live MIT DSpace connection)
    # Note: These are demonstration examples. Comment out as needed.

    # example_1_basic_harvest()
    # example_2_harvest_by_collection()
    # example_3_harvest_by_date()
    # example_4_custom_processing()
    # example_5_incremental_harvest()
    example_6_metadata_exploration()
    # example_7_export_formats()
    # example_8_error_handling()

    print("\n" + "="*50)
    print("Examples completed!")
    print("="*50)


if __name__ == '__main__':
    main()
