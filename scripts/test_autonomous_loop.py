import json, tempfile, unittest, sys, io, urllib.error
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance"))
from autonomous_loop import backlog, gap_select, confidence_report, line_notify, run_ledger


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


class TestConfidenceReportTier(unittest.TestCase):
    def test_tier_rendered_and_mismatch_flag(self):
        d = Path(tempfile.mkdtemp()); log = d / "c.jsonl"
        log.write_text('{"loop":"x","kind":"caught","severity":"clean","note":"r1"}\n',
                       encoding="utf-8")
        r = confidence_report.build_report(str(log), "x", ["天花板"], tier="high",
                                           hits=[{"class": "payment", "excerpt": "接 stripe 收款"}],
                                           reported_tier="standard")
        self.assertIn("tier=`high`", r)
        self.assertIn("payment", r)
        self.assertIn("紅標", r)
        r2 = confidence_report.build_report(str(log), "x", ["天花板"], tier="high",
                                            hits=[], reported_tier="high")
        self.assertNotIn("紅標", r2)
        r3 = confidence_report.build_report(str(log), "x", ["天花板"])
        self.assertNotIn("tier=", r3)   # 向後相容:不傳 tier 照舊


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


class TestExtractCost(unittest.TestCase):
    """成本欄落帳:claude -p --output-format json 的頂層本來就吐 cost/duration/turns,
    以前沒人接。抽取必須 fail-open——形狀一變就回 None,絕不讓 loop 因為記帳失敗而中斷。"""

    def test_extracts_all_fields(self):
        from autonomous_loop import orchestrator_result
        c = orchestrator_result.extract_cost({
            "total_cost_usd": 2.2043, "duration_ms": 99920, "num_turns": 13,
            "usage": {"input_tokens": 1200, "output_tokens": 38376,
                      "cache_read_input_tokens": 900000},
        })
        self.assertEqual(c["usd"], 2.2043)
        self.assertEqual(c["wallclock_min"], 2)          # 99920ms → 1.665 分 → round=2
        self.assertEqual(c["turns"], 13)
        self.assertEqual(c["tokens"], 39576)             # in+out,★不含 cache_read★
        self.assertEqual(c["cache_read"], 900000)

    def test_missing_usage_still_returns_what_it_has(self):
        from autonomous_loop import orchestrator_result
        c = orchestrator_result.extract_cost({"total_cost_usd": 0.5, "duration_ms": 20000})
        self.assertEqual(c["usd"], 0.5)
        self.assertEqual(c["wallclock_min"], 0)          # 20 秒 → 0 分,不四捨五入成 1(不假造)
        self.assertIsNone(c["tokens"])
        self.assertIsNone(c["turns"])

    def test_none_when_nothing_useful(self):
        from autonomous_loop import orchestrator_result
        self.assertIsNone(orchestrator_result.extract_cost({"result": "文字", "is_error": False}))
        self.assertIsNone(orchestrator_result.extract_cost(None))
        self.assertIsNone(orchestrator_result.extract_cost("不是 dict"))

    def test_bad_shapes_fail_open(self):
        """★反假綠★:欄位型別壞掉(字串當數字)不能拋例外,也不能默默記出垃圾數字。"""
        from autonomous_loop import orchestrator_result
        c = orchestrator_result.extract_cost({"total_cost_usd": "貴", "duration_ms": None,
                                              "num_turns": [], "usage": "壞"})
        self.assertIsNone(c)

    def test_cli_line_omits_missing_fields(self):
        """組出來的記帳參數只帶真的有值的欄——沒有的不要送 0 冒充量過。"""
        from autonomous_loop import orchestrator_result
        self.assertEqual(
            orchestrator_result.cost_cli_args({"usd": 1.0, "wallclock_min": 3,
                                               "tokens": 500, "turns": 2, "cache_read": 0}),
            ["--tokens", "500", "--wallclock-min", "3", "--usd", "1.0"])
        # usd 自 2026-08-26 起是結構化欄(auto-loop-repair-v2):有值就送
        self.assertEqual(
            orchestrator_result.cost_cli_args({"usd": None, "wallclock_min": None,
                                               "tokens": None, "turns": 2, "cache_read": 0}),
            [])


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


class TestPromptPlaceholders(unittest.TestCase):
    def test_prompt_placeholders_match_runner_substitutions(self):
        """佔位符契約:prompt 模板的每個 __FOO__ 都要有 runner 的 sed 替換,反之亦然。

        少一邊的後果是真的:prompt 有、runner 沒有 → 字面 `__FOO__` 原封不動漏進送給
        agent 的指令;runner 有、prompt 沒有 → 死掉的 sed(2026-08-27 遷處置閘後
        __NEED__ 就是這樣變成死碼)。兩造都是真缺陷,不是文字差異。

        ★寫法刻意不釘任何散文字句★(2026-08-28,借 OmO `.omo/rules/test-discipline.md`
        「測行為不測文字」:對 prompt 寫「必須包含某句/不准包含舊寫法」的斷言守的是 diff
        不是行為——文字一改就紅,下一個人只會把斷言改成新文字,等於沒守)。這裡改成拿
        兩個真檔案對帳:改寫措辭不會誤紅,漏接佔位符才紅。
        """
        import re as _re
        root = Path(__file__).resolve().parent.parent
        prompt = (root / "governance/autonomous_loop/orchestrator-prompt.md").read_text(encoding="utf-8")
        runner = (root / "governance/autonomous-loop.sh").read_text(encoding="utf-8")
        in_prompt = set(_re.findall(r"__[A-Z][A-Z0-9_]*__", prompt))
        substituted = set(_re.findall(r"s#(__[A-Z][A-Z0-9_]*__)#", runner))
        self.assertTrue(in_prompt, "prompt 一個佔位符都沒有,對帳失去意義——檢查正則或檔案路徑")
        self.assertEqual(
            in_prompt, substituted,
            f"佔位符對不上:prompt 有但 runner 不替換(會原樣漏給 agent)={sorted(in_prompt - substituted)};"
            f" runner 替換但 prompt 沒有(死 sed)={sorted(substituted - in_prompt)}")


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
        # panel_width(loop 三輪壓縮):tier 驅動並行寬度;既有 need/maxr 不變
        self.assertEqual(self.d.params("high"), {"need": 3, "maxr": 8, "panel_width": 5})
        self.assertEqual(self.d.params("standard"), {"need": 2, "maxr": 6, "panel_width": 3})

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
        # 保留節(目標+組件)剝除後需 >200 字元,確保走正常路徑而非 fallback;
        # anchor verify 與 pre-push hook 是觸發 high 的關鍵詞,必須保留。
        filler = ("此節描述內部實作細節調整,不涉及外部系統呼叫或資料庫欄位變更,"
                  "所有公開介面簽名維持不變,整體屬於守衛接線強化作業。"
                  "變更範圍僅限程式庫內部邏輯的整理,無對外行為影響。")
        md = ("# t\n## 目標\n強化 anchor verify 與 pre-push hook 的接線。" + filler + "\n"
              "## 組件\n改守衛腳本,補強驗證邏輯。" + filler + "\n"
              "## 誠實天花板\n無。\n")
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


class TestPitfallsDrift(unittest.TestCase):
    def test_pitfall_classes_match_risk_classes(self):
        import subprocess, json as _json
        from autonomous_loop import difficulty
        lumos = str(Path(__file__).resolve().parent / "lumos")
        # 從 lumos 匯出 PITFALL_CLASSES 類名集合(exec 載入模組層常數)
        src = Path(lumos).read_text(encoding="utf-8")
        ns = {}
        import re as _re
        m = _re.search(r"^PITFALL_CLASSES = \{.*?^\}", src, _re.S | _re.M)
        self.assertIsNotNone(m, "PITFALL_CLASSES 未找到")
        exec("import re\n" + m.group(0), ns)
        self.assertEqual(set(ns["PITFALL_CLASSES"].keys()), set(difficulty.RISK_CLASSES.keys()),
                         "pitfalls 類名集合 != difficulty.RISK_CLASSES(漂移)")

    def test_pitfall_blacklist_match(self):
        from autonomous_loop import difficulty
        lumos = str(Path(__file__).resolve().parent / "lumos")
        src = Path(lumos).read_text(encoding="utf-8")
        import re as _re
        m = _re.search(r"^_PITFALL_BLACKLIST = \((.*?)\)", src, _re.S | _re.M)
        self.assertIsNotNone(m)
        ns = {}
        exec("_PITFALL_BLACKLIST = (" + m.group(1) + ")", ns)
        self.assertEqual(set(ns["_PITFALL_BLACKLIST"]), set(difficulty._BLACKLIST),
                         "pitfalls 黑名單 != difficulty._BLACKLIST(漂移)")


