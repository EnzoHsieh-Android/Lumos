severity: major

### f1 gov 治理帳去重鍵拿 ts 當鑑別子,但 dispositions 的 ts 是 commit 時間不是事件時間,同 sha 重表態會被折成一筆

severity: major
blocking: 是
file: `scripts/lumos:4732-4734`
引句:「同 sha 兩筆 dispositions / recall-miss 各算各的,拿 ts 當鑑別子」
`_codeloop_dispositions_gov_log` 寫入的 `ts` 來自 `cmd_code_loop` 算好的 `_codeloop_git_ts(repo_root)`(scripts/lumos:20663-20668,取 `git show -s --format=%cI HEAD`),對同一顆 HEAD 呼叫兩次 `code-loop dispositions` 會拿到**完全相同**的 ts,於是 `_render_gov_stats` 的去重鍵 `(commit, nodes, gate, kind, token)`(scripts/lumos:4778)對兩筆表態算出同一把鍵、第二筆被折掉。實測(同一顆 commit 連續呼叫兩次 `code-loop dispositions`,兩份表態內容不同):兩筆治理帳的 `ts` 都是 `2026-09-09T02:00:10+08:00`;`lumos gov --stats` 印出 `code-loop 去重後筆數 1 原始行數 2`——跟 KEY 行與 S9 承諾的「同 sha 兩筆表態不折成一筆」相反。`t_gov_stats_dispositions` 測不到,因為它直接手寫兩筆 JSONL、各給一個相差 5 分鐘的假 ts,沒有走 `_codeloop_git_ts` 這條真實寫入路徑。緊鄰的 canary/blocked 案例(scripts/lumos:4731)已經因為同一問題採用「ts+note(內含隨機碼)」當鑑別子,這次 dispositions 沒有沿用同一補丁。

### f2 range-and-branch 測試沒有真的驗到「check --branch 讀到另一分支的表態」,拿掉那段讀取邏輯測試仍全線通過

severity: major
blocking: 是
file: `scripts/test_lumos.py:33188`
引句:「③check --branch release 讀到那筆 → 放行」
`t_codeloop_dispositions_range_and_branch` 的這一段先用 `--branch release` 寫入表態,再用 `--branch release` 跑 `check` 期待放行,意圖驗證「check 依 --branch 讀到寫在別的分支名下的表態」。但這段情境裡 checkout 在 `main`、`--at-sha` 也等於主線 tip,`_codeloop_guard_verdict` 的 merge-base 縮圈邏輯(scripts/lumos:21367 `_dispositions_verdict` 之前那段 `merge-base(主線, at_sha)`)算出 `_mb == marker_sha`,判成「分支 tip 已在主線上,沒有題要答」,`stack_questions_applicable` 直接被設成 `{}`。`_dispositions_verdict` 在 `app` 為空時於 scripts/lumos:21376 提早 return,根本不會走到 scripts/lumos:21378 的 `_codeloop_read_dispositions(repo_root, marker_branch)`。用副本驗證:把 `_codeloop_read_dispositions` 改成無視傳入的 `branch`、一律用 checkout 分支重建(等於讓「跨分支讀取」整個失效),`t_codeloop_dispositions_range_and_branch` 的全部 6 條斷言(含這條)仍然 6/6 全過。這條斷言測到的其實是「沒有適用題時不擋」,不是它自稱要測的「--branch 跨分支讀取」。

### f3 bound-tests-gate.md 的「怎麼跑」段落沒有跟上 pre-push 把低風險合約測試併進 code-loop check 的改動

