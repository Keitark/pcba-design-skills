#!/usr/bin/env python3
"""Validate all public skill packages, documentation, privacy, and licensing."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills"
SKILLS = {
    "manage-pcba-program",
    "plan-electronic-product",
    "qualify-pcba-sourcing",
    "design-and-review-circuit",
    "schematic-humanizer",
    "pcb-layout-review",
    "release-pcba-fabrication",
    "operate-jlcpcb-order",
}
REQUIRED = (
    ROOT / "README.md", ROOT / "README.ja.md",
    ROOT / "LICENSE", ROOT / "LICENSES" / "CC-BY-SA-4.0.txt",
    ROOT / "ASSET-LICENSES.md",
    ROOT / "SUPPORT.md", ROOT / "SUPPORT.ja.md",
    ROOT / "CONTRIBUTING.md", ROOT / "CONTRIBUTING.ja.md",
    ROOT / "assets" / "banner.png",
    ROOT / "docs" / "installation.md", ROOT / "docs" / "installation.ja.md",
    ROOT / "docs" / "choose-a-skill.md", ROOT / "docs" / "choose-a-skill.ja.md",
    ROOT / "docs" / "prompts.md", ROOT / "docs" / "prompts.ja.md",
    ROOT / "docs" / "artifact-contracts.md", ROOT / "docs" / "artifact-contracts.ja.md",
    ROOT / "docs" / "case-study-nescart.md", ROOT / "docs" / "case-study-nescart.ja.md",
    ROOT / "docs" / "privacy-review.md",
    ROOT / "scripts" / "install-skills.ps1", ROOT / "scripts" / "install-skills.sh",
)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
FORBIDDEN = {
    "github.com/keitark/schematic-humanizer": "old repository URL",
}
PRIVACY_PATTERNS = (
    (re.compile(r"\b(?![^\s@]+@example\.com\b)([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE), "email address"),
    (re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})\b"), "access token"),
    (re.compile(r"\b(?:api[_-]?key|access[_-]?token|secret|password|cookie|authorization)\b\s*[:=]\s*['\"]?([A-Za-z0-9_./+=-]{12,})", re.IGNORECASE), "credential value"),
    (re.compile(r"\b(?:pcbfile|quote|order|project)[_-]?(?:id|no|number)\b\s*[:=]\s*['\"]?([A-Za-z0-9-]{8,})", re.IGNORECASE), "private order identifier"),
    (re.compile(r"(?:pcbFileNo|quoteId|orderId)=[A-Za-z0-9-]{8,}", re.IGNORECASE), "private order URL identifier"),
)
WINDOWS_ABSOLUTE_RE = re.compile(r"\b([A-Za-z]:\\[^\s`'\"<>]+)")
POSIX_PRIVATE_HOME_RE = re.compile(r"(?<![:\w])(/(?:home|Users)/[^/\s`'\"]+(?:/[^\s`'\"]*)?)")
ABSOLUTE_PATH_ALLOWLIST = ("c:\\path\\to\\project", "/home/user/", "/Users/user/")
PLACEHOLDER_VALUES = {"example-token", "redacted", "placeholder", "fixture-id"}


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def skill_frontmatter(path: Path, errors: list[str]) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)} must start with YAML frontmatter", errors)
        return None
    try:
        _, raw, body = text.split("---", 2)
        data = yaml.safe_load(raw)
    except (ValueError, yaml.YAMLError) as exc:
        fail(f"invalid frontmatter in {path.relative_to(ROOT)}: {exc}", errors)
        return None
    if not isinstance(data, dict) or set(data) != {"name", "description"}:
        fail(f"{path.relative_to(ROOT)} frontmatter must contain only name and description", errors)
        return None
    if not body.strip():
        fail(f"{path.relative_to(ROOT)} body is empty", errors)
    return data


def validate_skills(errors: list[str]) -> None:
    found = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
    if found != SKILLS:
        fail(f"skill set mismatch; expected {sorted(SKILLS)}, found {sorted(found)}", errors)
    for name in sorted(SKILLS):
        directory = SKILL_ROOT / name
        skill_md = directory / "SKILL.md"
        metadata_file = directory / "agents" / "openai.yaml"
        license_file = directory / "LICENSE"
        if not skill_md.is_file() or not metadata_file.is_file() or not license_file.is_file():
            fail(f"{name}: missing SKILL.md, agents/openai.yaml, or standalone LICENSE", errors)
            continue
        if license_file.read_text(encoding="utf-8").strip() != (ROOT / "LICENSE").read_text(encoding="utf-8").strip():
            fail(f"{name}: standalone LICENSE differs from repository MIT license", errors)
        text = skill_md.read_text(encoding="utf-8")
        if len(text.splitlines()) > 500:
            fail(f"{name}: SKILL.md exceeds 500 lines", errors)
        if re.search(r"\bTODO\b", text, re.IGNORECASE):
            fail(f"{name}: SKILL.md contains TODO", errors)
        metadata = skill_frontmatter(skill_md, errors)
        if metadata:
            if metadata.get("name") != name or not NAME_RE.fullmatch(str(metadata.get("name", ""))):
                fail(f"{name}: directory/frontmatter name mismatch", errors)
            if len(str(metadata.get("description", "")).strip()) < 40:
                fail(f"{name}: description is too short", errors)
        try:
            openai = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
            interface = openai["interface"]
            for field in ("display_name", "short_description", "default_prompt"):
                if not isinstance(interface.get(field), str) or not interface[field].strip():
                    fail(f"{name}: openai.yaml missing {field}", errors)
            short = interface.get("short_description", "")
            if not 25 <= len(short) <= 64:
                fail(f"{name}: short_description must be 25-64 chars", errors)
            if f"${name}" not in interface.get("default_prompt", ""):
                fail(f"{name}: default_prompt must mention ${name}", errors)
        except (KeyError, TypeError, yaml.YAMLError) as exc:
            fail(f"{name}: invalid agents/openai.yaml: {exc}", errors)


def validate_required(errors: list[str]) -> None:
    for path in REQUIRED:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}", errors)


def validate_links(errors: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = raw.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if path_part and not (markdown.parent / path_part).resolve().exists():
                fail(f"broken link in {markdown.relative_to(ROOT)}: {target}", errors)


def validate_text_and_privacy(errors: list[str]) -> None:
    checked = {".md", ".yml", ".yaml", ".py", ".ps1", ".sh", ".json", ".csv", ".svg", ".txt"}
    tracked_result = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, text=True, capture_output=True, encoding="utf-8"
    )
    tracked = set(tracked_result.stdout.splitlines()) if tracked_result.returncode == 0 else set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in tracked and (path.suffix.lower() in {".pyc", ".pyo"} or "__pycache__" in path.parts):
            fail(f"tracked/generated cache file present: {path.relative_to(ROOT)}", errors)
        if path.suffix.lower() not in checked:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"not valid UTF-8: {path.relative_to(ROOT)}", errors)
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            if line.endswith((" ", "\t")):
                fail(f"trailing whitespace: {path.relative_to(ROOT)}:{line_no}", errors)
        if path.resolve() != Path(__file__).resolve():
            normalized = text.replace("/", "\\")
            for value, reason in FORBIDDEN.items():
                if value.lower() in text.lower() or value.replace("/", "\\").lower() in normalized.lower():
                    fail(f"{reason} in {path.relative_to(ROOT)}", errors)
            for pattern, reason in PRIVACY_PATTERNS:
                for match in pattern.finditer(text):
                    value = (match.group(1) if match.lastindex else match.group(0)).strip("'\"").lower()
                    if value in PLACEHOLDER_VALUES or value.endswith("@example.com"):
                        continue
                    fail(f"{reason} in {path.relative_to(ROOT)}", errors)
                    break
            for match in WINDOWS_ABSOLUTE_RE.finditer(text):
                value = match.group(1).rstrip(".,);]").lower()
                if not value.startswith(ABSOLUTE_PATH_ALLOWLIST[0]):
                    fail(f"absolute Windows path in {path.relative_to(ROOT)}", errors)
                    break
            for match in POSIX_PRIVATE_HOME_RE.finditer(text):
                value = match.group(1).rstrip(".,);]")
                if not value.startswith(ABSOLUTE_PATH_ALLOWLIST[1:]):
                    fail(f"private POSIX home path in {path.relative_to(ROOT)}", errors)
                    break


def validate_assets(errors: list[str]) -> None:
    license_text = (ROOT / "ASSET-LICENSES.md").read_text(encoding="utf-8") if (ROOT / "ASSET-LICENSES.md").exists() else ""
    case_dir = ROOT / "assets" / "case-studies" / "nescart"
    if not case_dir.is_dir():
        fail("missing nescart case-study asset directory", errors)
        return
    for asset in case_dir.iterdir():
        rel = asset.relative_to(ROOT).as_posix()
        if asset.is_file() and rel not in license_text:
            fail(f"case-study asset missing from ASSET-LICENSES.md: {rel}", errors)
    if "assets/banner.png" not in license_text:
        fail("banner missing from ASSET-LICENSES.md", errors)


def main() -> int:
    errors: list[str] = []
    validate_required(errors)
    validate_skills(errors)
    validate_links(errors)
    validate_text_and_privacy(errors)
    validate_assets(errors)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Repository validation passed: {len(SKILLS)} skills, bilingual docs, privacy and licensing checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
