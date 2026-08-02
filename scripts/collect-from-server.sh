#!/usr/bin/env bash
#
# collect-from-server.sh — gather DSpace 9.x deployment configuration and
# customisations from a running server into this repository.
#
# Safety properties, by design:
#   * The DSpace install is only ever READ. Nothing on the server is modified.
#   * Nothing is committed and nothing is pushed. That stays your decision.
#   * Credentials are redacted before any file is written.
#   * Repository content (database, assetstore, Solr) is never collected.
#
# Usage:
#   ./scripts/collect-from-server.sh --dry-run     # show what would be collected
#   ./scripts/collect-from-server.sh               # collect into ./deploy
#
# See docs/MIGRATION.md for the full procedure.

set -euo pipefail

# --------------------------------------------------------------------------
# Defaults and argument parsing
# --------------------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${REPO_ROOT}/deploy"
DSPACE_HOME="${DSPACE_HOME:-}"
FRONTEND_DIR="${DSPACE_FRONTEND:-}"
DRY_RUN=0
REPORT="${REPO_ROOT}/collect-report-$(date +%Y%m%d-%H%M%S).txt"

usage() {
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  cat <<'EOF'

Options:
  --dry-run              List what would be collected; write nothing.
  --dspace-home PATH     Backend install root (the dir containing config/).
  --frontend PATH        dspace-angular checkout root.
  --out PATH             Output directory. Default: ./deploy
  -h, --help             This message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)      DRY_RUN=1; shift ;;
    --dspace-home)  DSPACE_HOME="${2:?--dspace-home needs a path}"; shift 2 ;;
    --frontend)     FRONTEND_DIR="${2:?--frontend needs a path}"; shift 2 ;;
    --out)          OUT_DIR="${2:?--out needs a path}"; shift 2 ;;
    -h|--help)      usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""; C_YELLOW=""
fi

log()   { printf '%s\n' "$*"; [[ $DRY_RUN -eq 1 ]] || printf '%s\n' "$*" >>"$REPORT"; }
info()  { log "  $*"; }
ok()    { log "${C_GREEN}  ✓${C_RESET} $*"; }
warn()  { log "${C_YELLOW}  !${C_RESET} $*"; }
fail()  { printf '%s\n' "${C_RED}ERROR:${C_RESET} $*" >&2; exit 1; }
head1() { log ""; log "${C_BOLD}$*${C_RESET}"; }

# --------------------------------------------------------------------------
# Locate the DSpace backend
# --------------------------------------------------------------------------

detect_backend() {
  [[ -n "$DSPACE_HOME" ]] && { echo "$DSPACE_HOME"; return; }
  local candidate
  for candidate in /dspace /opt/dspace /srv/dspace /usr/local/dspace \
                   "$HOME/dspace" /var/dspace /data/dspace; do
    [[ -d "$candidate/config" ]] && { echo "$candidate"; return; }
  done
  # Fall back to a running container, if Docker is available.
  if command -v docker >/dev/null 2>&1; then
    local cid
    cid="$(docker ps --filter 'name=dspace' --format '{{.Names}}' 2>/dev/null | grep -v -- '-angular\|frontend\|solr\|db\|postgres' | head -1 || true)"
    [[ -n "$cid" ]] && { echo "docker:$cid"; return; }
  fi
  echo ""
}

detect_frontend() {
  [[ -n "$FRONTEND_DIR" ]] && { echo "$FRONTEND_DIR"; return; }
  local candidate
  for candidate in /dspace-angular /opt/dspace-angular /srv/dspace-angular \
                   "$HOME/dspace-angular" /var/www/dspace-angular \
                   "${DSPACE_HOME:-/nonexistent}/../dspace-angular"; do
    [[ -f "$candidate/angular.json" ]] && { (cd "$candidate" && pwd); return; }
  done
  echo ""
}

BACKEND="$(detect_backend)"
FRONTEND="$(detect_frontend)"

[[ -n "$BACKEND" ]] || fail "Could not find a DSpace install.
Pass it explicitly:  $0 --dspace-home /path/to/dspace
(the directory that contains config/dspace.cfg)"

# Docker installs need to be exported to a temp dir first.
DOCKER_STAGE=""
if [[ "$BACKEND" == docker:* ]]; then
  local_cid="${BACKEND#docker:}"
  DOCKER_STAGE="$(mktemp -d)"
  trap 'rm -rf "$DOCKER_STAGE"' EXIT
  docker cp "${local_cid}:/dspace/config" "$DOCKER_STAGE/config" 2>/dev/null \
    || fail "Found container '$local_cid' but could not copy /dspace/config out of it."
  BACKEND="$DOCKER_STAGE"
  BACKEND_LABEL="docker container ${local_cid}"
