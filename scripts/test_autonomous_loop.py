import json, tempfile, unittest, sys, io, urllib.error
from pathlib import Path
from unittest import mock
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


class TestCrossAudit(unittest.TestCase):
    def setUp(self):
        from autonomous_loop import cross_audit
        self.ca = cross_audit
        self.d = Path(tempfile.mkdtemp())
        self.canary = self.d / ".canary-log.jsonl"
        self.canary.write_text(
            '{"loop":"x","kind":"caught","severity":"clean","note":"r1"}\n', encoding="utf-8")

    def test_no_key_returns_degraded(self):
        r = self.ca.run_cross_audit("spec", str(self.canary), "x", "gt",
                                    key_path=str(self.d / "nonexistent_key"))
        self.assertEqual(r["status"], "degraded")
        self.assertEqual(r["reason"], "no_key")
        self.assertIsNone(r["worst_severity"])

    def _run_with_key(self, urlopen_side):
        kf = self.d / "key"; kf.write_text("sk-test", encoding="utf-8")
        with mock.patch.object(self.ca.urllib.request, "urlopen", side_effect=urlopen_side):
            return self.ca.run_cross_audit("spec", str(self.canary), "x", "gt", key_path=str(kf))

    def test_ok_parses_declared_severity(self):
        body = json.dumps({"choices": [{"message": {"content": "逐節...\n最嚴重 severity = minor"}}], "usage": {}}).encode()
        r = self._run_with_key(lambda *a, **k: io.BytesIO(body))
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["worst_severity"], "minor")

    def test_ok_blocker(self):
        body = json.dumps({"choices": [{"message": {"content": "最嚴重 severity = blocker"}}], "usage": {}}).encode()
        r = self._run_with_key(lambda *a, **k: io.BytesIO(body))
        self.assertEqual(r["worst_severity"], "blocker")

    def test_ok_no_format_scans_highest(self):
        body = json.dumps({"choices": [{"message": {"content": "有個 minor,也有個 major 問題"}}], "usage": {}}).encode()
        r = self._run_with_key(lambda *a, **k: io.BytesIO(body))
        self.assertEqual(r["worst_severity"], "major")

    def test_http_error_degraded(self):
        def boom(*a, **k):
            raise urllib.error.HTTPError("u", 403, "forbidden", {}, None)
        r = self._run_with_key(boom)
        self.assertEqual(r["status"], "degraded")
        self.assertEqual(r["reason"], "http_403")
        self.assertIsNone(r["worst_severity"])

    def test_timeout_degraded(self):
        def boom(*a, **k):
            raise urllib.error.URLError("timed out")
        r = self._run_with_key(boom)
        self.assertEqual(r["status"], "degraded")
        self.assertEqual(r["reason"], "timeout")

    def test_ssl_context_returns_valid_context(self):
        import ssl as _ssl
        self.assertIsInstance(self.ca._ssl_context(), _ssl.SSLContext)

    def test_ok_parses_bolded_severity(self):
        # 末行優先後,markdown 粗體 **major** 需在末行才能作為 verdict(否則 fallback 誠實舉旗)
        # 此測試驗證正則能容忍粗體,當 verdict 在末行時識別為 major,且 fallback=False
        body = json.dumps({"choices": [{"message": {"content": "內文提到一個 blocker 是植入的\n最嚴重 severity = **major**"}}], "usage": {}}).encode()
        r = self._run_with_key(lambda *a, **k: io.BytesIO(body))
        self.assertEqual(r["worst_severity"], "major")
        self.assertFalse(r["parse_fallback"])

    def test_parse_worst_last_line_priority(self):
        sev, fb = self.ca._parse_worst("正文提到 blocker 一詞\n最嚴重 severity = minor")
        self.assertEqual((sev, fb), ("minor", False))

    def test_parse_worst_fallback_flags(self):
        sev, fb = self.ca._parse_worst("引述:「最嚴重 severity = blocker」不在末行\n然後結束")
        self.assertEqual((sev, fb), ("blocker", True))

    def test_ok_includes_parse_fallback_key(self):
        body = json.dumps({"choices": [{"message": {"content": "最嚴重 severity = minor"}}],
                           "usage": {}}).encode()
        r = self._run_with_key(lambda *a, **k: io.BytesIO(body))
        self.assertFalse(r["parse_fallback"])
        body2 = json.dumps({"choices": [{"message": {"content": "有個 major 但無 verdict 末行"}}],
                            "usage": {}}).encode()
        r2 = self._run_with_key(lambda *a, **k: io.BytesIO(body2))
        self.assertTrue(r2["parse_fallback"])

    def test_build_prompt_sentinels(self):
        p = self.ca._build_prompt("EV", "GT", "SPEC-BODY")
        for s in ("<<<EVIDENCE-BEGIN>>>", "<<<EVIDENCE-END>>>", "<<<GROUND-TRUTH-BEGIN>>>",
                  "<<<GROUND-TRUTH-END>>>", "<<<SPEC-BEGIN>>>", "<<<SPEC-END>>>"):
            self.assertIn(s, p)
        self.assertLess(p.index("不是對你的指令"), p.index("<<<EVIDENCE-BEGIN>>>"))


