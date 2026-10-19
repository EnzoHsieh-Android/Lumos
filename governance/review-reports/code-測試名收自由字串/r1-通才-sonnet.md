severity: major

我只審 tests.patch。主程式 patch 只在追呼叫者時查。我在工作樹副本上做了故障變體。新增的 28 支測試本身全綠。圖譜固定席沒看出被破壞的合約:`bound-tests-gate` 的「證不出跑過就擋」被新的撞名判定沿用,`guard-kill` 的 rc 與 `--json` 沒動到。

## Findings

**1. 撞名檢查看不見被丟掉的標題,同一個 `-t` 篩選仍會選中它們**
severity: major
blocking: 是
- diff 位置:`t_name_filter_collision_not_green`,對應主程式 `_run_bound_tests` 的 `coll_cache[plat] = discover_test_methods(...)`。
- 問題:撞名比對的集合是 `discover_test_methods` 的結果。這個集合已經把含半形逗號或方括號的標題、`.each` 排除了。但 Jest/Playwright 的 `-t`/`-g` 是子字串比對,照樣會選中被排除的標題。測試只用能被收進集合的標題當撞名對象,這個洞沒被測到。
- 重現:node-jest,檔內有 `it('登入')`、`it('登入, 之後登出')`、`it.each([1])('登入 %s')`,run_cmd 輸出「Tests: 1 passed, 1 total」。
  - 輸入:`_run_bound_tests(root, [("S1","node-jest","登入","real")])`。
  - 預期:`unproven`(撞名)。
  - 實際:`('S1','node-jest','登入','green','',0.007)`。`discover_test_methods` 只回 `{'登入'}`。
  - 後果:被綁的「登入」若被 skip、同篩選選中的另一支是綠的,摘要「N passed」會讓它判綠。這正是這個撞名檢查要擋的情況。
- 引句:「_fs_write(root, "src/a.test.ts", "it('登入', () => {})\nit('登入後 看得到訂單', () => {})\nit('Login', () => {})\nit('login', () => {})\nit('結帳', () => {})\n")」

**2. 新增的 `_RAN_EVIDENCE` 兩條(node-vitest、playwright)沒有任何測試**
severity: major
blocking: 是
- 問題:新測試的 run_cmd 一律是 `false {method}`,或只驗到「red」,「跑過的證據」正規式從沒被走到。
- 重現:把兩條 `re` 都改成 `NEVERMATCH`,用 `-k ran`、跑 176 支,全綠(`K_vitest_re`、`K2_pw_re`)。
- 後果:這兩條正規式壞了(或過寬),所有 Vitest/Playwright 綁定不是全擋就是全放。這是守衛類的唯一驗證,而且是這次新增的行為。
- 引句:「check("④沒撞名的照常真跑(這支指令會失敗 → 紅)", res2 and res2[0][3] == "red", repr(res2))」

