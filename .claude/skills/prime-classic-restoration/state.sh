#!/usr/bin/env bash
# Session-state snapshot for the classic-restoration priming skill.
# Read-only. Invoked as dynamic context from SKILL.md, so its stdout lands in the
# session before the body reaches the model.
#
# Paths resolve from this script's own location and from reforged/.references,
# never from the caller's cwd and never hardcoded.

set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFORGED="$(cd "$HERE/../../.." && pwd)"
PLANS="$REFORGED/docs/plans/classic-restoration"
REFS="$REFORGED/.references"

ref() { # ref <key> -> local path with forward slashes, empty if missing
  [ -f "$REFS" ] || return 0
  grep "^$1=" "$REFS" | head -1 | cut -d= -f2- | tr -d '\r' | sed 's|\\|/|g'
}

repo_line() { # repo_line <label> <path>
  local label="$1" path="$2"
  if [ -z "$path" ] || [ ! -d "$path" ]; then
    echo "  $label: NOT RESOLVED (check .references)"
    return
  fi
  local dirty head
  dirty="$(git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
  head="$(git -C "$path" log -1 --pretty=format:'%h %s' 2>/dev/null | cut -c1-64)"
  echo "  $label: ${dirty} dirty | HEAD ${head:-unknown}"
}

echo "PLAN FOLDERS under docs/plans/classic-restoration/"
for d in "$PLANS"/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  tracker="no TRACKER.md"
  [ -f "$d/TRACKER.md" ] && tracker="TRACKER.md"
  data="$(ls "$d/data" 2>/dev/null | wc -l | tr -d ' ')"
  echo "  $name  ($tracker, data/ files: $data)"
done
echo "  shared: DOCTRINE.md, ZONE-PORT-PLAYBOOK.md"

echo
echo "WORKING TREES (uncommitted work is expected mid-patch)"
repo_line "specs        " "$REFORGED"
repo_line "server sheets" "$(ref server_datasheet)"
repo_line "client DC    " "$(ref client_datacenter)"

echo
echo "PROJECT STATE"
grep -m1 'Last updated' "$REFORGED/STATUS.md" 2>/dev/null | sed 's|^|  STATUS |'
echo "  recent CHANGELOG entries:"
grep -m3 '^## ' "$REFORGED/CHANGELOG.md" 2>/dev/null | sed 's|^|    |'
open_reqs="$(ls "$REFORGED/docs/dsl-requests"/*.md 2>/dev/null | wc -l | tr -d ' ')"
echo "  open DSL requests: $open_reqs (docs/dsl-requests/)"
