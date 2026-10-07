"""行為反例；正式 runner 的四個入口會呼叫本檔。"""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import review_convergence as ev

H = "a" * 64
B = "b" * 40
R = "c" * 40


def case(cid="C1", group="G1"):
    return {
        "id": cid,
        "group": group,
        "split": ev.split_for(group),
        "loop": "code-example",
        "finding": "r2:F1",
        "start_commit": B,
        "case_sha256": H,
        "grader_sha256": H,
        "environment_sha256": H,
    }


def manifest(cases=None):
    return {
        "version": 1,
        "cases": cases or [case()],
        "repeats": 2,
        "arms": {
            a: {
                "model": "pinned-model-v1",
                "workflow_sha256": ch * 64,
                "dispatch_sha256": ch * 64,
            }
            for a, ch in [("baseline", "d"), ("candidate", "e")]
        },
    }


def receipt(
    root, m, arm, repeat, repair=True, preserve=True, rounds=2, status="completed"
):
    c = m["cases"][0]
    obj = {
        "case_id": c["id"],
        "arm": arm,
        "repeat": repeat,
        "status": status,
        **{
            k: c[k]
            for k in (
                "start_commit",
                "case_sha256",
                "grader_sha256",
                "environment_sha256",
            )
        },
        **m["arms"][arm],
        "result_commit": R,
        "loaded_start_commit": B,
        "loaded_result_commit": R,
        "repair": repair,
        "preserve": preserve,
        "new_defects": 0,
        "rounds": rounds,
        "tokens": 10,
        "wall_seconds": 2.0,
    }
    p = root / (arm + str(repeat) + ".json")
    raw = json.dumps(obj).encode()
    p.write_bytes(raw)
    return {
        "case_id": c["id"],
        "arm": arm,
        "repeat": repeat,
        "receipt": {"path": p.name, "sha256": hashlib.sha256(raw).hexdigest()},
    }


