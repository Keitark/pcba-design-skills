#!/usr/bin/env python3
"""Record a project-local layout lesson without mutating the installed skill."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


MARK = "<!-- PROJECT-LAYOUT-LESSONS -->"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path(".pcba-workflow/layout-lessons.md"))
    parser.add_argument("--id", required=True)
    parser.add_argument("--trigger", required=True)
    parser.add_argument("--rule", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--check", default="manual")
    args = parser.parse_args()
    slug = re.sub(r"[^a-z0-9-]", "-", args.id.lower()).strip("-")
    if not slug:
        raise SystemExit("lesson id must contain letters or digits")
    entry = (
        f"\n### {slug}\n"
        f"- **Trigger:** {args.trigger}\n"
        f"- **Rule:** {args.rule}\n"
        f"- **Evidence:** {args.evidence}\n"
        f"- **Check:** {args.check}\n"
    )
    text = args.file.read_text(encoding="utf-8") if args.file.exists() else f"# Project layout lessons\n\n{MARK}\n"
    pattern = re.compile(r"\n### " + re.escape(slug) + r"\n(?:- .*\n)*")
    replaced = bool(pattern.search(text))
    text = pattern.sub("", text)
    if MARK not in text:
        text = text.rstrip() + f"\n\n{MARK}\n"
    text = text.replace(MARK, MARK + entry, 1)
    args.file.parent.mkdir(parents=True, exist_ok=True)
    args.file.write_text(text, encoding="utf-8")
    print(json.dumps({"recorded": slug, "replaced": replaced, "file": str(args.file)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
