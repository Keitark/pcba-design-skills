#!/usr/bin/env python3
"""Validate contract, revision consistency, and hashes for a PCBA release."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


APPROVALS = (
    "design_critical_substitution", "assembly_placement", "final_price", "payment",
)
REQUIRED_ARTIFACTS = {
    "board_source", "eda_project", "gerber", "drill", "bom", "cpl",
    "constraints", "render_top", "render_bottom", "circuit_review",
    "schematic_connectivity", "schematic_visual_audit", "layout_review",
    "sourcing_lock",
}
REQUIRED_CONSTRAINTS = {
    "board_width_mm", "board_height_mm", "layer_count", "thickness_mm",
    "surface_finish", "assembly_sides", "quantity_pcbs", "quantity_assembled",
}
ZERO_VERIFICATIONS = {
    "unexplained_raw_disconnects", "real_drc_errors", "layout_check_failures",
}
PASS_VERIFICATIONS = {
    "circuit_gate", "layout_gate", "raw_connectivity", "power_connectivity",
    "visual_mechanical_review", "dfm_review", "sourcing_lock_current",
    "revision_reconciled",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def passlike(value: object) -> bool:
    return value is True or (isinstance(value, str) and value.strip().upper() == "PASS")


def zero(value: object) -> bool:
    try:
        return float(value) == 0
    except (TypeError, ValueError):
        return False


def positive_number(value: object) -> bool:
    if isinstance(value, bool):
        return False
    try:
        number = float(value)
        return math.isfinite(number) and number > 0
    except (TypeError, ValueError):
        return False


def positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def valid_assembly_sides(value: object) -> bool:
    if isinstance(value, str):
        items = [item.strip().title() for item in value.replace("+", ",").replace(";", ",").split(",") if item.strip()]
    elif isinstance(value, list):
        items = [str(item).strip().title() for item in value if str(item).strip()]
    else:
        return False
    return bool(items) and set(items) <= {"Top", "Bottom"}


def contract_errors(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "pcba-release-manifest-v1":
        errors.append("invalid schema")
    revision = data.get("revision")
    if not revision:
        errors.append("revision is required")
    status = data.get("status")
    if status not in {"PASS", "BLOCKED", "USER_REVIEW"}:
        errors.append("invalid release status")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        if status == "PASS":
            errors.append("PASS artifacts must be a non-empty object")
        artifacts = {}
    for role, item in artifacts.items():
        if not isinstance(item, dict):
            errors.append(f"{role}: artifact entry must be an object")
        elif item.get("revision") != revision:
            errors.append(f"{role}: mixed revision {item.get('revision')!r}")

    approvals = data.get("approvals", {})
    approval_evidence = data.get("approval_evidence", {})
    for name in APPROVALS:
        decision = approvals.get(name)
        if decision not in {"PENDING", "APPROVED", "REJECTED"}:
            errors.append(f"approval {name}: invalid status")
        if decision in {"APPROVED", "REJECTED"} and not approval_evidence.get(name):
            errors.append(f"approval {name}: decision requires evidence")

    if status == "PASS":
        missing_artifacts = sorted(REQUIRED_ARTIFACTS - set(artifacts))
        if missing_artifacts:
            errors.append(f"PASS missing artifact roles: {missing_artifacts}")
        constraints = data.get("constraints", {})
        missing_constraints = sorted(REQUIRED_CONSTRAINTS - set(constraints))
        if missing_constraints:
            errors.append(f"PASS missing constraints: {missing_constraints}")
        for name in ("board_width_mm", "board_height_mm", "thickness_mm"):
            if not positive_number(constraints.get(name)):
                errors.append(f"PASS requires positive finite {name}")
        for name in ("layer_count", "quantity_pcbs", "quantity_assembled"):
            if not positive_integer(constraints.get(name)):
                errors.append(f"PASS requires positive integer {name}")
        if (positive_integer(constraints.get("quantity_pcbs")) and
                positive_integer(constraints.get("quantity_assembled")) and
                constraints["quantity_assembled"] > constraints["quantity_pcbs"]):
            errors.append("quantity_assembled may not exceed quantity_pcbs")
        finish = constraints.get("surface_finish")
        if (not isinstance(finish, str) or not finish.strip() or
                finish.strip().lower() in {"none", "tbd", "unknown"}):
            errors.append("PASS requires nonempty surface_finish")
        if not valid_assembly_sides(constraints.get("assembly_sides")):
            errors.append("PASS assembly_sides must contain Top and/or Bottom")
        verification = data.get("verification", {})
        for name in sorted(ZERO_VERIFICATIONS):
            if not zero(verification.get(name)):
                errors.append(f"PASS requires {name}=0")
        for name in sorted(PASS_VERIFICATIONS):
            if not passlike(verification.get(name)):
                errors.append(f"PASS requires {name}=PASS")
        substitution_required = verification.get("design_critical_substitution_required")
        if not isinstance(substitution_required, bool):
            errors.append("PASS requires boolean design_critical_substitution_required")
        elif substitution_required and approvals.get("design_critical_substitution") != "APPROVED":
            errors.append("required design-critical substitution is not approved")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = contract_errors(data)
    artifacts = data.get("artifacts") if isinstance(data.get("artifacts"), dict) else {}
    for role, item in artifacts.items():
        if not isinstance(item, dict):
            continue
        path = (args.manifest.parent / item.get("path", "")).resolve()
        if not path.is_file():
            errors.append(f"{role}: missing file {path}")
            continue
        actual = sha256(path)
        if actual != item.get("sha256"):
            errors.append(f"{role}: SHA-256 mismatch")
        if path.stat().st_size != item.get("size_bytes"):
            errors.append(f"{role}: size mismatch")
    if data.get("status") != "PASS":
        errors.append(f"manifest status is {data.get('status')!r}, not PASS")
    result = {
        "status": "PASS" if not errors else "BLOCKED",
        "manifest_status": data.get("status"),
        "artifacts": len(artifacts),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