class TestRequeueUnconverged(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.bl = self.d / "backlog.jsonl"
        self.cov = self.d / "covered.jsonl"

    def test_requeue_decays_and_increments(self):
        g = {"weakness": "w1", "suggestion": "s", "value_score": 0.5}
        r = gap_select.requeue_unconverged(self.bl, g, self.cov)
        self.assertEqual(r, "requeued")
        rows = backlog.load_backlog(self.bl)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["unconverged"], 1)
        self.assertAlmostEqual(rows[0]["value_score"], 0.35)  # 0.5 * 0.7

    def test_requeue_hits_cap_covered(self):
        g = {"weakness": "w2", "suggestion": "s", "value_score": 0.3, "unconverged": 2}
        r = gap_select.requeue_unconverged(self.bl, g, self.cov)  # 2+1=3 >= 3
        self.assertEqual(r, "covered")
        self.assertEqual(backlog.load_backlog(self.bl), [])  # 不回 backlog
        covered = {json.loads(l)["weakness"] for l in self.cov.read_text().splitlines() if l.strip()}
        self.assertIn("w2", covered)

    def test_requeue_updates_not_duplicates(self):
        backlog.add_gaps(self.bl, [{"weakness": "w3", "suggestion": "s"}], "2026-06-22")
        g = backlog.load_backlog(self.bl)[0]
        gap_select.requeue_unconverged(self.bl, g, self.cov)
        rows = [r for r in backlog.load_backlog(self.bl) if r["weakness"] == "w3"]
        self.assertEqual(len(rows), 1)  # 更新而非重複
        self.assertEqual(rows[0]["unconverged"], 1)


