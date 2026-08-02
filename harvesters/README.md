# DARE harvesting and import

The existing harvester (`harvest_cli.py`, on branch
`claude/mit-papers-harvest-script-et7oza`) fetches OAI-PMH records out to JSON.
It does not put anything into DSpace. These tools are the second half.

```
harvest_cli.py  →  harvested_papers.json  →  saf_builder.py  →  SAF  →  import-to-dspace.sh  →  DARE
```

## The pipeline

```bash
# 1. Verify the endpoint is real before harvesting it
python3 probe_sources.py --config sources.yaml --write

# 2. Harvest (existing tool)
python3 harvest_cli.py --url https://ir.uz.ac.zw --recent 90

# 3. Convert to Simple Archive Format — see what it would do first
python3 saf_builder.py \
    --input harvest_output/harvested_papers.json \
    --output saf_uz \
    --source-name "University of Zimbabwe Institutional Repository" \
    --source-url "https://ir.uz.ac.zw" \
    --dry-run

python3 saf_builder.py --input ... --output saf_uz --source-name ... --source-url ...

# 4. Import — test pass only, nothing created
DSPACE_EPERSON=admin@dare.co.zw ./import-to-dspace.sh saf_uz 123456789/42

# 5. Import for real
DSPACE_EPERSON=admin@dare.co.zw ./import-to-dspace.sh saf_uz 123456789/42 --live
```

## PROVENANCE

Every imported record carries, and this is not configurable:

| Field | Content |
|---|---|
| `dc.source` | Source repository name and URL |
| `dc.relation.uri` | The original item's URL |
| `dc.identifier.other` | The OAI identifier |
| `dc.description.provenance` | Harvest date, origin, and a note that the authoritative copy stays with the source |

A repository that presents harvested metadata as its own holdings misleads its
users, inflates its own statistics, and damages its standing with aggregators
that harvest DARE in turn. `sources.yaml` sets `separate_collection: true` for
the same reason: harvested records belong in their own collection, so a visitor
can tell what DARE **holds** from what DARE **indexes**.

`dc.identifier.uri` is deliberately *not* set to the source URL. DSpace assigns
that field the item's own handle at import; writing the origin there would make
DARE's handle resolution point at another repository.

## Safety properties

**`saf_builder.py`**
- Idempotent. A manifest keyed on OAI identifier means re-running adds only new
  records. Verified: a second run over the same input creates nothing.
- Records without a title are skipped — DSpace will accept them and they are
  unusable afterwards.
- Dates are normalised to the three shapes DSpace accepts (`YYYY`, `YYYY-MM`,
  `YYYY-MM-DD`). Anything else, `n.d.` included, is dropped rather than imported
  as junk.
- All metadata is XML-escaped. Titles containing `&` or `<` are common and will
  otherwise produce a batch that fails halfway through the import.

**`import-to-dspace.sh`**
- Validates the batch before touching DSpace. A malformed `dublin_core.xml`
  aborts an import partway, leaving some items created and some not.
- Runs DSpace's own `--test` pass first. `--live` is required to create anything.
- Keeps the mapfile outside the container. **This is the only record of what an
  import created** and the only way to undo it:
  ```bash
  dspace import --delete --mapfile=<mapfile>
  ```
  The mapfile is recovered even when the import fails partway.
- Reindexes Discovery afterwards. Skipping that is the usual reason a
  "successful" import appears to have done nothing — the items exist but do not
  appear in search or browse.

**`probe_sources.py`**
- Issues a real `Identify` request and accepts only well-formed OAI-PMH.
  Most repositories answer an unknown path with an HTML 404, which an XML parser
  reads as "no records" and a harvester reports as a successful empty run.
- Tries the DSpace 7/8/9 path (`/server/oai/request`), the DSpace 5/6 path
  (`/oai/request`), and the OJS and Invenio conventions.

## Sources

`sources.yaml` lists Zimbabwean institutional repositories, African
aggregators, and the existing MIT configuration.

**Every endpoint is marked `verified: false` and should be treated as a
candidate, not a fact.** Host names and OAI paths change, and several of these
institutions have rebuilt their repositories in recent years. Run the probe from
the server before harvesting anything.

## Housekeeping

`harvesters/` on the server is 9.1 GB, most of it `harvest_output/`, a `venv/`
and an accidental nested clone of this repository. `.gitignore` excludes all
three. Worth confirming whether the harvested output is reproducible from these
scripts before it is treated as data worth keeping — it sits on the same
unbacked-up disk as the repository itself.
