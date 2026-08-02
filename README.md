# DARE Digital Repository

Deployment repository for the DARE DSpace 9.x instance at
[dspace.dare.co.zw](https://dspace.dare.co.zw), plus the public landing page.

## Layout

```
index.html                      Landing page for dare.co.zw
scripts/collect-from-server.sh  Collects deployment config from the DSpace server
deploy/                         Collected configuration (created by the script)
  backend/config/               dspace.cfg, local.cfg.example, modules, spring, forms
  frontend/                     Custom Angular theme and config
  docker/                       Compose files and Dockerfiles
  webserver/                    nginx / apache vhosts
  SECRETS.md                    Which secrets are required, and how to inject them
docs/MIGRATION.md               Full migration procedure and rationale
.github/workflows/              CI
```

## Getting the server config in here

This repo is populated *from* the running server — run the collector there:

```bash
./scripts/collect-from-server.sh --dry-run   # see what it would take
./scripts/collect-from-server.sh             # collect, with secrets redacted
```

It reads the DSpace install read-only, never touches repository content, redacts
credentials before writing, and refuses to proceed if anything sensitive survives.
It does not commit and does not push — you review the diff and decide.

Full procedure: [docs/MIGRATION.md](docs/MIGRATION.md).

## What lives here, and what does not

| | |
|---|---|
| ✅ Deployment config, custom theme, submission forms, compose files, CI | In this repo |
| ⚠️ DSpace source (backend + `dspace-angular`) | Upstream images pinned to version; fork only if you have Java changes |
| ❌ PostgreSQL database, assetstore, Solr indexes | Backups / object storage — **never git** |

That last row is deliberate. The DSpace `eperson` table contains registered users'
names, email addresses and password hashes; the assetstore is gigabytes of deposited
files. Neither belongs in version control, and git history would make the exposure
permanent. `.gitignore` blocks `*.sql`, `*.dump` and `assetstore/` so it cannot happen
by accident.

Set up scheduled encrypted database dumps and assetstore sync to object storage
separately — and test the restore.

## Secrets

No credential values are stored in this repo. `deploy/SECRETS.md` lists which secrets
the deployment needs and the `DSPACE__P__*` environment variable that supplies each
one at runtime. Real values go in a local `.env`, which is gitignored.
