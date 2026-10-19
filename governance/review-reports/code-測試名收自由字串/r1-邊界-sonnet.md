severity: major

先講白話:這次改動讓「測試名」可以寫成整句話。名稱篩選是子字串比對,所以「事前撞名檢查」成了唯一擋住「名字被別的測試包含」的防線。我對邊界輸入的實測發現,這道檢查有兩個盲區,會讓被跳過的測試被判成綠。其餘極端輸入我都跑過,沒有問題。

## Findings

1. 撞名檢查看不到「被掃描器丟掉的標題」,被跳過的綁定測試會判綠
severity: major
   - blocking: 是
   - diff 段落:`_name_filter_collisions`、`_run_bound_tests`(檢查用 `discover_test_methods` 的結果),以及 `discover_test_methods` 裡的 `if nm is None or (titled and not _test_name_ok(nm)): continue`。
   - 問題:撞名比對的集合是 `discover_test_methods` 的輸出,而它已經把過不了 `_test_name_ok` 或 `_test_name_of_match` 的標題丟掉了。被丟掉的包括:
     - 含半形逗號或方括號的標題
     - 含 `\n`、`\u` 等不認得的跳脫的標題
     - 超過 200 字的標題
     - 帶 `${}` 的樣板字串標題
     - Dart 帶 `$x` 插值的標題

     這些測試真的存在,Jest 和 Vitest 的 `-t`、Playwright 的 `-g` 也選得到它們,但撞名檢查完全看不見。
   - 具體例:
     - 輸入:`a.test.js` 內容是 `it.skip('login', ...)`、`it('login, then logout', ...)`、`it('wait [3s] login', ...)`,合約綁 `[test:login]`。
     - 預期:撞名檢查回報會同時選中 3 支,結果記為 unproven。
     - 實際:`discover_test_methods` 只回 `{'login'}`,`_name_filter_collisions('login', …, 'regex')` 回 `[]`。
     - 真跑 `jest --rootDir . -t login` 輸出 `Tests: 1 skipped, 2 passed, 3 total`。
     - Node 的跑過證據正規式 `Tests:.*?[1-9]\d*\s+passed` 吃到「2 passed」,綁定的那支其實被跳過,卻判成綠。
   - 最小重現:在暫存目錄建上面那個 `a.test.js` 和 `jest.config.json`,執行 `python3.14 -c` 載入 `scripts/lumos` 後呼叫 `m._name_filter_collisions("login", m.discover_test_methods(Path("."), m.TEST_PROFILES["node-jest"]), "regex")`,印出 `[]`。再執行 `jest --rootDir . -t login`,印出上面那行 Tests。
   - 引句:「hit = _name_filter_collisions(method, coll_cache[plat], nf)」

2. Playwright 的 `-g` 還會比對檔名、專案名和 describe 路徑,撞名檢查只比標題
severity: major
   - blocking: 是
   - diff 段落:同上 `_name_filter_collisions`,以及 `_RAN_EVIDENCE["playwright"]`(`\b[1-9]\d*\s+passed\b`)。
   - 問題:`-g` 的比對對象是「專案名 › 檔案路徑 › describe › 標題」整串,不是只有標題。標題剛好是檔名或專案名的一部分時,整個檔案或整個專案的測試都會被選中。撞名檢查沒有納入這些,只比標題。
   - 具體例:
     - 輸入:`tests/login.spec.ts` 裡有 `test.skip('login', …)` 和 `test('logout works', …)`,合約綁 `[test:login]`。
     - 預期:unproven。
     - 實際:`_name_filter_collisions('login', {'login','logout works'}, 'regex')` 回 `[]`。
     - 真跑 `playwright test -g login`(1.64.1)輸出 `1 skipped` 和 `1 passed`,證據正規式命中,判綠。
     - 另外實測 `-g spec.ts` 和 `-g chromium` 各選中 6 支,也就是整個專案的測試。
   - 最小重現:在暫存目錄裝 `@playwright/test@1.64.1`,放上述 spec 檔,執行 `./node_modules/.bin/playwright test -g login`。
   - 引句:「name_filter=regex:跑單支用 -g,名字要跳脫(_run_cmd_expand)」