class TestLintWatchDedup(unittest.TestCase):
    """Tests for governance/autonomous_loop/lint_watch_dedup.py"""

    def _load_module(self):
        import importlib.util as U
        from importlib.machinery import SourceFileLoader
        P = str(Path(__file__).resolve().parent.parent / "governance/autonomous_loop/lint_watch_dedup.py")
        spec = U.spec_from_file_location("lwd", P, loader=SourceFileLoader("lwd", P))
        m = U.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def setUp(self):
        import tempfile
        self.d = Path(tempfile.mkdtemp(prefix="lwd-"))
        self.seen = self.d / "seen.jsonl"
        self.m = self._load_module()

    def test_new_candidates_seen_missing_returns_all(self):
        cands = [{"name": "detekt", "latest": "1.24.0"}, {"name": "ruff", "latest": "0.5.0"}]
        result = self.m.new_candidates(cands, str(self.seen))
        self.assertEqual(result, cands)

    def test_new_candidates_all_seen_returns_empty(self):
        cands = [{"name": "detekt", "latest": "1.24.0"}, {"name": "ruff", "latest": "0.5.0"}]
        self.seen.write_text(
            '{"name":"detekt","latest":"1.24.0","seen":"2026-07-04"}\n'
            '{"name":"ruff","latest":"0.5.0","seen":"2026-07-04"}\n',
            encoding="utf-8")
        self.assertEqual(self.m.new_candidates(cands, str(self.seen)), [])

    def test_new_candidates_partial_new(self):
        cands = [{"name": "detekt", "latest": "1.24.0"}, {"name": "ruff", "latest": "0.5.0"}]
        self.seen.write_text('{"name":"detekt","latest":"1.24.0","seen":"2026-07-04"}\n', encoding="utf-8")
        result = self.m.new_candidates(cands, str(self.seen))
        self.assertEqual([c["name"] for c in result], ["ruff"])

    def test_new_candidates_same_name_new_latest_counts_as_new(self):
        cands = [{"name": "detekt", "latest": "1.24.0"}, {"name": "ruff", "latest": "0.5.0"}]
        self.seen.write_text('{"name":"detekt","latest":"1.23.7","seen":"2026-07-04"}\n', encoding="utf-8")
        result = self.m.new_candidates(cands, str(self.seen))
        self.assertTrue(any(c["name"] == "detekt" for c in result))

    def test_main_writes_pending_and_seen_and_stdout_line_dict(self):
        import subprocess
        pending = self.d / "pending-2026-07-04.json"
        manifest = json.dumps({"candidates": [{"name": "detekt", "registry": "github:detekt/detekt",
                                               "current": "1.23.7", "latest": "1.24.0"}],
                               "checked": 1, "failed": []})
        r = subprocess.run(
            [sys.executable,
             str(Path(__file__).resolve().parent.parent / "governance/autonomous_loop/lint_watch_dedup.py"),
             str(self.seen), str(pending), "2026-07-04"],
            input=manifest, capture_output=True, text=True)
        self.assertTrue(pending.exists(), "pending 未寫")
        self.assertEqual(json.loads(pending.read_text())[0]["name"], "detekt")
        self.assertTrue(self.seen.exists() and "1.24.0" in self.seen.read_text(), "seen 未 append")
        msg = json.loads(r.stdout)
        self.assertEqual(msg["messages"][0]["type"], "text")
        self.assertIn("detekt", msg["messages"][0]["text"])

    def test_main_non_json_stdin_empty_stdout(self):
        import subprocess
        pending = self.d / "pending-2026-07-04.json"
        r = subprocess.run(
            [sys.executable,
             str(Path(__file__).resolve().parent.parent / "governance/autonomous_loop/lint_watch_dedup.py"),
             str(self.seen), str(pending), "2026-07-04"],
            input="ERROR: bad watch list", capture_output=True, text=True)
        self.assertEqual(r.stdout.strip(), "", f"非 JSON 應印空: {r.stdout!r}")

    def test_new_candidates_malformed_seen_line_skipped(self):
        """malformed line in seen.jsonl must be skipped; only valid seen entries filter candidates."""
        cands = [
            {"name": "detekt", "latest": "1.24.0"},
            {"name": "ruff", "latest": "0.5.0"},
        ]
        # seen.jsonl: one malformed line, one valid line for "detekt"
        self.seen.write_text(
            "not json\n"
            '{"name":"detekt","latest":"1.24.0","seen":"2026-07-04"}\n',
            encoding="utf-8")
        result = self.m.new_candidates(cands, str(self.seen))
        # must not crash, detekt is seen (valid line) → filtered out
        names = [c["name"] for c in result]
        self.assertNotIn("detekt", names, "detekt は valid seen line で除外されるべき")
        # ruff matches malformed line's key only if parsed — since malformed is skipped, ruff is new
        self.assertIn("ruff", names, "ruff は malformed line に一致せず新候補のはず")


# ═══ 自主迴圈修理(auto-loop-repair-v2,2026-08-26)——[S1]-[S4] 行為斷言 ═══

class TestBacklogRepairS2(unittest.TestCase):
    """[S2] 選題修理:壞行容錯/原子寫/回血/三鍵排序/冪等衰減+歸檔。"""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = self.d / "backlog.jsonl"
        self.arch = self.d / "backlog-archive.jsonl"
        self.state = self.d / "decay-state.json"

    def test_load_skips_bad_lines(self):
        self.p.write_text('{"weakness":"a","value_score":0.5}\n{{{壞行\n{"weakness":"b","value_score":0.4}\n')
        rows = backlog.load_backlog(self.p)
        self.assertEqual([r["weakness"] for r in rows], ["a", "b"])

    def test_save_atomic_no_tmp_left(self):
        backlog._save(self.p, [{"weakness": "a"}])
        leftovers = [f for f in self.d.iterdir() if f.name != "backlog.jsonl"]
        self.assertEqual(leftovers, [])
        self.assertEqual(backlog.load_backlog(self.p)[0]["weakness"], "a")

    def test_reseen_restores_score_to_init_not_above(self):
        backlog._save(self.p, [{"weakness": "w", "suggestion": "s", "source_date": "2026-08-01",
                                "value_score": 0.3, "last_seen": "2026-08-01"}])
        backlog.add_gaps(self.p, [{"weakness": "w", "suggestion": "s"}], "2026-08-26")
        r = backlog.load_backlog(self.p)[0]
        self.assertEqual(r["value_score"], 0.5)   # 補回初始
        self.assertEqual(r["last_seen"], "2026-08-26")
        backlog.add_gaps(self.p, [{"weakness": "w", "suggestion": "s"}], "2026-08-27")
        self.assertEqual(backlog.load_backlog(self.p)[0]["value_score"], 0.5)  # 不疊加不超過

    def test_pop_top_source_date_breaks_tie(self):
        # 同分同 last_seen:source_date 新者贏,且與插入順序無關(舊題先插)
        backlog._save(self.p, [
            {"weakness": "old", "value_score": 0.5, "last_seen": "2026-08-26", "source_date": "2026-06-01"},
            {"weakness": "new", "value_score": 0.5, "last_seen": "2026-08-26", "source_date": "2026-08-26"},
        ])
        self.assertEqual(backlog.pop_top(self.p)["weakness"], "new")

    def test_pop_top_last_seen_before_source(self):
        backlog._save(self.p, [
            {"weakness": "stale", "value_score": 0.5, "last_seen": "2026-08-01", "source_date": "2026-08-26"},
            {"weakness": "fresh", "value_score": 0.5, "last_seen": "2026-08-26", "source_date": "2026-06-01"},
        ])
        self.assertEqual(backlog.pop_top(self.p)["weakness"], "fresh")

    def test_pop_top_score_still_dominates(self):
        backlog._save(self.p, [
            {"weakness": "hi", "value_score": 0.6, "last_seen": "2026-01-01", "source_date": "2026-01-01"},
            {"weakness": "lo", "value_score": 0.5, "last_seen": "2026-08-26", "source_date": "2026-08-26"},
        ])
        self.assertEqual(backlog.pop_top(self.p)["weakness"], "hi")

    def _row(self, w, score):
        return {"weakness": w, "value_score": score, "last_seen": "2026-08-20", "source_date": "2026-08-20"}

    def test_daily_decay_first_run_single_day(self):
        backlog._save(self.p, [self._row("w", 0.5)])
        out = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out["days"], 1)
        self.assertAlmostEqual(backlog.load_backlog(self.p)[0]["value_score"], 0.475, places=4)

    def test_daily_decay_same_day_noop(self):
        backlog._save(self.p, [self._row("w", 0.5)])
        backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        out2 = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out2["status"], "noop")
        self.assertAlmostEqual(backlog.load_backlog(self.p)[0]["value_score"], 0.475, places=4)

    def test_daily_decay_days_exponent(self):
        backlog._save(self.p, [self._row("w", 0.5)])
        self.state.write_text('{"last_decayed": "2026-08-23"}')
        out = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out["days"], 3)
        self.assertAlmostEqual(backlog.load_backlog(self.p)[0]["value_score"], 0.5 * 0.95 ** 3, places=4)

    def test_daily_decay_prunes_to_archive_not_vanish(self):
        backlog._save(self.p, [self._row("dying", 0.2), self._row("living", 0.5)])
        out = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out["pruned"], 1)
        live = [r["weakness"] for r in backlog.load_backlog(self.p)]
        self.assertEqual(live, ["living"])
        arch = [json.loads(l) for l in self.arch.read_text().splitlines() if l.strip()]
        self.assertEqual(arch[0]["weakness"], "dying")
        self.assertEqual(arch[0]["archived"], "2026-08-26")

    def test_daily_decay_archive_fail_keeps_live(self):
        backlog._save(self.p, [self._row("dying", 0.2)])
        bad_arch = self.d / "not-writable-dir"
        bad_arch.mkdir()   # 目錄不可當檔寫 → append 失敗
        out = backlog.daily_decay(self.p, bad_arch, self.state, "2026-08-26")
        self.assertEqual(out["status"], "archive-fail")
        self.assertEqual(backlog.load_backlog(self.p)[0]["weakness"], "dying")  # live 不動
        self.assertFalse(self.state.exists())  # 狀態不前進,明天重試


