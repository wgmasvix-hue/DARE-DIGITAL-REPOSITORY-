#!/usr/bin/env python3
"""
probe_sources.py — verify OAI-PMH endpoints before harvesting them.

A wrong base URL rarely fails loudly. Most repositories answer an unknown path
with an HTML 404 page, which an XML parser reads as "no records" and a
harvester reports as a successful run that found nothing. This probe issues a
real Identify request and only accepts a well-formed OAI-PMH response.

    python3 probe_sources.py --config sources.yaml           # probe all
    python3 probe_sources.py --config sources.yaml --write   # record results
    python3 probe_sources.py --url https://ir.uz.ac.zw       # probe one host

Run it from the server; this needs outbound internet access.
"""

import argparse
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")
try:
    import yaml
except ImportError:
    yaml = None

OAI_NS = "{http://www.openarchives.org/OAI/2.0/}"

# Tried in order. The DSpace 7+ path first, since that is what a current
# installation serves.
CANDIDATE_PATHS = [
    "/server/oai/request",      # DSpace 7, 8, 9
    "/oai/request",             # DSpace 5, 6
    "/oai",                     # some proxied setups
    "/index.php/index/oai",     # OJS
    "/oai2d",                   # Zenodo / Invenio
    "/dspace-oai/request",      # older deployments
]

USER_AGENT = "DARE-Harvester/1.0 (+https://dare.co.zw; repository@dare.co.zw)"


def probe_one(base, path, timeout=20):
    """Issue Identify. Return (ok, detail) — ok only for real OAI-PMH XML."""
    url = urljoin(base.rstrip('/') + '/', path.lstrip('/'))
    try:
        r = requests.get(url, params={"verb": "Identify"},
                         timeout=timeout,
                         headers={"User-Agent": USER_AGENT},
                         allow_redirects=True)
    except requests.exceptions.SSLError as e:
        return False, f"TLS error ({str(e)[:60]})"
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.RequestException as e:
        return False, f"{type(e).__name__}"

    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"

    ctype = r.headers.get('Content-Type', '')
    if 'xml' not in ctype.lower():
        # The failure mode this whole script exists to catch.
        return False, f"not XML ({ctype.split(';')[0] or 'unknown'})"

    try:
        root = ET.fromstring(r.content)
    except ET.ParseError as e:
        return False, f"malformed XML ({str(e)[:40]})"

    if not root.tag.endswith('OAI-PMH'):
        return False, f"not OAI-PMH (root <{root.tag.split('}')[-1]}>)"

    err = root.find(f"{OAI_NS}error")
    if err is not None:
        return False, f"OAI error: {err.get('code')}"

    ident = root.find(f"{OAI_NS}Identify")
    if ident is None:
        return False, "no Identify element"

    name = ident.findtext(f"{OAI_NS}repositoryName", "").strip()
    gran = ident.findtext(f"{OAI_NS}granularity", "").strip()
    return True, f"{name or 'unnamed'} [{gran or 'granularity unknown'}]"


def probe_host(base, explicit_path=None, delay=1.0):
    paths = [explicit_path] if explicit_path else CANDIDATE_PATHS
    attempts = []
    for path in paths:
        ok, detail = probe_one(base, path)
        attempts.append((path, ok, detail))
        if ok:
            return path, detail, attempts
        time.sleep(delay)
    return None, None, attempts


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', help='sources.yaml')
    ap.add_argument('--url', help='probe a single host instead')
    ap.add_argument('--write', action='store_true',
                    help='write verified paths back into the config')
    ap.add_argument('--delay', type=float, default=1.0,
                    help='seconds between requests (default 1.0)')
    args = ap.parse_args()

    if args.url:
        path, detail, attempts = probe_host(args.url, delay=args.delay)
        for p, ok, d in attempts:
            print(f"  {'✓' if ok else '✗'} {p:<24} {d}")
        if path:
            print(f"\nOAI endpoint: {args.url.rstrip('/')}{path}")
            return 0
        print("\nNo OAI-PMH endpoint found. The repository may not expose one, "
              "may sit behind a different path, or may be offline.")
        return 1

    if not args.config:
        ap.error("give --config or --url")
    if yaml is None:
        sys.exit("ERROR: pip install PyYAML")

    cfg = yaml.safe_load(open(args.config))
    groups = [k for k in cfg if k not in ('defaults', 'policy')]

    total = ok_count = 0
    for group in groups:
        entries = cfg[group]
        if not isinstance(entries, dict):
            continue
        print(f"\n{group.upper()}")
        print("-" * 62)
        for key, src in entries.items():
            if not isinstance(src, dict) or 'host' not in src:
                continue
            total += 1
            host = src['host']
            print(f"  {src.get('name', key)}")
            print(f"    {host}")
            path, detail, attempts = probe_host(host, src.get('oai_path'),
                                                delay=args.delay)
            if path:
                ok_count += 1
                print(f"    ✓ {path}  ->  {detail}")
                src['oai_path'] = path
                src['verified'] = True
            else:
                reasons = "; ".join(f"{p}: {d}" for p, _, d in attempts[:3])
                print(f"    ✗ no endpoint  ({reasons})")
                src['verified'] = False

    print(f"\n{ok_count}/{total} source(s) verified")

    if args.write:
        with open(args.config, 'w') as f:
            yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
        print(f"Updated {args.config}")
    elif ok_count:
        print("Re-run with --write to record these paths.")

    return 0 if ok_count else 1


if __name__ == '__main__':
    sys.exit(main())