else
  BACKEND_LABEL="$BACKEND"
fi

[[ -d "$BACKEND/config" ]] || fail "No config/ directory under $BACKEND"

# --------------------------------------------------------------------------
# Secret handling
#
# KEY_RE matches configuration KEYS (left of = or :) that carry credentials.
# Components are delimited by . _ - so "keyword" and "key.size" do not match
# while "db.password" and "orcid.application-client-secret" do.
# --------------------------------------------------------------------------

KEY_RE='(^|[._-])(password|passwd|pwd|secret|secrets|credential|credentials|apikey|accesskey|secretkey|privatekey|token|passphrase|clientsecret)([._-]|$)'
KEY_RE_EXTRA='(client[._-]secret|api[._-]key|access[._-]key|secret[._-]key|private[._-]key|\.key$|mail\.server\.username|^s3\.|aws)'

is_secret_key() {
  local k
  k="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  [[ "$k" =~ $KEY_RE ]] && return 0
  [[ "$k" =~ $KEY_RE_EXTRA ]] && return 0
  return 1
}

# Map a DSpace property to the Docker env var that supplies it at runtime.
# DSpace 9 reads DSPACE__P__<property with dots as underscores>.
env_var_for() {
  printf 'DSPACE__P__%s' "$(printf '%s' "$1" | tr '.-' '__')"
}

REDACTED_KEYS_FILE="$(mktemp)"
cleanup() {
  local status=$?
  rm -f "$REDACTED_KEYS_FILE"
  [[ -n "${DOCKER_STAGE:-}" ]] && rm -rf "$DOCKER_STAGE"
  exit $status
}
trap cleanup EXIT

