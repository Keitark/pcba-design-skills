#!/usr/bin/env python3
"""Validate the public repository wrapper and Codex skill metadata."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "schematic-humanizer"
SKILL_MD = SKILL_DIR / "SKILL.md"

REQUIRED_FILES = (
    ROOT / "README.md",
    ROOT / "README.ja.md",
    ROOT / "LICENSE",
    ROOT / "SUPPORT.md",
    ROOT / "SUPPORT.ja.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "installation.md",
    ROOT / "docs" / "installation.ja.md",
    ROOT / "docs" / "adapters.md",
    ROOT / "docs" / "adapters.ja.md",
    ROOT / "assets" / "banner.svg",
    SKILL_MD,
    SKILL_DIR / "agents" / "openai.yaml",
)

LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_required_files(errors: list[str]) -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}", errors)


def validate_skill(errors: list[str]) -> None:
    if not SKILL_MD.is_file():
        return

    text = SKILL_MD.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > 500:
        fail(f"SKILL.md has {len(lines)} lines; keep it at or below 500", errors)
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter", errors)
        return

    try:
        _, frontmatter, body = text.split("---", 2)
        metadata = yaml.safe_load(frontmatter)
    except (ValueError, yaml.YAMLError) as exc:
        fail(f"invalid SKILL.md frontmatter: {exc}", errors)
        return

    if not isinstance(metadata, dict):
        fail("SKILL.md frontmatter must be a mapping", errors)
        return
    if set(metadata) != {"name", "description"}:
        fail("SKILL.md frontmatter must contain only name and description", errors)

    name = metadata.get("name")
    description = metadata.get("description")
    if name != "schematic-humanizer":
        fail("SKILL.md name must be schematic-humanizer", errors)
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        fail("skill name must use lowercase letters, digits, and hyphens", errors)
    if not isinstance(description, str) or len(description.strip()) < 40:
        fail("skill description must clearly explain capability and triggers", errors)
    if not body.strip():
        fail("SKILL.md body must not be empty", errors)
    if re.search(r"\b(?:TODO|TBD)\b", text, re.IGNORECASE):
        fail("SKILL.md contains TODO or TBD", errors)


def validate_links(errors: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (markdown.parent / path_part).resolve()
            if not resolved.exists():
                fail(
                    f"broken relative link in {markdown.relative_to(ROOT)}: {target}",
                    errors,
                )


def validate_text_hygiene(errors: list[str]) -> None:
    checked_suffixes = {".md", ".yml", ".yaml", ".py", ".svg"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in checked_suffixes:
            continue
        if ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"file is not valid UTF-8: {path.relative_to(ROOT)}", errors)
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if line.endswith((" ", "\t")):
                fail(
                    f"trailing whitespace: {path.relative_to(ROOT)}:{line_number}",
                    errors,
                )


def main() -> int:
    errors: list[str] = []
    validate_required_files(errors)
    validate_skill(errors)
    validate_links(errors)
    validate_text_hygiene(errors)

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
