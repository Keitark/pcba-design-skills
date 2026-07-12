#!/usr/bin/env python3
"""Score one PCB experiment into a project-local JSONL ledger."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


METRICS = {
    "opens": (10, 15, True),
    "real_drc": (20, 30, True),
    "power_disconnects": (20, 30, True),
    "layout_fails": (12, 20, False),
    "manufacturing_defects": (8, 16, True),
}


def delta(before: int, after: int, reward: int, penalty: int) -> int:
    improvement = before - after
    return improvement * (reward if improvement >= 0 else penalty)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=Path(".pcba-workflow/layout-experiments.jsonl"))
    parser.add_argument("--id", required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--outcome", choices=("accepted", "rejected", "no-change", "timeout"), required=True)
    parser.add_argument("--replayable", action="store_true")
    parser.add_argument("--justification", default="")
    for metric in METRICS:
        flag = metric.replace("_", "-")
        parser.add_argument(f"--before-{flag}", dest=f"before_{metric}", type=int, required=True)
        parser.add_argument(f"--after-{flag}", dest=f"after_{metric}", type=int, required=True)
    args = parser.parse_args()

    before = {name: getattr(args, f"before_{name}") for name in METRICS}
    after = {name: getattr(args, f"after_{name}") for name in METRICS}
    negative = [name for name in METRICS if before[name] < 0 or after[name] < 0]
    if negative:
        raise SystemExit(f"count metrics may not be negative: {negative}")
    score = sum(delta(before[name], after[name], *METRICS[name][:2]) for name in METRICS)
    if args.replayable:
        score += 3
    outcome_penalty = {"accepted": 0, "rejected": -4, "no-change": -2, "timeout": -5}[args.outcome]
    score += outcome_penalty
    if args.outcome in {"no-change", "timeout"}:
        score = min(score, outcome_penalty)
    improved = any(after[name] < before[name] for name in METRICS)
    regressed = [name for name in METRICS if after[name] > before[name]]
    hard_regressions = [name for name in regressed if METRICS[name][2]]

    if args.outcome == "accepted":
        if not improved or score <= 0:
            raise SystemExit("accepted requires a measured net-positive improvement")
        if hard_regressions:
            raise SystemExit(f"accepted may not regress hard metrics: {hard_regressions}")
        if regressed and not args.justification.strip():
            raise SystemExit("accepted soft tradeoffs require --justification")

    entry = {
        "schema": "pcb-layout-experiment-v1",
        "time_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "id": args.id, "method": args.method, "outcome": args.outcome,
        "score": score, "before": before, "after": after,
        "replayable": args.replayable, "justification": args.justification,
        "evidence": args.evidence,
    }
    prior: list[dict] = []
    if args.ledger.exists():
        prior = [json.loads(line) for line in args.ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    replaced = any(item.get("id") == args.id for item in prior)
    prior = [item for item in prior if item.get("id") != args.id] + [entry]
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in prior), encoding="utf-8")
    entry["replaced"] = replaced
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