# Rewrite a config file in place, redacting credential values.
# Handles "key = value" (.cfg/.properties) and "key: value" (.yml).
redact_file() {
  local file="$1" rel="$2" tmp
  tmp="$(mktemp)"
  local n=0

  while IFS= read -r line || [[ -n "$line" ]]; do
    # Preserve comments and blanks untouched.
    if [[ "$line" =~ ^[[:space:]]*($|#|//|\;) ]]; then
      printf '%s\n' "$line" >>"$tmp"; continue
    fi
    if [[ "$line" =~ ^([[:space:]]*)([A-Za-z0-9._-]+)([[:space:]]*[=:][[:space:]]*)(.*)$ ]]; then
      local indent="${BASH_REMATCH[1]}" key="${BASH_REMATCH[2]}"
      local sep="${BASH_REMATCH[3]}" val="${BASH_REMATCH[4]}"
      # Leave empty values and existing placeholders alone.
      if [[ -n "${val// /}" ]] && [[ ! "$val" =~ ^(__REDACTED__|\$\{|CHANGEME) ]] \
         && is_secret_key "$key"; then
        printf '%s%s%s__REDACTED__\n' "$indent" "$key" "$sep" >>"$tmp"
        printf '%s\t%s\t%s\n' "$rel" "$key" "$(env_var_for "$key")" >>"$REDACTED_KEYS_FILE"
        n=$((n+1))
        continue
      fi
    fi
    printf '%s\n' "$line" >>"$tmp"
  done <"$file"

  mv "$tmp" "$file"
  [[ $n -gt 0 ]] && info "${C_DIM}redacted ${n} value(s) in ${rel}${C_RESET}"
  return 0
}

# Post-redaction scan: anything that still looks live is a hard stop.
scan_for_leaks() {
  local root="$1" found=0 f
  while IFS= read -r -d '' f; do
    # Private key material, anywhere.
    if grep -qE -- '-----BEGIN [A-Z ]*PRIVATE KEY-----' "$f" 2>/dev/null; then
      warn "${C_RED}private key material in ${f#$root/}${C_RESET}"; found=1
    fi
    # AWS access key IDs.
    if grep -qE 'AKIA[0-9A-Z]{16}' "$f" 2>/dev/null; then
      warn "${C_RED}AWS access key in ${f#$root/}${C_RESET}"; found=1
    fi
    # A credential key that survived with a non-placeholder value.
    while IFS= read -r line; do
      [[ "$line" =~ ^[[:space:]]*(#|//|\;) ]] && continue
      if [[ "$line" =~ ^[[:space:]]*([A-Za-z0-9._-]+)[[:space:]]*[=:][[:space:]]*(.+)$ ]]; then
        local k="${BASH_REMATCH[1]}" v="${BASH_REMATCH[2]}"
        [[ "$v" =~ ^(__REDACTED__|\$\{|CHANGEME|\"\"|\'\'|null|true|false) ]] && continue
        if is_secret_key "$k"; then
          warn "${C_RED}unredacted ${k} in ${f#$root/}${C_RESET}"; found=1
        fi
      fi
    done < <(grep -aE '^[[:space:]]*[A-Za-z0-9._-]+[[:space:]]*[=:]' "$f" 2>/dev/null || true)
  done < <(find "$root" -type f \( -name '*.cfg' -o -name '*.properties' -o -name '*.yml' \
              -o -name '*.yaml' -o -name '*.xml' -o -name '*.env' -o -name '*.conf' \) -print0)
  return $found
}

# --------------------------------------------------------------------------
# Copy helper — excludes content, binaries and key material at the source
# --------------------------------------------------------------------------

EXCLUDE_PATTERNS=(
  'assetstore' 'assetstore*' 'solr' 'index'
  '*.jks' '*.p12' '*.pem' '*.key' '*.keystore' '*.pfx' '*.crt'
  '*.sql' '*.sql.gz' '*.dump' '*.bak'
  '*.log' 'log' 'logs'
  'node_modules' '.git' 'target' 'dist'
  '*.jar' '*.war' '*.class' '*.zip' '*.tar.gz'
)

EXCLUDES=()
for p in "${EXCLUDE_PATTERNS[@]}"; do EXCLUDES+=( --exclude="$p" ); done

# Directory copy with exclusions. rsync if present, GNU tar otherwise —
# servers reliably have one or the other.
if command -v rsync >/dev/null 2>&1; then
  COPIER="rsync"
elif tar --version 2>/dev/null | grep -qi 'gnu tar'; then
  COPIER="tar"
else
  fail "Need either rsync or GNU tar to copy directories safely.
Install one:  apt-get install rsync"
fi

copy_dir() {
  local src="$1" dest="$2"
  mkdir -p "$dest"
  case "$COPIER" in
    rsync) rsync -a "${EXCLUDES[@]}" "$src/" "$dest/" ;;
    tar)   tar -cf - "${EXCLUDES[@]}" -C "$src" . | tar -xf - -C "$dest" ;;
  esac
}

COLLECTED=0
SKIPPED=0

copy_path() {
  local src="$1" dest="$2" label="$3"
  if [[ ! -e "$src" ]]; then
    info "${C_DIM}absent: ${label}${C_RESET}"; SKIPPED=$((SKIPPED+1)); return 0
  fi
  if [[ ! -r "$src" ]]; then
    warn "unreadable (try sudo): ${label}"; SKIPPED=$((SKIPPED+1)); return 0
  fi
  if [[ $DRY_RUN -eq 1 ]]; then
    local size; size="$(du -sh "$src" 2>/dev/null | cut -f1 || echo '?')"
    ok "would collect ${label} ${C_DIM}(${size})${C_RESET}"
    COLLECTED=$((COLLECTED+1)); return 0
  fi
  mkdir -p "$(dirname "$dest")"
  if [[ -d "$src" ]]; then
    copy_dir "$src" "$dest" 2>/dev/null || warn "partial copy: ${label}"
  else
    cp -p "$src" "$dest"
  fi
  ok "collected ${label}"
  COLLECTED=$((COLLECTED+1))
}

# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------

if [[ $DRY_RUN -eq 0 ]]; then
  mkdir -p "$OUT_DIR"
  : >"$REPORT"
fi

log "${C_BOLD}DARE — DSpace deployment collection${C_RESET}"
log "${C_DIM}$(date -Is)${C_RESET}"
log ""
log "  backend   : ${BACKEND_LABEL}"
log "  frontend  : ${FRONTEND:-${C_YELLOW}not found${C_RESET}}"
log "  output    : ${OUT_DIR}"
log "  mode      : $([[ $DRY_RUN -eq 1 ]] && echo 'DRY RUN — nothing will be written' || echo 'collect')"

head1 "Backend configuration"
copy_path "$BACKEND/config" "$OUT_DIR/backend/config" "config/ (dspace.cfg, local.cfg, modules, spring, crosswalks, registries, emails, submission forms)"

head1 "Frontend theme and configuration"
if [[ -n "$FRONTEND" ]]; then
  copy_path "$FRONTEND/config"           "$OUT_DIR/frontend/config"       "frontend config/ (config.prod.yml)"
  copy_path "$FRONTEND/src/themes"       "$OUT_DIR/frontend/src/themes"   "src/themes/ (custom theme)"
  copy_path "$FRONTEND/src/environments" "$OUT_DIR/frontend/src/environments" "src/environments/"
  copy_path "$FRONTEND/angular.json"     "$OUT_DIR/frontend/angular.json" "angular.json"
  copy_path "$FRONTEND/package.json"     "$OUT_DIR/frontend/package.json" "package.json"
else
  warn "No dspace-angular checkout found — pass --frontend /path/to/dspace-angular"
  warn "Your custom theme is the main thing that lives there. Worth locating."
fi

head1 "Container and web-server configuration"
for f in docker-compose.yml docker-compose.yaml docker-compose-rest.yml \
         docker-compose-cli.yml Dockerfile Dockerfile.dependencies; do
  for base in "$BACKEND" "${FRONTEND:-/nonexistent}" "$PWD" "$HOME"; do
    [[ -f "$base/$f" ]] && copy_path "$base/$f" "$OUT_DIR/docker/$f" "$f (from $base)" && break
  done
done
copy_path "$BACKEND/docker" "$OUT_DIR/docker/backend-docker" "backend docker/"

# nginx / apache vhosts that reference the DSpace hostname
for vhost_dir in /etc/nginx/sites-available /etc/nginx/conf.d /etc/apache2/sites-available; do
  [[ -d "$vhost_dir" ]] || continue
  while IFS= read -r vh; do
    copy_path "$vh" "$OUT_DIR/webserver/$(basename "$vh")" "vhost $(basename "$vh")"
  done < <(grep -rlE 'dspace|dare\.co\.zw' "$vhost_dir" 2>/dev/null || true)
done

# --------------------------------------------------------------------------
# Redact, then verify
# --------------------------------------------------------------------------

if [[ $DRY_RUN -eq 0 ]]; then
  head1 "Redacting credentials"
  while IFS= read -r -d '' f; do
    redact_file "$f" "${f#$OUT_DIR/}"
  done < <(find "$OUT_DIR" -type f \( -name '*.cfg' -o -name '*.properties' \
              -o -name '*.yml' -o -name '*.yaml' -o -name '*.env' -o -name '*.conf' \) -print0)

  if [[ -s "$REDACTED_KEYS_FILE" ]]; then
    ok "$(wc -l <"$REDACTED_KEYS_FILE" | tr -d ' ') value(s) redacted"
  else
    info "no credential-shaped keys found"
  fi

  # local.cfg is the one file people habitually edit in place. Keep only the
  # redacted template in git; .gitignore blocks the real one.
  if [[ -f "$OUT_DIR/backend/config/local.cfg" ]]; then
    mv "$OUT_DIR/backend/config/local.cfg" "$OUT_DIR/backend/config/local.cfg.example"
    ok "local.cfg → local.cfg.example (real file stays out of git)"
  fi

  head1 "Verifying nothing sensitive survived"
  if scan_for_leaks "$OUT_DIR"; then
    ok "scan clean"
  else
    log ""
    fail "Potential secrets remain in ${OUT_DIR} (listed above).
Nothing has been committed. Remove or redact them, re-run the scan, and only
then commit. Any credential that was exposed should be rotated."
  fi

  # Write the secrets inventory: which secrets exist and how to inject them.
  # Never their values.
  {
    echo "# Secrets required at runtime"
    echo
    echo "These values were redacted out of the collected configuration."
    echo "They are supplied at runtime via environment variables — DSpace 9 reads"
    echo '`DSPACE__P__<property>` with dots and dashes replaced by underscores.'
    echo
    echo "**This file lists which secrets exist, never their values.**"
    echo
    echo "| File | Property | Environment variable |"
    echo "|---|---|---|"
    sort -u "$REDACTED_KEYS_FILE" | while IFS=$'\t' read -r file key envvar; do
      echo "| \`$file\` | \`$key\` | \`$envvar\` |"
    done
    echo
    echo "## Setting them"
    echo
    echo 'Put the real values in a `.env` file beside your compose file — `.gitignore`'
    echo "blocks it from ever being committed:"
    echo
    echo '```bash'
    sort -u "$REDACTED_KEYS_FILE" | while IFS=$'\t' read -r _ _ envvar; do
      echo "${envvar}="
    done
    echo '```'
  } >"$OUT_DIR/SECRETS.md"
  ok "wrote deploy/SECRETS.md"
fi

# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

head1 "Summary"
log "  collected : ${COLLECTED}"
log "  skipped   : ${SKIPPED}"

if [[ $DRY_RUN -eq 1 ]]; then
  log ""
  log "Dry run — nothing was written. Re-run without --dry-run to collect."
else
  log ""
  log "  report    : ${REPORT#$REPO_ROOT/}"
  log ""
  log "${C_BOLD}Nothing has been committed or pushed.${C_RESET} Review, then:"
  log ""
  log "    git status && git diff"
  log "    git add -A"
  log "    git commit -m 'Add DSpace deployment config from server'"
  log "    git push -u origin claude/server-repo-migration-k3ej1e"
  log ""
  log "${C_YELLOW}Read the diff before committing.${C_RESET} Redaction is a safety net,"
  log "not a guarantee — you know your config better than a regex does."
fi
