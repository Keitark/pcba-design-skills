#!/usr/bin/env python3
"""Reconcile every submitted CPL row with a supplier-imported placement table."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


ALIASES = {
    "reference": ("Designator", "Reference", "Ref", "Top Designator", "Bottom Designator"),
    "x": ("Mid X", "X", "PosX", "Center X"),
    "y": ("Mid Y", "Y", "PosY", "Center Y"),
    "side": ("Layer", "Side"),
    "rotation": ("Rotation", "Rot", "Angle"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def input_record(path: Path | None) -> dict | None:
    if path is None:
        return None
    return {"file": path.name, "sha256": sha256(path) if path.is_file() else None}


def field(row: dict, key: str) -> str:
    for alias in ALIASES[key]:
        if alias in row and str(row[alias]).strip():
            return str(row[alias]).strip()
    raise ValueError(f"missing {key}; accepted headers: {ALIASES[key]}")


def side(value: str) -> str:
    normalized = value.strip().lower().replace(".", "")
    if normalized in {"top", "t", "front", "fcu"}:
        return "Top"
    if normalized in {"bottom", "bot", "b", "back", "bcu"}:
        return "Bottom"
    raise ValueError(f"unknown side {value!r}")


def angle_delta(actual: float, expected: float) -> float:
    return abs((actual - expected + 180.0) % 360.0 - 180.0)


def finite_number(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def load_rows(path: Path, unit: str) -> dict[str, dict]:
    scale = 25.4 if unit == "inch" else 1.0
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = [key for key, aliases in ALIASES.items() if not headers.intersection(aliases)]
        if missing:
            raise ValueError(f"{path.name}: missing accepted headers for {missing}")
        raw_rows = list(reader)
    if not raw_rows:
        raise ValueError(f"{path.name}: placement table has no rows")
    rows: dict[str, dict] = {}
    for number, raw in enumerate(raw_rows, start=2):
        try:
            ref = field(raw, "reference")
            if ref in rows:
                raise ValueError(f"duplicate reference {ref}")
            x = finite_number(field(raw, "x"), "x") * scale
            y = finite_number(field(raw, "y"), "y") * scale
            rotation = finite_number(field(raw, "rotation"), "rotation") % 360.0
            rows[ref] = {
                "reference": ref,
                "x_mm": x,
                "y_mm": y,
                "side": side(field(raw, "side")),
                "rotation_deg": rotation,
            }
        except ValueError as exc:
            raise ValueError(f"{path}:{number}: {exc}") from exc
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitted", type=Path, required=True)
    parser.add_argument("--imported", type=Path, required=True)
    parser.add_argument("--submitted-unit", choices=("mm", "inch"), default="mm")
    parser.add_argument("--imported-unit", choices=("mm", "inch"), default="mm")
    parser.add_argument("--mapping", type=Path, help="expected supplier import transform JSON")
    parser.add_argument("--position-tolerance-mm", type=float, default=0.02)
    parser.add_argument("--rotation-tolerance-deg", type=float, default=0.1)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if (not math.isfinite(args.position_tolerance_mm) or
            not 0 < args.position_tolerance_mm <= 0.10):
        raise SystemExit("--position-tolerance-mm must be >0 and <=0.10")
    if (not math.isfinite(args.rotation_tolerance_deg) or
            not 0 < args.rotation_tolerance_deg <= 1.0):
        raise SystemExit("--rotation-tolerance-deg must be >0 and <=1.0")
    inputs = {
        "submitted": input_record(args.submitted),
        "imported": input_record(args.imported),
        "mapping": input_record(args.mapping),
    }
    settings = {
        "submitted_unit": args.submitted_unit,
        "imported_unit": args.imported_unit,
        "position_tolerance_mm": args.position_tolerance_mm,
        "rotation_tolerance_deg": args.rotation_tolerance_deg,
    }

    try:
        submitted = load_rows(args.submitted, args.submitted_unit)
        imported = load_rows(args.imported, args.imported_unit)
    except (OSError, ValueError) as exc:
        report = {
            "schema": "cpl-import-reconciliation-v1", "status": "BLOCKED",
            "inputs": inputs, "settings": settings,
            "unresolved_count": 1, "errors": [str(exc)],
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 1

    mapping = json.loads(args.mapping.read_text(encoding="utf-8")) if args.mapping else {}
    defaults = mapping.get("default", {})
    reference_rules = mapping.get("references", {})
    results = []
    all_refs = sorted(set(submitted) | set(imported))
    observed_deltas = []
    for ref in all_refs:
        item = {"reference": ref, "status": "BLOCKED", "errors": []}
        if ref not in submitted:
            item["errors"].append("unexpected imported reference")
        elif ref not in imported:
            item["errors"].append("missing imported reference")
        else:
            source = submitted[ref]
            actual = imported[ref]
            rule = dict(defaults)
            rule.update(reference_rules.get(ref, {}))
            try:
                expected_x = source["x_mm"] + finite_number(rule.get("dx_mm", 0.0), f"{ref} dx_mm")
                expected_y = source["y_mm"] + finite_number(rule.get("dy_mm", 0.0), f"{ref} dy_mm")
                rotation_offset = finite_number(rule.get("rotation_offset_deg", 0.0), f"{ref} rotation_offset_deg")
            except ValueError as exc:
                item["errors"].append(str(exc))
                results.append(item)
                continue
            expected_rotation = (source["rotation_deg"] + rotation_offset) % 360.0
            dx = actual["x_mm"] - expected_x
            dy = actual["y_mm"] - expected_y
            dr = angle_delta(actual["rotation_deg"], expected_rotation)
            observed_deltas.append((actual["x_mm"] - source["x_mm"], actual["y_mm"] - source["y_mm"]))
            if abs(dx) > args.position_tolerance_mm or abs(dy) > args.position_tolerance_mm:
                item["errors"].append("position outside tolerance")
            if source["side"] != actual["side"]:
                item["errors"].append("side mismatch")
            if dr > args.rotation_tolerance_deg:
                item["errors"].append("rotation outside tolerance")
            item.update({
                "submitted": source, "imported": actual,
                "expected_import": {"x_mm": expected_x, "y_mm": expected_y,
                                    "side": source["side"], "rotation_deg": expected_rotation},
                "delta_from_expected": {"x_mm": dx, "y_mm": dy, "rotation_deg": dr},
            })
            if not item["errors"]:
                item["status"] = "PASS"
        results.append(item)

    failures = [item for item in results if item["status"] != "PASS"]
    mean_delta = {
        "x_mm": sum(item[0] for item in observed_deltas) / len(observed_deltas),
        "y_mm": sum(item[1] for item in observed_deltas) / len(observed_deltas),
    } if observed_deltas else None
    report = {
        "schema": "cpl-import-reconciliation-v1",
        "status": "PASS" if not failures else "BLOCKED",
        "inputs": inputs,
        "settings": settings,
        "submitted_count": len(submitted), "imported_count": len(imported),
        "unresolved_count": len(failures),
        "observed_mean_import_delta_mm": mean_delta,
        "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