class CohortTests(unittest.TestCase):
    def test_all_loops_without_cap_decision_and_context_not_used(self):
        rows = [
            {
                "loop": "code-success",
                "round": "r1",
                "kind": "none",
                "severity": "clean",
                "tokens": 3,
            },
            {"loop": "code-capped", "round": "r1", "kind": "none", "severity": "major"},
            {"loop": "code-capped", "round": "r2", "kind": "none", "severity": "minor"},
            {"loop": "design-x", "round": "r1", "kind": "none"},
        ]
        out = ev.build_cohort(rows)
        self.assertEqual(
            [x["loop"] for x in out["loops"]], ["code-capped", "code-success"]
        )
        self.assertEqual(out["observed_code_loops"], 2)
        self.assertEqual(out["loops"][0]["rounds"], ["r1", "r2"])
        self.assertIsNone(out["loops"][0]["tokens"]["total"])
        self.assertIsNone(out["loops"][0]["converged"])

    def test_missing_not_zero_mixed_and_duplicate_receipts(self):
        rows = [
            {
                "loop": "code-x",
                "round": "r1",
                "kind": "none",
                "token": "T",
                "tokens": 5,
            },
            {
                "loop": "code-x",
                "round": "r1",
                "kind": "none",
                "token": "T",
                "tokens": 5,
            },
            {"loop": "code-x", "kind": "none", "tokens": True},
        ]
        x = ev.build_cohort(rows)["loops"][0]
        self.assertIsNone(x["round_count"])
        self.assertEqual(x["tokens"]["known_records"], 1)
        self.assertIsNone(x["tokens"]["total"])
        self.assertEqual(x["duplicate_records"], 1)

    def test_invalid_input_and_unicode_line_separators(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rows.jsonl"
            p.write_text(
                json.dumps(
                    {"loop": "code-A\u2028B", "kind": "none"}, ensure_ascii=False
                )
                + "\r\n"
            )
            self.assertEqual(len(ev.read_ledger(p)), 1)
            p.write_text("{bad}\n")
            with self.assertRaises(ev.DataError):
                ev.read_ledger(p)
            p.write_bytes(b"\xff")
            with self.assertRaises(ev.DataError):
                ev.read_ledger(p)
            p.unlink()
            p.symlink_to("/dev/zero")
            with self.assertRaises(ev.DataError):
                ev.read_ledger(p)

    def test_round_reentry_and_global_token_conflict(self):
        rows = [{"loop": "code-x", "round": r, "tokens": 1} for r in ["r1", "r2", "r1"]]
        self.assertIsNone(ev.build_cohort(rows)["loops"][0]["round_count"])
        rows = [
            {"loop": loop, "round": "r1", "token": "T", "tokens": n}
            for loop, n in [("code-a", 5), ("code-b", 7)]
        ]
        for x in ev.build_cohort(rows)["loops"]:
            self.assertTrue(x["conflicting_tokens"])
            self.assertIsNone(x["tokens"]["total"])

    @unittest.skipUnless(importlib.util.find_spec("resource"), "resource capability required")
    def test_directory_rejection_does_not_leak_descriptors(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "normal"
            p.write_bytes(b"fixed-payload")
            script = """import resource,sys
import review_convergence as e
soft,hard=resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE,(min(64,soft),hard))
rejected=0
for _ in range(80):
    try:e.read_bytes('.')
    except e.DataError:rejected+=1
assert rejected == 80, 'directory rejection was not exercised'
assert e.read_bytes(sys.argv[1]) == b'fixed-payload'
"""
            r = subprocess.run(
                [sys.executable, "-c", script, str(p)],
                cwd=Path(ev.__file__).parent,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_render_control_characters_without_changing_data(self):
        points = [*range(0x7F, 0xA0), 0x202E, 0x2028]
        data = {"loop": "code-" + "".join(map(chr, points))}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ledger.jsonl"
            p.write_text(json.dumps(data) + "\n")
            self.assertEqual(json.loads(p.read_text()), data)
            self.assertIn(chr(0x9B), data["loop"])
            result = subprocess.run(
                [sys.executable, ev.__file__, "cohort", str(p)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for point in points:
                self.assertNotIn(chr(point), result.stdout)
            self.assertEqual(
                json.loads(result.stdout)["loops"][0]["loop"], data["loop"]
            )

    def test_token_identity_keeps_json_types_and_ignores_key_order(self):
        for number in (0, 1):
            a = {"loop": "code-x", "round": "r1", "token": "T", "tokens": number}
            b = dict(a, tokens=bool(number))
            self.assertIs(type(a["tokens"]), int)
            self.assertIs(type(b["tokens"]), bool)
            for rows in ([a, b], [b, a]):
                x = ev.build_cohort(rows)["loops"][0]
                self.assertTrue(x["conflicting_tokens"])
                self.assertIsNone(x["tokens"]["total"])
        a = {"loop": "code-x", "round": "r1", "token": "T", "tokens": 1}
        b = dict(reversed(list(a.items())))
        x = ev.build_cohort([a, b])["loops"][0]
        self.assertFalse(x["conflicting_tokens"])
        self.assertEqual(x["tokens"]["total"], 1)

    def test_short_record_amplification_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "records.jsonl"
            raw = b"{}\n" * 100001
            p.write_bytes(raw)
            self.assertLess(len(raw), 16 * 1024 * 1024)
            self.assertEqual(p.read_bytes(), raw)
            with self.assertRaisesRegex(ev.DataError, "^input-record-limit$"):
                ev.read_ledger(p)

    def test_equal_json_numbers_are_duplicates_but_booleans_are_distinct(self):
        a = {"loop": "code-x", "round": "r1", "token": "T", "tokens": 1,
             "extra": {"values": [1, False, None]}}
        b = copy.deepcopy(a)
        b["tokens"] = 1.0
        b["extra"]["values"][0] = 1.0
        self.assertIs(type(a["tokens"]), int)
        self.assertIs(type(b["tokens"]), float)
        self.assertEqual(a["tokens"], b["tokens"])
        for rows in ([a, b], [b, a]):
            x = ev.build_cohort(rows)["loops"][0]
            self.assertFalse(x["conflicting_tokens"])
            self.assertEqual(x["tokens"]["total"], 1)
        b["extra"]["values"][1] = 0
        self.assertIs(type(a["extra"]["values"][1]), bool)
        self.assertIs(type(b["extra"]["values"][1]), int)
        self.assertTrue(ev.build_cohort([a, b])["loops"][0]["conflicting_tokens"])


class CaseTests(unittest.TestCase):
    def test_template_loop_matches_manifest_identifier_boundary(self):
        accepted, rejected = "code-" + "x" * 123, "code-" + "x" * 124
        self.assertEqual((len(accepted), len(rejected)), (128, 129))
        self.assertEqual(ev.case_template(accepted)["loop"], accepted)
        with self.assertRaises(ev.DataError):
            ev.case_template(rejected)
        result = subprocess.run([sys.executable, ev.__file__, "template", rejected],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_template_unknown_and_group_split_stable(self):
        x = ev.case_template("code-x")
        self.assertIsNone(x["start_commit"])
        self.assertIsNone(x["grader_sha256"])
        self.assertEqual(ev.split_for("root-group"), ev.split_for("root-group"))
        with self.assertRaises(ev.DataError):
            ev.validate_manifest({**manifest(), "cases": [x]})

    def test_duplicate_ids_mixed_group_and_bad_sha(self):
        m = manifest([case(), case()])
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)
        m = manifest([case(), case("C2")])
        m["cases"][1]["split"] = (
            "held" if m["cases"][0]["split"] == "train" else "train"
        )
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)
        m = manifest()
        m["cases"][0]["start_commit"] = "main"
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)

    def test_different_model_and_bool_repeats_rejected(self):
        m = manifest()
        m["arms"]["candidate"]["model"] = "different"
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)
        m = manifest()
        m["repeats"] = True
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)

    def test_surrogate_rejected_and_supported_maximum_fits_reader(self):
        m = manifest()
        m["cases"][0]["group"] = "bad\ud800"
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)
        with self.assertRaises(ev.DataError):
            ev.parse('"\\ud800"')
        m = manifest([case(str(i)) for i in range(100)])
        m["repeats"] = 20
        ev.validate_manifest(m)
        self.assertLess(len(json.dumps(m).encode()), 1024 * 1024)
        m["repeats"] = 21
        with self.assertRaises(ev.DataError):
            ev.validate_manifest(m)


