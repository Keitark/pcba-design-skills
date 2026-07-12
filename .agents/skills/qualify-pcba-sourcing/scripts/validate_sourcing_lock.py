#!/usr/bin/env python3
"""Validate sourcing-lock-v1 evidence, quantities, approvals, and cost."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
from pathlib import Path


FIELDS = [
    "reference", "function", "quantity_per_board", "assembly_quantity",
    "required_quantity", "order_quantity", "manufacturer", "requested_mpn",
    "mpn", "supplier_part_number", "package", "package_verified", "footprint",
    "pinout_verified", "cad_status", "model_3d_status", "lifecycle",
    "stock_checked_at", "stock_quantity", "moq", "unit_price", "currency",
    "assembly_class", "line_parts_cost", "setup_fee", "extended_fee",
    "line_total_cost", "datasheet_url", "approved_alternates",
    "substitution_approved", "substitution_approval_evidence",
    "design_critical", "approval_required", "status", "evidence_url",
]
ROW_STATUSES = {"PASS", "BLOCKED", "USER_REVIEW"}
LIFECYCLES = {"active", "nrnd", "eol", "obsolete", "last-time-buy", "unknown"}
EVIDENCE_STATES = {"verified", "unverified", "missing", "not-required"}


def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def references(value: str) -> list[str]:
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]


def integer(row: dict[str, str], field: str, number: int, errors: list[str], *, positive: bool = True) -> int | None:
    try:
        value = int(row.get(field, ""))
        if value < (1 if positive else 0):
            raise ValueError
        return value
    except (ValueError, TypeError):
        qualifier = "positive" if positive else "non-negative"
        errors.append(f"row {number}: {field} must be a {qualifier} integer")
        return None


def decimal(row: dict[str, str], field: str, number: int, errors: list[str]) -> float | None:
    try:
        value = float(row.get(field, ""))
        if not math.isfinite(value) or value < 0:
            raise ValueError
        return value
    except (ValueError, TypeError):
        errors.append(f"row {number}: {field} must be a non-negative finite number")
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--max-age-days", type=int, default=14)
    parser.add_argument("--as-of", help="ISO timestamp used for deterministic validation")
    args = parser.parse_args()
    as_of = parse_time(args.as_of) if args.as_of else dt.datetime.now(dt.timezone.utc)

    errors: list[str] = []
    warnings: list[str] = []
    with args.csv_file.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        missing = [field for field in FIELDS if field not in headers]
        extra = [field for field in headers if field not in FIELDS]
        if missing:
            errors.append(f"missing headers: {missing}")
        if extra:
            warnings.append(f"extra headers: {extra}")
        rows = list(reader)

    if not rows:
        errors.append("sourcing lock has no component rows")

    seen: set[str] = set()
    row_statuses: list[str] = []
    assembly_quantities: set[int] = set()
    currencies: set[str] = set()
    total_cost = 0.0
    for number, row in enumerate(rows, start=2):
        refs = references(row.get("reference", ""))
        if not refs:
            errors.append(f"row {number}: reference is required")
        for ref in refs:
            if ref in seen:
                errors.append(f"row {number}: duplicate reference {ref}")
            seen.add(ref)
        for field in (
            "function", "manufacturer", "requested_mpn", "mpn",
            "supplier_part_number", "package", "footprint", "currency",
            "assembly_class", "datasheet_url", "evidence_url",
        ):
            if not row.get(field, "").strip():
                errors.append(f"row {number}: {field} is required")
        for field in (
            "package_verified", "pinout_verified", "substitution_approved",
            "design_critical", "approval_required",
        ):
            if row.get(field, "").strip().lower() not in {"yes", "no"}:
                errors.append(f"row {number}: {field} must be yes or no")

        status = row.get("status", "").strip()
        row_statuses.append(status)
        if status not in ROW_STATUSES:
            errors.append(f"row {number}: invalid status")
        elif status == "BLOCKED":
            errors.append(f"row {number}: status is BLOCKED")

        package = row.get("package", "").strip()
        if re.search(r"\b(?:or|either|tbd|unknown)\b", package, re.IGNORECASE) or "|" in package:
            errors.append(f"row {number}: package is ambiguous")
        lifecycle = row.get("lifecycle", "").strip().lower()
        if lifecycle not in LIFECYCLES:
            errors.append(f"row {number}: invalid lifecycle")
        cad = row.get("cad_status", "").strip().lower()
        model = row.get("model_3d_status", "").strip().lower()
        if cad not in EVIDENCE_STATES:
            errors.append(f"row {number}: invalid cad_status")
        if model not in EVIDENCE_STATES:
            errors.append(f"row {number}: invalid model_3d_status")

        quantity = integer(row, "quantity_per_board", number, errors)
        assembly_quantity = integer(row, "assembly_quantity", number, errors)
        required = integer(row, "required_quantity", number, errors)
        order_quantity = integer(row, "order_quantity", number, errors)
        stock = integer(row, "stock_quantity", number, errors, positive=False)
        moq = integer(row, "moq", number, errors)
        if quantity is not None and refs and quantity != len(refs):
            errors.append(f"row {number}: quantity_per_board must equal grouped reference count")
        if assembly_quantity is not None:
            assembly_quantities.add(assembly_quantity)
        if quantity is not None and assembly_quantity is not None and required != quantity * assembly_quantity:
            errors.append(f"row {number}: required_quantity does not equal quantity_per_board * assembly_quantity")
        if order_quantity is not None and required is not None and order_quantity < required:
            errors.append(f"row {number}: order_quantity is below required_quantity")
        if order_quantity is not None and moq is not None and order_quantity < moq:
            errors.append(f"row {number}: order_quantity is below MOQ")
        if order_quantity is not None and stock is not None and stock < order_quantity:
            errors.append(f"row {number}: stock is below order_quantity")

        unit_price = decimal(row, "unit_price", number, errors)
        line_parts = decimal(row, "line_parts_cost", number, errors)
        setup_fee = decimal(row, "setup_fee", number, errors)
        extended_fee = decimal(row, "extended_fee", number, errors)
        line_total = decimal(row, "line_total_cost", number, errors)
        if order_quantity is not None and unit_price is not None and line_parts is not None:
            if not math.isclose(line_parts, order_quantity * unit_price, abs_tol=0.005):
                errors.append(f"row {number}: line_parts_cost does not equal order_quantity * unit_price")
        if None not in (line_parts, setup_fee, extended_fee, line_total):
            expected_total = float(line_parts) + float(setup_fee) + float(extended_fee)
            if not math.isclose(float(line_total), expected_total, abs_tol=0.005):
                errors.append(f"row {number}: line_total_cost does not reconcile")
            total_cost += float(line_total)
        currency = row.get("currency", "").strip().upper()
        if currency:
            currencies.add(currency)

        requested_mpn = row.get("requested_mpn", "").strip()
        selected_mpn = row.get("mpn", "").strip()
        if requested_mpn and selected_mpn and requested_mpn != selected_mpn:
            approved_alternates = references(row.get("approved_alternates", ""))
            if selected_mpn not in approved_alternates:
                errors.append(f"row {number}: selected alternate is not listed in approved_alternates")
            if row.get("substitution_approved", "").strip().lower() != "yes":
                errors.append(f"row {number}: selected alternate is not approved")
            if not row.get("substitution_approval_evidence", "").strip():
                errors.append(f"row {number}: approved alternate requires substitution_approval_evidence")

        if row.get("design_critical", "").lower() == "yes":
            if row.get("pinout_verified", "").lower() != "yes":
                errors.append(f"row {number}: design-critical pinout is unverified")
            if row.get("approval_required", "").lower() != "yes":
                errors.append(f"row {number}: design-critical part must require approval")
        if row.get("package_verified", "").lower() != "yes":
            errors.append(f"row {number}: package is unverified")
        if row.get("pinout_verified", "").lower() != "yes":
            errors.append(f"row {number}: pinout is unverified")
        if lifecycle in {"eol", "obsolete", "unknown"}:
            errors.append(f"row {number}: lifecycle is not orderable ({lifecycle})")
        if cad != "verified":
            errors.append(f"row {number}: CAD is not verified")
        if model not in {"verified", "not-required"}:
            errors.append(f"row {number}: 3D model is not verified or not-required")
        if status == "PASS":
            if lifecycle != "active":
                errors.append(f"row {number}: PASS requires active lifecycle")

        try:
            checked = parse_time(row.get("stock_checked_at", ""))
            age = as_of - checked
            if age.total_seconds() < 0:
                errors.append(f"row {number}: stock timestamp is in the future")
            elif age > dt.timedelta(days=args.max_age_days):
                errors.append(f"row {number}: stock evidence is stale ({age.days} days)")
        except (ValueError, TypeError):
            errors.append(f"row {number}: invalid stock_checked_at")
        if not row.get("datasheet_url", "").startswith(("https://", "http://")):
            errors.append(f"row {number}: datasheet_url must be an URL")

    if len(assembly_quantities) > 1:
        errors.append("assembly_quantity must be identical across sourcing rows")
    if len(currencies) > 1:
        errors.append("one sourcing lock must use one currency for total assembled cost")

    if errors or "BLOCKED" in row_statuses:
        overall = "BLOCKED"
    elif "USER_REVIEW" in row_statuses:
        overall = "USER_REVIEW"
    else:
        overall = "PASS"
    result = {
        "schema": "sourcing-lock-v1", "file": str(args.csv_file),
        "status": overall, "rows": len(rows), "references": len(seen),
        "assembly_quantity": next(iter(assembly_quantities)) if len(assembly_quantities) == 1 else None,
        "currency": next(iter(currencies)) if len(currencies) == 1 else None,
        "total_assembled_cost": round(total_cost, 6),
        "errors": errors, "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
