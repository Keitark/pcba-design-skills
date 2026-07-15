from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(
        [sys.executable, str(script), *map(str, args)], cwd=cwd or ROOT,
        text=True, capture_output=True, encoding="utf-8", env=env,
    )


class ToolTests(unittest.TestCase):
    def test_connectivity_self_test(self) -> None:
        script = ROOT / ".agents/skills/schematic-humanizer/scripts/compare_connectivity.py"
        result = run(script, "--self-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SELF-TEST PASS", result.stdout)

    def test_program_state_invalidation(self) -> None:
        script = ROOT / ".agents/skills/manage-pcba-program/scripts/program_state.py"
        affected = {
            "product-definition": {"product_definition", "sourcing", "circuit", "schematic_visual", "placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "netlist": {"circuit", "schematic_visual", "placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "circuit": {"circuit", "schematic_visual", "placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "mpn-package": {"sourcing", "circuit", "schematic_visual", "placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "footprint": {"placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "placement": {"placement", "routing", "manufacturing_release", "assembly_placement", "order"},
            "routing": {"routing", "manufacturing_release", "assembly_placement", "order"},
            "bom": {"sourcing", "manufacturing_release", "assembly_placement", "order"},
            "cpl": {"manufacturing_release", "assembly_placement", "order"},
            "browser-placement": {"manufacturing_release", "assembly_placement", "order"},
        }
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "program-state.json"
            self.assertEqual(run(script, "--file", state, "init", "--project", "fixture").returncode, 0)
            base = json.loads(state.read_text(encoding="utf-8"))
            for stage in base["stages"].values():
                stage.update({"status": "PASS", "evidence": ["fixture-evidence"]})
            for approval in base["approvals"]:
                base["approvals"][approval] = "APPROVED"
                base["approval_evidence"][approval] = ["fixture-approval"]

            all_stages = set(base["stages"])
            for change, expected in affected.items():
                with self.subTest(change=change):
                    state.write_text(json.dumps(base), encoding="utf-8")
                    result = run(script, "--file", state, "invalidate", "--change", change, "--reason", "fixture change")
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    data = json.loads(state.read_text(encoding="utf-8"))
                    blocked = {name for name, stage in data["stages"].items() if stage["status"] == "BLOCKED"}
                    self.assertEqual(blocked, expected)
                    self.assertEqual({name for name in all_stages - expected if data["stages"][name]["status"] != "PASS"}, set())
                    self.assertEqual(data["approvals"]["assembly_placement"], "PENDING")
                    self.assertEqual(data["approvals"]["final_price"], "PENDING")
                    self.assertEqual(data["approvals"]["payment"], "PENDING")
                    if change in {"product-definition", "netlist", "circuit", "mpn-package", "bom"}:
                        self.assertEqual(data["approvals"]["design_critical_substitution"], "PENDING")
                    else:
                        self.assertEqual(data["approvals"]["design_critical_substitution"], "APPROVED")
                    self.assertEqual(data["manual_browser_edits_present"], change == "browser-placement")
                    self.assertEqual(data["invalidation_log"][-1]["change"], change)

    def test_program_state_blocks_impossible_pass_and_allows_gated_transition(self) -> None:
        script = ROOT / ".agents/skills/manage-pcba-program/scripts/program_state.py"
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp) / "program-state.json"
            self.assertEqual(run(script, "--file", state, "init", "--project", "fixture").returncode, 0)
            before = state.read_text(encoding="utf-8")
            impossible = run(script, "--file", state, "set-stage", "--stage", "order", "--status", "PASS", "--evidence", "cart.json")
            self.assertNotEqual(impossible.returncode, 0)
            self.assertEqual(state.read_text(encoding="utf-8"), before)
            early_approval = run(
                script, "--file", state, "set-approval", "--approval", "assembly_placement",
                "--status", "APPROVED", "--evidence", "preview.png",
            )
            self.assertNotEqual(early_approval.returncode, 0)
            self.assertEqual(state.read_text(encoding="utf-8"), before)

            for stage in ("product_definition", "circuit", "schematic_visual"):
                result = run(script, "--file", state, "set-stage", "--stage", stage,
                             "--status", "PASS", "--evidence", f"{stage}.json")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            placement_without_sourcing = run(
                script, "--file", state, "set-stage", "--stage", "placement",
                "--status", "PASS", "--evidence", "placement.json",
            )
            self.assertNotEqual(placement_without_sourcing.returncode, 0)
            for stage in ("sourcing", "placement", "routing", "manufacturing_release"):
                result = run(script, "--file", state, "set-stage", "--stage", stage,
                             "--status", "PASS", "--evidence", f"{stage}.json")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-stage", "--stage", "assembly_placement",
                         "--status", "USER_REVIEW", "--evidence", "placement-review.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-approval", "--approval", "assembly_placement",
                         "--status", "APPROVED", "--evidence", "assembly_placement.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-stage", "--stage", "assembly_placement",
                         "--status", "PASS", "--evidence", "placement-approved.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-stage", "--stage", "order",
                         "--status", "USER_REVIEW", "--evidence", "final-quote.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-approval", "--approval", "final_price",
                         "--status", "APPROVED", "--evidence", "final_price.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payment_without_substitution_gate = run(
                script, "--file", state, "set-approval", "--approval", "payment",
                "--status", "APPROVED", "--evidence", "payment.json",
            )
            self.assertNotEqual(payment_without_substitution_gate.returncode, 0)
            result = run(
                script, "--file", state, "set-approval", "--approval",
                "design_critical_substitution", "--status", "APPROVED",
                "--evidence", "no-substitution-or-approved-change.json",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-approval", "--approval", "payment",
                         "--status", "APPROVED", "--evidence", "payment.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run(script, "--file", state, "set-stage", "--stage", "order",
                         "--status", "PASS", "--evidence", "order-record.json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def sourcing_row(self, checked: str = "2026-07-10T00:00:00+00:00") -> dict[str, str]:
        return {
            "reference": "U1", "function": "MCU", "quantity_per_board": "1",
            "assembly_quantity": "3", "required_quantity": "3", "order_quantity": "3",
            "manufacturer": "Example", "requested_mpn": "EXACT-1", "mpn": "EXACT-1",
            "supplier_part_number": "C1", "package": "QFN-32", "package_verified": "yes",
            "footprint": "QFN-32-1EP", "pinout_verified": "yes",
            "cad_status": "verified", "model_3d_status": "verified",
            "lifecycle": "active", "stock_checked_at": checked,
            "stock_quantity": "1000", "moq": "1", "unit_price": "1.25",
            "currency": "USD", "assembly_class": "Basic", "line_parts_cost": "3.75",
            "setup_fee": "0", "extended_fee": "0", "line_total_cost": "3.75",
            "datasheet_url": "https://example.com/datasheet.pdf",
            "approved_alternates": "", "substitution_approved": "no",
            "substitution_approval_evidence": "", "design_critical": "yes",
            "approval_required": "yes", "status": "PASS",
            "evidence_url": "https://example.com/part",
        }

    def write_sourcing(self, path: Path, row: dict[str, str]) -> None:
        headers = (ROOT / ".agents/skills/qualify-pcba-sourcing/assets/sourcing-lock.csv").read_text(encoding="utf-8").strip().split(",")
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader()
            writer.writerow(row)

    def test_sourcing_valid_and_stale(self) -> None:
        script = ROOT / ".agents/skills/qualify-pcba-sourcing/scripts/validate_sourcing_lock.py"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sourcing.csv"
            self.write_sourcing(path, self.sourcing_row())
            valid = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00", "--max-age-days", "14")
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            self.assertEqual(json.loads(valid.stdout)["total_assembled_cost"], 3.75)
            stale = run(script, path, "--as-of", "2026-08-12T00:00:00+00:00", "--max-age-days", "14")
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("stale", stale.stdout)

    def test_sourcing_rejects_package_and_pinout_gaps(self) -> None:
        script = ROOT / ".agents/skills/qualify-pcba-sourcing/scripts/validate_sourcing_lock.py"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sourcing.csv"
            row = self.sourcing_row()
            row["package"] = ""
            row["pinout_verified"] = "no"
            self.write_sourcing(path, row)
            result = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("package is required", result.stdout)
            self.assertIn("pinout is unverified", result.stdout)

    def test_sourcing_rejects_missing_mpn_ambiguous_package_and_unapproved_alternate(self) -> None:
        script = ROOT / ".agents/skills/qualify-pcba-sourcing/scripts/validate_sourcing_lock.py"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sourcing.csv"
            row = self.sourcing_row()
            row["mpn"] = ""
            row["package"] = "QFN-32 or QFN-40"
            self.write_sourcing(path, row)
            missing = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("mpn is required", missing.stdout)
            self.assertIn("package is ambiguous", missing.stdout)

            row = self.sourcing_row()
            row["mpn"] = "ALTERNATE-2"
            row["approved_alternates"] = "ALTERNATE-2"
            self.write_sourcing(path, row)
            unapproved = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(unapproved.returncode, 0)
            self.assertIn("selected alternate is not approved", unapproved.stdout)
            self.assertIn("substitution_approval_evidence", unapproved.stdout)

    def test_sourcing_aggregates_row_gate_and_rejects_unusable_pass(self) -> None:
        script = ROOT / ".agents/skills/qualify-pcba-sourcing/scripts/validate_sourcing_lock.py"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sourcing.csv"
            row = self.sourcing_row()
            row["status"] = "BLOCKED"
            self.write_sourcing(path, row)
            blocked = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(blocked.returncode, 0)
            self.assertEqual(json.loads(blocked.stdout)["status"], "BLOCKED")

            row = self.sourcing_row()
            row["status"] = "USER_REVIEW"
            self.write_sourcing(path, row)
            review = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(review.returncode, 0)
            self.assertEqual(json.loads(review.stdout)["status"], "USER_REVIEW")

            row = self.sourcing_row()
            row.update({
                "lifecycle": "obsolete", "cad_status": "missing",
                "model_3d_status": "missing", "stock_quantity": "0",
            })
            self.write_sourcing(path, row)
            unusable = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(unusable.returncode, 0)
            self.assertIn("PASS requires active lifecycle", unusable.stdout)
            self.assertIn("CAD is not verified", unusable.stdout)
            self.assertIn("stock is below order_quantity", unusable.stdout)

    def test_sourcing_reconciles_grouped_quantity_and_cost(self) -> None:
        script = ROOT / ".agents/skills/qualify-pcba-sourcing/scripts/validate_sourcing_lock.py"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sourcing.csv"
            row = self.sourcing_row()
            row["reference"] = "U1,U2"
            row["line_total_cost"] = "99"
            self.write_sourcing(path, row)
            result = run(script, path, "--as-of", "2026-07-12T00:00:00+00:00")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("quantity_per_board must equal grouped reference count", result.stdout)
            self.assertIn("line_total_cost does not reconcile", result.stdout)

    def experiment_args(self) -> list[str]:
        return [
            "--id", "fixture", "--method", "local reroute", "--evidence", "report.json",
            "--outcome", "accepted", "--before-opens", "2", "--after-opens", "0",
            "--before-real-drc", "0", "--after-real-drc", "0",
            "--before-power-disconnects", "0", "--after-power-disconnects", "0",
            "--before-layout-fails", "0", "--after-layout-fails", "0",
            "--before-manufacturing-defects", "0", "--after-manufacturing-defects", "0",
        ]

    def test_layout_scoring(self) -> None:
        script = ROOT / ".agents/skills/pcb-layout-review/scripts/score_experiment.py"
        with tempfile.TemporaryDirectory() as temp:
            ledger = Path(temp) / "ledger.jsonl"
            result = run(script, "--ledger", ledger, *self.experiment_args())
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertGreater(json.loads(result.stdout)["score"], 0)
            bad = self.experiment_args()
            bad[bad.index("--after-real-drc") + 1] = "1"
            rejected = run(script, "--ledger", ledger, *bad)
            self.assertNotEqual(rejected.returncode, 0)
            no_change = self.experiment_args()
            no_change[no_change.index("--outcome") + 1] = "no-change"
            no_change[no_change.index("--after-opens") + 1] = "2"
            neutral = run(script, "--ledger", ledger, *no_change)
            self.assertEqual(neutral.returncode, 0)
            self.assertLess(json.loads(neutral.stdout)["score"], 0)
            replayable_no_change = no_change + ["--replayable"]
            replayable = run(script, "--ledger", ledger, *replayable_no_change)
            self.assertEqual(replayable.returncode, 0)
            self.assertLess(json.loads(replayable.stdout)["score"], 0)
            timeout = list(replayable_no_change)
            timeout[timeout.index("no-change")] = "timeout"
            timed_out = run(script, "--ledger", ledger, *timeout)
            self.assertEqual(timed_out.returncode, 0)
            self.assertLess(json.loads(timed_out.stdout)["score"], 0)
            negative = self.experiment_args()
            negative[negative.index("--after-opens") + 1] = "-1"
            self.assertNotEqual(run(script, "--ledger", ledger, *negative).returncode, 0)

    def test_release_manifest_hash_and_revision(self) -> None:
        build = ROOT / ".agents/skills/release-pcba-fabrication/scripts/build_release_manifest.py"
        validate = ROOT / ".agents/skills/release-pcba-fabrication/scripts/validate_release_manifest.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            roles = (
                "board_source", "eda_project", "gerber", "drill", "bom", "cpl",
                "constraints", "render_top", "render_bottom", "circuit_review",
                "schematic_connectivity", "schematic_visual_audit", "layout_review",
                "sourcing_lock",
            )
            artifacts: dict[str, Path] = {}
            for role in roles:
                path = root / f"{role}.dat"
                path.write_text(f"{role} fixture\n", encoding="utf-8")
                artifacts[role] = path
            manifest = root / "release-manifest.json"
            incomplete = run(
                build, "--output", root / "incomplete.json", "--release", "fixture",
                "--revision", "RevA", "--status", "PASS",
                "--artifact", f"gerber={artifacts['gerber']}",
                "--artifact-revision", "gerber=RevA",
            )
            self.assertNotEqual(incomplete.returncode, 0)

            blocked = run(
                build, "--output", root / "blocked.json", "--release", "fixture",
                "--revision", "RevA", "--artifact", f"gerber={artifacts['gerber']}",
                "--artifact-revision", "gerber=RevA",
            )
            self.assertEqual(blocked.returncode, 0, blocked.stdout + blocked.stderr)
            self.assertNotEqual(run(validate, root / "blocked.json").returncode, 0)

            args = ["--output", manifest, "--release", "fixture", "--revision", "RevA", "--status", "PASS"]
            for role, path in artifacts.items():
                args.extend(["--artifact", f"{role}={path}", "--artifact-revision", f"{role}=RevA"])
            for value in (
                "board_width_mm=100", "board_height_mm=70", "layer_count=4",
                "thickness_mm=1.2", "surface_finish=HASL", "assembly_sides=Top",
                "quantity_pcbs=5", "quantity_assembled=3",
            ):
                args.extend(["--constraint", value])
            for value in (
                "unexplained_raw_disconnects=0", "real_drc_errors=0", "layout_check_failures=0",
                "circuit_gate=PASS", "layout_gate=PASS", "raw_connectivity=PASS",
                "power_connectivity=PASS", "visual_mechanical_review=PASS", "dfm_review=PASS",
                "sourcing_lock_current=PASS", "revision_reconciled=PASS",
                "design_critical_substitution_required=false",
            ):
                args.extend(["--verification", value])
            result = run(build, *args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(run(validate, manifest).returncode, 0)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["constraints"]["thickness_mm"] = -1
            data["constraints"]["quantity_assembled"] = 6
            invalid_constraints = root / "invalid-constraints.json"
            invalid_constraints.write_text(json.dumps(data), encoding="utf-8")
            invalid = run(validate, invalid_constraints)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("positive finite thickness_mm", invalid.stdout)
            self.assertIn("may not exceed", invalid.stdout)

            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["verification"]["design_critical_substitution_required"] = True
            unapproved_substitution = root / "unapproved-substitution.json"
            unapproved_substitution.write_text(json.dumps(data), encoding="utf-8")
            self.assertNotEqual(run(validate, unapproved_substitution).returncode, 0)
            artifacts["bom"].write_text("tampered", encoding="utf-8")
            self.assertNotEqual(run(validate, manifest).returncode, 0)
            mixed = run(build, "--output", root / "mixed.json", "--release", "mixed", "--revision", "RevA",
                        "--artifact", f"gerber={artifacts['gerber']}", "--artifact-revision", "gerber=RevB")
            self.assertNotEqual(mixed.returncode, 0)

    def write_cpl_fixture(self, root: Path, duplicate: bool = False, mirrored: bool = False,
                          wrong_pin1: bool = False, span_variance: bool = False,
                          approve_variance: bool = False, board_side: str = "Top",
                          cpl_side: str | None = None,
                          source_rotation: float = 180.0) -> tuple[Path, Path, Path, Path]:
        supplier_pads = [
            {"instance": "s1", "name": "1", "x_mm": 0.0, "y_mm": 0.0},
            {"instance": "s2", "name": "2", "x_mm": 2.0, "y_mm": 0.0},
            {"instance": "s3", "name": "2" if duplicate else "3", "x_mm": 0.0, "y_mm": 1.0},
        ]
        scale = 1.2 if span_variance else 1.0
        board_points = [(0.5, 0.25), (0.5, 0.25 + 2.0 * scale), (0.5 - 1.0 * scale, 0.25)]
        if mirrored:
            board_points = [(-x, y) for x, y in board_points]
        board_pads = [
            {"instance": "b1", "name": "1", "x_mm": board_points[0][0], "y_mm": board_points[0][1]},
            {"instance": "b2", "name": "2", "x_mm": board_points[1][0], "y_mm": board_points[1][1]},
            {"instance": "b3", "name": "2" if duplicate else "3", "x_mm": board_points[2][0], "y_mm": board_points[2][1]},
        ]
        board = {
            "schema": "pcba-footprint-geometry-v1",
            "components": [{"reference": "U1", "supplier_part": "C1", "x_mm": 10.0,
                            "y_mm": 20.0, "side": board_side, "rotation_deg": source_rotation,
                            "pin1_instance": "b2" if wrong_pin1 else "b1", "pads": board_pads}],
        }
        supplier = {
            "schema": "pcba-supplier-package-geometry-v1",
            "packages": [{"supplier_part": "C1", "pin1_instance": "s1", "pads": supplier_pads}],
        }
        package_rule = {"pad_map": {"b1": "s1", "b2": "s2", "b3": "s3"}}
        if approve_variance:
            package_rule.update({
                "land_pattern_rms_limit_mm": 0.5,
                "evidence": "Exact manufacturer package drawing; symmetric lead-span variance",
            })
        mapping = {"packages": {"C1": package_rule}}
        board_path = root / "board.json"
        supplier_path = root / "supplier.json"
        mapping_path = root / "mapping.json"
        cpl_path = root / "source.csv"
        board_path.write_text(json.dumps(board), encoding="utf-8")
        supplier_path.write_text(json.dumps(supplier), encoding="utf-8")
        mapping_path.write_text(json.dumps(mapping), encoding="utf-8")
        cpl_path.write_text(
            f"Designator,Mid X,Mid Y,Layer,Rotation\nU1,10,20,{cpl_side or board_side},{source_rotation}\n",
            encoding="utf-8",
        )
        return board_path, supplier_path, mapping_path, cpl_path

    def run_cpl(self, root: Path, duplicate: bool = False, mirrored: bool = False,
                wrong_pin1: bool = False, use_mapping: bool = True,
                span_variance: bool = False, approve_variance: bool = False,
                board_side: str = "Top", cpl_side: str | None = None,
                source_rotation: float = 180.0):
        script = ROOT / ".agents/skills/operate-jlcpcb-order/scripts/audit_cpl_geometry.py"
        board, supplier, mapping, cpl = self.write_cpl_fixture(
            root, duplicate, mirrored, wrong_pin1, span_variance,
            approve_variance, board_side, cpl_side, source_rotation
        )
        args = ["--board-geometry", board, "--supplier-geometry", supplier, "--cpl", cpl,
                "--report", root / "report.json", "--output", root / "corrected.csv"]
        if use_mapping:
            args.extend(["--mapping", mapping])
        return run(script, *args)

    def test_cpl_rotation_translation_and_pin1(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = self.run_cpl(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            item = report["results"][0]
            self.assertEqual(item["rotation_deg"], 270)
            self.assertAlmostEqual(item["offset_x_mm"], 0.5)
            self.assertAlmostEqual(item["offset_y_mm"], 0.25)
            self.assertAlmostEqual(item["candidate_x_mm"], 9.5)
            self.assertAlmostEqual(item["candidate_y_mm"], 19.75)
            self.assertEqual(report["inputs"]["cpl"]["sha256"], self.sha256(root / "source.csv"))
            self.assertEqual(report["settings"]["coordinate_contract"], "pcba-footprint-geometry-v1")
            self.assertEqual(report["output"]["sha256"], self.sha256(root / "corrected.csv"))

    def test_cpl_preserves_fractional_rotation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = self.run_cpl(root, source_rotation=45.5)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["results"][0]["rotation_deg"], 135.5)
            with (root / "corrected.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["Rotation"], "135.5")

    def test_cpl_rejects_side_mismatch_and_accepts_canonical_bottom(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mismatch = self.run_cpl(root, board_side="Top", cpl_side="Bottom")
            self.assertNotEqual(mismatch.returncode, 0)
            self.assertIn("side mismatch", mismatch.stdout)
            self.assertFalse((root / "corrected.csv").exists())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bottom = self.run_cpl(root, board_side="Bottom", cpl_side="Bottom")
            self.assertEqual(bottom.returncode, 0, bottom.stdout + bottom.stderr)
            with (root / "corrected.csv").open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["Layer"], "Bottom")
            self.assertEqual(rows[0]["Mid X"], "9.5000")
            self.assertEqual(rows[0]["Mid Y"], "19.7500")

    def test_cpl_duplicate_pads_require_explicit_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            blocked = self.run_cpl(root, duplicate=True, use_mapping=False)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("duplicated electrical pad names", blocked.stdout)
            passed = self.run_cpl(root, duplicate=True, use_mapping=True)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)

    def test_cpl_rejects_mirror_and_pin1_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            mirrored = self.run_cpl(Path(temp), mirrored=True)
            self.assertNotEqual(mirrored.returncode, 0)
        with tempfile.TemporaryDirectory() as temp:
            wrong = self.run_cpl(Path(temp), wrong_pin1=True)
            self.assertNotEqual(wrong.returncode, 0)
            self.assertIn("pin-1", wrong.stdout)

    def test_cpl_land_pattern_variance_needs_package_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            blocked = self.run_cpl(root, span_variance=True)
            self.assertNotEqual(blocked.returncode, 0)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            item = report["results"][0]
            self.assertEqual(item["registration_status"], "PASS")
            self.assertEqual(item["land_pattern_status"], "BLOCKED_LAND_PATTERN")
            self.assertEqual(item["rotation_deg"], 270)
            approved = self.run_cpl(root, span_variance=True, approve_variance=True)
            self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
            approved_report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(approved_report["results"][0]["land_pattern_status"], "PASS_APPROVED_VARIANCE")

    def test_cpl_ambiguous_rotation_requires_angle_and_evidence(self) -> None:
        script = ROOT / ".agents/skills/operate-jlcpcb-order/scripts/audit_cpl_geometry.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            board = {
                "schema": "pcba-footprint-geometry-v1",
                "components": [{
                    "reference": "U1", "supplier_part": "C1", "x_mm": 10,
                    "y_mm": 20, "side": "Top", "rotation_deg": 0,
                    "pin1_instance": "b1", "pads": [
                        {"instance": "b1", "name": "TAB", "x_mm": 0.5, "y_mm": 0.25},
                        {"instance": "b2", "name": "TAB", "x_mm": 0.5, "y_mm": 0.25},
                    ],
                }],
            }
            supplier = {
                "schema": "pcba-supplier-package-geometry-v1",
                "packages": [{
                    "supplier_part": "C1", "pin1_instance": "s1", "pads": [
                        {"instance": "s1", "name": "EP", "x_mm": 0, "y_mm": 0},
                        {"instance": "s2", "name": "EP", "x_mm": 0, "y_mm": 0},
                    ],
                }],
            }
            board_path = root / "board.json"
            supplier_path = root / "supplier.json"
            cpl_path = root / "source.csv"
            mapping_path = root / "mapping.json"
            board_path.write_text(json.dumps(board), encoding="utf-8")
            supplier_path.write_text(json.dumps(supplier), encoding="utf-8")
            cpl_path.write_text("Designator,Mid X,Mid Y,Layer,Rotation\nU1,10,20,Top,0\n", encoding="utf-8")
            base_rule = {"pad_map": {"b1": "s1", "b2": "s2"}}

            def audit(rule: dict) -> subprocess.CompletedProcess[str]:
                mapping_path.write_text(json.dumps({"packages": {"C1": rule}}), encoding="utf-8")
                return run(
                    script, "--board-geometry", board_path,
                    "--supplier-geometry", supplier_path, "--cpl", cpl_path,
                    "--mapping", mapping_path, "--report", root / "report.json",
                    "--output", root / "corrected.csv",
                )

            no_angle = audit(dict(base_rule))
            self.assertNotEqual(no_angle.returncode, 0)
            self.assertIn("BLOCKED_AMBIGUOUS_ROTATION", no_angle.stdout)
            no_evidence = audit({**base_rule, "approved_registration_angle_deg": 0})
            self.assertNotEqual(no_evidence.returncode, 0)
            approved = audit({
                **base_rule, "approved_registration_angle_deg": 0,
                "evidence": "Manufacturer package drawing and physical pin-1 review",
            })
            self.assertEqual(approved.returncode, 0, approved.stdout + approved.stderr)
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["results"][0]["registration_status"], "PASS_APPROVED_ROTATION")

    def test_cpl_rejects_global_tolerance_bypass(self) -> None:
        script = ROOT / ".agents/skills/operate-jlcpcb-order/scripts/audit_cpl_geometry.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            board, supplier, mapping, cpl = self.write_cpl_fixture(root)
            common = [
                "--board-geometry", board, "--supplier-geometry", supplier,
                "--cpl", cpl, "--mapping", mapping, "--report", root / "report.json",
                "--output", root / "corrected.csv",
            ]
            self.assertNotEqual(run(script, *common, "--tolerance-mm", "0.11").returncode, 0)
            self.assertNotEqual(run(script, *common, "--ambiguity-mm", "-1").returncode, 0)

    def test_cpl_rejects_nonfinite_geometry(self) -> None:
        script = ROOT / ".agents/skills/operate-jlcpcb-order/scripts/audit_cpl_geometry.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            board, supplier, mapping, cpl = self.write_cpl_fixture(root)
            data = json.loads(board.read_text(encoding="utf-8"))
            data["components"][0]["x_mm"] = "NaN"
            board.write_text(json.dumps(data), encoding="utf-8")
            result = run(
                script, "--board-geometry", board, "--supplier-geometry", supplier,
                "--cpl", cpl, "--mapping", mapping, "--report", root / "report.json",
                "--output", root / "corrected.csv",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be finite", result.stdout)
            self.assertFalse((root / "corrected.csv").exists())

    def test_cpl_import_reconciliation_and_mapping(self) -> None:
        script = ROOT / ".agents/skills/operate-jlcpcb-order/scripts/reconcile_cpl_import.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            submitted = root / "submitted.csv"
            imported = root / "imported.csv"
            report = root / "report.json"
            submitted.write_text(
                "Designator,Mid X,Mid Y,Layer,Rotation\nU1,10,20,Top,90\nU2,30,40,Bottom,180\n",
                encoding="utf-8",
            )
            imported.write_text(
                "Reference,X,Y,Side,Angle\nU1,10.5,19.75,Top,180\nU2,30.5,39.75,Bottom,270\n",
                encoding="utf-8",
            )
            blocked = run(script, "--submitted", submitted, "--imported", imported, "--report", report)
            self.assertNotEqual(blocked.returncode, 0)
            mapping = root / "mapping.json"
            mapping.write_text(json.dumps({
                "default": {"dx_mm": 0.5, "dy_mm": -0.25, "rotation_offset_deg": 90}
            }), encoding="utf-8")
            passed = run(script, "--submitted", submitted, "--imported", imported,
                         "--mapping", mapping, "--report", report)
            self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
            report_data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(report_data["inputs"]["submitted"]["sha256"], self.sha256(submitted))
            self.assertEqual(report_data["inputs"]["imported"]["sha256"], self.sha256(imported))
            self.assertEqual(report_data["settings"]["submitted_unit"], "mm")
            self.assertEqual(report_data["settings"]["position_tolerance_mm"], 0.02)
            tolerance_bypass = run(
                script, "--submitted", submitted, "--imported", imported,
                "--mapping", mapping, "--report", report,
                "--position-tolerance-mm", "1",
            )
            self.assertNotEqual(tolerance_bypass.returncode, 0)
            imported.write_text("Reference,X,Y,Side,Angle\nU1,10.5,19.75,Top,180\n", encoding="utf-8")
            missing = run(script, "--submitted", submitted, "--imported", imported,
                          "--mapping", mapping, "--report", report)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("missing imported reference", missing.stdout)

            submitted.write_text("Designator,Mid X,Mid Y,Layer,Rotation\n", encoding="utf-8")
            imported.write_text("Reference,X,Y,Side,Angle\n", encoding="utf-8")
            empty = run(script, "--submitted", submitted, "--imported", imported, "--report", report)
            self.assertNotEqual(empty.returncode, 0)
            self.assertIn("has no rows", empty.stdout)

            submitted.write_text("Designator,Mid X,Mid Y,Layer,Rotation\nU1,NaN,20,Top,90\n", encoding="utf-8")
            imported.write_text("Reference,X,Y,Side,Angle\nU1,10,20,Top,90\n", encoding="utf-8")
            nonfinite = run(script, "--submitted", submitted, "--imported", imported, "--report", report)
            self.assertNotEqual(nonfinite.returncode, 0)
            self.assertIn("must be finite", nonfinite.stdout)

    def test_workflow_record_valid_chain_close_and_hash_drift(self) -> None:
        script = ROOT / ".agents/skills/manage-pcba-program/scripts/workflow_record.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            frame = root / ".pcba-workflow/frames/001-before.png"
            report = root / ".pcba-workflow/snapshots/connectivity.json"
            initialized = run(
                script, "--root", ".pcba-workflow", "init",
                "--project", "fixture", "--stop-before", "final-submit", cwd=root,
            )
            self.assertEqual(initialized.returncode, 0, initialized.stdout + initialized.stderr)
            frame.write_bytes(b"safe public frame")
            report.write_text('{"status":"PASS"}\n', encoding="utf-8")
            added = run(
                script, "--root", ".pcba-workflow", "add",
                "--stage", "schematic_netlist", "--action", "capture-before",
                "--tool", "schematic-humanizer", "--gate-status", "PASS",
                "--caption-en", "Raw netlist-style schematic",
                "--caption-ja", "ネットリスト風回路図",
                "--output", report, "--frame", frame, cwd=root,
            )
            self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
            validated = run(script, "--root", ".pcba-workflow", "validate", cwd=root)
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            closed = run(script, "--root", ".pcba-workflow", "close", cwd=root)
            self.assertEqual(closed.returncode, 0, closed.stdout + closed.stderr)

            frame.write_bytes(b"edited after close")
            drifted = run(script, "--root", ".pcba-workflow", "validate", cwd=root)
            self.assertNotEqual(drifted.returncode, 0)
            self.assertIn("hash mismatch", drifted.stdout)

    def test_workflow_record_rejects_sequence_gap_and_missing_artifact(self) -> None:
        script = ROOT / ".agents/skills/manage-pcba-program/scripts/workflow_record.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(run(
                script, "--root", ".pcba-workflow", "init", "--project", "fixture",
                cwd=root,
            ).returncode, 0)
            artifact = root / "evidence.txt"
            artifact.write_text("evidence", encoding="utf-8")
            self.assertEqual(run(
                script, "--root", ".pcba-workflow", "add",
                "--stage", "product_definition", "--action", "capture-brief",
                "--tool", "plan-electronic-product", "--caption-en", "Product brief",
                "--output", artifact, cwd=root,
            ).returncode, 0)
            artifact.unlink()
            missing = run(script, "--root", ".pcba-workflow", "validate", cwd=root)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("missing outputs artifact", missing.stdout)

            artifact.write_text("evidence", encoding="utf-8")
            event_path = root / ".pcba-workflow/events.jsonl"
            event = json.loads(event_path.read_text(encoding="utf-8"))
            event["sequence"] = 3
            event_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
            gap = run(script, "--root", ".pcba-workflow", "validate", cwd=root)
            self.assertNotEqual(gap.returncode, 0)
            self.assertIn("sequence must be 1", gap.stdout)
            self.assertIn("event hash mismatch", gap.stdout)

    def test_workflow_record_rejects_public_private_identifiers(self) -> None:
        script = ROOT / ".agents/skills/manage-pcba-program/scripts/workflow_record.py"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(run(
                script, "--root", ".pcba-workflow", "init", "--project", "fixture",
                cwd=root,
            ).returncode, 0)
            private_caption = run(
                script, "--root", ".pcba-workflow", "add",
                "--stage", "quote", "--action", "capture-quote",
                "--tool", "operate-jlcpcb-order",
                "--caption-en", "Quote for person@example.com",
                cwd=root,
            )
            self.assertNotEqual(private_caption.returncode, 0)
            self.assertIn("possible private identifier", private_caption.stderr)

    @staticmethod
    def sha256(path: Path) -> str:
        import hashlib

        return hashlib.sha256(path.read_bytes()).hexdigest().upper()


if __name__ == "__main__":
    unittest.main()