severity: major
blocking: 是
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:41`
引句:「★低風險不再另外跑 bound-tests(check 裡已跑一次)★」
`bound-tests-gate.md` 第 41 行仍寫「低風險推送:pre-push 直接呼叫 `lumos bound-tests --advisory`」,這是 2026-09-07 的舊接線。這次 diff 把 `scripts/hooks/pre-push` 對 `refs/heads/*` 的低風險路徑改成呼叫 `code-loop check --bound-tests-advisory`(合約測試改在 check 內部以 advisory 模式跑一次),並刪掉原本獨立的 `bound_tests_advisory "$_range"` 呼叫;重寫後的 `t_prepush_computes_impact_once` 專門加了一條斷言釘住「不再另外跑 bound-tests」。`bound-tests-gate.md` 的 `about_code` 明列 `scripts/hooks/pre-push`,且是這次派工單固定席清單裡的 ★INVARIANT★ 節點,但它的「怎麼跑」段落沒有同步,S10 的文件更新清單裡也沒有列到這篇——下一個 session 照這篇文件的敘述去找「pre-push 直接呼叫 bound-tests」的呼叫點會找不到。

### f4 S2 承諾的「每棧至少一題有命中/不命中/註解假命中測試」實際只有 kt 做到,cs/sql/swift/node 四棧零直接觸發測試

severity: minor
blocking: 否
file: `scripts/test_lumos.py:32935-32938`
引句:「[表態閘 S2]每題有唯一 id 與非空 when、id 集合釘住」
這支測試函式自陳涵蓋 S2,但函式體裡對 `_stack_applicability`/`_STACK_QUESTION_SPECS` 的直接呼叫(scripts/test_lumos.py:32952/32955/32957)全部只餵 `kt` 這個棧;`vue` 只在檔尾用 package.json 判前端那段順帶驗了一次「命中」(check ⑦),沒有不命中與註解假命中樣本;`cs`/`sql`/`swift`/`node` 四棧、共 20 題(32 題裡的多數)完全沒有任何一條直接對 `when` regex 的命中/不命中測試(全檔搜尋 `_stack_applicability(` 只出現在 kt 的四處呼叫)。我另外對這 20 題各起一組手動樣本跑過,目前沒發現規則本身寫錯,但這是巧合不是被測試逼出來的——往後任何一條 regex 手滑(漏轉義、寫反大小寫類、pattern 打錯),在合入前不會被任何測試攔下。

### f5 t_stack_question_triggers 的翻紅釘註解指錯了受影響的檢查編號

severity: minor
blocking: 否
file: `scripts/test_lumos.py:32938`
引句:「把 changed_lines 只收 + 行 → ⑤翻紅」
docstring 說「拔掉 changed_lines 只收 + 行的處理會讓 ⑤ 翻紅」,但函式裡標號 ⑤ 出現了兩次(scripts/test_lumos.py 的「⑤stack_questions 語意不變」與「⑤applicable 只列命中題、meta 列全表」),兩者都跟「純刪除也要觸發」無關;真正驗證「拿掉刪除行處理」會翻紅的是標號 ⑥ 那條(「⑥純刪除 diff 也觸發」)。不影響測試本身能否抓到迴歸,但這段自我說明對不上實際編號,下一個要重跑「翻紅釘」驗證的人會對錯位置。

## 圖譜鏡頭

- Systems/棧別提問表態閘.md、Projects/棧別提問表態閘_計劃.md:S1-S8、S10 逐條核對程式碼與文件皆一致(樣板、驗形狀、序列早退、範圍算法、`_validate_repo_ref(at_sha=)` 沿用、CJK 理由門檻、鏡頭附表態、效能檢核目錄的 id 對照表逐字比對 32 個 id 與 regex 完全吻合)。S9 的「同 sha 兩筆表態不折成一筆」與程式碼實測不符,見 f1。
- Systems/pitfalls-code-loop.md:KEY 行已補上「2026-09-09 起另一條不看 tier 的分支……見 [[Systems/棧別提問表態閘]]」,與程式碼的序列早退(合約測試→表態→tier high 留痕)一致,未受破壞。
- Systems/bound-tests-gate.md:「怎麼跑」段落未同步 pre-push 低風險路徑改走 `code-loop check --bound-tests-advisory` 的接線變化,見 f3;KEY 行本身(★INVARIANT★ 對紅/懸空/不合法 blocked=True rc1 那條)描述的是 check 內部判定語意,沒有被這次改動推翻,只有外層「怎麼跑」的敘事過時。
- Systems/convergence-evidence-gate.md:通篇不提 `_codeloop_*` 系列函式,管的是 design-loop 的 `loop status --gate`/panel K 值收斂,跟這次改的 code-loop dispositions 是兩條互不相交的機制;不受影響。
- 機器附加的固定席清單(canary-audit、design-loop、guard-kill、lumos-cli-lifecycle、lumos-cli-read、slim-get/slim-install/slim-uninstall、授權與歸屬、測試假綠形態):牽連理由都是「about_code 剛好列到 ci.yml/pre-push/scripts/lumos/scripts/test_lumos.py」這幾支被大量子系統共用的檔案,逐篇讀過 KEY/INVARIANT 內容後,它們各自宣稱的行為(canary 記帳持久化與 second 純 telemetry、design-loop 處置閘第五步的 .md 材料要求、guard kill 的 rc 優先序與 JSON 純度、CLAUDE.md re-inject 的 sentinel 邊界、search 排除 superseded 語意、三支 .ps1 的 ASCII/`$Args` 規則)都跟這次表態閘的程式碼路徑沒有交集,判「不影響」。
- Issues/code-loop守衛main-direct盲區.md:該事故講的是 main-direct push 繞過 pre-push 的守衛盲區,與 CI 端 `code-loop check` 的重算後盾機制有關;這次只改了 CI 擋下時的錯誤訊息文字(ci.yml)與 check 內部多一道表態判定,沒有改動「main-direct 有沒有被攔」那個判準本身,不影響該事故的結論。

最嚴重 severity: major,blocking 條數 3