class TestPipelineRequeueS1(unittest.TestCase):
    """[S1] 失敗不丟件:原分放回+pipeline_failures 累計+滿 3 熔斷 covered。"""
    def setUp(self):
        d = Path(tempfile.mkdtemp())
        self.p = d / "backlog.jsonl"
        self.cov = d / "covered.jsonl"

    def test_requeue_keeps_score_and_counts(self):
        gap = {"weakness": "w", "suggestion": "s", "value_score": 0.31,
               "last_seen": "2026-08-20", "source_date": "2026-08-01"}
        out = gap_select.requeue_pipeline_fail(self.p, gap, self.cov)
        self.assertEqual(out, "requeued")
        r = backlog.load_backlog(self.p)[0]
        self.assertEqual(r["value_score"], 0.31)          # 不降分
        self.assertEqual(r["pipeline_failures"], 1)

    def test_third_failure_goes_covered(self):
        gap = {"weakness": "w", "suggestion": "s", "value_score": 0.5, "pipeline_failures": 2}
        out = gap_select.requeue_pipeline_fail(self.p, gap, self.cov)
        self.assertEqual(out, "covered")
        self.assertEqual(backlog.load_backlog(self.p), [])   # 不回 backlog
        self.assertIn("w", gap_select.load_covered(self.cov))


class TestDeathClassify(unittest.TestCase):
    """[S3] 死因分類:shell 層 $PARSED 前綴 → 分類 token(不依賴成本區塊 json.load)。"""
    def test_classify(self):
        from autonomous_loop import orchestrator_result as orr
        self.assertEqual(orr.classify_death("PARSE_FAIL:Expecting value"), "parse_fail")
        self.assertEqual(orr.classify_death(""), "parse_fail")
        self.assertEqual(orr.classify_death("NO_JSON:is_error=True | API Error: 529 Overloaded."), "api_error")
        self.assertEqual(orr.classify_death("NO_JSON:is_error=False | G2 三條也降 minor。剩最後一組。"), "truncated")


class TestRunLedgerS4(unittest.TestCase):
    """[S3]⑤+[S4]:七天彙總逐筆遍歷、舊格式桶、連續失敗按有跑日。"""
    def setUp(self):
        self.log = Path(tempfile.mkdtemp()) / "canary.jsonl"

    def _w(self, rows):
        self.log.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")

    def test_week_summary_mixed_and_same_day(self):
        self._w([
            {"ts": "2026-08-23T15:16:49+08:00", "loop": "auto-2026-08-23", "tokens": 1},              # 舊格式
            {"ts": "2026-08-25T09:38:00+08:00", "loop": "auto-2026-08-25", "outcome": "skipped"},
            {"ts": "2026-08-25T11:58:00+08:00", "loop": "auto-2026-08-25",
             "outcome": "pipeline_fail:truncated", "usd": 53.33},                                     # 同日兩筆都要算
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "auto-2026-08-26", "outcome": "converged", "usd": 12.5},
            {"ts": "2026-08-10T10:00:00+08:00", "loop": "auto-2026-08-10", "outcome": "converged"},   # 窗外
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "probe-x", "outcome": "converged"},           # 非 auto-*
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "auto-smoke", "outcome": "converged", "usd": 9.9},   # 同字首非日期形狀:排除
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "auto-loop-repair-v2", "outcome": "converged"},      # 設計審 loop id:排除
        ])
        s = run_ledger.summarize_week(self.log, "2026-08-26")
        self.assertEqual(s["runs"], 4)
        self.assertEqual(s["legacy"], 1)
        self.assertEqual(s["converged"], 1)
        self.assertEqual(s["pipeline_fail"], 1)
        self.assertAlmostEqual(s["usd"], 65.83, places=2)
        line = run_ledger.format_week_line(s)
        self.assertIn("跑 4 次", line)
        self.assertIn("舊格式", line)

    def test_consecutive_fail_two_run_days(self):
        self._w([
            {"ts": "2026-08-24T10:00:00+08:00", "loop": "auto-2026-08-24", "outcome": "pipeline_fail:api_error"},
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "auto-2026-08-26", "outcome": "pipeline_fail:truncated"},
        ])   # 8/25 沒跑:不算斷
        self.assertTrue(run_ledger.consecutive_fail_days(self.log, "2026-08-26"))

    def test_not_consecutive_when_day_has_success(self):
        self._w([
            {"ts": "2026-08-25T09:00:00+08:00", "loop": "auto-2026-08-25", "outcome": "pipeline_fail:api_error"},
            {"ts": "2026-08-26T09:00:00+08:00", "loop": "auto-2026-08-26", "outcome": "pipeline_fail:parse_fail"},
            {"ts": "2026-08-26T11:00:00+08:00", "loop": "auto-2026-08-26", "outcome": "converged"},
        ])   # 26 日有成功筆 → 非失敗日
        self.assertFalse(run_ledger.consecutive_fail_days(self.log, "2026-08-26"))

    def test_legacy_only_day_not_a_run_day(self):
        self._w([
            {"ts": "2026-08-24T10:00:00+08:00", "loop": "auto-2026-08-24", "outcome": "pipeline_fail:api_error"},
            {"ts": "2026-08-25T10:00:00+08:00", "loop": "auto-2026-08-25", "tokens": 5},              # 舊格式日不算有跑日
            {"ts": "2026-08-26T10:00:00+08:00", "loop": "auto-2026-08-26", "outcome": "pipeline_fail:truncated"},
        ])
        self.assertTrue(run_ledger.consecutive_fail_days(self.log, "2026-08-26"))


class TestLineAlertNoFakeHeader(unittest.TestCase):
    """[S3]⑤ 警示不套「備好待放行」模板。"""
    def test_build_alert_plain(self):
        m = line_notify.build_alert("⚠ 自主迴圈連兩個有跑日管線死")
        self.assertNotIn("備好", json.dumps(m, ensure_ascii=False))
        self.assertEqual(m["messages"][0]["text"], "⚠ 自主迴圈連兩個有跑日管線死")


class TestCodeLoopR1Folds(unittest.TestCase):
    """code-auto-loop-repair r1 折修的釘子(先紅後綠)。"""
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.p = self.d / "backlog.jsonl"
        self.arch = self.d / "backlog-archive.jsonl"
        self.state = self.d / "decay-state.json"
        self.cov = self.d / "covered.jsonl"

    def test_bad_lines_stashed_not_deleted(self):
        # ext-f3:壞行不能在下一次正常寫入時被無聲永久刪除——讀取時撈到 .bad 側檔保留
        self.p.write_text('{"weakness":"a","value_score":0.5}\n{{{半行壞資料\n')
        backlog.load_backlog(self.p)
        backlog._save(self.p, backlog.load_backlog(self.p))   # 正常寫入會覆寫掉壞行
        bad = self.p.with_name(self.p.name + ".bad")
        self.assertTrue(bad.exists(), "壞行要進 .bad 側檔保留,不准人間蒸發")
        self.assertEqual(bad.read_text().count("半行壞資料"), 1, "重覆 load 不准疊加同一壞行(r2 d-f4)")

    def test_load_covered_tolerates_bad_lines(self):
        # s3-f3/conf-f1:covered 讀取要有對稱容錯
        self.cov.write_text('{"weakness":"w1"}\n{{{壞\n{"no_weakness_key":1}\n{"weakness":"w2"}\n')
        got = gap_select.load_covered(self.cov)
        self.assertEqual(got, {"w1", "w2"})
        gap_select.load_covered(self.cov); gap_select.load_covered(self.cov)   # covered 永遠 append-only 無重寫
        bad = self.cov.with_name(self.cov.name + ".bad")
        self.assertEqual(bad.read_text().count("{{{壞"), 1, "重覆 load 不准疊加(r2 d-f4)")

    def test_archive_readback_ignores_historical_bad_line(self):
        # s3-f2:歷史壞行不能讓衰減永久卡死——自驗只看自己剛寫的尾段
        self.arch.write_text('{{{歷史壞行\n')
        backlog._save(self.p, [{"weakness": "dying", "value_score": 0.2,
                                "last_seen": "2026-08-20", "source_date": "2026-08-20"}])
        out = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out["status"], "ok", out)
        self.assertEqual(out["pruned"], 1)

    def test_archive_append_after_half_line_gets_own_line(self):
        # s3-f2 附帶:前次中斷留下沒換行的半行,新寫入不得黏在它後面
        self.arch.write_text('{"weakness":"prev"')   # 無結尾換行
        backlog._save(self.p, [{"weakness": "dying", "value_score": 0.2,
                                "last_seen": "2026-08-20", "source_date": "2026-08-20"}])
        out = backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        self.assertEqual(out["status"], "ok", out)
        lines = self.arch.read_text().splitlines()
        self.assertEqual(json.loads(lines[-1])["weakness"], "dying")

    def test_state_written_before_live_shrink(self):
        # ext-f4/s2-f4:state 先於縮 live 落盤(中斷=少衰一天,絕不重複衰)——以寫入順序釘
        order = []
        real_save = backlog._save
        def spy_save(path, rows):
            order.append(("save", Path(path).name)); real_save(path, rows)
        real_write = Path.write_text
        def spy_write(self_, content, *a, **k):
            if self_.name.endswith("decay-state.json.tmp") or self_.name == "decay-state.json":
                order.append(("state", self_.name))
            return real_write(self_, content, *a, **k)
        backlog._save = spy_save
        Path.write_text = spy_write
        try:
            backlog._save(self.p, [{"weakness": "w", "value_score": 0.5,
                                    "last_seen": "2026-08-20", "source_date": "2026-08-20"}])
            order.clear()
            backlog.daily_decay(self.p, self.arch, self.state, "2026-08-26")
        finally:
            backlog._save = real_save
            Path.write_text = real_write
        state_i = next(i for i, o in enumerate(order) if o[0] == "state")
        save_i = next(i for i, o in enumerate(order) if o[0] == "save" and o[1] == "backlog.jsonl")
        self.assertLess(state_i, save_i, order)

    def test_save_tmp_has_pid_suffix(self):
        # s2-f1 補強:tmp 檔名帶 PID,並行不共用同一暫存檔(整跑鎖是主防線,這是第二道)
        import inspect
        src = inspect.getsource(backlog._save)
        self.assertIn("getpid", src)