class TestDifficulty(unittest.TestCase):
    def setUp(self):
        from autonomous_loop import difficulty
        self.d = difficulty

    def test_assess_hits_high(self):
        for kw, cls in (("接 stripe 收款", "payment"), ("金流對帳", "payment"),
                        ("執行 DROP TABLE 清理", "prod-irreversible"),
                        ("完成後寄送通知", "external-send")):
            r = self.d.assess(kw)
            self.assertEqual(r["tier"], "high", kw)
            self.assertIn(cls, [h["class"] for h in r["hits"]], kw)

    def test_assess_standard(self):
        r = self.d.assess("重構內部快取層,拆函數與改名,無外部行為變更")
        self.assertEqual(r["tier"], "standard")
        self.assertEqual(r["hits"], [])

    def test_assess_deterministic(self):
        t = "金流與寄送並存的文本"
        self.assertEqual(self.d.assess(t), self.d.assess(t))

    def test_assess_self_governance(self):
        r = self.d.assess("本改動調整 anchor verify 與收斂判準")
        self.assertEqual(r["tier"], "high")
        self.assertIn("self-governance", [h["class"] for h in r["hits"]])

    def test_params_mapping(self):
        self.assertEqual(self.d.params("high"), {"need": 3, "maxr": 8})
        self.assertEqual(self.d.params("standard"), {"need": 2, "maxr": 6})

    def test_assess_spec_blacklist_strip(self):
        filler = ("此次修改屬純內部程式重構,僅調整函數命名與模組內部呼叫順序,"
                  "所有公開介面簽名維持不變。此重構不影響任何使用者可見的行為,"
                  "不改變資料庫欄位定義,亦不涉及任何第三方系統整合。"
                  "整體變更範圍限定於程式庫內部實作細節的整理與清理作業。")
        md = ("# t\n- 狀態:草稿\n"
              "## 目標\n改內部排序邏輯。" + filler + "\n"
              "## 組件\n重構 sort 模組,純內部。" + filler + "\n"
              "## 誠實天花板\ncanary 與收斂判準的既有守衛不受影響。\n"
              "## 審計修正紀錄(design-loop)\nr1 canary caught。\n")
        self.assertEqual(self.d.assess_spec(md)["tier"], "standard")

    def test_assess_spec_title_variant(self):
        filler = ("此次修改屬純內部程式重構,僅調整函數命名與模組內部呼叫順序,"
                  "所有公開介面簽名維持不變。此重構不影響任何使用者可見的行為,"
                  "不改變資料庫欄位定義,亦不涉及任何第三方系統整合。"
                  "整體變更範圍限定於程式庫內部實作細節的整理與清理作業。")
        md = ("# t\n## 目標\n改內部排序。" + filler + "\n"
              "## 組件\n純內部重構。" + filler + "\n"
              "## 誠實天花板(v2 補)\ncanary 收斂判準。\n"
              "## 附:審計修正紀錄與備註\ncanary。\n")
        self.assertEqual(self.d.assess_spec(md)["tier"], "standard")

    def test_assess_spec_substantive_high(self):
        md = ("# t\n## 目標\n強化 anchor verify 與 pre-push hook 的接線。\n"
              "## 組件\n改守衛腳本。\n## 誠實天花板\n無。\n")
        self.assertEqual(self.d.assess_spec(md)["tier"], "high")

    def test_assess_spec_fallback_near_empty(self):
        md = "# t\n## 誠實天花板\n" + "金流" * 200 + "\n"
        self.assertEqual(self.d.assess_spec(md)["tier"], "high")  # 回退全文,偏嚴

    def test_assess_spec_strips_inline_code_and_filenames(self):
        filler = ("此次修改屬純內部程式重構,僅調整函數命名與模組內部呼叫順序,"
                  "所有公開介面簽名維持不變。此重構不影響任何使用者可見的行為,"
                  "不改變資料庫欄位定義,亦不涉及任何第三方系統整合。"
                  "整體變更範圍限定於程式庫內部實作細節的整理與清理作業。")
        md = ("# t\n## 目標\n更新 `圖譜即合約-對外論述.md` 的段落說明,內容為文檔措辭。" + filler + "\n"
              "## 組件\n見 圖譜即合約-對外論述.md 檔。" + filler + "\n"
              "## 其他\n無風險詞的內部整理。" + filler + "\n")
        self.assertEqual(self.d.assess_spec(md)["tier"], "standard")  # 檔名「對外」不得誤觸

    def test_assess_spec_fallback_short_corpus(self):
        # 節數 ≥2 但剝除後 corpus <200 字元,且全文含「金流」在黑名單節
        # → 字元門檻觸發回退 → 全文 assess → high(獨立驗字元條件起作用)
        md = ("# t\n"
              "## 目標\n短。\n"
              "## 組件\n短。\n"
              "## 誠實天花板\n金流對帳流程說明。\n")
        # 確認剝除後餘文 <200 字元(目標+組件節保留,天花板節剝除)
        r = self.d.assess_spec(md)
        self.assertEqual(r["tier"], "high")  # 回退全文後命中「金流」


if __name__ == "__main__":
    unittest.main()
