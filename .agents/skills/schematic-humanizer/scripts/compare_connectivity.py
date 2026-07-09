#!/usr/bin/env python3
"""Normalize and compare schematic connectivity.

Inputs may be KiCad XML netlists or canonical schematic-connectivity-v1 JSON.
Exit 0 for exact equivalence, 1 for connectivity drift, and 2 for bad input.
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SCHEMA = "schematic-connectivity-v1"
FORMATS = ("auto", "kicad-xml", "canonical-json")


@dataclass(frozen=True, order=True)
class Component:
    value: str
    footprint: str
    device: str


@dataclass(frozen=True, order=True)
class Pin:
    ref: str
    pin: str


@dataclass(frozen=True)
class Connectivity:
    components: dict[str, Component]
    nets: dict[str, frozenset[Pin]]


def _child_text(parent: ET.Element, tag: str) -> str:
    child = parent.find(tag)
    return "" if child is None or child.text is None else child.text.strip()


def _validate(connectivity: Connectivity, source: str) -> Connectivity:
    if not connectivity.components:
        raise ValueError(f"no components found in {source}")
    if not connectivity.nets:
        raise ValueError(f"no nets found in {source}")
    assigned: dict[Pin, str] = {}
    for net_name, pins in connectivity.nets.items():
        for pin in pins:
            if pin.ref not in connectivity.components:
                raise ValueError(f"net {net_name!r} references unknown component {pin.ref!r} in {source}")
            previous = assigned.get(pin)
            if previous is not None:
                raise ValueError(
                    f"pin {pin.ref}.{pin.pin} belongs to both {previous!r} and {net_name!r} in {source}"
                )
            assigned[pin] = net_name
    return connectivity


def parse_kicad_xml(root: ET.Element, source: str) -> Connectivity:
    components: dict[str, Component] = {}
    for node in root.findall("./components/comp"):
        ref = (node.get("ref") or "").strip()
        if not ref:
            raise ValueError(f"component without a reference in {source}")
        if ref in components:
            raise ValueError(f"duplicate component reference {ref!r} in {source}")
        libsource = node.find("libsource")
        library = "" if libsource is None else (libsource.get("lib") or "").strip()
        part = "" if libsource is None else (libsource.get("part") or "").strip()
        components[ref] = Component(
            value=_child_text(node, "value"),
            footprint=_child_text(node, "footprint"),
            device=":".join(field for field in (library, part) if field),
        )

    nets: dict[str, frozenset[Pin]] = {}
    for node in root.findall("./nets/net"):
        name = (node.get("name") or "").strip()
        if not name:
            raise ValueError(f"net without a name in {source}")
        if name in nets:
            raise ValueError(f"duplicate net name {name!r} in {source}")
        pins: set[Pin] = set()
        for member in node.findall("node"):
            ref = (member.get("ref") or "").strip()
            number = (member.get("pin") or "").strip()
            if not ref or not number:
                raise ValueError(f"incomplete node on net {name!r} in {source}")
            pin = Pin(ref, number)
            if pin in pins:
                raise ValueError(f"duplicate node {ref}.{number} on net {name!r} in {source}")
            pins.add(pin)
        nets[name] = frozenset(pins)
    return _validate(Connectivity(components, nets), source)


def _required_text(value: Any, field: str, source: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string in {source}")
    return value.strip()


def _optional_text(value: Any, field: str, source: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string in {source}")
    return value.strip()


def parse_canonical_json(data: Any, source: str) -> Connectivity:
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"expected schema {SCHEMA!r} in {source}")
    component_rows = data.get("components")
    net_rows = data.get("nets")
    if not isinstance(component_rows, list) or not isinstance(net_rows, list):
        raise ValueError(f"components and nets must be arrays in {source}")

    components: dict[str, Component] = {}
    for index, row in enumerate(component_rows):
        if not isinstance(row, dict):
            raise ValueError(f"components[{index}] must be an object in {source}")
        ref = _required_text(row.get("ref"), f"components[{index}].ref", source)
        if ref in components:
            raise ValueError(f"duplicate component reference {ref!r} in {source}")
        components[ref] = Component(
            value=_optional_text(row.get("value"), f"components[{index}].value", source),
            footprint=_optional_text(row.get("footprint"), f"components[{index}].footprint", source),
            device=_optional_text(row.get("device"), f"components[{index}].device", source),
        )

    nets: dict[str, frozenset[Pin]] = {}
    for index, row in enumerate(net_rows):
        if not isinstance(row, dict):
            raise ValueError(f"nets[{index}] must be an object in {source}")
        name = _required_text(row.get("name"), f"nets[{index}].name", source)
        if name in nets:
            raise ValueError(f"duplicate net name {name!r} in {source}")
        pin_rows = row.get("pins")
        if not isinstance(pin_rows, list):
            raise ValueError(f"nets[{index}].pins must be an array in {source}")
        pins: set[Pin] = set()
        for pin_index, pin_row in enumerate(pin_rows):
            if not isinstance(pin_row, dict):
                raise ValueError(f"nets[{index}].pins[{pin_index}] must be an object in {source}")
            pin = Pin(
                _required_text(pin_row.get("ref"), f"nets[{index}].pins[{pin_index}].ref", source),
                _required_text(pin_row.get("pin"), f"nets[{index}].pins[{pin_index}].pin", source),
            )
            if pin in pins:
                raise ValueError(f"duplicate node {pin.ref}.{pin.pin} on net {name!r} in {source}")
            pins.add(pin)
        nets[name] = frozenset(pins)
    return _validate(Connectivity(components, nets), source)


def load_connectivity(path: Path, input_format: str = "auto") -> Connectivity:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    selected = input_format
    if selected == "auto":
        selected = "kicad-xml" if raw.lstrip().startswith("<") else "canonical-json"
    try:
        if selected == "kicad-xml":
            return parse_kicad_xml(ET.fromstring(raw), str(path))
        if selected == "canonical-json":
            return parse_canonical_json(json.loads(raw), str(path))
    except (ET.ParseError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot parse {selected} input {path}: {exc}") from exc
    raise ValueError(f"unsupported input format {selected!r}")


def canonical_data(connectivity: Connectivity) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "components": [
            {"ref": ref, **asdict(component)}
            for ref, component in sorted(connectivity.components.items())
        ],
        "nets": [
            {
                "name": name,
                "pins": [asdict(pin) for pin in sorted(pins)],
            }
            for name, pins in sorted(connectivity.nets.items())
        ],
    }


def pin_text(pin: Pin) -> str:
    return f"{pin.ref}.{pin.pin}"


def _print_set_delta(title: str, removed: set[str], added: set[str]) -> None:
    if removed:
        print(f"  removed {title}: {', '.join(sorted(removed))}")
    if added:
        print(f"  added {title}: {', '.join(sorted(added))}")


def compare(before: Connectivity, after: Connectivity) -> bool:
    same = True
    before_refs = set(before.components)
    after_refs = set(after.components)
    if before_refs != after_refs:
        same = False
        _print_set_delta("components", before_refs - after_refs, after_refs - before_refs)
    for ref in sorted(before_refs & after_refs):
        if before.components[ref] != after.components[ref]:
            same = False
            print(f"  changed component {ref}: {before.components[ref]} -> {after.components[ref]}")

    before_names = set(before.nets)
    after_names = set(after.nets)
    if before_names != after_names:
        same = False
        _print_set_delta("nets", before_names - after_names, after_names - before_names)
    for name in sorted(before_names & after_names):
        left = before.nets[name]
        right = after.nets[name]
        if left != right:
            same = False
            print(f"  changed net {name!r}:")
            removed = sorted(pin_text(pin) for pin in left - right)
            added = sorted(pin_text(pin) for pin in right - left)
            if removed:
                print(f"    removed pins: {', '.join(removed)}")
            if added:
                print(f"    added pins: {', '.join(added)}")
    return same


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize or compare KiCad XML and canonical schematic connectivity."
    )
    parser.add_argument("before", type=Path, nargs="?", help="baseline XML or canonical JSON")
    parser.add_argument("after", type=Path, nargs="?", help="final XML or canonical JSON")
    parser.add_argument("--before-format", choices=FORMATS, default="auto")
    parser.add_argument("--after-format", choices=FORMATS, default="auto")
    parser.add_argument("--normalize", type=Path, help="normalize one input to canonical JSON")
    parser.add_argument("--input-format", choices=FORMATS, default="auto")
    parser.add_argument("--output", type=Path, help="canonical JSON output for --normalize")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def self_test() -> int:
    baseline_xml = """<export><components>
      <comp ref="R1"><value>1k</value><footprint>R_0603</footprint><libsource lib="Device" part="R"/></comp>
      <comp ref="U1"><value>Logic</value><footprint>SOIC-8</footprint><libsource lib="74xx" part="74HC00"/></comp>
      </components><nets>
      <net code="1" name="SIGNAL"><node ref="R1" pin="1"/><node ref="U1" pin="1"/></net>
      <net code="2" name="GND"><node ref="R1" pin="2"/><node ref="U1" pin="2"/></net>
      </nets></export>"""
    equivalent_xml = baseline_xml.replace('code="1"', 'code="91"').replace('code="2"', 'code="7"')
    baseline = parse_kicad_xml(ET.fromstring(baseline_xml), "self-test KiCad baseline")
    equivalent = parse_kicad_xml(ET.fromstring(equivalent_xml), "self-test KiCad equivalent")
    canonical = parse_canonical_json(canonical_data(baseline), "self-test canonical JSON")
    drift_data = canonical_data(baseline)
    drift_data["nets"][1]["pins"][0]["pin"] = "99"
    drifted = parse_canonical_json(drift_data, "self-test drifted JSON")
    if baseline != equivalent:
        print("SELF-TEST FAIL: KiCad net-code churn affected equivalence.")
        return 1
    if baseline != canonical:
        print("SELF-TEST FAIL: canonical JSON round-trip changed connectivity.")
        return 1
    if baseline == drifted:
        print("SELF-TEST FAIL: canonical pin-membership drift was not detected.")
        return 1
    print("SELF-TEST PASS: KiCad XML equivalence, canonical JSON round-trip, and drift detection.")
    return 0


def main() -> int:
    args = parse_args()
    if args.self_test:
        if any((args.before, args.after, args.normalize, args.output)):
            print("ERROR: --self-test does not accept input or output paths", file=sys.stderr)
            return 2
        return self_test()

    if args.normalize is not None:
        if args.before is not None or args.after is not None or args.output is None:
            print("ERROR: use --normalize INPUT --output OUTPUT without comparison paths", file=sys.stderr)
            return 2
        try:
            connectivity = load_connectivity(args.normalize, args.input_format)
            args.output.write_text(
                json.dumps(canonical_data(connectivity), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except (OSError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(
            f"WROTE: {args.output} ({len(connectivity.components)} components, "
            f"{len(connectivity.nets)} nets)"
        )
        return 0

    if args.before is None or args.after is None or args.output is not None:
        print("ERROR: provide BEFORE and AFTER, or use --normalize INPUT --output OUTPUT", file=sys.stderr)
        return 2
    try:
        before = load_connectivity(args.before, args.before_format)
        after = load_connectivity(args.after, args.after_format)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(
        f"Baseline: {len(before.components)} components, {len(before.nets)} nets; "
        f"Final: {len(after.components)} components, {len(after.nets)} nets"
    )
    if compare(before, after):
        pin_count = sum(len(pins) for pins in before.nets.values())
        print(f"PASS: connectivity matches exactly ({pin_count} net pin memberships).")
        return 0
    print("FAIL: connectivity drift detected.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
