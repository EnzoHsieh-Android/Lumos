import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("unfamiliar_stack_brief.py")
SPEC = importlib.util.spec_from_file_location("unfamiliar_stack_brief", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_manifest(root):
    cases = []
    sessions = []
    for number in range(1, 6):
        case_id = f"U{number}"
        source = root / f"cases/{case_id}/buggy.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"fixture {case_id}\n", encoding="utf-8")
        brief = source.with_name("brief.json")
        brief.write_text('{"rules": []}', encoding="utf-8")
        cases.append({
            "id": case_id,
            "language": f"language-{number}",
            "files": [{"path": str(p.relative_to(root)), "sha256": digest(p)}
                      for p in (source, brief)],
            "dispatch_common": [str(source.relative_to(root))],
            "dispatch_brief": str(brief.relative_to(root)),
            "oracle": {"command": ["true"], "expected": "target-failure"},
            "primary_defect": f"defect-{number}",
            "normal_counterexample": f"normal-{number}",
        })
        for arm in ("control", "brief"):
            sessions.append({
                "case_id": case_id,
                "arm": arm,
                "model": "fixed-model",
                "effort": "fixed-effort",
                "materials": [str(source.relative_to(root))] + (
                    [str(brief.relative_to(root))] if arm == "brief" else []),
            })
    return {"version": "v1", "cases": cases, "sessions": sessions}


def t_unfamiliar_stack_brief_manifest_hashes(test):
    frozen = Path(__file__).with_name("unfamiliar-stack-brief") / "qualification-v1.json"
    qualified = MODULE.verify_manifest(frozen)
    test.assertEqual(5, len(qualified["cases"]))
    test.assertEqual(21, sum(len(case["files"]) for case in qualified["cases"]))
    revised = MODULE.verify_manifest(frozen.with_name("qualification-v2.json"))
    test.assertEqual(5, len(revised["cases"]))
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        manifest = valid_manifest(root)
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        test.assertEqual(manifest, MODULE.preflight_run(path, root / "new-output"))
        test.assertFalse((root / "new-output").exists())
        MODULE.verify_manifest(path)
        (root / manifest["cases"][0]["files"][0]["path"]).write_text("tampered\n", encoding="utf-8")
        with test.assertRaisesRegex(MODULE.ManifestError, "sha256"):
            MODULE.verify_manifest(path)


def t_unfamiliar_stack_brief_preflight_rejects_invalid_inputs(test):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        path = root / "manifest.json"
        manifest = valid_manifest(root)
        path.write_text(json.dumps(manifest), encoding="utf-8")
        output = root / "existing-output"
        output.mkdir()
        sentinel = output / "sentinel.bin"
        sentinel.write_bytes(b"do-not-touch")
        before = digest(sentinel)
        with test.assertRaisesRegex(MODULE.ManifestError, "output"):
            MODULE.preflight_run(path, output)
        test.assertEqual(before, digest(sentinel))

        for mutator, message in (
            (lambda m: m["cases"].pop(), "five cases"),
            (lambda m: m["sessions"].pop(), "ten sessions"),
            (lambda m: m["sessions"][0].update(model="other"), "same model"),
            (lambda m: m["sessions"][0]["materials"].append("answer-key.json"), "answer key"),
            (lambda m: m["cases"][0].pop("oracle"), "oracle"),
            (lambda m: m["cases"][0].pop("primary_defect"), "primary_defect"),
            (lambda m: m["cases"][0].pop("normal_counterexample"), "normal_counterexample"),
            (lambda m: m["sessions"][0]["materials"].append("cases/U1/brief.json"), "materials"),
            (lambda m: m["sessions"][0]["materials"].append("cases/U1/fixed.cs"), "materials"),
            (lambda m: m["sessions"][1].update(materials=[]), "materials"),
            (lambda m: m["cases"][0].update(dispatch_common=["missing.txt"]), "frozen"),
            (lambda m: m["sessions"][0].update(case_id=[]), "case"),
        ):
            broken = valid_manifest(root)
            mutator(broken)
            path.write_text(json.dumps(broken), encoding="utf-8")
            with test.assertRaisesRegex(MODULE.ManifestError, message):
                MODULE.preflight_run(path, root / "new-output")


class ManifestTests(unittest.TestCase):
    def test_u4_result_preservation_and_capacity(self):
        # Shared task: return all results in input order, including an empty input.
        root = Path(__file__).with_name("unfamiliar-stack-brief")
        for version, scenario, expected in (
            ("buggy", "target", 1), ("buggy", "normal", 0),
            ("fixed", "target", 0), ("fixed", "normal", 0),
        ):
            result = subprocess.run(
                ["node", str(root / f"cases/U4/{version}-v2.js"), scenario],
                capture_output=True, text=True, timeout=10, check=False,
            )
            self.assertEqual(expected, result.returncode, result.stdout + result.stderr)

    def test_manifest_hashes(self):
        t_unfamiliar_stack_brief_manifest_hashes(self)

    def test_preflight_rejects_invalid_inputs_without_touching_existing_output(self):
        t_unfamiliar_stack_brief_preflight_rejects_invalid_inputs(self)


def receipts(control_hits=0, brief_hits=0, brief_false_positives=0, brief_normal_harms=0):
    rows = []
    for number in range(1, 6):
        for arm in ("control", "brief"):
            rows.append({
                "case_id": f"U{number}",
                "arm": arm,
                "valid": True,
                "primary_hit": number <= (control_hits if arm == "control" else brief_hits),
                "evidence_grounded": True,
                "false_positives": brief_false_positives if arm == "brief" and number == 1 else 0,
                "normal_counterexample_harmed": arm == "brief" and number <= brief_normal_harms,
                "familiarity": "unfamiliar",
                "elapsed_seconds": 10,
                "tokens": 100,
            })
    return rows


def t_unfamiliar_stack_brief_summary_decisions(test):
    proceed = MODULE.summarize_receipts(receipts(control_hits=1, brief_hits=3, brief_false_positives=1))
    test.assertEqual("proceed-to-historical", proceed["decision"])
    test.assertEqual(2, proceed["additional_primary_hits"])
    test.assertEqual(1, proceed["brief_false_positives"])

    all_hit = MODULE.summarize_receipts(receipts(control_hits=5, brief_hits=5))
    test.assertEqual("stop", all_hit["decision"])
    test.assertEqual(0, all_hit["additional_primary_hits"])

    all_miss = MODULE.summarize_receipts(receipts())
    test.assertEqual("stop", all_miss["decision"])
    test.assertEqual(0, all_miss["control_primary_hits"])
    test.assertEqual(0, all_miss["brief_primary_hits"])

    noisy = MODULE.summarize_receipts(receipts(control_hits=0, brief_hits=2, brief_false_positives=2))
    test.assertEqual("stop", noisy["decision"])
    test.assertEqual(2, noisy["brief_false_positives"])

    invalid = receipts(control_hits=1, brief_hits=3)
    invalid[0]["valid"] = False
    incomplete = MODULE.summarize_receipts(invalid)
    test.assertEqual("incomplete", incomplete["decision"])
    test.assertEqual(1, len(incomplete["invalid_sessions"]))

    # S5: only actual booleans and non-negative finite metrics are scored.
    for field, value in (
        ("valid", "false"), ("primary_hit", "false"), ("evidence_grounded", "false"),
        ("normal_counterexample_harmed", "false"), ("tokens", -100),
        ("tokens", True), ("elapsed_seconds", "bad"), ("elapsed_seconds", float("inf")),
        ("false_positives", "bad"), ("case_id", []), ("arm", {}),
    ):
        rows = receipts(control_hits=1, brief_hits=3)
        rows[1][field] = value
        with test.subTest(field=field, value=value):
            summary = MODULE.summarize_receipts(rows)
            test.assertEqual("incomplete", summary["decision"])
            test.assertTrue(summary["invalid_sessions"])
            test.assertIn(rows[1], summary["raw_receipts"])


class SummaryTests(unittest.TestCase):
    def test_summary_decisions_keep_metrics_separate(self):
        t_unfamiliar_stack_brief_summary_decisions(self)


if __name__ == "__main__":
    unittest.main()
