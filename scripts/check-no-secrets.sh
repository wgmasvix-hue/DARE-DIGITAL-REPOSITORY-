#!/usr/bin/env bash
#
# check-no-secrets.sh — refuse to let credentials or repository content into git.
#
# Runs in CI on every push and pull request, and can be installed locally as a
# pre-commit hook:
#
#     ln -s ../../scripts/check-no-secrets.sh .git/hooks/pre-commit
#
# Usage:
#   ./scripts/check-no-secrets.sh            # scan tracked files
#   ./scripts/check-no-secrets.sh --staged   # scan staged changes (pre-commit)
#
# Exit 0 = clean, 1 = violations found.

set -uo pipefail

MODE="tracked"
[[ "${1:-}" == "--staged" ]] && MODE="staged"

cd "$(git rev-parse --show-toplevel)" || exit 1

if [[ -t 1 ]]; then
  C_RESET=$'\033[0m'; C_BOLD=$'\033[1m'; C_DIM=$'\033[2m'
  C_RED=$'\033[31m'; C_GREEN=$'\033[32m'
else
  C_RESET=""; C_BOLD=""; C_DIM=""; C_RED=""; C_GREEN=""
fi

VIOLATIONS=0
violation() {
  printf '%s\n' "${C_RED}✗${C_RESET} $1"
  printf '%s\n' "  ${C_DIM}$2${C_RESET}"
  VIOLATIONS=$((VIOLATIONS+1))
}

# Files under consideration.
if [[ "$MODE" == "staged" ]]; then
  mapfile -t FILES < <(git diff --cached --name-only --diff-filter=ACM)
else
  mapfile -t FILES < <(git ls-files)
fi

[[ ${#FILES[@]} -eq 0 ]] && { echo "No files to check."; exit 0; }

printf '%s\n' "${C_BOLD}Checking ${#FILES[@]} file(s) for secrets and repository content${C_RESET}"
echo

# --------------------------------------------------------------------------
# 1. Repository content and key material must never be committed
# --------------------------------------------------------------------------

for f in "${FILES[@]}"; do
  case "$f" in
    *.sql|*.sql.gz|*.dump|*.pgdump|*.bak)
      violation "$f" "Database dump. Contains user emails and password hashes — belongs in encrypted backups, not git." ;;
    */assetstore/*|assetstore/*)
      violation "$f" "Assetstore content. Deposited files belong in object storage." ;;
    *.jks|*.p12|*.keystore|*.pfx)
      violation "$f" "Java keystore / PKCS#12 key material." ;;
    *.pem|*.key)
      violation "$f" "Private key material." ;;
    .env|.env.*)
      [[ "$f" == ".env.example" ]] && continue
      violation "$f" "Environment file with real values. Only .env.example is committable." ;;
    deploy/backend/config/local.cfg)
      violation "$f" "Live local.cfg. Commit local.cfg.example instead." ;;
  esac
done

# --------------------------------------------------------------------------
# 2. Credential-shaped config values that were not redacted
#
# Key components are delimited by . _ - so "keyword" and "key.size" do not
# match, while "db.password" and "orcid.application-client-secret" do.
# --------------------------------------------------------------------------

KEY_RE='(^|[._-])(password|passwd|pwd|secret|credential|credentials|apikey|accesskey|secretkey|privatekey|token|passphrase)([._-]|$)'
KEY_RE_EXTRA='(client[._-]secret|api[._-]key|access[._-]key|secret[._-]key|private[._-]key|\.key$|mail\.server\.username|^s3\.|aws)'

for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  case "$f" in
    *.cfg|*.properties|*.yml|*.yaml|*.conf|*.env|*.example) ;;
    *) continue ;;
  esac
  # The scanners themselves contain these patterns by necessity.
  [[ "$f" == scripts/* ]] && continue

  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*(#|//|\;) ]] && continue
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z0-9._-]+)[[:space:]]*[=:][[:space:]]*(.+)$ ]]; then
      # Capture before any further regex test — BASH_REMATCH is overwritten
      # by each subsequent match.
      key="${BASH_REMATCH[1]}"
      v="${BASH_REMATCH[2]}"
      k="$(printf '%s' "$key" | tr '[:upper:]' '[:lower:]')"
      # Placeholders and empty values are fine — that is the desired state.
      [[ "$v" =~ ^(__REDACTED__|\$\{|CHANGEME|\"\"|\'\'|null|true|false|[0-9]+)[[:space:]]*$ ]] && continue
      if [[ "$k" =~ $KEY_RE ]] || [[ "$k" =~ $KEY_RE_EXTRA ]]; then
        violation "$f" "Unredacted credential '${key}' has a live-looking value. Replace with __REDACTED__ and inject via DSPACE__P__* at runtime."
      fi
    fi
  done < <(grep -aE '^[[:space:]]*[A-Za-z0-9._-]+[[:space:]]*[=:]' "$f" 2>/dev/null)
done

# --------------------------------------------------------------------------
# 3. Key material or cloud credentials embedded in any file
# --------------------------------------------------------------------------

for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  [[ "$f" == scripts/check-no-secrets.sh ]] && continue
  if grep -qaE -- '^-----BEGIN [A-Z ]*PRIVATE KEY-----' "$f" 2>/dev/null; then
    violation "$f" "Embedded private key block."
  fi
  if grep -qaE 'AKIA[0-9A-Z]{16}' "$f" 2>/dev/null; then
    violation "$f" "AWS access key ID."
  fi
done

# --------------------------------------------------------------------------
# 4. Oversized files — usually content that slipped through
# --------------------------------------------------------------------------

for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  size=$(wc -c <"$f" 2>/dev/null || echo 0)
  if [[ "$size" -gt 5242880 ]]; then
    violation "$f" "$(( size / 1048576 )) MB — too large for a config repo. Is this repository content?"
  fi
done

# --------------------------------------------------------------------------

echo
if [[ $VIOLATIONS -eq 0 ]]; then
  printf '%s\n' "${C_GREEN}✓ Clean — no secrets or repository content found.${C_RESET}"
  exit 0
fi

printf '%s\n' "${C_RED}${C_BOLD}${VIOLATIONS} violation(s).${C_RESET}"
cat <<'EOF'

Nothing was blocked from your working tree — this only stops it reaching the
remote. Remove the offending content, and if a real credential was exposed at
any point, rotate it: git history preserves it even after a later delete.
EOF
exit 1
