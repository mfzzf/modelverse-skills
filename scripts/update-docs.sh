#!/usr/bin/env bash
# update-docs.sh — refresh references/ from the upstream ModelVerse docs.
#
# Upstream: git.ucloudadmin.com/channel-docs/ai-docs/modelverse  (internal)
# Strategy: shallow clone into a temp dir, rsync `api_doc/` → references/
# with --delete so removed files disappear locally, prune nav/asset noise,
# regenerate INDEX.md, then show a git diff and let the human decide whether
# to commit.
#
# Usage:
#   scripts/update-docs.sh                     # sync, then show diff
#   scripts/update-docs.sh --commit            # also commit if anything changed
#   UPSTREAM=git@... scripts/update-docs.sh    # override remote
#   BRANCH=feature/foo scripts/update-docs.sh  # override branch

set -euo pipefail

UPSTREAM="${UPSTREAM:-https://git.ucloudadmin.com/channel-docs/ai-docs/modelverse.git}"
BRANCH="${BRANCH:-master}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d -t modelverse-docs-XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

echo "→ cloning $UPSTREAM ($BRANCH) into $TMP"
git clone --depth 1 --branch "$BRANCH" "$UPSTREAM" "$TMP" >/dev/null

UPSTREAM_SHA="$(git -C "$TMP" rev-parse HEAD)"
UPSTREAM_DATE="$(git -C "$TMP" log -1 --format=%cI)"
echo "  upstream HEAD: $UPSTREAM_SHA  ($UPSTREAM_DATE)"

if [[ ! -d "$TMP/api_doc" ]]; then
  echo "error: api_doc/ not found in upstream — has the layout changed?" >&2
  exit 1
fi

echo "→ syncing api_doc/ → references/ (with --delete)"
rsync -a --delete --exclude='_meta.json' --exclude='*.png' "$TMP/api_doc/" "$ROOT/references/"

echo "→ regenerating references/INDEX.md"
cd "$ROOT/references"
{
  echo "# References Index"
  echo ""
  echo "Verbatim mirror of UCloud's ModelVerse \`api_doc/\` upstream. Per-model recipe is authoritative — when SKILL.md says \"check the recipe\", this is the tree it means."
  echo ""
  echo "_Last synced: ${UPSTREAM_DATE}_  ·  _upstream commit:_ \`${UPSTREAM_SHA:0:12}\`"
  echo ""
  emit_group() {
    local title="$1" glob="$2"
    shopt -s nullglob
    local files=($glob)
    shopt -u nullglob
    [[ ${#files[@]} -gt 0 ]] || return 0
    echo "## $title"
    for f in "${files[@]}"; do echo "- [\`$f\`](./$f)"; done
    echo ""
  }
  emit_group "Common"           "common/*.md"
  emit_group "Text"             "text_api/*.md"
  emit_group "Image"            "image_api/*.md"
  emit_group "Video (all async / task-poll)" "video_api/*.md"
  emit_group "Audio"            "audio_api/*.md"
  shopt -s nullglob
  toplevel=(*.md)
  shopt -u nullglob
  if [[ ${#toplevel[@]} -gt 1 ]]; then  # exclude INDEX.md itself
    echo "## Top-level"
    for f in "${toplevel[@]}"; do
      [[ "$f" == "INDEX.md" ]] && continue
      echo "- [\`$f\`](./$f)"
    done
    echo ""
  fi
} > INDEX.md
cd "$ROOT"

echo "→ git status:"
git -C "$ROOT" status --short references/

if git -C "$ROOT" diff --quiet --exit-code references/ && \
   git -C "$ROOT" diff --cached --quiet --exit-code references/; then
  if ! git -C "$ROOT" status --porcelain references/ | grep -q .; then
    echo "✓ already up to date — nothing changed."
    exit 0
  fi
fi

echo
echo "→ files changed (summary):"
git -C "$ROOT" diff --stat references/ | tail -20 || true
echo
echo "Inspect full diff with:  git -C '$ROOT' diff references/"

if [[ "${1:-}" == "--commit" ]]; then
  git -C "$ROOT" add references/
  git -C "$ROOT" commit -m "sync references/ from upstream@${UPSTREAM_SHA:0:12}"
  echo
  echo "✓ committed. Push with: git push origin main"
else
  echo
  echo "Run again with --commit to stage & commit, or review and commit manually."
fi