**3. `t_playwright_profile_discover` 的斷言變成空轉**
severity: minor
blocking: 否
- 原本它守「多字 title 收不進來」。現在 `[test:should]` 只是前半,舊的識別字正規式也不會綁到它。
- 重現:把 `PLAYWRIGHT_TEST_RE` 還原成舊的識別字版,這支仍 2 passed。同一個故障只有 `t_playwright_free_string_names_discovered` ①會紅,所以整體仍抓得到。
- 但這支的斷言名稱「多字 title 未被收成 real」已經不是它在驗的事。
- 引句:「check("playwright: 多字 title 未被收成 real(真綁不為 2)",」

**4. 改動多處測試期望,但邊界的故障變體沒有任何測試紅**
severity: minor
blocking: 否
我做了三個故障變體,都 0 條紅:
- 拿掉 `_unwrap_backticks` 的 `s.count("`") == 2`。輸入「`a` and `b`」會被錯誤拆殼成 `a` and `b`。
- 拿掉 `_split_test_ref` 的 `m.group(2) == ":"`。輸入 `[test:wbe：x]`(拉丁字母加全形冒號)在多平台會誤報 ValueError。
- 拿掉 `_dispositions_split_test` 的 `body[m.end() - 1] == ":"`。
`⑧` 只測了中文前綴,碰不到這兩個分支。
- 引句:「check("⑧全形冒號、前面不是平台 → 整串歸預設平台", m.resolve_test_refs("[test:說明：甲]", P, "web") == [("web", "說明：甲")], "")」

**5. Dart 取代舊測試時漏掉 scaffold 檔名錨的斷言**
severity: minor
blocking: 否
- 舊的 `fnmatch(scaffold_name…, file_name_match)` 沒搬到新測試。
- node 和 swift 測試有這項,dart 現在沒有。
- 重現:把 dart 的 `scaffold_name` 從 `{m}_test` 改成 `{m}`,`-k dart` 和 `-k scaffold` 都不紅。
- 補充:舊那支本來就被同名函式蓋掉、從沒跑過,所以不是回歸,但說明裡寫「內容搬到」不實。
- 引句:「內容搬到 t_dart_profile_discovery_titles」

**6. 文件字串宣稱的故障變體和實際不符**
severity: minor
blocking: 否
- `t_js_free_string_test_names_discovered` 寫「.each/樣板排除拿掉 → ②紅」。
- `it.each(...)` 在正規式修飾詞清單裡根本沒有,本來就收不進來,沒有可拿掉的排除碼。
- ②對 `.each` 這半邊是結構性必過,只有樣板那半有效。
- 引句:「應抓到的錯:擷取群組退回識別字 → ①紅;名稱規則過濾拿掉 → ③紅;.each/樣板排除拿掉 → ②紅。」

**7. 逐條列出懸空的上限 15 行沒有測試**
severity: minor
blocking: 否
- 把 `_CLAUSE_HANG_SHOW` 改成 1000,`-k clause`、129 支全綠。
- `t_clause_check_marks_hanging` 只用 1 條懸空,「…另有 N 條」那行從沒被走到。
- 引句:「check(f"②[{tag}] 逐條列出懸空的編號與名稱", "S1(第 1 行)不存在的 測試" in out and "S2(" not in out, out)」

**8. `_kill_method_name` 留了沒人呼叫的布林相容路徑,前綴行為也變了**
severity: minor
blocking: 否
- 所有呼叫者都改傳 `pdata`。docstring 寫「舊呼叫端的 multiplatform 布林」,但傳 True 現在不剝前綴,和舊行為相反,也沒有測試,是死碼。
- 行為變更:配方 `test` 寫 `android:Foo` 而 `android` 未定義時,舊版會剝掉前綴,新版整串 `android:Foo` 照跑。測試沒有覆蓋這種輸入。
- 引句:「pdata 可以是 load_platforms 的結果,或舊呼叫端的 multiplatform 布林(True 時沒有平台表,只拆反引號)。」

**9. 清理類:順手刪掉的說明註解**
severity: minor
blocking: 否
- 這次改動在刪 dart 舊測試時,同一 hunk 把 `t_swift_profile_discovery` 前面的標題註解一起刪了。它標明「尚無真專案,只有合成樣本」,是這批 swift/node 測試的可信度聲明。
- 引句:「# ── iOS/Node 補棧(2026-09-08,Projects/iOS與Node後端補棧_計劃;★尚無真專案,只有這裡的合成樣本★)──」

## 已查過、判不影響的項目
- `_ns_wd_binding_norm`:把它換成原樣傳回,`-k wording`/`-k binding` 各 2 條紅,有被測到。
- `_TITLE_CALL_HEAD`、`_test_name_ok` 的長度上限、`_name_filter_collisions` 的大小寫:各有測試翻紅。
- 效能:`t_js_comment_strip_linear` 的剝註解 8000 行是線性。新測試最慢 3.2 秒。

最嚴重:major,blocking 共 2 條(#1、#2)。

我的臨時目錄 `/tmp/lumos-seat-work/code-測試名收自由字串/通才-sonnet/`(含 scripts 副本與 `r/` 內的 `gctl-fscoll-*`)留給編排者收貨後刪除。
