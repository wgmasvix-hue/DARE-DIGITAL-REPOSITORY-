#!/usr/bin/env bash
#
# import-to-dspace.sh — import a SAF batch into DSpace, reversibly.
#
# Always runs DSpace's own --test pass first, and always keeps the mapfile,
# because the mapfile is the only thing that makes an import undoable:
#
#     dspace import --delete --mapfile=<mapfile>
#
# Lose it and every imported item has to be found and deleted by hand.
#
# Usage:
#   ./import-to-dspace.sh saf_batch 123456789/42
#   ./import-to-dspace.sh saf_batch 123456789/42 --live     # actually import
#
# Without --live it stops after the test pass.

set -euo pipefail

SAF_DIR="${1:-}"
COLLECTION="${2:-}"
LIVE=0
[[ "${3:-}" == "--live" ]] && LIVE=1

CONTAINER="${DSPACE_CONTAINER:-dspace}"
EPERSON="${DSPACE_EPERSON:-}"
MAPDIR="${DSPACE_MAPFILE_DIR:-/opt/dspace9/harvesters/mapfiles}"

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
else
  C_RESET=""; C_BOLD=""; C_RED=""; C_GREEN=""; C_YELLOW=""
fi
ok()   { printf '%s\n' "${C_GREEN}  ✓${C_RESET} $*"; }
warn() { printf '%s\n' "${C_YELLOW}  !${C_RESET} $*"; }
fail() { printf '%s\n' "${C_RED}ERROR:${C_RESET} $*" >&2; exit 1; }

usage() {
  sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 2
}

[[ -n "$SAF_DIR" && -n "$COLLECTION" ]] || usage
[[ -d "$SAF_DIR" ]] || fail "SAF directory not found: $SAF_DIR"

command -v docker >/dev/null 2>&1 || fail "docker not found"
docker inspect "$CONTAINER" >/dev/null 2>&1 \
  || fail "container '$CONTAINER' not found. Set DSPACE_CONTAINER."

ITEM_COUNT=$(find "$SAF_DIR" -maxdepth 1 -type d -name 'item_*' | wc -l)
[[ "$ITEM_COUNT" -gt 0 ]] || fail "no item_* directories in $SAF_DIR"

# --- Pre-flight -------------------------------------------------------------

printf '%s\n' "${C_BOLD}DSpace SAF import${C_RESET}"
echo
echo "  batch      : ${SAF_DIR}  (${ITEM_COUNT} items)"
echo "  collection : ${COLLECTION}"
echo "  container  : ${CONTAINER}"
echo "  mode       : $([[ $LIVE -eq 1 ]] && echo 'LIVE — items will be created' || echo 'TEST ONLY')"
echo

# Validate before touching DSpace: a malformed dublin_core.xml aborts the
# import partway through, leaving some items created and some not.
if [[ -x "$(dirname "${BASH_SOURCE[0]}")/saf_builder.py" ]] \
   || [[ -f "$(dirname "${BASH_SOURCE[0]}")/saf_builder.py" ]]; then
  echo "Validating batch…"
  python3 "$(dirname "${BASH_SOURCE[0]}")/saf_builder.py" --validate "$SAF_DIR" \
    || fail "batch failed validation — fix it before importing"
  echo
fi

# Resolve the submitting eperson if not supplied.
if [[ -z "$EPERSON" ]]; then
  fail "Set DSPACE_EPERSON to the submitting account, e.g.
    DSPACE_EPERSON=admin@dare.co.zw $0 $SAF_DIR $COLLECTION"
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
REMOTE_SAF="/tmp/saf-${STAMP}"
REMOTE_MAP="/tmp/mapfile-${STAMP}.txt"
mkdir -p "$MAPDIR"

# --- Stage the batch into the container -------------------------------------

echo "Copying batch into ${CONTAINER}…"
docker cp "$SAF_DIR" "${CONTAINER}:${REMOTE_SAF}" \
  || fail "could not copy batch into the container"
ok "staged at ${REMOTE_SAF}"

cleanup_remote() {
  docker exec "$CONTAINER" rm -rf "$REMOTE_SAF" >/dev/null 2>&1 || true
}

# --- Test pass --------------------------------------------------------------
# DSpace's own dry run. Parses every item and reports what it would create
# without writing anything.

echo
echo "Test pass (no changes)…"
if ! docker exec "$CONTAINER" /dspace/bin/dspace import \
      --add --test \
      --eperson="$EPERSON" \
      --collection="$COLLECTION" \
      --source="$REMOTE_SAF" \
      --mapfile="$REMOTE_MAP" 2>&1 | tail -25; then
  cleanup_remote
  fail "test pass failed — nothing was imported"
fi
ok "test pass completed"

if [[ $LIVE -eq 0 ]]; then
  cleanup_remote
  echo
  printf '%s\n' "${C_BOLD}Test only.${C_RESET} Nothing was imported."
  echo "Re-run with --live once the output above looks right:"
  echo
  echo "    DSPACE_EPERSON=${EPERSON} $0 ${SAF_DIR} ${COLLECTION} --live"
  exit 0
fi

# --- Live import ------------------------------------------------------------

echo
echo "Importing…"
if ! docker exec "$CONTAINER" /dspace/bin/dspace import \
      --add \
      --eperson="$EPERSON" \
      --collection="$COLLECTION" \
      --source="$REMOTE_SAF" \
      --mapfile="$REMOTE_MAP" 2>&1 | tail -25; then
  warn "import reported an error — recovering the mapfile before cleanup"
  docker cp "${CONTAINER}:${REMOTE_MAP}" "${MAPDIR}/mapfile-${STAMP}.txt" 2>/dev/null || true
  cleanup_remote
  fail "import failed. Any items that WERE created are listed in
${MAPDIR}/mapfile-${STAMP}.txt and can be removed with:
  docker exec $CONTAINER /dspace/bin/dspace import --delete --mapfile=<path in container>"
fi

# The mapfile is the undo record. Retrieve it before the staging dir goes.
docker cp "${CONTAINER}:${REMOTE_MAP}" "${MAPDIR}/mapfile-${STAMP}.txt" \
  || warn "could not retrieve the mapfile — rollback will need manual work"
cleanup_remote

IMPORTED=$(wc -l < "${MAPDIR}/mapfile-${STAMP}.txt" 2>/dev/null || echo 0)
ok "imported ${IMPORTED} item(s)"
ok "mapfile: ${MAPDIR}/mapfile-${STAMP}.txt"

# --- Reindex ----------------------------------------------------------------
# Imported items do not appear in search or browse until Discovery indexes
# them. Skipping this is the usual reason a "successful" import seems to have
# done nothing.

echo
echo "Indexing new items…"
docker exec "$CONTAINER" /dspace/bin/dspace index-discovery >/dev/null 2>&1 \
  && ok "discovery index updated" \
  || warn "indexing failed — run: docker exec $CONTAINER /dspace/bin/dspace index-discovery -b"

cat <<EOF

${C_BOLD}Done.${C_RESET} ${IMPORTED} item(s) in ${COLLECTION}.

To undo this import entirely:

    docker cp ${MAPDIR}/mapfile-${STAMP}.txt ${CONTAINER}:/tmp/undo.txt
    docker exec ${CONTAINER} /dspace/bin/dspace import --delete --mapfile=/tmp/undo.txt

Keep the mapfile. It is the only record of what this run created.
EOF
