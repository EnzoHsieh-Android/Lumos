severity: minor

沒有 blocking 發現。修後 `2e62dcdb` 的 `scripts` 與 web-gaps 現行 HEAD 沒有差異,所以我直接在 web-gaps 跑。

**1. Jest、Vitest、Flutter 的標題頭尾有空白,現在被丟掉,綁定會變懸空**
severity: minor
- blocking: 否
- 歸因:有證據的修復回歸
- 位置:`_test_name_of_match` 新增的空白判斷。它對所有字串標題型都生效,但理由只講 Playwright 不修剪標題。Jest 的 `-t` 是子字串比對,`' lead'` 其實綁得到。
- 具體例:`src/a.test.ts` 內容是 `it(' lead', () => {})` 加 `it('ok', () => {})`。
  - 修前 `discover_test_methods` 回 `{'lead','ok'}`。
  - 修後回 `{'ok'}`。
  - 原本綁 `lead` 的 Jest 專案,推送前會變成懸空。
- 判準:修前取自 `5f8f8e48:scripts/lumos`,修後取自現行版本,用同一支探針各跑一次。
- 引句:「if unescape and name != name.strip():」

**2. 名稱本身以 @tag 結尾時,撞名判斷會漏**
severity: minor
- blocking: 否
- 歸因:有證據的修復回歸。r3 新加的 `_PW_TAG_TAIL_RE.sub` 是起因;修前沒有 tag 處理,所以這是新引入的不一致。
- 具體例:綁定名 `login @smoke`,另有一支標題 `login @smoke @slow`。
  - 實際執行的 `-g` 規則 `\slogin @smoke(?:\s@\S+)*$` 會選中兩支。
  - 我用 `re.search` 對 `chromium a.spec.ts login @smoke @slow` 試過,結果是 True。
  - `_name_filter_collisions("login @smoke",[("test","login @smoke"),("test","login @smoke @slow")],"regex_tail")` 卻回 `[]`,因為被比對的標題尾巴先被剝掉了。
- 引句:「cmp = _PW_TAG_TAIL_RE.sub("", cmp)」

**3. `t_playwright_tail_tags_and_own` 沒有拿正規式實際比對標題**
severity: minor
- blocking: 否
- 歸因:未判定
- 這條測試的 ① 只比對展開後的字串是否逐字相等。⑤ 的 fixture 是 `echo ... {method}`,不會用 `-g`。所以「`\sX(?:\s@\S+)*$` 選得到帶 tag 的標題、選不到 `relogin`」這件事,沒有任何斷言直接驗證。對照「實作測試品質」第 3 點:字串相等不能單獨當功能正確的證明。
- 不過,把正規式改成別的寫法,① 一定會紅,所以不會靜默放行。
- 引句:「== "npx playwright test -g '\\sa \\(b\\) login(?:\\s@\\S+)*$'",」

**被重新驗證的主張**

- **新增與改動的 11 支測試**:在 web-gaps HEAD 逐支跑,全過。包含 playwright_tail_tags_and_own、name_collision_describe_plus_test、titled_names_with_edge_spaces、comment_strip_multiline、guard_kill_collision_cli、guard_settle_name_checks、bind_name_problem_pass、clause_visible_linear、anchor_hint_scans_once、test_name_rule_text、comment_strip_big_string。
- **相鄰子集**:kill_recipe、bind、collision、comment_strip、playwright、anchor、settle、test_name、guard_kill 九組,沒有紅的。
- **故障變體(在副本上改,不碰 repo)**

| 故障 | 結果 |
|---|---|
| `_C_STRIP_RE` 單引號改回群組加星號的寫法 | `t_comment_strip_big_string_memory` 紅。macOS 與 Linux 的 `ru_maxrss` 單位已換算,Windows 會跳過。 |
| `cmd_guard_kill` 的撞名判斷改成 `None` | `t_guard_kill_collision_cli` 紅。這條測試實跑 CLI 並檢查「撞名」原因,不是只看原始碼有沒有呼叫。 |
| `guard settle` 拿掉共用名稱檢查 | `t_guard_settle_name_checks_cli` 的 ①② 兩條都紅。 |
| `lumos` 換回修前版 | `t_clause_visible_linear` 的 ① 紅(4.35 秒),但「反引號」那組在舊版也過。所以抓平方級的只有「沒收尾」那組。 |

- **`_clause_visible` 改寫**:修前和修後各跑一次,拿 504 個條款行比對(單一 `[test:]` 欄位,搭配反引號、未閉合、`[manual:]` 等組合),只有 18 條不同,全是「前一個 `[test:` 沒收尾、後面又接一個欄位」的壞格式。完整的單欄位行看得見的文字相同。4 萬字的壞輸入約 0.6 到 7 毫秒。
- **`_C_STRIP_RE` 新增的三種多行字串**:`"""`、`'''`、`@"` 沒收尾時會吃到檔尾,但字串內容原樣保留,不會刪掉後面的測試。我推了一遍,沒收尾的情況不會造成回溯爆炸。
- **`_split_test_ref_ex(lenient=True)`**:`_kill_method_name` 在「已定義前綴」「冒號後緊接名稱」「冒號後有空白」三種情況下,結果和舊版的 `split(":",1)` 一致。
- **`_anchor_migration_hint` 快取鍵**:`profile_name` 在真實的平台資料裡一定有(`scripts/lumos:6002`、`6016`),沒有不同 profile 共用快取的問題。

**回答三問**
1. **原問題的修復效果**:上面四個故障變體都能把對應測試翻紅,有行為證據。例外是第 3 條寫的 Playwright 正規式語意,只有字串快照。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:撞名判斷的三個呼叫端是 guard kill、推送前的閘、guard settle。guard kill 和 guard settle 有實跑 CLI 的行為測試。推送前的閘靠既有 `_run_bound_tests` 的撞名測試,同樣通過。
3. **新發現在修前、修後各是什麼結果**:發現 1 修前沒這問題,修後有。發現 2 是這輪新引入的不一致。發現 3 是測試強度問題,不分修前修後。

**沒驗到的部分**
- 沒有實際安裝 Playwright 去驗 `-g` 的真實比對字串,只能依作者記載的 1.64.1 實測。
- 沒跑全套測試。
- 嵌套兩層以上的 describe 跨層撞名,程式碼自己已明寫「只看一層」,我沒有驗證。
- 逃脫字元標題的撞名:`_raw_test_titles` 拿的是未還原的原字(例如 `can\'t`),這條在本輪之前就存在,不算這輪的修補。

最嚴重 severity:minor,blocking 共 0 條。
