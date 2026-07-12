#!/usr/bin/env python3
"""Create, validate, update, and invalidate pcba-program-state-v1 files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


STAGES = (
    "product_definition", "sourcing", "circuit", "schematic_visual",
    "placement", "routing", "manufacturing_release", "assembly_placement",
    "order",
)
STATUSES = {"PASS", "BLOCKED", "USER_REVIEW"}
APPROVALS = ("design_critical_substitution", "assembly_placement", "final_price", "payment")
INVALIDATION = {
    "product-definition": STAGES,
    "netlist": STAGES[2:],
    "circuit": STAGES[2:],
    "mpn-package": STAGES[1:],
    "footprint": STAGES[4:],
    "placement": STAGES[4:],
    "routing": STAGES[5:],
    "bom": ("sourcing", "manufacturing_release", "assembly_placement", "order"),
    "cpl": ("manufacturing_release", "assembly_placement", "order"),
    "browser-placement": ("manufacturing_release", "assembly_placement", "order"),
    "stock-price": ("sourcing", "order"),
}

STAGE_PREREQUISITES = {
    "sourcing": ("product_definition",),
    "circuit": ("product_definition",),
    "placement": ("circuit", "schematic_visual"),
    "routing": ("placement",),
    "manufacturing_release": ("circuit", "schematic_visual", "placement", "routing"),
    "assembly_placement": ("manufacturing_release",),
    "order": STAGES[:-1],
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def initial(project_id: str) -> dict:
    return {
        "schema": "pcba-program-state-v1",
        "project_id": project_id,
        "updated_at": now(),
        "stages": {stage: {"status": "BLOCKED", "evidence": []} for stage in STAGES},
        "artifacts": {},
        "risks": [],
        "approvals": {
            "design_critical_substitution": "PENDING",
            "assembly_placement": "PENDING",
            "final_price": "PENDING",
            "payment": "PENDING",
        },
        "approval_evidence": {name: [] for name in APPROVALS},
        "manual_browser_edits_present": False,
        "invalidation_log": [],
    }


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, state: dict) -> None:
    state["updated_at"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(state: dict) -> list[str]:
    errors: list[str] = []
    if state.get("schema") != "pcba-program-state-v1":
        errors.append("schema must be pcba-program-state-v1")
    if not state.get("project_id"):
        errors.append("project_id is required")
    stages = state.get("stages", {})
    if set(stages) != set(STAGES):
        errors.append("stage set does not match pcba-program-state-v1")
    for stage in STAGES:
        if stages.get(stage, {}).get("status") not in STATUSES:
            errors.append(f"{stage}: invalid status")
        status = stages.get(stage, {}).get("status")
        if status in {"PASS", "USER_REVIEW"} and not stages.get(stage, {}).get("evidence"):
            errors.append(f"{stage}: {status} requires evidence")
        if status in {"PASS", "USER_REVIEW"}:
            missing = [name for name in STAGE_PREREQUISITES.get(stage, ())
                       if stages.get(name, {}).get("status") != "PASS"]
            if missing:
                errors.append(f"{stage}: prerequisites are not PASS: {missing}")
    approvals = state.get("approvals", {})
    for name in APPROVALS:
        if approvals.get(name) not in {"PENDING", "APPROVED", "REJECTED"}:
            errors.append(f"approval {name}: invalid status")
        if approvals.get(name) in {"APPROVED", "REJECTED"} and not state.get("approval_evidence", {}).get(name):
            errors.append(f"approval {name}: decision requires evidence")
    if state.get("manual_browser_edits_present") and stages.get("assembly_placement", {}).get("status") == "PASS":
        errors.append("assembly_placement cannot PASS with manual browser edits")
    if stages.get("assembly_placement", {}).get("status") == "PASS" and approvals.get("assembly_placement") != "APPROVED":
        errors.append("assembly_placement PASS requires its independent approval")
    if stages.get("order", {}).get("status") == "PASS":
        missing = [name for name in APPROVALS if approvals.get(name) != "APPROVED"]
        if missing:
            errors.append(f"order PASS requires all independent approvals: {missing}")
    if approvals.get("assembly_placement") == "APPROVED" and stages.get("assembly_placement", {}).get("status") not in {"USER_REVIEW", "PASS"}:
        errors.append("assembly placement approval requires completed evidence at USER_REVIEW or PASS")
    if approvals.get("final_price") == "APPROVED":
        if stages.get("assembly_placement", {}).get("status") != "PASS":
            errors.append("final price approval requires PASS assembly placement")
        if stages.get("order", {}).get("status") not in {"USER_REVIEW", "PASS"}:
            errors.append("final price approval requires an order stage at USER_REVIEW or PASS")
    if approvals.get("payment") == "APPROVED":
        missing_prior = [name for name in APPROVALS[:-1] if approvals.get(name) != "APPROVED"]
        if missing_prior:
            errors.append(f"payment approval requires all prior approvals: {missing_prior}")
        if stages.get("order", {}).get("status") not in {"USER_REVIEW", "PASS"}:
            errors.append("payment approval requires an order stage at USER_REVIEW or PASS")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=Path(".pcba-workflow/program-state.json"))
    sub = parser.add_subparsers(dest="command", required=True)
    init_p = sub.add_parser("init")
    init_p.add_argument("--project", required=True)
    set_p = sub.add_parser("set-stage")
    set_p.add_argument("--stage", choices=STAGES, required=True)
    set_p.add_argument("--status", choices=sorted(STATUSES), required=True)
    set_p.add_argument("--evidence", action="append", default=[])
    approval_p = sub.add_parser("set-approval")
    approval_p.add_argument("--approval", choices=APPROVALS, required=True)
    approval_p.add_argument("--status", choices=("PENDING", "APPROVED", "REJECTED"), required=True)
    approval_p.add_argument("--evidence", action="append", default=[])
    inv_p = sub.add_parser("invalidate")
    inv_p.add_argument("--change", choices=sorted(INVALIDATION), required=True)
    inv_p.add_argument("--reason", required=True)
    sub.add_parser("validate")
    args = parser.parse_args()

    if args.command == "init":
        if args.file.exists():
            raise SystemExit(f"refusing to overwrite existing state: {args.file}")
        state = initial(args.project)
        save(args.file, state)
    else:
        state = load(args.file)
        errors = validate(state)
        if errors:
            print(json.dumps({"status": "BLOCKED", "errors": errors}, indent=2))
            return 1
        if args.command == "set-stage":
            if args.status == "PASS" and not args.evidence:
                raise SystemExit("PASS requires at least one --evidence")
            if args.stage == "assembly_placement" and args.status == "PASS" and state.get("manual_browser_edits_present"):
                raise SystemExit("assembly_placement cannot PASS with manual browser edits")
            if args.stage == "placement" and args.status in {"PASS", "USER_REVIEW"} and state["stages"]["sourcing"]["status"] != "PASS":
                raise SystemExit("placement freeze requires sourcing PASS at the transition")
            state["stages"][args.stage] = {"status": args.status, "evidence": args.evidence}
            errors = validate(state)
            if errors:
                print(json.dumps({"status": "BLOCKED", "errors": errors}, indent=2))
                return 1
            save(args.file, state)
        elif args.command == "set-approval":
            if args.status in {"APPROVED", "REJECTED"} and not args.evidence:
                raise SystemExit("an approval decision requires --evidence")
            if args.approval == "assembly_placement" and args.status == "APPROVED" and state.get("manual_browser_edits_present"):
                raise SystemExit("assembly placement cannot be approved with manual browser edits")
            state["approvals"][args.approval] = args.status
            state["approval_evidence"][args.approval] = args.evidence
            errors = validate(state)
            if errors:
                print(json.dumps({"status": "BLOCKED", "errors": errors}, indent=2))
                return 1
            save(args.file, state)
        elif args.command == "invalidate":
            affected = INVALIDATION[args.change]
            for stage in affected:
                state["stages"][stage]["status"] = "BLOCKED"
                state["stages"][stage]["evidence"] = []
            if "assembly_placement" in affected:
                state["approvals"]["assembly_placement"] = "PENDING"
                state["approval_evidence"]["assembly_placement"] = []
            if "order" in affected:
                state["approvals"]["final_price"] = "PENDING"
                state["approvals"]["payment"] = "PENDING"
                state["approval_evidence"]["final_price"] = []
                state["approval_evidence"]["payment"] = []
            if args.change in {"product-definition", "netlist", "circuit", "mpn-package", "bom"}:
                state["approvals"]["design_critical_substitution"] = "PENDING"
                state["approval_evidence"]["design_critical_substitution"] = []
            if args.change == "browser-placement":
                state["manual_browser_edits_present"] = True
            elif args.change == "cpl":
                state["manual_browser_edits_present"] = False
            state["invalidation_log"].append({
                "time_utc": now(), "change": args.change,
                "reason": args.reason, "affected_stages": list(affected),
            })
            save(args.file, state)

    final = load(args.file)
    errors = validate(final)
    print(json.dumps({"status": "PASS" if not errors else "BLOCKED", "file": str(args.file), "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