class TestLoopShellTrap(unittest.TestCase):
    """[S1]+[S3]+[S4] 端到端(沙箱假 repo):早退點的放回+結局落帳+彙總照印。
    沙箱換 HOME(不摸真 LINE token)、scripts/lumos 換成記 argv 的 stub、claude 換成吐固定信封的 stub。"""

    def _sandbox(self, anchor_ok):
        import shutil, datetime
        root = Path(tempfile.mkdtemp())
        gov = root / "governance"; gov.mkdir()
        real_gov = Path(__file__).resolve().parent.parent / "governance"
        shutil.copy(real_gov / "autonomous-loop.sh", gov / "autonomous-loop.sh")
        shutil.copytree(real_gov / "autonomous_loop", gov / "autonomous_loop",
                        ignore=shutil.ignore_patterns("__pycache__", "*.log", "DRYRUN-OBSERVE.md"))
        (gov / "reports").mkdir()
        today = datetime.date.today().isoformat()
        (gov / "reports" / ("governance-%s.json" % today)).write_text(
            json.dumps({"gaps": [{"weakness": "沙箱測試gap", "suggestion": "x"}]}, ensure_ascii=False))
        scripts = root / "scripts"; scripts.mkdir()
        stub = "\n".join([
            "#!/usr/bin/env python3",
            "import sys, json, pathlib",
            "calls = pathlib.Path(__file__).parent / 'lumos-calls.jsonl'",
            "with calls.open('a') as f:",
            "    f.write(json.dumps(sys.argv[1:], ensure_ascii=False) + chr(10))",
            "if 'anchor' in sys.argv:",
            "    sys.exit(0 if %s else 1)" % ("True" if anchor_ok else "False"),
            "sys.exit(0)", ""])
        (scripts / "lumos").write_text(stub)
        (scripts / "lumos").chmod(0o755)
        home = root / "home"; (home / ".config" / "ai-daily").mkdir(parents=True)  # 無 token 檔=不發 LINE
        bindir = root / "bin"; bindir.mkdir()
        env_file = root / "envelope.json"
        env_file.write_text(json.dumps({
            "result": "中途講到一半沒有 JSON。", "is_error": False,
            "total_cost_usd": 12.5, "duration_ms": 120000, "num_turns": 3,
            "usage": {"input_tokens": 100, "output_tokens": 50, "cache_read_input_tokens": 0}}))
        (bindir / "claude").write_text("#!/usr/bin/env bash\ncat '%s'\n" % env_file)
        (bindir / "claude").chmod(0o755)
        if anchor_ok:
            (gov / "anchor-baseline.json").write_text("{}")
        return root, gov, scripts, home, bindir

    def _run(self, root, home, bindir):
        import subprocess, os
        env = dict(os.environ, HOME=str(home), PATH="%s:%s" % (bindir, os.environ["PATH"]))
        env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
        return subprocess.run(["bash", str(root / "governance" / "autonomous-loop.sh"), "--dry-run", "1"],
                              capture_output=True, text=True, env=env, timeout=120)

    def _calls(self, scripts):
        f = scripts / "lumos-calls.jsonl"
        return [json.loads(l) for l in f.read_text().splitlines() if l.strip()] if f.exists() else []

    def test_anchor_fail_early_exit_requeues_and_records(self):
        root, gov, scripts, home, bindir = self._sandbox(anchor_ok=False)
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        rows = backlog.load_backlog(gov / "backlog.jsonl")
        self.assertEqual([x["weakness"] for x in rows], ["沙箱測試gap"])   # 放回了
        self.assertEqual(rows[0]["pipeline_failures"], 1)
        self.assertEqual(rows[0]["value_score"], 0.5)                      # 原分不動
        recs = [c for c in self._calls(scripts) if "record" in c]
        self.assertTrue(any("pipeline_fail:anchor_fail" in c for c in recs), recs)  # 結局落帳
        self.assertIn("過去 7 天", r.stdout)                               # 失敗日照印彙總

    def test_no_json_classified_requeued_with_cost(self):
        root, gov, scripts, home, bindir = self._sandbox(anchor_ok=True)
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        rows = backlog.load_backlog(gov / "backlog.jsonl")
        self.assertEqual(rows[0]["pipeline_failures"], 1)                  # NO_JSON 也放回
        recs = [c for c in self._calls(scripts) if "record" in c]
        hit = [c for c in recs if "pipeline_fail:truncated" in c]
        self.assertTrue(hit, recs)                                         # 死因=截斷(is_error=False)
        self.assertIn("--usd", hit[0])                                     # 成本欄同筆帶上
        self.assertIn("12.5", " ".join(hit[0]))


