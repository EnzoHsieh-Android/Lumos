severity: major

正確性鏡頭,範圍是 r1-lumos.patch(主程式包),對照 web-gaps 工作樹 HEAD 960cd3e6。所有實驗都在臨時目錄做,已刪。

白話版:這次改動把「測試名」從識別字放寬成任意句子,所以測試工具靠子字串去篩測試。這個篩法有兩個漏洞,一是防撞名的檢查看不到某些標題,二是歸檔的保護網沒有測試守。掃描、切平台前綴、剝註解這幾塊我逐項走過,都站得住。

## 發現

**1. 撞名檢查看不見被 discover 排除的標題,被綁的測試被跳過時仍可能判綠**
severity: major
blocking: 是
- 位置:`_run_bound_tests` 新增的撞名檢查。它只拿 `discover_test_methods` 的結果當「別的標題」。
- 輸入:`a.test.ts` 裡有四支。
  - `it.skip('login', …)`
  - ``it(`login ${role}`, …)``(樣板帶 `${`)
  - `it('login, admin', …)`(含半形逗號)
  - `it('login\tab', …)`(非還原跳脫)
- 實跑:`discover_test_methods` 只收到 `{'login'}`,`_name_filter_collisions("login", …)` 回 `[]`。前三支的標題都含 `login`,沒有一支被列為撞名。
- 預期:`jest -t login` 會同時選中四支(Jest 的 `-t` 是不分大小寫的子字串比對),所以該判「撞名、證不出」。
- 實際:不走撞名分支,正常跑。被綁的 `login` 被跳過,樣板那支跑過,摘要變成 `Tests: 1 skipped, 1 passed`。node-jest 的跑過證據樣式 `Tests:.*?[1-9]\d*\s+passed` 吃得到,判 green。
- 限制:我沒有裝 jest,只在函式層重現,沒有端到端跑 jest。
- 原因:`_test_name_ok` 與跳脫規則把一部分標題擋在 discover 之外,但這些標題照樣會被名稱篩選選中。撞名檢查用的集合應該是「掃描器看得到的全部標題」,不能只用「可綁定的標題」。
- 引句:「hit = _name_filter_collisions(method, coll_cache[plat], nf)」

**2. 歸檔的 `guard_re` 改回舊的 ASCII `\b`,所有測試照綠**
severity: major
blocking: 是
- 位置:`cmd_archive` 裡 `guard_re = _test_name_boundary_re(live_guard_tests)`。這條是用來擋「護著中文名合約的驗證紀錄被誤歸檔」,歸檔會搬走資料。
- 重現:我在 `--shared` clone 裡把這一行換回舊寫法 `re.compile(r"\b(?:" + "|".join(map(re.escape, live_guard_tests)) + r")\b", re.ASCII)`,再跑 `-k archive_and_trace`,結果 `3 passed, 0 failed`。
- 原因:`t_archive_and_trace_free_string_names` 的 ①② 只測 helper `_test_name_boundary_re`,③ 走的是 `guard trace`。沒有任何測試實際呼叫 `cmd_archive`。同一個測試把 `guard trace` 那一行(`pat = _test_name_boundary_re([bare])`)換回舊寫法則會紅(`2 passed, 1 failed`)。可見歸檔那一處是唯一沒被守的。
- 引句:「guard_re = _test_name_boundary_re(live_guard_tests)」

**3. 殺傷力驗證(guard kill)跑單支測試時沒有撞名檢查**
severity: minor
blocking: 否(未能重現,從 major 自降一級)
- 位置:`cmd_guard_kill`。
- 說明:全庫只有 `_run_bound_tests` 呼叫 `_name_filter_collisions`(grep 只有一處呼叫)。guard kill 只有跳脫,用 `-t 名稱` 這種子字串篩選時,別支同名前綴的測試變紅,也會被記成「這條配方殺掉了」。
- 引句:「cmd = _run_cmd_expand(run_cmd, method, name_filter=pentry["profile"].get("name_filter", "ident"))」

**4. `_unwrap_backticks` 的「恰好兩個反引號」條件沒有測試守**
severity: minor
blocking: 否
- 重現:移除 `s.count("`") == 2` 後,`-k backtick`、`-k split_rules`、`-k identifier` 全綠。
- 影響:標題 ``` `a` 和 `b` ```(頭尾都是反引號、中間還有)會被拆成 ``a` 和 `b``,與掃描器收到的名稱對不上。
- 原因:現有測試只用 `` `useFoo` 回傳 x ``(結尾不是反引號),碰不到這個分支。
- 引句:「if len(s) >= 2 and s[0] == s[-1] == "`" and s.count("`") == 2:」

