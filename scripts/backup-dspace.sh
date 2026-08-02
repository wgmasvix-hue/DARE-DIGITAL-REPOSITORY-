#!/usr/bin/env bash
#
# backup-dspace.sh — back up DSpace repository content: the PostgreSQL
# database and the assetstore.
#
# These are the two things that cannot be rebuilt. Configuration lives in git;
# Solr indexes are regenerated from the database. Lose the database or the
# assetstore and the repository is gone.
#
# The output of this script must NEVER be committed to git — it contains
# registered users' names, email addresses and password hashes. .gitignore
# blocks *.sql, *.dump and *.tar.gz for that reason.
#
# Usage:
#   ./scripts/backup-dspace.sh --dry-run        # show what it would do
#   ./scripts/backup-dspace.sh                  # run a backup
#   ./scripts/backup-dspace.sh --dest /mnt/bak  # custom destination
#
# Install as a nightly cron job:
#   ./scripts/backup-dspace.sh --install-cron

set -euo pipefail

DEST="${DSPACE_BACKUP_DIR:-/var/backups/dspace}"
DB_CONTAINER="${DSPACE_DB_CONTAINER:-}"
APP_CONTAINER="${DSPACE_APP_CONTAINER:-}"
KEEP="${DSPACE_BACKUP_KEEP:-7}"
DRY_RUN=0
INSTALL_CRON=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)      DRY_RUN=1; shift ;;
    --dest)         DEST="${2:?--dest needs a path}"; shift 2 ;;
    --keep)         KEEP="${2:?--keep needs a number}"; shift 2 ;;
    --db)           DB_CONTAINER="${2:?}"; shift 2 ;;
    --app)          APP_CONTAINER="${2:?}"; shift 2 ;;
    --install-cron) INSTALL_CRON=1; shift ;;
    -h|--help)      sed -n '2,22p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""
fi
ok()   { printf '%s\n' "${C_GREEN}  ✓${C_RESET} $*"; }
info() { printf '%s\n' "  $*"; }
warn() { printf '%s\n' "${C_YELLOW}  !${C_RESET} $*"; }
fail() { printf '%s\n' "${C_RED}ERROR:${C_RESET} $*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || fail "docker not found"

# --------------------------------------------------------------------------
# Find the containers
# --------------------------------------------------------------------------

[[ -n "$DB_CONTAINER" ]] || DB_CONTAINER="$(
  docker ps --format '{{.Names}}\t{{.Image}}' 2>/dev/null \
    | grep -iE 'postgres|pgsql|dspacedb' | head -1 | cut -f1 || true)"
[[ -n "$APP_CONTAINER" ]] || APP_CONTAINER="$(
  docker ps --format '{{.Names}}\t{{.Image}}' 2>/dev/null \
    | grep -iE 'dspace/dspace:|dspace-backend' | head -1 | cut -f1 || true)"

[[ -n "$DB_CONTAINER" ]] || fail "Could not find the PostgreSQL container. Pass --db <name>."
[[ -n "$APP_CONTAINER" ]] || warn "Could not find the DSpace backend container; assetstore may be skipped."

# Credentials come from the container's own environment, not from us.
db_env() { docker exec "$DB_CONTAINER" printenv "$1" 2>/dev/null || true; }
DB_NAME="$(db_env POSTGRES_DB)";  DB_NAME="${DB_NAME:-dspace}"
DB_USER="$(db_env POSTGRES_USER)"; DB_USER="${DB_USER:-dspace}"

# Where the assetstore actually lives, according to Docker.
ASSETSTORE_HOST=""
if [[ -n "$APP_CONTAINER" ]]; then
  ASSETSTORE_HOST="$(docker inspect "$APP_CONTAINER" --format \
    '{{range .Mounts}}{{if eq .Destination "/dspace/assetstore"}}{{.Source}}{{end}}{{end}}' 2>/dev/null || true)"
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
TARGET="${DEST}/${STAMP}"

printf '%s\n' "${C_BOLD}DSpace backup${C_RESET}"
printf '%s\n' "${C_DIM}$(date -Is)${C_RESET}"
echo
info "database container : ${DB_CONTAINER} (db=${DB_NAME}, user=${DB_USER})"
info "backend container  : ${APP_CONTAINER:-${C_YELLOW}not found${C_RESET}}"
info "assetstore         : ${ASSETSTORE_HOST:-${C_YELLOW}named volume or not mounted${C_RESET}}"
info "destination        : ${TARGET}"
info "retention          : ${KEEP} most recent"
echo

# --------------------------------------------------------------------------
# Cron installation
# --------------------------------------------------------------------------

if [[ $INSTALL_CRON -eq 1 ]]; then
  SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
  LINE="17 2 * * * ${SELF} --dest ${DEST} --keep ${KEEP} >> /var/log/dspace-backup.log 2>&1"
  if crontab -l 2>/dev/null | grep -qF "$SELF"; then
    warn "cron entry already present; leaving it alone"
  else
    ( crontab -l 2>/dev/null; echo "$LINE" ) | crontab -
    ok "installed nightly cron at 02:17"
  fi
  info "${C_DIM}${LINE}${C_RESET}"
  exit 0