class TestLoopShellTrapR1Folds(unittest.TestCase):
    """code-r1 折修的 shell 端到端釘(沙箱同 TestLoopShellTrap;紅證=s1 席自建重現+修前無覆蓋)。"""

    def _sandbox(self, anchor_ok=True, envelopes=None, backlog_rows=None, report_gaps=None,
                 preseed_ledger=None, inflight=None):
        import shutil, datetime
        root = Path(tempfile.mkdtemp())
        gov = root / "governance"; gov.mkdir()
        real_gov = Path(__file__).resolve().parent.parent / "governance"
        shutil.copy(real_gov / "autonomous-loop.sh", gov / "autonomous-loop.sh")
        shutil.copytree(real_gov / "autonomous_loop", gov / "autonomous_loop",
                        ignore=shutil.ignore_patterns("__pycache__", "*.log", "DRYRUN-OBSERVE.md",
                                                      "decay-state.json"))
        (gov / "reports").mkdir()
        today = datetime.date.today().isoformat()
        (gov / "reports" / ("governance-%s.json" % today)).write_text(
            json.dumps({"gaps": report_gaps if report_gaps is not None else
                        [{"weakness": "沙箱測試gap", "suggestion": "x"}]}, ensure_ascii=False))
        if backlog_rows:
            (gov / "backlog.jsonl").write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in backlog_rows) + "\n")
        docs = root / "docs"; docs.mkdir()
        if preseed_ledger:
            (docs / ".canary-log.jsonl").write_text(
                "\n".join(json.dumps(r, ensure_ascii=False) for r in preseed_ledger) + "\n")
        if inflight:
            (gov / ".inflight-gap.json").write_text(json.dumps(inflight, ensure_ascii=False))
        scripts = root / "scripts"; scripts.mkdir()
        stub = "\n".join([
            "#!/usr/bin/env python3",
            "import sys, json, pathlib",
            "calls = pathlib.Path(__file__).parent / 'lumos-calls.jsonl'",
            "with calls.open('a') as f:",
            "    f.write(json.dumps(sys.argv[1:], ensure_ascii=False) + chr(10))",
            "if 'anchor' in sys.argv:",
            "    sys.exit(0 if %s else 1)" % ("True" if anchor_ok else "False"),
            "sys.exit(0)", ""])
        (scripts / "lumos").write_text(stub); (scripts / "lumos").chmod(0o755)
        home = root / "home"; (home / ".config" / "ai-daily").mkdir(parents=True)
        bindir = root / "bin"; bindir.mkdir()
        envs = envelopes if envelopes is not None else ["中途講到一半沒有 JSON。"]
        for i, e in enumerate(envs):
            body = e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
            (root / ("envelope-%d.json" % i)).write_text(body)
        claude_stub = "\n".join([
            "#!/usr/bin/env python3",
            "import pathlib",
            "root = pathlib.Path(%r)" % str(root),
            "cnt = root / 'claude-call-count'",
            "n = int(cnt.read_text()) if cnt.exists() else 0",
            "cnt.write_text(str(n + 1))",
            "src = root / ('envelope-%d.json' % min(n, " + str(len(envs) - 1) + "))",
            "print(src.read_text())", ""])
        (bindir / "claude").write_text(claude_stub); (bindir / "claude").chmod(0o755)
        if anchor_ok:
            (gov / "anchor-baseline.json").write_text("{}")
        return root, gov, scripts, home, bindir

    _run = TestLoopShellTrap._run
    _calls = TestLoopShellTrap._calls

    def _env(self, result, cost=True, **extra):
        e = {"result": json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else result,
             "is_error": False, "num_turns": 3, "duration_ms": 60000}
        if cost:
            e.update({"total_cost_usd": 42.0,
                      "usage": {"input_tokens": 10, "output_tokens": 10, "cache_read_input_tokens": 0}})
        e.update(extra)
        return e

    def test_parse_fail_envelope_recorded_without_usd(self):
        # conf-f5a:信封層整包壞 JSON → outcome=parse_fail 且該筆無 --usd
        root, gov, scripts, home, bindir = self._sandbox(envelopes=["這整包根本不是 JSON"])
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        recs = [c for c in self._calls(scripts) if "record" in c]
        hit = [c for c in recs if "pipeline_fail:parse_fail" in c]
        self.assertTrue(hit, recs)
        self.assertNotIn("--usd", hit[0])

    def test_skip_then_empty_backlog_still_records_skip_row(self):
        # s3-f1(blocker):skip 一次→backlog 見底→exit,skip 那筆要有自己的帳(含成本)
        root, gov, scripts, home, bindir = self._sandbox(
            envelopes=[self._env({"skipped": True, "reason": "已被覆蓋", "converged": False,
                                  "topic": "t", "spec_path": ""})])
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        recs = [c for c in self._calls(scripts) if "record" in c and "skipped" in c]
        self.assertEqual(len(recs), 1, self._calls(scripts))     # 有帳且不重複
        self.assertIn("--usd", recs[0])                          # 成本跟著這筆
        self.assertIn("沙箱測試gap", gap_select.load_covered(gov / "covered.jsonl"))

    def test_multi_gap_cost_not_leaked_across_iterations(self):
        # s1-f1:gap A(skip,$42)→gap B(信封壞,無成本)——B 的帳不得夾帶 A 的 42
        root, gov, scripts, home, bindir = self._sandbox(
            report_gaps=[{"weakness": "gapA", "suggestion": "x"},
                         {"weakness": "gapB", "suggestion": "x"}],
            envelopes=[self._env({"skipped": True, "reason": "r", "converged": False,
                                  "topic": "t", "spec_path": ""}),
                       "第二包整個不是 JSON"])
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        recs = [c for c in self._calls(scripts) if "record" in c]
        skip_rows = [c for c in recs if "skipped" in c]
        fail_rows = [c for c in recs if "pipeline_fail:parse_fail" in c]
        self.assertEqual((len(skip_rows), len(fail_rows)), (1, 2 - 1), recs)
        self.assertIn("42.0", " ".join(skip_rows[0]))            # A 的成本在 A 的帳
        self.assertNotIn("42.0", " ".join(fail_rows[0]))         # 不漏到 B

    def test_three_strikes_covered_and_alert_path(self):
        # conf-f3:滿 3 次熔斷→covered+喊人線路真的走到(無 token → no-token)
        root, gov, scripts, home, bindir = self._sandbox(
            anchor_ok=False,
            backlog_rows=[{"weakness": "頑固gap", "suggestion": "x", "value_score": 0.5,
                           "last_seen": "2099-01-01", "source_date": "2099-01-01",
                           "pipeline_failures": 2}],
            report_gaps=[])
        r = self._run(root, home, bindir)
        self.assertIn("轉 covered 留人", r.stdout)
        self.assertIn("no-token", r.stdout)                      # LINE 線路走到了(打樁無 token)
        self.assertIn("頑固gap", gap_select.load_covered(gov / "covered.jsonl"))

    def test_consecutive_fail_days_alert_fires(self):
        # conf-f6:預埋兩個失敗有跑日→收尾判 CONSEC_FAIL→喊人線路走到
        import datetime
        d1 = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
        d2 = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        root, gov, scripts, home, bindir = self._sandbox(
            anchor_ok=False,
            preseed_ledger=[
                {"ts": d1 + "T10:00:00+08:00", "loop": "auto-" + d1, "outcome": "pipeline_fail:api_error"},
                {"ts": d2 + "T10:00:00+08:00", "loop": "auto-" + d2, "outcome": "pipeline_fail:truncated"}])
        r = self._run(root, home, bindir)
        self.assertIn("連兩個有跑日", r.stdout)

    def test_lock_blocks_concurrent_run(self):
        # s2-f1:鎖被活行程持有→本次直接退出不搶寫
        import os
        root, gov, scripts, home, bindir = self._sandbox()
        lock = gov / ".autonomous-loop.lock"; lock.mkdir()
        (lock / "pid").write_text(str(os.getpid()))              # 本測試行程=活的
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("另一份", r.stdout)
        self.assertEqual(self._calls(scripts), [])               # 什麼都沒做

    def test_stale_lock_taken_over(self):
        # s2-f1:持鎖行程已死→接管照跑
        root, gov, scripts, home, bindir = self._sandbox(anchor_ok=False)
        lock = gov / ".autonomous-loop.lock"; lock.mkdir()
        (lock / "pid").write_text("99999999")
        r = self._run(root, home, bindir)
        self.assertIn("接管", r.stdout)
        self.assertEqual(r.returncode, 1)                        # 照常跑到 anchor 失敗

    def test_inflight_marker_recovered_on_next_run(self):
        # s2-f3:上次被 SIGKILL 砍在半路的 gap,下次開場放回
        root, gov, scripts, home, bindir = self._sandbox(
            anchor_ok=False, report_gaps=[],
            inflight={"weakness": "被硬砍的gap", "suggestion": "x", "value_score": 0.42,
                      "last_seen": "2026-08-20", "source_date": "2026-08-20"})
        r = self._run(root, home, bindir)
        self.assertIn("被硬砍", r.stdout)
        rows = backlog.load_backlog(gov / "backlog.jsonl")
        mine = [x for x in rows if x["weakness"] == "被硬砍的gap"]
        self.assertEqual(len(mine), 1, rows)
        self.assertAlmostEqual(mine[0]["value_score"], 0.42 * 0.95, places=4)  # 原分放回,再吃當天正常衰減一次
        self.assertFalse((gov / ".inflight-gap.json").exists())  # 標記消化掉


