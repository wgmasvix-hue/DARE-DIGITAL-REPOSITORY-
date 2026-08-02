#!/usr/bin/env python3
"""
saf_builder.py — turn harvested OAI-PMH records into a DSpace Simple Archive
Format batch, ready for `dspace import`.

The existing harvester writes JSON to ./harvest_output but never puts anything
into DSpace. This is the missing half.

    harvest_cli.py  ->  harvested_papers.json  ->  [this]  ->  SAF  ->  dspace import

Provenance is not optional here. Every item carries the source repository, the
original URL and the OAI identifier, because a repository that presents
harvested records as its own holdings misleads its users and its aggregators.
See PROVENANCE in the README.

Usage:
    python3 saf_builder.py --input harvest_output/harvested_papers.json \\
                           --output saf_batch \\
                           --source-name "MIT Main Repository" \\
                           --source-url  "https://dspace.mit.edu" \\
                           --dry-run
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

# Records already turned into SAF, so re-runs are safe and incremental.
MANIFEST_NAME = ".saf-manifest.json"


# ---------------------------------------------------------------------------
# Metadata mapping
# ---------------------------------------------------------------------------

def normalise_date(raw):
    """
    OAI-DC dates arrive as 2024, 2024-05, 2024-05-17, or a full timestamp.
    DSpace accepts all three shapes for dc.date.issued, but not free text, so
    anything unrecognised is dropped rather than imported as garbage.
    """
    if not raw:
        return None
    raw = str(raw).strip()
    m = re.match(r'^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?', raw)
    if not m:
        return None
    year, month, day = m.group(1), m.group(2), m.group(3)
    if year and month and day:
        return f"{year}-{month}-{day}"
    if year and month:
        return f"{year}-{month}"
    return year


def dcvalue(element, qualifier, value, language=None):
    """One <dcvalue> line, XML-escaped."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    qual = qualifier if qualifier else "none"
    lang = f' language="{escape(language)}"' if language else ""
    return (f'  <dcvalue element="{element}" qualifier="{qual}"{lang}>'
            f'{escape(value)}</dcvalue>')


def build_dublin_core(record, source_name, source_url, harvested_on):
    """
    Map a harvested OAI-DC record onto DSpace Dublin Core.

    Deliberate choices:
      * dc.identifier.uri is NOT set to the source URL. DSpace assigns that
        field the item's own handle on import; writing the origin there would
        make DARE's handle resolution point at another repository.
        The origin goes to dc.relation.uri instead.
      * dc.creator is mapped to dc.contributor.author, which is what DSpace's
        browse and author facets actually index.
    """
    lines = []

    titles = record.get('titles') or []
    if not titles:
        return None                       # a record with no title is unusable
    lines.append(dcvalue("title", None, titles[0]))
    for extra in titles[1:]:
        lines.append(dcvalue("title", "alternative", extra))

    for creator in record.get('creators') or []:
        lines.append(dcvalue("contributor", "author", creator))

    for subject in record.get('subjects') or []:
        lines.append(dcvalue("subject", None, subject))

    lines.append(dcvalue("description", "abstract", record.get('description')))
    lines.append(dcvalue("date", "issued", normalise_date(record.get('date_issued'))))
    lines.append(dcvalue("type", None, record.get('type')))
    lines.append(dcvalue("rights", None, record.get('rights')))
    lines.append(dcvalue("language", "iso", record.get('language')))
    lines.append(dcvalue("publisher", None, record.get('publisher')))

    # --- Provenance ---------------------------------------------------------
    # What makes a harvested record honest rather than a claim of ownership.
    lines.append(dcvalue("source", None, f"{source_name} ({source_url})"))
    lines.append(dcvalue("relation", "uri", record.get('url')))
    lines.append(dcvalue("identifier", "other", record.get('identifier')))
    lines.append(dcvalue(
        "description", "provenance",
        f"Metadata harvested via OAI-PMH from {source_name} <{source_url}> "
        f"on {harvested_on}. Original record: {record.get('identifier', 'unknown')}. "
        f"This item is a metadata record; the authoritative copy remains with "
        f"the source repository."
    ))

    body = "\n".join(line for line in lines if line)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<dublin_core schema="dc">\n{body}\n</dublin_core>\n'


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def record_key(record):
    """
    Prefer the OAI identifier — stable and unique per source. Fall back to a
    hash of title plus date so records lacking an identifier still dedupe.
    """
    ident = (record.get('identifier') or '').strip()
    if ident:
        return ident
    titles = record.get('titles') or []
    basis = (titles[0] if titles else '') + '|' + str(record.get('date_issued') or '')
    if not basis.strip('|'):
        return None
    return "sha1:" + hashlib.sha1(basis.encode('utf-8')).hexdigest()