fi

if [[ $DRY_RUN -eq 1 ]]; then
  info "Would dump database ${DB_NAME} to ${TARGET}/database.sql.gz"
  if [[ -n "$ASSETSTORE_HOST" ]]; then
    info "Would archive ${ASSETSTORE_HOST} ($(du -sh "$ASSETSTORE_HOST" 2>/dev/null | cut -f1 || echo '?')) to ${TARGET}/assetstore.tar.gz"
  else
    info "Would stream assetstore out of ${APP_CONTAINER}"
  fi
  info "Would prune backups older than the ${KEEP} most recent"
  echo
  info "Dry run — nothing written."
  exit 0
fi

mkdir -p "$TARGET"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

info "dumping database…"
if ! docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner 2>/dev/null \
     | gzip > "${TARGET}/database.sql.gz"; then
  rm -rf "$TARGET"
  fail "pg_dump failed. Check: docker exec ${DB_CONTAINER} pg_dump -U ${DB_USER} -d ${DB_NAME}"
fi

# An empty or truncated dump is worse than none, because it looks like success.
DB_SIZE=$(wc -c <"${TARGET}/database.sql.gz")
[[ "$DB_SIZE" -gt 1024 ]] || { rm -rf "$TARGET"; fail "dump is only ${DB_SIZE} bytes — treating as failed"; }
gzip -t "${TARGET}/database.sql.gz" 2>/dev/null || { rm -rf "$TARGET"; fail "dump failed gzip integrity check"; }
if ! zcat "${TARGET}/database.sql.gz" | head -100 | grep -q 'PostgreSQL database dump'; then
  warn "dump header looks unusual — verify before relying on it"
fi
ok "database  $(du -h "${TARGET}/database.sql.gz" | cut -f1)"

# --------------------------------------------------------------------------
# Assetstore
# --------------------------------------------------------------------------

info "archiving assetstore…"
if [[ -n "$ASSETSTORE_HOST" && -d "$ASSETSTORE_HOST" ]]; then
  tar -czf "${TARGET}/assetstore.tar.gz" -C "$(dirname "$ASSETSTORE_HOST")" "$(basename "$ASSETSTORE_HOST")" \
    || { warn "assetstore archive incomplete"; }
elif [[ -n "$APP_CONTAINER" ]]; then
  docker exec "$APP_CONTAINER" tar -cf - -C /dspace assetstore 2>/dev/null \
    | gzip > "${TARGET}/assetstore.tar.gz" \
    || warn "could not stream assetstore from container"
else
  warn "assetstore not backed up — locate it and pass --app <container>"
fi

if [[ -f "${TARGET}/assetstore.tar.gz" ]]; then
  tar -tzf "${TARGET}/assetstore.tar.gz" >/dev/null 2>&1 \
    && ok "assetstore  $(du -h "${TARGET}/assetstore.tar.gz" | cut -f1)" \
    || warn "assetstore archive failed its integrity check"
fi

# --------------------------------------------------------------------------
# Manifest and rotation
# --------------------------------------------------------------------------

{
  echo "DSpace backup ${STAMP}"
  echo "host:       $(hostname)"
  echo "database:   ${DB_NAME} (from ${DB_CONTAINER})"
  echo "assetstore: ${ASSETSTORE_HOST:-streamed from ${APP_CONTAINER}}"
  echo
  echo "Restore:"
  echo "  zcat database.sql.gz | docker exec -i ${DB_CONTAINER} psql -U ${DB_USER} -d ${DB_NAME}"
  echo "  tar -xzf assetstore.tar.gz -C /path/to/assetstore/parent"
  echo "  # then rebuild the search index:"
  echo "  docker exec ${APP_CONTAINER:-dspace} /dspace/bin/dspace index-discovery -b"
} >"${TARGET}/MANIFEST.txt"

chmod -R go-rwx "$TARGET" 2>/dev/null || true

# Keep only the most recent N.
mapfile -t OLD < <(find "$DEST" -maxdepth 1 -mindepth 1 -type d -name '20*' | sort -r | tail -n +$((KEEP+1)))
for d in "${OLD[@]}"; do
  rm -rf "$d" && info "${C_DIM}pruned $(basename "$d")${C_RESET}"
done

echo
ok "backup complete: ${TARGET}  ($(du -sh "$TARGET" | cut -f1))"
cat <<EOF

${C_YELLOW}This backup is on the same server as the data it protects.${C_RESET}
That covers accidental deletion and bad upgrades. It does NOT cover losing
the VPS. Copy it off-box — e.g.:

    rclone sync ${DEST} remote:dare-backups
    restic -r s3:… backup ${DEST}

And test a restore. An untested backup is not a backup.
EOF