3. `guard kill` 沒有撞名檢查,歸因只做子字串比對
severity: minor
(未能重現)
   - blocking: 否
   - 問題:`cmd_guard_kill` 用 `_run_cmd_expand(run_cmd, method, name_filter=…)` 跑 `-t` / `-g`,沒有走 `_name_filter_collisions`。`_kill_attribute` 用 `line.find(method)` 找失敗行。
   - 具體例:綁 `login`,另有 `login fails when x` 也被壞法打紅,它的失敗行含 `login`,可能被當成強殺(killed)。
   - 缺口:我沒有搭出完整的 kill 環境,所以降為 minor。
   - 引句:「cmd = _run_cmd_expand(run_cmd, method, name_filter=pentry["profile"].get("name_filter", "ident"))」

4. 驗收條款裡標題含行內反引號,會被規格閘吃掉一段
severity: minor
   - blocking: 否
   - 問題:`_spec_gate_items` 和 `_spec_gate_prepare` 現在先過 `_strip_inline_markup`,反引號包住的字會被刪掉。
   - 具體例:
     - 輸入:`- [S1] … [test:uses \`foo\` flag works]`,測試檔裡有同名標題。
     - 預期:bound。
     - 實際:`clause_bindings` 回 dangling,refs 是 `'uses  flag works'`(兩個空白)。
     - `[test:\`kotlin name\`]` 則回 untagged。
   - 影響:含 `<Foo>`、`` `x` `` 這類 markdown 寫法的標題,沒辦法照字面寫成會紅的條款,只能改標題或改用 `[manual:]`。
   - 引句:「items += [(b["id"], plat, method, "real") for plat, method in resolve_test_refs(_strip_inline_markup(seg)[0], split, default)]」

5. Playwright 的 `test.skip('原因')`、`test.fixme('原因')` 被當成測試宣告
severity: minor
   - blocking: 否
   - 問題:測試本體裡的執行期標註 `test.skip('flaky on webkit')` 通過了「字面後面緊接 `)`」的條件,被掃成名為 `flaky on webkit` 的真測試。
   - 實測:`scan` 對 `test('real', …{ test.skip('flaky on webkit'); test.fixme('later'); })` 回 `['real','flaky on webkit','later']`。
   - 後果:綁這個名字會顯示 real,真跑時 Playwright 回 No tests found,變成語意不明的紅。
   - 引句:「PLAYWRIGHT_TEST_RE = re.compile(_TITLE_CALL_HEAD + r"test(?:\.describe(?:\.(?:serial|parallel|only|skip))?|\.(?:only|skip|fixme|fail))?\(\s*"」

## 無問題項(實測)

以下三項實測後沒有發現會出錯的輸入:

- **掃描與剝註解**:
  - 標題含 `//`(網址)、`/*`、`*/`,都保留且不吞掉後面的測試。
  - 未閉合的 `'` 只影響該行。
  - 樣板字串的 `${x}` 不收,`\${x}` 還原成 `${x}`,Dart 的 `\$5` 還原成 `$5`,`$x` 不收。
  - `\'`、`\"`、`\\` 都正確還原。
  - `'a'+'b'` 和 `'a'.repeat(3)` 不收。
  - 純空白標題被丟掉。
- **名稱長度與效能**:
  - 200 字(含 200 個中文字)收,201 字不收。
  - 效能壓力輸入全在 0.4 秒內。這些輸入包括 200 萬個 `'`、100 萬個反引號、50 萬個 `/*`、20 萬個密集的 `it('`、Dart 的 `$` 洪水。
- **跳脫與 shell 引號**:
  - 以 Jest 29.7 和 Playwright 1.64.1 真跑 `_name_filter_escape` 加 `shlex.quote`。
  - 含 `$5.00 (net)`、`a|b`、`/slashy/`、`*`、引號、反斜線、中文、`${b}` 的名字,都精確選中 1 支。
  - `/…/` 當正規式的路徑已被 `\/` 躲掉。

## 圖譜鏡頭

- `lumos-cli-read`、`guard-kill`、`lifecycle`、`授權與歸屬`、`design-loop` 的合約:這份 diff 不碰它們宣稱的行為,判不影響。
- `bound-tests-gate`:它宣稱「閘逐支真跑,證不出跑過就擋」。發現 1 和 2 讓這個承諾在 JS 三家上有洞:被跳過的綁定測試可以靠別支測試的 passed 被判綠。
- `測試假綠形態`:發現 1 和 2 屬於它描述的假綠類型,而且沒有前置斷言證明「被測那支真的跑到」。

最嚴重 severity: major,blocking 共 2 條(發現 1、發現 2)。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/governance/review-reports/code-測試名收自由字串/r1-lumos.patch`

臨時目錄已用字面路徑刪除。
