#!/usr/bin/env python3
"""
Command-line interface for MIT Papers Harvester
Usage: python harvest_cli.py --url <dspace-url> [options]
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

from harvest_mit_papers import DSpaceHarvester

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Harvest MIT papers from DSpace 9 repositories using OAI-PMH protocol',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Harvest all papers from MIT DSpace
  %(prog)s --url https://dspace.mit.edu

  # Harvest papers from specific collection
  %(prog)s --url https://dspace.mit.edu --set "com_123_456"

  # Harvest papers from last 30 days
  %(prog)s --url https://dspace.mit.edu --recent 30

  # Harvest with custom date range
  %(prog)s --url https://dspace.mit.edu --from 2024-01-01 --until 2024-12-31

  # Harvest and save as both JSON and CSV
  %(prog)s --url https://dspace.mit.edu --formats json csv

  # List available collections
  %(prog)s --url https://dspace.mit.edu --list-sets
        """
    )

    parser.add_argument(
        '--url', '-u',
        required=True,
        help='Base URL of DSpace repository (e.g., https://dspace.mit.edu)'
    )

    parser.add_argument(
        '--output', '-o',
        default='./harvest_output',
        help='Output directory for harvested data (default: ./harvest_output)'
    )

    parser.add_argument(
        '--set', '-s',
        help='Specific collection/set to harvest (e.g., com_123_456)'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv', 'both'],
        default='both',
        help='Output format (default: both)'
    )

    parser.add_argument(
        '--from',
        metavar='DATE',
        help='Start date for harvest (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--until',
        metavar='DATE',
        help='End date for harvest (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--recent',
        type=int,
        metavar='DAYS',
        help='Harvest records from last N days'
    )

    parser.add_argument(
        '--metadata-prefix',
        default='oai_dc',
        help='Metadata format (default: oai_dc)'
    )

    parser.add_argument(
        '--list-sets',
        action='store_true',
        help='List available sets and exit'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    return parser.parse_args()


def setup_logging(level: str):
    """Configure logging"""
    numeric_level = getattr(logging, level)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('harvest.log'),
            logging.StreamHandler()
        ]
    )


def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def main():
    """Main CLI entry point"""
    args = parse_arguments()

    # Setup logging
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)

    # Validate dates
    if args.__dict__.get('from') and not validate_date(args.__dict__['from']):
        logger.error("Invalid 'from' date format. Use YYYY-MM-DD")
        sys.exit(1)

    if args.__dict__.get('until') and not validate_date(args.__dict__['until']):
        logger.error("Invalid 'until' date format. Use YYYY-MM-DD")
        sys.exit(1)

    if args.recent and args.recent < 0:
        logger.error("Recent days must be positive")
        sys.exit(1)

    # Initialize harvester
    logger.info(f"Initializing harvester for: {args.url}")
    harvester = DSpaceHarvester(args.url, args.output)

    # Option 1: List available sets
    if args.list_sets:
        logger.info("\n=== Available Collections ===")
        sets = harvester.get_available_sets()
        if sets:
            for s in sets:
                print(f"{s['spec']:40} | {s['name']}")
        else:
            logger.warning("No sets found or unable to retrieve sets")
        sys.exit(0)

    # Prepare harvest parameters
    from_date = None
    until_date = None

    if args.recent:
        from_date = (datetime.now() - timedelta(days=args.recent)).strftime('%Y-%m-%d')
        logger.info(f"Harvesting records from the last {args.recent} days (since {from_date})")

    if args.__dict__.get('from'):
        from_date = args.__dict__['from']

    if args.__dict__.get('until'):
        until_date = args.__dict__['until']

    # Execute harvest
    logger.info("\n=== Starting Harvest ===")
    logger.info(f"Repository: {args.url}")
    logger.info(f"Set: {args.set or 'All collections'}")
    logger.info(f"Format: {args.metadata_prefix}")

    records = harvester.get_oai_records(
        set_spec=args.set,
        metadata_prefix=args.metadata_prefix,
        from_date=from_date,
        until_date=until_date
    )

    if not records:
        logger.warning("No records harvested")
        sys.exit(0)

    # Save output
    logger.info("\n=== Saving Output ===")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_filename = f"mit_papers_{timestamp}"

    if args.format in ['json', 'both']:
        harvester.save_json(records, f'{base_filename}.json')

    if args.format in ['csv', 'both']:
        harvester.save_csv(records, f'{base_filename}.csv')

    logger.info(f"\n=== Harvest Complete ===")
    logger.info(f"Total records: {len(records)}")
    logger.info(f"Output directory: {Path(args.output).absolute()}")


if __name__ == '__main__':
    main()
