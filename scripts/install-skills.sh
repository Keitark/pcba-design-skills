#!/usr/bin/env sh
set -eu

usage() {
  echo "usage: $0 codex-personal|codex-project|claude-personal|claude-project [--project DIR] (--all|SKILL...)" >&2
  exit 2
}

[ "$#" -ge 2 ] || usage
target=$1
shift
project_root=$(pwd)
if [ "${1:-}" = "--project" ]; then
  [ "$#" -ge 3 ] || usage
  project_root=$2
  shift 2
fi

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/.." && pwd)
source_root="$repo_root/.agents/skills"

case "$target" in
  codex-personal) destination_root="${CODEX_HOME:-$HOME/.codex}/skills" ;;
  codex-project) destination_root="$project_root/.agents/skills" ;;
  claude-personal) destination_root="$HOME/.claude/skills" ;;
  claude-project) destination_root="$project_root/.claude/skills" ;;
  *) usage ;;
esac

if [ "$1" = "--all" ]; then
  [ "$#" -eq 1 ] || usage
  set -- $(find "$source_root" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
fi

seen=" "
for name in "$@"; do
  case "$seen" in
    *" $name "*) echo "duplicate skill argument: $name" >&2; exit 1 ;;
  esac
  seen="$seen$name "
done

for name in "$@"; do
  source_dir="$source_root/$name"
  destination="$destination_root/$name"
  [ -f "$source_dir/SKILL.md" ] || { echo "unknown skill: $name" >&2; exit 1; }
  [ ! -e "$destination" ] || { echo "destination already exists: $destination" >&2; exit 1; }
done

mkdir -p "$destination_root"
for name in "$@"; do
  source_dir="$source_root/$name"
  destination="$destination_root/$name"
  cp -R "$source_dir" "$destination"
  echo "Installed $name -> $destination"
done
