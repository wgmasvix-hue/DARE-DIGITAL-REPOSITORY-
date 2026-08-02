# Migrating the DARE DSpace server into this repository

This document explains what moves into git, what deliberately does not, and how to
run the collection.

## What this repo is

A **deployment repository** for the DSpace 9.x instance serving
`dspace.dare.co.zw`. It should be enough to rebuild the instance from scratch,
given a database backup and an assetstore backup restored separately.

## The three categories

DSpace on a server is three different things. They do not all belong in the same place.

### 1. Deployment configuration and customisations — YES, in git

- `local.cfg`, `dspace.cfg`, `config/modules/*.cfg`
- Submission forms (`submission-forms.xml`, `item-submission.xml`)
- Spring configuration, crosswalks, metadata registries
- Controlled vocabularies
- Email templates
- The custom Angular theme and `config.prod.yml`
- `docker-compose.yml`, Dockerfiles, nginx / TLS configuration
- CI workflows

These are text, they are reviewable, and they are what makes the instance *yours*.

### 2. DSpace source code — NOT copied in

DSpace 9 backend (`DSpace/DSpace`) and frontend (`DSpace/dspace-angular`) are large
upstream codebases. Copying them into this repo means you can never cleanly take an
upstream security patch again.

The right pattern is to build from the official images pinned to your version, and
layer only your theme and config on top. If you have genuine Java-side code changes,
those should live in a **fork** of `DSpace/DSpace` so upstream merges stay possible.

### 3. Repository content — NEVER in git

| Content | Where it belongs |
|---|---|
| PostgreSQL database | Encrypted `pg_dump` to object storage, on a schedule |
| Assetstore (the actual deposited files) | Object storage / filesystem backup, on a schedule |
| Solr indexes | Rebuilt from the database — never backed up, never committed |

The database is the important one to be firm about. A DSpace `eperson` table holds
registered users' full names, email addresses, and bcrypt password hashes. Pushing it
to a GitHub repository publishes that. Even in a private repo it is the wrong control
boundary, and git history makes it effectively permanent. `.gitignore` in this repo
blocks `*.sql`, `*.dump` and `assetstore/` for exactly this reason.

## Running the collection

On the **DSpace server**:

```bash
# 1. Get this repo onto the server
git clone <this-repo-url> dare-repo
cd dare-repo
git checkout claude/server-repo-migration-k3ej1e

# 2. Look at what would be collected — nothing is written, nothing is pushed
./scripts/collect-from-server.sh --dry-run

# 3. Collect into ./deploy, with secrets redacted
./scripts/collect-from-server.sh

# 4. Read the report and diff. This is the step that matters.
cat collect-report-*.txt
git status
git diff

# 5. Only when you are satisfied
git add -A && git commit -m "Add DSpace deployment config from server"
git push -u origin claude/server-repo-migration-k3ej1e
```

The script defaults to safe behaviour: it never pushes, it never deletes, it reads
your DSpace install read-only, and it redacts credentials before writing anything.

### Autodetection

The script looks for your DSpace install in this order:

1. `--dspace-home <path>` if you pass it
2. `$DSPACE_HOME`
3. `/dspace`, `/opt/dspace`, `/srv/dspace`, `/usr/local/dspace`
4. A running DSpace container, if Docker is present

Frontend is found via `--frontend <path>`, `$DSPACE_FRONTEND`, or by looking for a
`dspace-angular` checkout next to the backend.

## Secret redaction

Any config value whose key matches a credential pattern — `*password*`, `*secret*`,
`*.client-id`, `jwt.*`, `s3.*key*`, `mail.server.username`, and others — is replaced
with `__REDACTED__` before the file is written into `deploy/`.

Every redaction is recorded in `deploy/SECRETS.md` along with the Docker environment
variable that supplies it at runtime (DSpace 9 maps `db.password` to
`DSPACE__P__db_password`). That file lists *which* secrets exist and how to inject
them — never their values.

After redaction the script runs a scan for anything that still looks like a live
credential. If it finds something, it stops and tells you rather than writing the file.

**Redaction is a safety net, not a substitute for reading the diff.** Review
`git diff` before you commit.

## What to set up separately

These are outside this repo, and worth doing:

- Scheduled encrypted `pg_dump` of the DSpace database to object storage
- Scheduled assetstore sync to object storage
- A tested *restore* procedure — an untested backup is not a backup
- Rotation of any credential that has previously been committed anywhere
