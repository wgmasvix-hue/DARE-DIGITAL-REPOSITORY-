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
import socket
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
    "/jspui/oai/request",       # DSpace 5/6 deployed under /jspui (common in ZW)
    "/xmlui/oai/request",       # DSpace 5/6 under /xmlui
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


def resolves(host_url):
    """
    Separate "this hostname does not exist" from "the server refused us".
    Both surface as ConnectionError from requests, but they need entirely
    different fixes — a wrong name versus a firewall or a dead service.
    """
    name = host_url.split('//', 1)[-1].split('/')[0].split(':')[0]
    try:
        return True, socket.gethostbyname(name)
    except socket.gaierror as e:
        return False, str(e)


def probe_host(base, explicit_path=None, delay=1.0, timeout=20):
    """
    Try each candidate path over HTTPS, then fall back to HTTP.

    Plenty of regional repositories still serve plain HTTP, or present an
    expired certificate. Refusing to look at those means reporting a live
    repository as dead.
    """
    ok_dns, dns_detail = resolves(base)
    if not ok_dns:
        return None, None, [("(dns)", False, f"does not resolve — {dns_detail}")]

    paths = [explicit_path] if explicit_path else CANDIDATE_PATHS
    attempts = []

    schemes = [base]
    if base.startswith('https://'):
        schemes.append('http://' + base[len('https://'):])

    for scheme_base in schemes:
        label = '' if scheme_base == base else ' [http]'
        for path in paths:
            ok, detail = probe_one(scheme_base, path, timeout=timeout)
            attempts.append((path + label, ok, detail))
            if ok:
                return (path if not label else scheme_base.rstrip('/') + path), detail, attempts
            time.sleep(delay)
    return None, None, attempts


def update_config_in_place(path, results):
    """
    Rewrite only `verified:` and `oai_path:` under each source key, leaving
    every comment and every other line exactly as authored.
    """
    lines = open(path).read().split('\n')
    current = None
    changed = 0
    out = []
    for line in lines:
        stripped = line.strip()
        # A source key: two-space indent, ends in a colon, no value.
        if line.startswith('  ') and not line.startswith('    ') \
           and stripped.endswith(':') and not stripped.startswith('#'):
            current = stripped[:-1]
        elif line and not line.startswith(' '):
            current = None

        if current in results:
            r = results[current]
            if stripped.startswith('verified:'):
                indent = line[:len(line) - len(line.lstrip())]
                comment = line.split('#', 1)[1] if '#' in line else None
                new = f"{indent}verified: {str(r['verified']).lower()}"
                if comment:
                    new += f"  #{comment}"
                if new != line:
                    changed += 1
                out.append(new)
                continue
            if stripped.startswith('oai_path:') and r.get('oai_path'):
                indent = line[:len(line) - len(line.lstrip())]
                new = f'{indent}oai_path: "{r["oai_path"]}"'
                if new != line:
                    changed += 1
                out.append(new)
                continue
        out.append(line)

    open(path, 'w').write('\n'.join(out))
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', help='sources.yaml')
    ap.add_argument('--url', help='probe a single host instead')
    ap.add_argument('--write', action='store_true',
                    help='write verified paths back into the config')
    ap.add_argument('--delay', type=float, default=1.0,
                    help='seconds between requests (default 1.0)')
    ap.add_argument('--timeout', type=float, default=20,
                    help='per-request timeout in seconds (default 20). Regional\n'
                         'university servers are often slow; try 60 before\n'
                         'concluding a host is dead.')
    ap.add_argument('--only', help='probe just this key, e.g. nust')
    args = ap.parse_args()

    if args.url:
        path, detail, attempts = probe_host(args.url, delay=args.delay,
                                            timeout=args.timeout)
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

    results = {}
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
            if args.only and key != args.only:
                continue
            total += 1
            host = src['host']
            print(f"  {src.get('name', key)}")
            print(f"    {host}")
            path, detail, attempts = probe_host(host, src.get('oai_path'),
                                                delay=args.delay,
                                                timeout=args.timeout)
            if path:
                ok_count += 1
                print(f"    ✓ {path}  ->  {detail}")
                src['oai_path'] = path
                src['verified'] = True
                results[key] = {'verified': True, 'oai_path': path}
            else:
                uniq = []
                for p, _, d in attempts:
                    if d not in [x.split(": ",1)[-1] for x in uniq]:
                        uniq.append(f"{p}: {d}")
                reasons = "; ".join(uniq[:4])
                print(f"    ✗ no endpoint  ({reasons})")
                src['verified'] = False
                results[key] = {'verified': False}

    print(f"\n{ok_count}/{total} source(s) verified")

    if args.write:
        # Surgical, line-based update. yaml.safe_dump would round-trip the file
        # and silently discard every comment in it, including the policy
        # rationale — which is most of the value of this config.
        written = update_config_in_place(args.config, results)
        print(f"Updated {args.config} ({written} field(s) changed; comments preserved)")
    elif ok_count:
        print("Re-run with --write to record these paths.")

    return 0 if ok_count else 1


if __name__ == '__main__':
    sys.exit(main())
