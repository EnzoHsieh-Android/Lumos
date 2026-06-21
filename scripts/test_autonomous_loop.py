import json, tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance"))
from autonomous_loop import backlog, gap_select, confidence_report, line_notify


class TestBacklog(unittest.TestCase):
    def setUp(self):
        self.p = Path(tempfile.mkdtemp()) / "backlog.jsonl"

    def test_load_missing_returns_empty(self):
        self.assertEqual(backlog.load_backlog(self.p), [])

    def test_add_sets_initial_fields(self):
        backlog.add_gaps(self.p, [{"weakness": "w1", "suggestion": "s1"}], "2026-06-20")
        r = backlog.load_backlog(self.p)[0]
        self.assertEqual(r["value_score"], 0.5)
        self.assertEqual(r["source_date"], "2026-06-20")

    def test_decay_prunes_below_floor(self):
        backlog.add_gaps(self.p, [{"weakness": "w1", "suggestion": "s1"}], "2026-06-20")
        for i in range(20):
            backlog.decay_and_prune(self.p, "2026-07-%02d" % (i + 1))
        self.assertEqual(backlog.load_backlog(self.p), [])

    def test_dedup_by_weakness(self):
        g = [{"weakness": "w1", "suggestion": "s1"}]
        backlog.add_gaps(self.p, g, "2026-06-20")
        backlog.add_gaps(self.p, g, "2026-06-21")
        self.assertEqual(len(backlog.load_backlog(self.p)), 1)

    def test_pop_top_returns_highest_and_removes(self):
        backlog.add_gaps(self.p, [{"weakness": "a", "suggestion": "s"}], "2026-06-20")
        backlog.add_gaps(self.p, [{"weakness": "b", "suggestion": "s"}], "2026-06-20")
        rows = backlog.load_backlog(self.p)
        rows[0]["value_score"] = 0.9
        backlog._save(self.p, rows)
        top = backlog.pop_top(self.p)
        self.assertEqual(top["weakness"], "a")
        self.assertEqual(len(backlog.load_backlog(self.p)), 1)


class TestGapSelect(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.report = self.d / "governance-2026-06-20.json"
        self.report.write_text(json.dumps({"date": "2026-06-20", "gaps": [
            {"weakness": "w1", "suggestion": "s1"}, {"weakness": "w2", "suggestion": "s2"}]}),
            encoding="utf-8")
        self.bl = self.d / "backlog.jsonl"
        self.pend = self.d / "pending"; self.pend.mkdir()

    def test_read_gaps(self):
        self.assertEqual(len(gap_select.read_report_gaps(self.report)), 2)

    def test_read_gaps_missing_file(self):
        self.assertEqual(gap_select.read_report_gaps(self.d / "nope.json"), [])

    def test_gate_blocks_when_pending(self):
        (self.pend / "x.md").write_text("pending")
        got = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20")
        self.assertIsNone(got)
        self.assertEqual(len(backlog.load_backlog(self.bl)), 2)

    def test_selects_top1_when_clear(self):
        got = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20")
        self.assertIsNotNone(got)
        self.assertIn("weakness", got)
        self.assertEqual(len(backlog.load_backlog(self.bl)), 1)  # pop 後剩 1

    def test_covered_gap_excluded_and_not_readded(self):
        cov = self.d / "covered.jsonl"
        gap_select.mark_covered(cov, "w1")              # w1 標記為已覆蓋
        got = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20", cov)
        self.assertEqual(got["weakness"], "w2")         # w1 被排除 → 選 w2
        self.assertNotIn("w1", [r["weakness"] for r in backlog.load_backlog(self.bl)])  # w1 沒被加回
        # 再 select 一次(模擬循環):w1 仍不回來
        got2 = gap_select.select(self.report, self.bl, self.pend, "dryrun", "2026-06-20", cov)
        if got2:
            self.assertNotEqual(got2["weakness"], "w1")


class TestConfidenceReport(unittest.TestCase):
    def test_build_lists_rounds_and_risks(self):
        d = Path(tempfile.mkdtemp()); log = d / "canary.jsonl"
        log.write_text("\n".join([
            json.dumps({"loop": "foo", "kind": "caught", "severity": "blocker", "auditor": "opus", "note": "r1", "token": "t1"}),
            json.dumps({"loop": "foo", "kind": "caught", "severity": "clean", "auditor": "opus", "note": "r2", "token": "t2"}),
            json.dumps({"loop": "other", "kind": "missed", "severity": "major", "token": "t3"}),
        ]), encoding="utf-8")
        md = confidence_report.build_report(log, "foo", ["severity 自報是最弱環"])
        self.assertIn("blocker", md)
        self.assertIn("clean", md)
        self.assertNotIn("t3", md)
        self.assertIn("severity 自報是最弱環", md)

    def test_build_missing_log(self):
        md = confidence_report.build_report(Path("/no/such.jsonl"), "foo", ["risk1"])
        self.assertIn("共 0 輪", md)
        self.assertIn("risk1", md)


class TestLineNotify(unittest.TestCase):
    def test_build_message_has_title_and_pr(self):
        m = line_notify.build_message("X spec", "5輪收斂、1 missed", "http://pr/1")
        s = json.dumps(m, ensure_ascii=False)
        self.assertIn("X spec", s); self.assertIn("http://pr/1", s)

    def test_build_message_dryrun_no_pr(self):
        m = line_notify.build_message("X spec", "dry-run", None)
        self.assertIn("messages", m)
        self.assertIn("dry-run", json.dumps(m, ensure_ascii=False))


class TestOrchestratorResult(unittest.TestCase):
    def test_extracts_last_json_skipping_noise_braces(self):
        from autonomous_loop import orchestrator_result
        s = ('一段敘述 收斂需 {clean,minor} 的門檻,撞 cap 停止。\n---\n'
             '{"topic":"judge-severity-gate","converged":false,"rounds":2}')
        r = orchestrator_result.extract_json(s)
        self.assertIsNotNone(r)
        self.assertEqual(r["topic"], "judge-severity-gate")
        self.assertEqual(r["converged"], False)

    def test_none_when_no_json(self):
        from autonomous_loop import orchestrator_result
        self.assertIsNone(orchestrator_result.extract_json("no json {clean,minor} here"))


if __name__ == "__main__":
    unittest.main()