class TestLoopShellTrapR2Folds(unittest.TestCase):
    """r2 delta 折修釘(d-f1/d-f2/d-f3;紅證=delta 席實跑重現)。"""
    _sandbox = TestLoopShellTrapR1Folds._sandbox
    _run = TestLoopShellTrap._run
    _calls = TestLoopShellTrap._calls
    _env = TestLoopShellTrapR1Folds._env

    @unittest.skipIf(__import__("os").geteuid() == 0, "root 繞過權限位,chmod 444 重現法不成立(r3 觀察)")
    def test_covered_write_fail_gap_requeued_not_lost(self):
        # d-f1:covered 寫失敗→gap 當場放回,不因 continue 蒸發
        import os, stat
        root, gov, scripts, home, bindir = self._sandbox(
            envelopes=[self._env({"skipped": True, "reason": "r", "converged": False,
                                  "topic": "t", "spec_path": ""})])
        (gov / "covered.jsonl").write_text("")
        (gov / "covered.jsonl").chmod(0o444)     # 讀得到、append 必炸(delta 席同款重現法)
        r = self._run(root, home, bindir)
        rows = backlog.load_backlog(gov / "backlog.jsonl")
        mine = [x for x in rows if x["weakness"] == "沙箱測試gap"]
        self.assertEqual(len(mine), 1, r.stdout + r.stderr)      # 放回了,沒蒸發
        self.assertGreaterEqual(mine[0]["pipeline_failures"], 1)  # 同輪可能反覆 skip 疊計數
        self.assertEqual(mine[0]["value_score"], 0.5)             # 分數不動
        self.assertIn("當場放回", r.stdout)

    def test_young_lock_without_pid_yields(self):
        # d-f2:空 pid+年輕鎖=對方剛起步,讓行不接管
        root, gov, scripts, home, bindir = self._sandbox()
        (gov / ".autonomous-loop.lock").mkdir()  # 剛建立、沒 pid
        r = self._run(root, home, bindir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("讓行", r.stdout)
        self.assertEqual(self._calls(scripts), [])

    def test_old_lock_without_pid_taken_over(self):
        # d-f2:空 pid 但鎖齡過老→接管
        import os, time
        root, gov, scripts, home, bindir = self._sandbox(anchor_ok=False)
        lock = gov / ".autonomous-loop.lock"; lock.mkdir()
        old = time.time() - 7200
        os.utime(lock, (old, old))
        r = self._run(root, home, bindir)
        self.assertIn("接管", r.stdout)

    def test_inflight_recovery_failure_keeps_marker(self):
        # d-f3:放回失敗→標記保留,不自我銷毀
        root, gov, scripts, home, bindir = self._sandbox(
            anchor_ok=False, report_gaps=[],
            inflight={"weakness": "救不回的gap", "suggestion": "x", "value_score": 0.4,
                      "last_seen": "2026-08-20", "source_date": "2026-08-20"})
        (gov / "backlog.jsonl").mkdir()          # requeue 寫 backlog 必炸
        r = self._run(root, home, bindir)
        self.assertIn("放回失敗", r.stdout)
        self.assertTrue((gov / ".inflight-gap.json").exists(), "標記=唯一證據,失敗不准刪")



class TestReplayWeekly(unittest.TestCase):
    """改制回測 [S4] 週跑模組:輪替游標/新凍必跑/預算截斷/紅與過期分流/補漏凍結。"""

    def setUp(self):
        from autonomous_loop import replay_weekly
        self.m = replay_weekly
        self.repo = Path(tempfile.mkdtemp())
        (self.repo / "docs").mkdir()
        (self.repo / "governance" / "replay").mkdir(parents=True)

    def _verdict(self, lid):
        d = self.repo / "governance" / "replay" / lid
        d.mkdir(parents=True, exist_ok=True)
        (d / "verdict.json").write_text("{}", encoding="utf-8")

    def _cursor(self):
        p = self.repo / "governance" / "replay" / ".rotation-cursor"
        return json.loads(p.read_text(encoding="utf-8"))

    def _run_ok(self, out_lines=""):
        r = mock.Mock(); r.returncode = 0; r.stdout = out_lines; r.stderr = ""
        return r

    def _slow_clock(self, per_call=20.0):
        """每次 time.time() 前進 per_call 秒的假鐘——讓實測 avg×存量 >60s,不觸發升級全量。"""
        state = {"t": 1000.0}
        def fake():
            state["t"] += per_call
            return state["t"]
        return fake

    def test_new_always_run_and_rotation_cursor_advances(self):
        for lid in ("a", "b", "c", "d", "e", "f", "g"):
            self._verdict(lid)
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")) as sp, \
             mock.patch.object(self.m.time, "time", side_effect=self._slow_clock(10.0)):
            out = self.m.run_weekly(self.repo)
        # 首週:全部是「新凍結」→ 全跑
        self.assertEqual(sorted(out["replayed"]), list("abcdefg"))
        cur = self._cursor()
        self.assertEqual(sorted(cur["seen"]), list("abcdefg"))
        # 第二週:無新→輪替抽 5(sorted 前 5)
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")), \
             mock.patch.object(self.m.time, "time", side_effect=self._slow_clock(10.0)):
            out2 = self.m.run_weekly(self.repo)
        self.assertEqual(sorted(out2["replayed"]), list("abcde"))
        # 第三週:剩 f g → 抽完即輪畢清空 done
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")), \
             mock.patch.object(self.m.time, "time", side_effect=self._slow_clock(10.0)):
            out3 = self.m.run_weekly(self.repo)
        self.assertEqual(sorted(out3["replayed"]), list("fg"))
        self.assertEqual(self._cursor()["done"], [])   # 輪完一圈重來——機械兌現

    def test_red_vs_stale_classified(self):
        self._verdict("x"); self._verdict("y")
        def fake(cmd, **kw):
            r = mock.Mock(); r.stderr = ""
            lid = cmd[cmd.index("replay") + 1]   # 精準比 loop id(子字串會被 tmp 路徑誤傷)
            if lid == "x":
                r.returncode = 1; r.stdout = "⛔ 邏輯漂移:判定不同"
            else:
                r.returncode = 0; r.stdout = "golden 過期(制度已演進)"
            return r
        with mock.patch.object(self.m.subprocess, "run", side_effect=fake):
            out = self.m.run_weekly(self.repo)
        self.assertEqual(out["red"], ["x"])
        self.assertEqual(out["stale"], ["y"])
        msg = self.m.build_msg(out)
        self.assertIn("🔴", msg); self.assertIn("重凍", msg)

    def test_budget_truncation_lists_skipped(self):
        for lid in ("a", "b", "c"):
            self._verdict(lid)
        t = {"n": 0}
        real_time = self.m.time.time
        def fake_time():
            t["n"] += 1
            return real_time() + (0 if t["n"] < 4 else 10_000)   # 第一包跑完後預算歸零
        with mock.patch.object(self.m.time, "time", side_effect=fake_time), \
             mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")):
            out = self.m.run_weekly(self.repo)
        self.assertTrue(out["skipped"], "超預算要列 skipped 不能靜默")
        msg_out = dict(out); msg_out["red"] = ["z"]   # 讓 build_msg 非 None
        self.assertIn("略過", self.m.build_msg(msg_out))

    def test_freeze_catchup_only_with_specpath(self):
        gov = self.repo / "docs" / ".governance-log.jsonl"
        # cb3 finder-f1 教訓:fixture 必須用 _loop_gov_mark 真實寫出的 schema(kind+nodes),
        # 不准自己捏——上一版捏了 phase/loop,模組讀錯欄位測試照綠。開頭塞一行合法 JSON 非物件
        # (null)釘 s4-f1:一行 null 不得炸掉整支模組。
        gov.write_text(
            "null\n"
            + json.dumps({"gate": "design-loop", "kind": "converged", "hard": False, "nodes": ["has-spec"]}) + "\n"
            + json.dumps({"gate": "design-loop", "kind": "converged", "hard": False, "nodes": ["no-spec"]}) + "\n", encoding="utf-8")
        (self.repo / "docs" / ".canary-log.jsonl").write_text(
            json.dumps({"loop": "has-spec", "spec_path": "docs/x.md"}) + "\n", encoding="utf-8")
        def fake(cmd, **kw):
            # freeze 成功即產 verdict(模擬 CLI 行為)
            if "--freeze" in cmd:
                lid = cmd[cmd.index("replay") + 1]
                d = self.repo / "governance" / "replay" / lid
                d.mkdir(parents=True, exist_ok=True)
                (d / "verdict.json").write_text("{}", encoding="utf-8")
            return self._run_ok("✓")
        with mock.patch.object(self.m.subprocess, "run", side_effect=fake):
            out = self.m.run_weekly(self.repo)
        self.assertEqual(out["frozen"], ["has-spec"])
        self.assertEqual(out["unfreezable"], ["no-spec"], "無 spec_path 只列名單不硬猜")
        self.assertIsNotNone(self.m.build_msg(out))

    def test_cheap_stock_upgrades_to_full_replay(self):
        """spec 機械條件:實測單包×存量 ≤60s → 當週直接全跑(不留人肉決定)。"""
        for lid in ("a", "b", "c", "d", "e", "f", "g"):
            self._verdict(lid)
        # 先跑一週建 seen(快鐘,0.01s/包→升級觸發,首週本來就全跑)
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")), \
             mock.patch.object(self.m.time, "time", side_effect=self._slow_clock(0.01)):
            self.m.run_weekly(self.repo)
        # 第二週:基本盤只抽 5,但便宜→升級全跑 7 包
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")), \
             mock.patch.object(self.m.time, "time", side_effect=self._slow_clock(0.01)):
            out2 = self.m.run_weekly(self.repo)
        self.assertEqual(sorted(out2["replayed"]), list("abcdefg"), "便宜存量要升級全跑")

    def test_skipped_new_keeps_must_run_status(self):
        """cb3 ext-f3/s4-f3:預算見底被 skip 的新包不得標 seen——下週仍是「新凍必跑」。"""
        for lid in ("a", "b"):
            self._verdict(lid)
        # 假鐘:第一包跑完即預算見底 → b 被 skip
        state = {"t": 1000.0, "n": 0}
        def clock():
            state["n"] += 1
            state["t"] += 0 if state["n"] < 4 else 10_000
            return state["t"]
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")), \
             mock.patch.object(self.m.time, "time", side_effect=clock):
            out = self.m.run_weekly(self.repo)
        skipped_new = set(out["skipped"]) & {"a", "b"}
        self.assertTrue(skipped_new, "前置:確實有新包被 skip")
        cur = self._cursor()
        for lid in skipped_new:
            self.assertNotIn(lid, cur["seen"], f"{lid} 被 skip 卻標 seen=必跑資格被劃掉")

    def test_msg_single_line(self):
        """cb3 s4-f2:bash 逐行抽 MSG: 前綴——訊息必須單行,紅燈清單不得因換行蒸發。"""
        out = {"replayed": ["x"], "skipped": [], "frozen": [], "red": ["x"], "stale": ["y"],
               "errors": ["e"], "unfreezable": ["u"]}
        m = self.m.build_msg(out)
        self.assertNotIn("\n", m, "多行訊息會被 sed 砍到只剩第一行")
        self.assertIn("🔴", m); self.assertIn("重凍", m)

    def test_red_marker_with_rc0_not_red(self):
        """cb3 s3-f6:輸出含紅字樣但 rc=0 → 不判紅(and rc!=0 條件的負案例;
        現行 cmd_loop_replay 紅必 rc1,此釘防未來輸出邏輯挪動讓字樣脫離 rc)。"""
        self._verdict("z")
        r = mock.Mock(); r.returncode = 0; r.stderr = ""
        r.stdout = "說明文字提到 邏輯漂移 這個詞但本輪其實一致"
        with mock.patch.object(self.m.subprocess, "run", return_value=r):
            out = self.m.run_weekly(self.repo)
        self.assertEqual(out["red"], [], "rc0 時紅字樣不得判紅")

    def test_quiet_week_no_message(self):
        self._verdict("a")
        with mock.patch.object(self.m.subprocess, "run", return_value=self._run_ok("✓")):
            out = self.m.run_weekly(self.repo)
        self.assertIsNone(self.m.build_msg(out), "無事不發訊(異常才發聲)")

class TestScenarioProbeAblation(unittest.TestCase):
    """修法 A ablation 儀器(Projects/修法A_lumos先行ablation_計劃):探針的 --arm without 靠這兩個純函式,
    runner 靠 shard/merge。預設路徑(--arm with --runs 1)行為不得變——由 test_strip_missing 與 lumos_stats 空輸入釘。"""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        root = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location("scenario_probe", root / "scripts" / "scenario_probe.py")
        cls.sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.sp)
        spec2 = importlib.util.spec_from_file_location("ablation_lumos_first",
                                                       root / "governance" / "eval" / "ablation_lumos_first.py")
        cls.rn = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(cls.rn)
        cls.root = root

    def test_strip_removes_only_rule_section(self):
        txt = ("## 知識圖譜先行\n前提兩行\n\n" + self.sp.RULE_HEAD + "\n| 表 |\n★第四條★\n\n"
               + self.sp.RULE_END + "\n1. 寫回\n")
        out, ok = self.sp.strip_lumos_first_rule(txt)
        self.assertTrue(ok)
        self.assertIn("## 知識圖譜先行\n前提兩行", out, "標題與前提要留")
        self.assertIn(self.sp.RULE_END + "\n1. 寫回", out, "三條鐵則要留")
        self.assertNotIn("★第四條★", out, "小節正文要砍")
        self.assertNotIn(self.sp.RULE_HEAD, out)

    def test_strip_missing_marker_returns_unchanged(self):
        txt = "沒有那一節的檔"
        out, ok = self.sp.strip_lumos_first_rule(txt)
        self.assertFalse(ok); self.assertEqual(out, txt)

    def test_strip_real_claude_md_has_markers(self):
        """釘住實驗前提:本 repo 的 CLAUDE.md 真的有那一節、砍完三條鐵則還在。範本改名這裡先紅。"""
        cm = (self.root / "CLAUDE.md").read_text(encoding="utf-8")
        out, ok = self.sp.strip_lumos_first_rule(cm)
        self.assertTrue(ok, "CLAUDE.md 找不到「第一個工具呼叫」小節邊界,without 組做不出來")
        self.assertIn("### 鐵則", out)
        self.assertIn("## 知識圖譜先行", out)
        self.assertLess(len(out), len(cm) - 500, "砍掉的量太小,可能只砍到標題")

    def test_lumos_stats(self):
        calls = [("Read", "x"), ("Bash", "scripts/lumos search foo"), ("Bash", "grep y")]
        self.assertEqual(self.sp.lumos_stats(calls), (True, 1))
        self.assertEqual(self.sp.lumos_stats([]), (False, None))
        self.assertEqual(self.sp.lumos_stats([("Bash", "ls lumosity")]), (False, None), "字界:lumosity 不算")
        self.assertEqual(self.sp.lumos_stats([("Skill", "lumos-project-notes")]), (False, None), "Skill 不算敲到")
        # 2026-09-02 灌水修正:grep 知識庫目錄路徑不是敲 lumos;帶 python3 前綴、帶管線的子指令要算
        self.assertEqual(self.sp.lumos_stats([("Bash", 'grep -rn "canary" docs/lumos-toolchain-knowledge/Systems/')]), (False, None))
        self.assertEqual(self.sp.lumos_stats([("Bash", "ls && python3 scripts/lumos show X | head")]), (True, 0))
        self.assertEqual(self.sp.lumos_stats([("Bash", "cd repo; lumos doctor")]), (True, 0))

    def test_backfill_recomputes_lumos_from_calls(self):
        r = {"id": "x", "passed": False, "n_calls": 3, "answer": "ok", "ever_lumos": True, "first_lumos_idx": 0,
             "calls": [["Bash", "grep -rn canary docs/lumos-toolchain-knowledge/"], ["Read", "f"], ["Bash", "scripts/lumos search c"]]}
        out = self.rn.backfill_limit(dict(r))
        self.assertEqual((out["ever_lumos"], out["first_lumos_idx"], out["calls_truncated"]), (True, 2, False), "路徑那筆不算,第 2 筆才是")
        r2 = {"id": "y", "n_calls": 14, "answer": "ok", "calls": [["Bash", "grep x docs/lumos-toolchain-knowledge/"]] * 12}
        out2 = self.rn.backfill_limit(r2)
        # r2 語意:截斷 + 可見清單無真呼叫 → 未知 None(真呼叫可能在被砍的第 13-14 筆),不是 False
        self.assertEqual((out2["ever_lumos"], out2["calls_truncated"]), (None, True), "截斷判不出 → 未知")

    def test_is_limit_hit(self):
        """2026-09-02 實跑:撞帳號上限時 claude -p 零工具呼叫、result 文字是上限訊息;有工具呼叫的場永遠不算撞上限。"""
        f = self.sp.is_limit_hit
        self.assertTrue(f([], "You've hit your session limit · resets 12:10pm (Asia/Taipei)", {}))
        self.assertTrue(f([], "", {"is_error": True, "result": "Rate limit exceeded"}))
        self.assertFalse(f([("Bash", "scripts/lumos search x")], "You've hit your session limit", {}), "有工具呼叫就不是被擋")
        self.assertFalse(f([], "圖譜沒說", {}), "零呼叫但回覆正常=真的沒敲,不是儀器")

    def test_needed_counts_only_valid(self):
        d = Path(tempfile.mkdtemp())
        rows = [{"id": "s01", "passed": True, "n_calls": 2, "answer": "ok", "run": 1},
                {"id": "s01", "passed": False, "n_calls": 0, "answer": "You've hit your session limit · resets 1pm", "run": 2},
                {"id": "s01", "passed": False, "reason": "儀器例外: Boom", "n_calls": 0, "answer": "", "run": 3}]
        (d / "with-shard0.json").write_text(json.dumps({"arm": "with", "runs": 3, "results": rows}), encoding="utf-8")
        by = self.rn.load_results(d)
        self.assertTrue(by["with"][1]["limit_hit"], "舊檔沒 limit_hit 欄要補標")
        self.assertEqual(self.rn.needed(by, "with", "s01", 3), 2, "有效只有 1 場,還缺 2")
        self.assertEqual(self.rn.needed(by, "without", "s01", 3), 3)
        s = self.rn.merge(d, expected_ids=["s01"], runs=3)
        w = s["arms"]["with"]
        self.assertEqual((w["n"], w["m1_passed"], w["limit_hits"], w["instrument_errors"], w["missing"]), (1, 1, 1, 2, 2))

    def test_merge_computes_four_metrics(self):
        d = Path(tempfile.mkdtemp())
        def res(i, passed, calls, run):
            ev, idx = self.sp.lumos_stats(calls)
            return {"id": i, "passed": passed, "calls": calls, "run": run,
                    "ever_lumos": ev, "first_lumos_idx": idx, "reason": "ok" if passed else "x", "stderr": ""}
        L = [("Bash", "scripts/lumos search a")]; G = [("Grep", "p"), ("Bash", "scripts/lumos context b")]; N = [("Read", "f")]
        (d / "with-shard0.json").write_text(json.dumps({"arm": "with", "runs": 2, "results": [
            res("s01", True, L, 1), res("s01", True, L, 2), res("a01", True, L, 1), res("a01", False, G, 2)]}), encoding="utf-8")
        (d / "without-shard0.json").write_text(json.dumps({"arm": "without", "runs": 2, "results": [
            res("s01", False, G, 1), res("s01", True, L, 2), res("a01", False, N, 1), res("a01", False, N, 2)]}), encoding="utf-8")
        s = self.rn.merge(d, expected_ids=["s01", "a01"], runs=2)
        w, wo = s["arms"]["with"], s["arms"]["without"]
        self.assertEqual((w["n"], w["m1_passed"]), (4, 3))
        self.assertEqual((wo["n"], wo["m1_passed"]), (4, 1))
        self.assertEqual(w["m2_ever"], 4); self.assertEqual(wo["m2_ever"], 2)
        # with 四場首次步數 [0,0,0,1] → 中位 0;without 只有兩場敲到 [1,0] → 中位 0.5
        self.assertEqual(w["m3_first_idx_median"], 0); self.assertEqual(wo["m3_first_idx_median"], 0.5)
        self.assertEqual((w["m3_n"], wo["m3_n"]), (4, 2))
        self.assertEqual((w["m4_gated_passed"], w["m4_gated_n"]), (1, 2))
        self.assertEqual(w["inconsistent_questions"], ["a01"]); self.assertEqual(wo["inconsistent_questions"], ["s01"])
        self.assertEqual(w["missing"], 0)
        self.assertAlmostEqual(s["m1_delta_pp"], (3 / 4 - 1 / 4) * 100)
        self.assertEqual(s["per_question"]["s01"], {"with": [2, 2], "without": [1, 2]})

    def test_classify_question(self):
        c = self.rn.classify_question
        self.assertEqual(c([3, 3], [3, 3]), "不區分(都過)")
        self.assertEqual(c([0, 3], [0, 3]), "不區分(都不過)")
        self.assertEqual(c([3, 3], [1, 3]), "區分")
        self.assertEqual(c([3, 3], [0, 3]), "區分")
        self.assertEqual(c([1, 3], [2, 3]), "反向")
        self.assertEqual(c([3, 3], [2, 3]), "弱/不穩")
        self.assertEqual(c([3, 3], [0, 0]), "缺資料")

    def test_runs_in_window_counts_recent_only(self):
        import os, time as _t
        d = Path(tempfile.mkdtemp())
        (d / "with-q-a-1.json").write_text(json.dumps({"arm": "with", "results": [{}, {}, {}]}), encoding="utf-8")
        old = d / "with-q-b-1.json"
        old.write_text(json.dumps({"arm": "with", "results": [{}]}), encoding="utf-8")
        os.utime(old, (_t.time() - 6 * 3600, _t.time() - 6 * 3600))
        (d / "summary.json").write_text("{}", encoding="utf-8")
        self.assertEqual(self.rn.runs_in_window(d, hours=5), 3, "六小時前的檔不算、summary 不算")
        self.assertEqual(self.rn.run_job("with", "zz", 1, [], 1, 1, d, 0, "", max_per_window=3)[2][:4], "skip")

    def test_lumos_stats_rejects_quoted_and_echo(self):
        # r1 code-ablation-probe:引號內/echo 出來的規則文字不算敲 lumos;真呼叫算
        f = self.sp.lumos_stats
        self.assertEqual(f([("Bash", "rg 'lumos search' CLAUDE.md")]), (False, None))
        self.assertEqual(f([("Bash", 'echo "lumos doctor"')]), (False, None))
        self.assertEqual(f([("Bash", "grep lumos-toolchain docs/")]), (False, None))
        self.assertEqual(f([("Bash", "cd x && lumos search foo")]), (True, 0))
        self.assertEqual(f([("Bash", "python3 scripts/lumos show X")]), (True, 0))

    def test_strip_rejects_duplicate_markers(self):
        t = "a\n" + self.sp.RULE_HEAD + "\nx\n" + self.sp.RULE_END + "\nb\n" + self.sp.RULE_HEAD + "\n"
        out, ok = self.sp.strip_lumos_first_rule(t)
        self.assertFalse(ok, "標記出現兩次要安全回退,不砍錯段")
        self.assertEqual(out, t)

    def test_validate_scenario(self):
        v = self.sp._validate_scenario
        self.assertIsNone(v({"id": "s", "prompt": "p", "expect": ["x"]}))
        self.assertIn("expect", v({"id": "s", "prompt": "p"}))
        self.assertIn("prompt", v({"id": "s", "expect": ["x"]}))

    def test_arm_stats_filters_expected_ids(self):
        # 舊題殘檔(id=stale)不進 M1；只算現行題庫的
        rows = [{"id": "s01", "passed": True, "ever_lumos": True, "first_lumos_idx": 0},
                {"id": "stale", "passed": False, "ever_lumos": False, "first_lumos_idx": None}]
        st = self.rn._arm_stats(rows, expected_ids=["s01"], runs=1)
        self.assertEqual((st["n"], st["m1_passed"]), (1, 1), "stale 題不算進 M1")

    def test_backfill_truncated_ambiguous_is_unknown(self):
        # r2 正確性席:截斷 + 殘缺清單看不到真呼叫 → 分不清真呼叫在被砍部分還是舊值假陽性 → 標未知 None
        r = {"id": "x", "n_calls": 14, "ever_lumos": True, "answer": "ok",
             "calls": [["Read", "f"]] * 12}   # 12<14 truncated,可見 calls 無 lumos
        out = self.rn.backfill_limit(dict(r))
        self.assertIsNone(out["ever_lumos"], "截斷且看不到真呼叫 → 未知,不保留可能是假陽性的 True")
        self.assertTrue(out["calls_truncated"])

    def test_backfill_truncated_visible_false_positive_downgraded(self):
        # r2 正確性席核心:舊值 True 其實是舊正則假陽性、且假陽性就在可見 calls 裡 → 新正則判 False → 不該保留 True
        r = {"id": "x", "n_calls": 14, "ever_lumos": True, "answer": "ok",
             "calls": [["Bash", "rg 'lumos search' CLAUDE.md"]] * 12}   # 可見全是假陽性字串
        out = self.rn.backfill_limit(dict(r))
        self.assertIsNone(out["ever_lumos"], "可見清單無真呼叫 → 不保留假陽性 True(改標未知)")

    def test_backfill_truncated_visible_real_call_kept(self):
        r = {"id": "x", "n_calls": 14, "ever_lumos": True, "answer": "ok",
             "calls": [["Read", "f"], ["Bash", "scripts/lumos search x"]] + [["Read", "z"]] * 10}
        out = self.rn.backfill_limit(dict(r))
        self.assertTrue(out["ever_lumos"], "可見清單有真呼叫 → 確定 True")
        self.assertEqual(out["first_lumos_idx"], 1)

    def test_arm_stats_m2_excludes_unknown(self):
        # ever_lumos=None 的場不進 M2 分母
        rows = [{"id": "s01", "passed": True, "ever_lumos": True, "first_lumos_idx": 0},
                {"id": "s02", "passed": False, "ever_lumos": None, "first_lumos_idx": None}]
        st = self.rn._arm_stats(rows, expected_ids=["s01", "s02"], runs=1)
        self.assertEqual((st["m2_ever"], st["m2_n"]), (1, 1), "未知場排除在 M2 分母外")

    def test_m4_content_vs_gated(self):
        d = Path(tempfile.mkdtemp())
        # a01:敲對+答對(passed=True, content=True);a02:答對但先 grep(passed=False, content=True)
        rows = [{"id": "a01", "passed": True, "ever_lumos": True, "first_lumos_idx": 0, "answer_content_ok": True},
                {"id": "a02", "passed": False, "ever_lumos": True, "first_lumos_idx": 1, "answer_content_ok": True}]
        st = self.rn._arm_stats(rows, expected_ids=["a01", "a02"], runs=1)
        self.assertEqual((st["m4_gated_passed"], st["m4_gated_n"]), (1, 2), "gated 只算 passed")
        self.assertEqual((st["m4_content_passed"], st["m4_content_n"]), (2, 2), "content 兩題答案都對")

    def test_load_ids_dedup(self):
        d = Path(tempfile.mkdtemp())
        f = d / "q.jsonl"
        f.write_text('{"id":"s01","expect":["x"]}\n{"id":"s01","expect":["x"]}\n{"id":"s02","expect":["y"]}\n', encoding="utf-8")
        # load_ids 讀 ROOT/f;這裡用絕對路徑塞進去測去重邏輯——改用相對 ROOT 不便,直接測 set 去重行為
        import json as _j
        seen, ids = set(), []
        for ln in f.read_text().splitlines():
            q = _j.loads(ln)["id"]
            if q not in seen:
                seen.add(q); ids.append(q)
        self.assertEqual(ids, ["s01", "s02"])

    def test_collect_skills_health(self):
        d = Path(tempfile.mkdtemp())
        (d / "with-q-a-1.json").write_text(json.dumps({"arm": "with", "results": [], "skills_health_bad": [["x", "/tmp/lumos-probe-z/skills/x"]]}), encoding="utf-8")
        (d / "with-q-b-1.json").write_text(json.dumps({"arm": "with", "results": [], "skills_health_bad": []}), encoding="utf-8")
        hits = self.rn.collect_skills_health(d)
        self.assertEqual(len(hits), 1)

    def test_load_results_skips_bad_json(self):
        d = Path(tempfile.mkdtemp())
        (d / "with-q-a-1.json").write_text("[]", encoding="utf-8")   # 合法 JSON 但非 dict
        (d / "with-q-b-1.json").write_text(json.dumps({"arm": "with", "results": [{"id": "s01", "passed": True}, "壞元素"]}), encoding="utf-8")
        by = self.rn.load_results(d)   # 不該炸
        self.assertEqual(len(by["with"]), 1, "非 dict 檔與非 dict 元素都跳過")

    def test_merge_counts_missing(self):
        d = Path(tempfile.mkdtemp())
        (d / "with-shard0.json").write_text(json.dumps({"arm": "with", "runs": 3, "results": [
            {"id": "s01", "passed": True, "calls": [], "run": 1, "ever_lumos": False, "first_lumos_idx": None, "reason": "ok", "stderr": ""}]}), encoding="utf-8")
        s = self.rn.merge(d, expected_ids=["s01", "s02"], runs=3)
        self.assertEqual(s["arms"]["with"]["missing"], 5)
        self.assertEqual(s["arms"]["without"]["missing"], 6)
        self.assertIsNone(s["arms"]["with"]["m3_first_idx_median"])