def load_manifest(path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            print(f"  ! {path} is corrupt; treating as empty", file=sys.stderr)
    return {"imported": {}, "created": {}}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--input', required=True, help='harvested JSON file')
    ap.add_argument('--output', default='saf_batch', help='SAF output directory')
    ap.add_argument('--source-name', required=True, help='e.g. "MIT Main Repository"')
    ap.add_argument('--source-url', required=True, help='e.g. "https://dspace.mit.edu"')
    ap.add_argument('--manifest', default=None,
                    help=f'dedupe manifest (default: <output>/{MANIFEST_NAME})')
    ap.add_argument('--limit', type=int, default=0, help='stop after N new records')
    ap.add_argument('--dry-run', action='store_true',
                    help='report what would be built; write nothing')
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        sys.exit(f"ERROR: {in_path} not found")

    try:
        records = json.loads(in_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        sys.exit(f"ERROR: {in_path} is not valid JSON — {e}")

    if isinstance(records, dict):          # tolerate {"records": [...]}
        records = records.get('records', [])
    if not isinstance(records, list):
        sys.exit("ERROR: expected a JSON list of records")

    out_dir = Path(args.output)
    manifest_path = Path(args.manifest) if args.manifest else out_dir / MANIFEST_NAME
    manifest = load_manifest(manifest_path)
    seen = set(manifest.get("created", {})) | set(manifest.get("imported", {}))

    harvested_on = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    print(f"Source     : {args.source_name} <{args.source_url}>")
    print(f"Input      : {in_path}  ({len(records)} records)")
    print(f"Output     : {out_dir}")
    print(f"Already in manifest: {len(seen)}")
    print(f"Mode       : {'DRY RUN — nothing written' if args.dry_run else 'build'}")
    print()

    stats = {"new": 0, "duplicate": 0, "no_title": 0, "no_key": 0}
    index = max((int(d.name.split('_')[1]) for d in out_dir.glob('item_*')
                 if d.name.split('_')[-1].isdigit()), default=0)

    for record in records:
        key = record_key(record)
        if key is None:
            stats["no_key"] += 1
            continue
        if key in seen:
            stats["duplicate"] += 1
            continue

        dc_xml = build_dublin_core(record, args.source_name, args.source_url, harvested_on)
        if dc_xml is None:
            stats["no_title"] += 1
            continue

        stats["new"] += 1
        index += 1
        item_dir = out_dir / f"item_{index:05d}"

        if not args.dry_run:
            item_dir.mkdir(parents=True, exist_ok=True)
            (item_dir / "dublin_core.xml").write_text(dc_xml, encoding='utf-8')
            # Metadata-only item: `contents` must exist but stays empty. DSpace
            # treats a missing contents file as an error, not as "no bitstreams".
            (item_dir / "contents").write_text("", encoding='utf-8')
            manifest.setdefault("created", {})[key] = {
                "dir": item_dir.name,
                "title": (record.get('titles') or [''])[0][:200],
                "built": harvested_on,
            }

        seen.add(key)
        if args.limit and stats["new"] >= args.limit:
            break

    if not args.dry_run and stats["new"]:
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                 encoding='utf-8')

    print(f"  new items      : {stats['new']}")
    print(f"  duplicates     : {stats['duplicate']}  (already in manifest)")
    print(f"  skipped, no title : {stats['no_title']}")
    print(f"  skipped, no key   : {stats['no_key']}")
    print()

    if args.dry_run:
        print("Dry run — nothing written.")
        return 0

    if not stats["new"]:
        print("Nothing new to import.")
        return 0

    print(f"Wrote {stats['new']} item(s) to {out_dir}")
    print(f"Manifest: {manifest_path}")
    print()
    print("Next: validate, then import into a collection reserved for harvested")
    print("records — not alongside local deposits.")
    print()
    print(f"    python3 {Path(__file__).name} --validate {out_dir}")
    print(f"    ./import-to-dspace.sh {out_dir} <collection-handle>")
    return 0


if __name__ == '__main__':
    # A standalone validation mode, so a batch can be checked without rebuilding.
    if len(sys.argv) == 3 and sys.argv[1] == '--validate':
        target = Path(sys.argv[2])
        bad = 0
        items = sorted(target.glob('item_*'))
        for item in items:
            for required in ('dublin_core.xml', 'contents'):
                if not (item / required).exists():
                    print(f"  ✗ {item.name}: missing {required}")
                    bad += 1
            dc = item / 'dublin_core.xml'
            if dc.exists():
                import xml.etree.ElementTree as ET
                try:
                    root = ET.parse(dc).getroot()
                    if not root.findall(".//dcvalue[@element='title']"):
                        print(f"  ✗ {item.name}: no dc.title")
                        bad += 1
                except ET.ParseError as e:
                    print(f"  ✗ {item.name}: malformed XML — {e}")
                    bad += 1
        print(f"\n{len(items)} item(s) checked, {bad} problem(s)")
        sys.exit(1 if bad else 0)
    sys.exit(main())
