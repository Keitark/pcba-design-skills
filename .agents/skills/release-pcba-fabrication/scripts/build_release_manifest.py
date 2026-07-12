#!/usr/bin/env python3
"""Build a revision-consistent pcba-release-manifest-v1 file."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

from validate_release_manifest import APPROVALS, contract_errors


def pairs(values: list[str], label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"{label} must use KEY=VALUE: {value}")
        key, item = value.split("=", 1)
        if not key or key in result:
            raise SystemExit(f"invalid or duplicate {label} key: {key}")
        result[key] = item
    return result


def scalar(value: str):
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none"}:
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(".pcba-workflow/release-manifest.json"))
    parser.add_argument("--release", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--status", choices=("PASS", "BLOCKED", "USER_REVIEW"), default="BLOCKED")
    parser.add_argument("--artifact", action="append", default=[], metavar="ROLE=PATH")
    parser.add_argument("--artifact-revision", action="append", default=[], metavar="ROLE=REVISION")
    parser.add_argument("--constraint", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--verification", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--approval", action="append", default=[], metavar="NAME=STATUS")
    parser.add_argument("--approval-evidence", action="append", default=[], metavar="NAME=EVIDENCE")
    args = parser.parse_args()

    artifact_paths = pairs(args.artifact, "artifact")
    artifact_revisions = pairs(args.artifact_revision, "artifact revision")
    if not artifact_paths:
        raise SystemExit("at least one --artifact is required")
    if set(artifact_paths) != set(artifact_revisions):
        raise SystemExit("every artifact needs exactly one --artifact-revision")
    mismatched = {role: rev for role, rev in artifact_revisions.items() if rev != args.revision}
    if mismatched:
        raise SystemExit(f"mixed artifact revisions: {mismatched}")

    base = args.output.parent.resolve()
    artifacts: dict[str, dict] = {}
    for role, raw_path in artifact_paths.items():
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise SystemExit(f"artifact not found: {role}={path}")
        stored = Path(os.path.relpath(path, base)).as_posix()
        artifacts[role] = {
            "path": stored, "revision": artifact_revisions[role],
            "size_bytes": path.stat().st_size, "sha256": sha256(path),
        }

    approval_values = pairs(args.approval, "approval")
    approval_evidence = pairs(args.approval_evidence, "approval evidence")
    unknown_approvals = (set(approval_values) | set(approval_evidence)) - set(APPROVALS)
    if unknown_approvals:
        raise SystemExit(f"unknown approvals: {sorted(unknown_approvals)}")
    approvals = {name: approval_values.get(name, "PENDING") for name in APPROVALS}
    evidence = {name: [approval_evidence[name]] if name in approval_evidence else [] for name in APPROVALS}

    manifest = {
        "schema": "pcba-release-manifest-v1",
        "release": args.release,
        "revision": args.revision,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": args.status,
        "artifacts": artifacts,
        "constraints": {key: scalar(value) for key, value in pairs(args.constraint, "constraint").items()},
        "verification": {key: scalar(value) for key, value in pairs(args.verification, "verification").items()},
        "approvals": approvals,
        "approval_evidence": evidence,
    }
    errors = contract_errors(manifest)
    if errors:
        raise SystemExit("release manifest contract failed: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "manifest": str(args.output), "artifacts": len(artifacts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
