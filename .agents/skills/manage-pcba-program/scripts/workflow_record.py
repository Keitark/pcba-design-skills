#!/usr/bin/env python3
"""Create and validate a hash-chained PCBA workflow recording."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
from pathlib import Path


SCHEMA = "pcba-workflow-recording-v1"
STAGES = (
    "product_definition", "sourcing", "circuit", "schematic_netlist",
    "schematic_visual", "placement", "routing", "manufacturing_release",
    "assembly_placement", "quote", "order_stop", "media",
)
GATE_STATUSES = ("PASS", "BLOCKED", "USER_REVIEW")
ZERO_HASH = "0" * 64
SENSITIVE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    re.compile(
        r"(?:batchnum|pcbfileno|cartaccessid|cookie|authorization|"
        r"session(?:id|token)|api[_-]?key|access[_-]?token)\s*[:=/?]\s*"
        r"[A-Z0-9._-]+", re.I,
    ),
    re.compile(r"\bW\d{12,}\b", re.I),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_hash(value: dict) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def session_path(root: Path) -> Path:
    return root / "recording-session.json"


def events_path(root: Path) -> Path:
    return root / "events.jsonl"


def read_session(root: Path) -> dict:
    path = session_path(root)
    if not path.is_file():
        raise ValueError(f"recording session is missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_session(root: Path, session: dict) -> None:
    path = session_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(session, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def public_text_errors(label: str, text: str) -> list[str]:
    errors: list[str] = []
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(text):
            errors.append(f"{label}: possible private identifier: {pattern.pattern}")
    return errors


def artifact_record(raw_path: str, root: Path, role: str, public: bool) -> dict:
    project_root = root.resolve().parent
    path = Path(raw_path).resolve()
    if not path.is_file():
        raise ValueError(f"{role} file does not exist: {path}")
    try:
        relative = path.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(
            f"{role} must be inside the project root {project_root}: {path}"
        ) from exc
    stored = relative.as_posix()
    if public:
        privacy = public_text_errors(f"{role} path", stored)
        if privacy:
            raise ValueError("; ".join(privacy))
    return {
        "path": stored,
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


def snapshot_artifact_record(
    source: dict, root: Path, role: str, sequence: int, index: int,
) -> dict:
    """Copy a mutable input/output into an immutable event checkpoint."""
    project_root = root.resolve().parent
    source_path = project_root / source["path"]
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", source_path.name).strip("-")
    if not safe_name:
        safe_name = "artifact"
    snapshot_dir = root / "snapshots" / f"{sequence:04d}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    destination = snapshot_dir / (
        f"{role}-{index:02d}-{source['sha256'][:12]}-{safe_name}"
    )
    if destination.exists():
        if sha256_file(destination) != source["sha256"]:
            raise ValueError(f"snapshot collision with different content: {destination}")
    else:
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        shutil.copy2(source_path, temporary)
        temporary.replace(destination)
    record = artifact_record(str(destination), root, role, False)
    record["source_path"] = source["path"]
    return record


def load_events(root: Path) -> tuple[list[dict], list[str]]:
    path = events_path(root)
    if not path.exists():
        return [], []
    events: list[dict] = []
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            errors.append(f"line {line_number}: blank lines are not allowed")
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc}")
    return events, errors


def validate_recording(root: Path) -> list[str]:
    errors: list[str] = []
    try:
        session = read_session(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [str(exc)]
    if session.get("schema") != SCHEMA:
        errors.append(f"session schema must be {SCHEMA}")
    if session.get("status") not in {"ACTIVE", "CLOSED"}:
        errors.append("session status must be ACTIVE or CLOSED")
    if not session.get("project_id"):
        errors.append("project_id is required")

    events, parse_errors = load_events(root)
    errors.extend(parse_errors)
    previous = ZERO_HASH
    project_root = root.resolve().parent
    for index, event in enumerate(events, 1):
        if event.get("schema") != SCHEMA:
            errors.append(f"event {index}: invalid schema")
        if event.get("sequence") != index:
            errors.append(f"event {index}: sequence must be {index}")
        if event.get("stage") not in STAGES:
            errors.append(f"event {index}: invalid stage")
        gate_status = event.get("gate_status")
        if gate_status is not None and gate_status not in GATE_STATUSES:
            errors.append(f"event {index}: invalid gate_status")
        if event.get("previous_event_sha256") != previous:
            errors.append(f"event {index}: previous-event hash mismatch")
        supplied_hash = event.get("event_sha256")
        unhashed = dict(event)
        unhashed.pop("event_sha256", None)
        actual_hash = canonical_hash(unhashed)
        if supplied_hash != actual_hash:
            errors.append(f"event {index}: event hash mismatch")
        previous = supplied_hash or actual_hash

        captions = event.get("caption", {})
        for language in ("en", "ja"):
            errors.extend(public_text_errors(
                f"event {index} caption.{language}", captions.get(language, "")
            ))
        for group in ("inputs", "outputs", "frames", "private_evidence"):
            for artifact in event.get(group, []):
                stored = artifact.get("path", "")
                path = project_root / stored
                if not path.is_file():
                    errors.append(f"event {index}: missing {group} artifact: {stored}")
                    continue
                if artifact.get("sha256") != sha256_file(path):
                    errors.append(f"event {index}: hash mismatch: {stored}")
                if artifact.get("size") != path.stat().st_size:
                    errors.append(f"event {index}: size mismatch: {stored}")
                if group == "frames":
                    errors.extend(public_text_errors(
                        f"event {index} public frame path", stored
                    ))

    if session.get("status") == "CLOSED":
        path = events_path(root)
        if not path.is_file():
            errors.append("closed session is missing events.jsonl")
        else:
            if session.get("events_sha256") != sha256_file(path):
                errors.append("closed session event-log hash mismatch")
        if session.get("event_count") != len(events):
            errors.append("closed session event count mismatch")
        if session.get("final_event_sha256") != previous:
            errors.append("closed session final-event hash mismatch")
    return errors


def command_init(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    if session_path(root).exists() or events_path(root).exists():
        raise SystemExit(f"refusing to overwrite an existing recording in {root}")
    root.mkdir(parents=True, exist_ok=True)
    for directory in ("frames", "private", "snapshots"):
        (root / directory).mkdir(exist_ok=True)
    events_path(root).write_text("", encoding="utf-8")
    write_session(root, {
        "schema": SCHEMA,
        "project_id": args.project,
        "status": "ACTIVE",
        "created_at_utc": utc_now(),
        "stop_before": args.stop_before,
        "events_file": "events.jsonl",
    })
    return print_result(root)


def command_add(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    session = read_session(root)
    if session.get("status") != "ACTIVE":
        raise SystemExit("cannot append to a closed recording")
    errors = validate_recording(root)
    if errors:
        print(json.dumps({"status": "BLOCKED", "errors": errors}, indent=2))
        return 1
    events, _ = load_events(root)
    previous = events[-1]["event_sha256"] if events else ZERO_HASH
    sequence = len(events) + 1
    privacy_errors = []
    privacy_errors.extend(public_text_errors("caption.en", args.caption_en))
    privacy_errors.extend(public_text_errors("caption.ja", args.caption_ja or ""))
    if privacy_errors:
        raise SystemExit("; ".join(privacy_errors))

    input_sources = [
        artifact_record(path, root, "input", False) for path in args.input
    ]
    output_sources = [
        artifact_record(path, root, "output", False) for path in args.output
    ]
    frame_records = [
        artifact_record(path, root, "frame", True) for path in args.frame
    ]
    private_records = [
        artifact_record(path, root, "private evidence", False)
        for path in args.private_evidence
    ]
    event = {
        "schema": SCHEMA,
        "sequence": sequence,
        "time_utc": utc_now(),
        "stage": args.stage,
        "action": args.action,
        "tool": args.tool,
        "gate_status": args.gate_status,
        "caption": {"en": args.caption_en, "ja": args.caption_ja or ""},
        "source_revision": args.source_revision or "",
        "inputs": [
            snapshot_artifact_record(source, root, "input", sequence, index)
            for index, source in enumerate(input_sources, 1)
        ],
        "outputs": [
            snapshot_artifact_record(source, root, "output", sequence, index)
            for index, source in enumerate(output_sources, 1)
        ],
        "frames": frame_records,
        "private_evidence": private_records,
        "previous_event_sha256": previous,
    }
    event["event_sha256"] = canonical_hash(event)
    with events_path(root).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
    return print_result(root)


def command_close(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    session = read_session(root)
    if session.get("status") != "ACTIVE":
        raise SystemExit("recording is already closed")
    errors = validate_recording(root)
    if errors:
        print(json.dumps({"status": "BLOCKED", "errors": errors}, indent=2))
        return 1
    events, _ = load_events(root)
    session.update({
        "status": "CLOSED",
        "closed_at_utc": utc_now(),
        "event_count": len(events),
        "events_sha256": sha256_file(events_path(root)),
        "final_event_sha256": events[-1]["event_sha256"] if events else ZERO_HASH,
    })
    write_session(root, session)
    return print_result(root)


def print_result(root: Path) -> int:
    errors = validate_recording(root)
    events, _ = load_events(root)
    print(json.dumps({
        "status": "PASS" if not errors else "BLOCKED",
        "root": str(root),
        "events": len(events),
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(".pcba-workflow"))
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("--project", required=True)
    init_parser.add_argument("--stop-before", default="final-submit")

    add_parser = sub.add_parser("add")
    add_parser.add_argument("--stage", choices=STAGES, required=True)
    add_parser.add_argument("--action", required=True)
    add_parser.add_argument("--tool", required=True)
    add_parser.add_argument("--gate-status", choices=GATE_STATUSES)
    add_parser.add_argument("--caption-en", required=True)
    add_parser.add_argument("--caption-ja")
    add_parser.add_argument("--source-revision")
    add_parser.add_argument("--input", action="append", default=[])
    add_parser.add_argument("--output", action="append", default=[])
    add_parser.add_argument("--frame", action="append", default=[])
    add_parser.add_argument("--private-evidence", action="append", default=[])

    sub.add_parser("validate")
    sub.add_parser("close")
    args = parser.parse_args()

    if args.command == "init":
        return command_init(args)
    if args.command == "add":
        return command_add(args)
    if args.command == "close":
        return command_close(args)
    return print_result(args.root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