**5. `guard settle` 沒有套用 `guard bind` 的整理與多平台冒號檢查**
severity: minor
blocking: 否(未能重現)
- 位置:新的 `if not _test_name_ok(method):` 只用 strip 後的值判斷,後面卻把沒 strip 的 `method` 寫進 `[test:{method}]`,並拿去跟 `_guard_formal_line` 裡已 strip 的名單比對。
- 預期的壞法:`--test ' 登入 成功'` 第一次寫成 `[test: 登入 成功]`;中斷後重跑,`method in names` 對不上,會誤報「已有同一句正式行、綁的測試裡沒有這支」。
- 另一處不一致:`bind` 在多平台且名稱含冒號時會擋、要求帶 `--platform`,`settle` 沒有同樣的擋(`settle` 本來也沒有 `--platform`),冒號名會寫出之後報 bad-name 的 `[test:API: x]`。
- 引句:「print(f"擋下:測試名『{_kill_esc(method)}』不合法(不能是空的、不能以減號開頭、不能含方括號或半形逗號、不能有控制字元)", file=sys.stderr)」

**6. Playwright profile 新加檔名錨 `*.spec.*` / `*.test.*`,舊綁定可能變懸空**
severity: minor
blocking: 否
- 輸入:舊筆記綁了 `e2e/login.ts` 或 `x.e2e.ts` 裡的 `test('login')`(自訂 testMatch 的專案)。
- 結果:從此掃不到,變 dangling,推送閘擋下。方向是 fail-closed,但舊筆記沒有遷移提示。
- 引句:「"file_name_match": ["*.spec.*", "*.test.*"],」

**7. note-shape 第二道 `_test_in_tree` 用 `git grep -w -F` 找名稱,碰到被跳脫的標題會誤報找不到**
severity: minor
blocking: 否(未能重現)
- 輸入:原始碼是 `it('don\'t submit', …)`,掃描還原成 `don't submit`,但 `git grep "don't submit"` 在原文裡找不到(原文是 `don\'t`)。
- 影響:被推的版本對照時會誤報「指不到真測試」。預設是 warn,只有改成 block 才擋推送。
- 引句:「跳脫只認 \' \" \\ \` \$(_test_name_of_match 還原)」

**8. ⚠ 需要編排者確認**
- Playwright 的 `-g` 若如我記憶是比對包含檔名的完整標題路徑(我沒有驗證),那名稱 `checkout` 會選中 `checkout.spec.ts` 裡每一支,撞名檢查同樣看不到。請用 playwright 1.64 實跑一次再判。

## 圖譜固定席
- `guard-kill`:rc 優先序與 `--json` 純淨度兩條。diff 只動 test 名稱判法與指令展開,沒動 rc 判定與 JSON 輸出,不影響。但發現 3 說明名稱篩選會放寬「殺掉」的認定。
- `bound-tests-gate`:「unfilterable 一律 blocked」這條仍成立,撞名會走 `unproven`。但發現 1 顯示撞名檢查的輸入集合不完整,會有漏網。
- 其餘固定席(`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`授權與歸屬`、`design-loop`)沒有被這個 diff 碰到,不影響。

## 已走過且正常的路徑
- 標題含 `//`、`/*`、`http://`:剝註解後保留。
- 200 與 201 字邊界:201 字不收。
- `'a' + 'b'`、`.each`、`test.step`、`xit`:不收。
- 註解與字串交錯、含單引號的 JSX 行:正常。
- 多平台前綴切法:`web:` 前綴、`API: x` 擋、`wbe:x` 擋、`http://x` 擋、全形冒號限已定義平台,都符合設計。
- 翻紅測試:`_name_filter_escape` 不跳脫、拿掉 collision→weak 分支、拿掉大小寫不分、把 `✓` 改回 `if True`、`_spec_gate_items` 改回讀原行、剝註解改回只剝 `//`,各自都會紅。
- 正則複雜度:`{0,200}` 與互斥的字元類,沒有災難性回溯。

最嚴重 severity:major;blocking 共 2 條(發現 1、2)。

相關檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/scripts/lumos`、`/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/scripts/test_lumos.py`。
