#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: bin/install.sh [target-repository] [--mode copy|link]

Installs all ai-sdlc-skills-* folders into <target>/.agents/skills.
  copy  Team/shared mode. Copies immutable skill folders (default).
  link  Local development mode. Creates symlinks to this checkout.

Existing destinations are never overwritten.
EOF
}

TARGET="."
MODE="copy"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --mode)
      [ "$#" -ge 2 ] || { echo "Missing value for --mode" >&2; exit 2; }
      MODE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
    *)
      TARGET="$1"
      shift
      ;;
  esac
done

case "$MODE" in
  copy|link) ;;
  *)
    echo "Unknown mode: $MODE (expected copy or link)" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SOURCE_ROOT="$(dirname "$SCRIPT_DIR")/skills"
TARGET_ROOT="$(CDPATH= cd -- "$TARGET" && pwd)"

if ! git -C "$TARGET_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Target is not a Git repository: $TARGET_ROOT" >&2
  exit 2
fi

DEST_ROOT="$TARGET_ROOT/.agents/skills"
mkdir -p "$DEST_ROOT"

found=0
for source in "$SOURCE_ROOT"/ai-sdlc-skills-*; do
  [ -d "$source" ] || continue
  name="$(basename "$source")"
  destination="$DEST_ROOT/$name"
  found=$((found + 1))
  if [ -e "$destination" ] || [ -L "$destination" ]; then
    echo "Refusing to overwrite existing skill: $destination" >&2
    exit 3
  fi
done

if [ "$found" -eq 0 ]; then
  echo "No ai-sdlc-skills-* folders found under $SOURCE_ROOT" >&2
  exit 4
fi

installed=0
for source in "$SOURCE_ROOT"/ai-sdlc-skills-*; do
  [ -d "$source" ] || continue
  name="$(basename "$source")"
  destination="$DEST_ROOT/$name"
  if [ "$MODE" = "copy" ]; then
    cp -R "$source" "$destination"
    find "$destination" -depth -name '__pycache__' -type d -exec rm -rf {} +
    find "$destination" -name '*.pyc' -type f -delete
  else
    ln -s "$source" "$destination"
  fi
  echo "Installed $name ($MODE)"
  installed=$((installed + 1))
done

echo "Installed $installed skills into $DEST_ROOT"
echo "Restart Codex if the skills do not appear immediately."