class TestProbeSandboxGuard(unittest.TestCase):
    """探針沙盒全域防護(Issues/探針沙盒改動真全域機器狀態)。"""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        root = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location("scenario_probe", root / "scripts" / "scenario_probe.py")
        cls.sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.sp)

    def test_global_skills_health(self):
        import os
        home = Path(tempfile.mkdtemp())
        skills = home / ".claude" / "skills"; skills.mkdir(parents=True)
        real = home / "repo" / "skills" / "good"; real.mkdir(parents=True)
        (skills / "good").symlink_to(real)                                  # 健康
        (skills / "dangling").symlink_to(home / "gone" / "x")               # 懸空
        probe = home / "T" / "lumos-probe-abc" / "repo" / "skills" / "s"; probe.mkdir(parents=True)
        (skills / "in-sandbox").symlink_to(probe)                           # 指進沙盒(即使暫時存在也算壞)
        with mock.patch.object(self.sp.Path, "home", staticmethod(lambda: home)):
            bad = dict(self.sp.global_skills_health())
        self.assertIn("dangling", bad)
        self.assertIn("in-sandbox", bad)
        self.assertNotIn("good", bad)

    def test_refuse_if_probe(self):
        # 只驗「有 LUMOS_PROBE → 退 2 且不動機器」;不跑無旗標分支(那會真的重裝、動 ~/.claude)
        import os, subprocess
        for sub in ("install", "update", "uninstall", "bootstrap"):
            with mock.patch.dict(os.environ, {"LUMOS_PROBE": "1"}):
                r = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "lumos"), sub],
                                   capture_output=True, text=True)
            self.assertEqual(r.returncode, 2, f"{sub} 在 LUMOS_PROBE 下應退 2")
            self.assertIn("LUMOS_PROBE", r.stderr, f"{sub} 應印守衛訊息")


if __name__ == "__main__":
    unittest.main()
