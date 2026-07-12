#!/usr/bin/env python3
"""Audit CPL origins/rotations using explicit physical pad instances."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


MAX_GLOBAL_LAND_PATTERN_TOLERANCE_MM = 0.10


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def input_record(path: Path | None) -> dict | None:
    return {"file": path.name, "sha256": sha256(path)} if path else None


def finite_number(value: object, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def rotate(point: tuple[float, float], degrees: float) -> tuple[float, float]:
    radians = math.radians(degrees)
    x, y = point
    return (x * math.cos(radians) - y * math.sin(radians),
            x * math.sin(radians) + y * math.cos(radians))


def pad_index(pads: list[dict], label: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for pad in pads:
        instance = str(pad.get("instance", ""))
        if not instance or instance in result:
            raise ValueError(f"{label}: blank or duplicate pad instance {instance!r}")
        finite_number(pad.get("x_mm"), f"{label} {instance} x_mm")
        finite_number(pad.get("y_mm"), f"{label} {instance} y_mm")
        result[instance] = pad
    return result


def derive_mapping(board_pads: dict[str, dict], supplier_pads: dict[str, dict], explicit: dict | None) -> dict[str, str]:
    if explicit is not None:
        mapping = {str(key): str(value) for key, value in explicit.items()}
        if set(mapping) != set(board_pads) or set(mapping.values()) != set(supplier_pads) or len(set(mapping.values())) != len(mapping):
            raise ValueError("explicit pad_map must cover each board and supplier physical instance exactly once")
        return mapping
    board_names = [str(pad.get("name", "")) for pad in board_pads.values()]
    supplier_names = [str(pad.get("name", "")) for pad in supplier_pads.values()]
    if Counter(board_names) != Counter(supplier_names):
        raise ValueError("pad names/counts differ; provide explicit physical-instance pad_map")
    if any(count > 1 for count in Counter(board_names).values()):
        raise ValueError("duplicated electrical pad names require explicit physical-instance pad_map")
    supplier_by_name = {str(pad["name"]): instance for instance, pad in supplier_pads.items()}
    return {instance: supplier_by_name[str(pad["name"])] for instance, pad in board_pads.items()}


def solve(board_pads: dict[str, dict], supplier_pads: dict[str, dict], mapping: dict[str, str]):
    candidates = []
    for angle in (0, 90, 180, 270):
        deltas = []
        for board_instance, supplier_instance in mapping.items():
            board = board_pads[board_instance]
            supplier = supplier_pads[supplier_instance]
            sx, sy = rotate((finite_number(supplier["x_mm"], "supplier pad x_mm"),
                             finite_number(supplier["y_mm"], "supplier pad y_mm")), angle)
            deltas.append((finite_number(board["x_mm"], "board pad x_mm") - sx,
                           finite_number(board["y_mm"], "board pad y_mm") - sy))
        dx = sum(item[0] for item in deltas) / len(deltas)
        dy = sum(item[1] for item in deltas) / len(deltas)
        rms = math.sqrt(sum((x - dx) ** 2 + (y - dy) ** 2 for x, y in deltas) / len(deltas))
        candidates.append((rms, angle, dx, dy))
    return sorted(candidates)


def cpl_rows(path: Path) -> tuple[list[dict], dict[str, dict]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        required = {"Designator", "Mid X", "Mid Y", "Layer", "Rotation"}
        missing = sorted(required - set(headers))
        if missing:
            raise ValueError(f"CPL missing required columns: {missing}")
        rows = list(reader)
    if not rows:
        raise ValueError("CPL has no placement rows")
    by_ref: dict[str, dict] = {}
    for row in rows:
        ref = row.get("Designator", "").strip()
        if not ref or ref in by_ref:
            raise ValueError(f"blank or duplicate CPL Designator {ref!r}")
        for field_name in ("Mid X", "Mid Y", "Rotation"):
            finite_number(row.get(field_name), f"{ref} CPL {field_name}")
        by_ref[ref] = row
    return rows, by_ref


def normalize_side(value: object, label: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"top", "t", "front", "f"}:
        return "Top"
    if normalized in {"bottom", "bot", "b", "back"}:
        return "Bottom"
    raise ValueError(f"{label}: side must be Top or Bottom, got {value!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board-geometry", type=Path, required=True)
    parser.add_argument("--supplier-geometry", type=Path, required=True)
    parser.add_argument("--cpl", type=Path, required=True)
    parser.add_argument("--mapping", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance-mm", type=float, default=0.10)
    parser.add_argument("--ambiguity-mm", type=float, default=0.01)
    args = parser.parse_args()

    if (not math.isfinite(args.tolerance_mm) or args.tolerance_mm <= 0 or
            args.tolerance_mm > MAX_GLOBAL_LAND_PATTERN_TOLERANCE_MM):
        raise SystemExit(
            f"--tolerance-mm must be >0 and <= {MAX_GLOBAL_LAND_PATTERN_TOLERANCE_MM}; "
            "use package-specific evidence for larger variance"
        )
    if not math.isfinite(args.ambiguity_mm) or args.ambiguity_mm <= 0:
        raise SystemExit("--ambiguity-mm must be a positive finite value")

    board = json.loads(args.board_geometry.read_text(encoding="utf-8"))
    supplier = json.loads(args.supplier_geometry.read_text(encoding="utf-8"))
    mapping_data = json.loads(args.mapping.read_text(encoding="utf-8")) if args.mapping else {"packages": {}}
    if board.get("schema") != "pcba-footprint-geometry-v1":
        raise SystemExit("invalid board geometry schema")
    if supplier.get("schema") != "pcba-supplier-package-geometry-v1":
        raise SystemExit("invalid supplier geometry schema")
    packages = {item["supplier_part"]: item for item in supplier.get("packages", [])}
    rows, by_ref = cpl_rows(args.cpl)
    components = board.get("components", [])
    expected = [item.get("reference") for item in components]
    if len(expected) != len(set(expected)):
        raise SystemExit("duplicate board component reference")

    results = []
    corrections: dict[str, tuple[float, float, float, str]] = {}
    for component in components:
        ref = component["reference"]
        part = component["supplier_part"]
        result = {"reference": ref, "supplier_part": part, "status": "BLOCKED"}
        try:
            if ref not in by_ref:
                raise ValueError("reference missing from CPL")
            if part not in packages:
                raise ValueError("supplier package geometry missing")
            board_side = normalize_side(component.get("side"), f"{ref} board")
            cpl_side = normalize_side(by_ref[ref].get("Layer"), f"{ref} CPL")
            if cpl_side != board_side:
                raise ValueError(f"side mismatch: board={board_side}, CPL={cpl_side}")
            board_pads = pad_index(component.get("pads", []), f"{ref} board")
            supplier_pads = pad_index(packages[part].get("pads", []), f"{part} supplier")
            if len(board_pads) < 2:
                raise ValueError("at least two physical pads are required")
            package_rule = mapping_data.get("packages", {}).get(part, {})
            explicit = package_rule.get("pad_map")
            physical_map = derive_mapping(board_pads, supplier_pads, explicit)
            candidates = solve(board_pads, supplier_pads, physical_map)
            best, second = candidates[0], candidates[1]
            rms, angle, dx, dy = best
            board_pin1 = component.get("pin1_instance")
            supplier_pin1 = packages[part].get("pin1_instance")
            pin1_match = bool(board_pin1 and supplier_pin1 and physical_map.get(board_pin1) == supplier_pin1)
            ambiguous = (second[0] - rms) < args.ambiguity_mm
            source_rotation = finite_number(component.get("rotation_deg", 0), f"{ref} rotation_deg") % 360
            global_dx, global_dy = rotate((dx, dy), source_rotation)
            x = finite_number(component.get("x_mm"), f"{ref} x_mm") + global_dx
            y = finite_number(component.get("y_mm"), f"{ref} y_mm") + global_dy
            rotation = (source_rotation + angle) % 360
            approved_angle = package_rule.get("approved_registration_angle_deg")
            approved_angle_value = (
                finite_number(approved_angle, f"{part} approved_registration_angle_deg") % 360
                if approved_angle is not None else None
            )
            package_evidence = str(package_rule.get("evidence", "")).strip()
            registration_status = "PASS"
            registration_error = ""
            if not pin1_match:
                registration_status = "BLOCKED_PIN1"
                registration_error = "physical pin-1 instances do not agree"
            elif ambiguous and (
                approved_angle_value is None or abs(approved_angle_value - angle) > 1e-6 or not package_evidence
            ):
                registration_status = "BLOCKED_AMBIGUOUS_ROTATION"
                registration_error = (
                    "best rotation is geometrically ambiguous without matching "
                    "approved_registration_angle_deg and nonempty package/pin-1 evidence"
                )
            elif ambiguous:
                registration_status = "PASS_APPROVED_ROTATION"

            land_pattern_status = "PASS"
            land_pattern_error = ""
            if rms > args.tolerance_mm:
                approved_limit = package_rule.get("land_pattern_rms_limit_mm")
                evidence = package_evidence
                approved_limit_value = (
                    finite_number(approved_limit, f"{part} land_pattern_rms_limit_mm")
                    if approved_limit is not None else None
                )
                if (approved_limit_value is not None and approved_limit_value > 0 and
                        rms <= approved_limit_value and evidence):
                    land_pattern_status = "PASS_APPROVED_VARIANCE"
                else:
                    land_pattern_status = "BLOCKED_LAND_PATTERN"
                    land_pattern_error = (
                        f"best RMS residual {rms:.4f} mm exceeds {args.tolerance_mm:.4f} mm; "
                        "provide a package-specific limit and evidence after manufacturer drawing review"
                    )

            passed = registration_status.startswith("PASS") and land_pattern_status.startswith("PASS")
            if passed:
                corrections[ref] = (x, y, rotation, board_side)
            result.update({
                "status": "PASS" if passed else "BLOCKED", "physical_pads": len(board_pads),
                "registration_status": registration_status,
                "land_pattern_status": land_pattern_status,
                "rms_mm": round(rms, 6), "second_rms_mm": round(second[0], 6),
                "ambiguous_geometry": ambiguous, "pin1_match": pin1_match,
                "offset_x_mm": round(dx, 6), "offset_y_mm": round(dy, 6),
                "registration_angle_deg": angle,
                "candidate_x_mm": round(x, 6), "candidate_y_mm": round(y, 6),
                "rotation_deg": round(rotation, 6), "board_side": board_side,
                "cpl_side": cpl_side,
                "error": "; ".join(item for item in (registration_error, land_pattern_error) if item),
            })
        except (KeyError, TypeError, ValueError) as exc:
            result["error"] = str(exc)
        results.append(result)

    unexpected = sorted(set(by_ref) - set(expected))
    if unexpected:
        results.append({"status": "BLOCKED", "error": f"unexpected CPL references: {unexpected}"})
    failures = [item for item in results if item.get("status") != "PASS"]
    report = {
        "schema": "cpl-geometry-audit-v1",
        "status": "PASS" if not failures else "BLOCKED",
        "inputs": {
            "board_geometry": input_record(args.board_geometry),
            "supplier_geometry": input_record(args.supplier_geometry),
            "mapping": input_record(args.mapping),
            "cpl": input_record(args.cpl),
        },
        "settings": {
            "coordinate_contract": "pcba-footprint-geometry-v1",
            "tolerance_mm": args.tolerance_mm,
            "ambiguity_mm": args.ambiguity_mm,
        },
        "references_expected": len(expected), "references_cpl": len(by_ref),
        "unresolved_count": len(failures), "results": results,
    }
    if failures:
        if args.output.exists():
            args.output.unlink()
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 1

    output_rows = []
    for row in rows:
        updated = dict(row)
        x, y, rotation, side = corrections[row["Designator"]]
        updated["Mid X"] = f"{x:.4f}"
        updated["Mid Y"] = f"{y:.4f}"
        updated["Rotation"] = f"{rotation:.6f}".rstrip("0").rstrip(".")
        updated["Layer"] = side
        output_rows.append(updated)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)
    report["output"] = {"file": args.output.name, "sha256": sha256(args.output)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