class TrialTests(unittest.TestCase):
    def test_valid_receipt_path_can_exceed_identifier_limit(self):
        with tempfile.TemporaryDirectory() as td:
            root, m = Path(td), manifest()
            record = receipt(root, m, "baseline", 1)
            name = "p" * 124 + ".json"
            (root / record["receipt"]["path"]).rename(root / name)
            record["receipt"]["path"] = name
            self.assertEqual(len(name), 129)
            self.assertTrue((root / name).is_file())
            out = ev.compare(m, [record], root)
            self.assertEqual(out["valid_trials"], 1)
            self.assertEqual(out["invalid_records"], [])

    def test_different_input_wrong_loaded_source_and_tampered_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            r = receipt(root, m, "baseline", 1)
            p = root / r["receipt"]["path"]
            data = json.loads(p.read_text())
            data["loaded_start_commit"] = R
            p.write_text(json.dumps(data))
            r["receipt"]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertIn("loaded-source", ev.check_trial(r, m, root)[1])
            data["loaded_start_commit"] = B
            data["case_sha256"] = "f" * 64
            p.write_text(json.dumps(data))
            r["receipt"]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertIn("case_sha256", ev.check_trial(r, m, root)[1])
            p.write_text("{}")
            self.assertIn("receipt-hash", ev.check_trial(r, m, root)[1])

    def test_unknown_cancelled_failed_and_nonfinite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            r = receipt(root, m, "baseline", 1, repair=False)
            data, err = ev.check_trial(r, m, root)
            self.assertIsNone(err)
            self.assertFalse(data["quality_pass"])
            r = receipt(root, m, "candidate", 1, preserve=None)
            self.assertIn("outcome-unknown", ev.check_trial(r, m, root)[1])
            r = receipt(root, m, "candidate", 2, status="cancelled")
            self.assertIn("cancelled", ev.check_trial(r, m, root)[1])
            p = root / "nan.json"
            p.write_text('{"tokens":NaN}')
            with self.assertRaises(ev.DataError):
                ev.read_json(p)
            p.write_text('{"tokens":1e999}')
            with self.assertRaises(ev.DataError):
                ev.read_json(p)
            p.write_text('{"tokens":1,"tokens":2}')
            with self.assertRaises(ev.DataError):
                ev.read_json(p)

    def test_paths_outside_root_and_duplicate_trial(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            r = receipt(root, m, "baseline", 1)
            bad = copy.deepcopy(r)
            bad["receipt"]["path"] = "../outside.json"
            self.assertIn("receipt", ev.check_trial(bad, m, root)[1])
            out = ev.compare(m, [r, r], root)
            self.assertEqual(out["duplicate_slots"], 1)
            self.assertEqual(out["valid_trials"], 0)

    def test_nul_path_is_an_invalid_record_not_a_batch_crash(self):
        bad = {
            "case_id": "C1",
            "arm": "baseline",
            "repeat": 1,
            "receipt": {"path": "bad\0name", "sha256": H},
        }
        out = ev.compare(manifest(), [bad], Path("/tmp"))
        self.assertEqual(out["valid_trials"], 0)
        self.assertEqual(out["invalid_records"][0]["reason"], "receipt-path")

    def test_invalid_cost_has_a_reason(self):
        for field in ["tokens", "wall_seconds"]:
            for value in [True, -1, "bad", [], {}, 10**20]:
                d = {
                    "status": "completed",
                    "repair": False,
                    "preserve": True,
                    "new_defects": 0,
                    "rounds": 1,
                    field: value,
                }
                with self.assertRaises(ev.DataError):
                    ev.validate_outcome(d)


class ComparisonTests(unittest.TestCase):
    def test_faster_but_regressed_is_not_improvement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            rs = []
            for i in [1, 2]:
                rs += [
                    receipt(root, m, "baseline", i, rounds=3),
                    receipt(root, m, "candidate", i, preserve=False, rounds=1),
                ]
            x = ev.compare(m, rs, root)
            self.assertEqual(x["paired_trials"], 2)
            self.assertEqual(x["arms"]["candidate"]["quality_passes"], 0)
            self.assertEqual(x["quality_delta"], -1.0)
            self.assertIsNone(x["round_delta_on_joint_success"])

    def test_missing_pair_no_delta_and_repeated_trial_means(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            rs = [receipt(root, m, "baseline", 1)]
            x = ev.compare(m, rs, root)
            self.assertEqual(x["missing_slots"], 3)
            self.assertIsNone(x["quality_delta"])
            self.assertEqual(x["expected_trials"], 4)
            rs += [
                receipt(root, m, "candidate", 1, rounds=1),
                receipt(root, m, "baseline", 2, rounds=4),
                receipt(root, m, "candidate", 2, rounds=2),
            ]
            x = ev.compare(m, rs, root)
            self.assertEqual(x["paired_trials"], 2)
            self.assertEqual(x["round_delta_on_joint_success"], -1.5)
            self.assertEqual(x["arms"]["candidate"]["quality_passes"], 2)

    def test_holdout_separation_and_unknown_cost(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            rs = [
                receipt(root, m, a, i)
                for a in ["baseline", "candidate"]
                for i in [1, 2]
            ]
            p = root / rs[0]["receipt"]["path"]
            data = json.loads(p.read_text())
            data["tokens"] = None
            p.write_text(json.dumps(data))
            rs[0]["receipt"]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
            x = ev.compare(m, rs, root)
            self.assertIsNone(x["arms"]["baseline"]["tokens_mean"])
            self.assertEqual(x["arms"]["baseline"]["tokens_known"], 1)
            self.assertIn(m["cases"][0]["split"], x["by_split"])

    def test_missing_or_duplicate_slots_do_not_report_complete_cost_means(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            rs = [receipt(root, m, "baseline", i) for i in [1, 2]]
            c = receipt(root, m, "candidate", 1)
            rs.append(c)
            self.assertIsNone(
                ev.compare(m, rs, root)["arms"]["candidate"]["tokens_mean"]
            )
            d = receipt(root, m, "candidate", 2)
            rs.extend([d, d])
            self.assertIsNone(
                ev.compare(m, rs, root)["arms"]["candidate"]["tokens_mean"]
            )

    def test_repair_preservation_and_new_defects_are_separate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = manifest()
            rs = [receipt(root, m, "baseline", i, repair=False) for i in [1, 2]]
            rs += [receipt(root, m, "candidate", i, preserve=False) for i in [1, 2]]
            p = root / rs[-1]["receipt"]["path"]
            d = json.loads(p.read_text())
            d["new_defects"] = 3
            p.write_text(json.dumps(d))
            rs[-1]["receipt"]["sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
            x = ev.compare(m, rs, root)
            self.assertEqual(x["arms"]["baseline"]["repair_passes"], 0)
            self.assertEqual(x["arms"]["candidate"]["repair_passes"], 2)
            self.assertEqual(x["arms"]["baseline"]["preserve_passes"], 2)
            self.assertEqual(x["arms"]["candidate"]["preserve_passes"], 0)
            self.assertEqual(x["arms"]["candidate"]["new_defects_total"], 3)


if __name__ == "__main__":
    unittest.main()
