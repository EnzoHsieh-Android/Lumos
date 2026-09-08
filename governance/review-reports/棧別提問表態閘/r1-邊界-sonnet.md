severity: blocker
# r1 邊界席(sonnet)——棧別提問表態閘


### B1 tier=high 判準與棧命中互不相關,BLOCKING 觸發條件對 kt/swift/vue 三棧近乎打不開
severity: blocker
blocking: 是——這是設計的核心承諾(缺一問就不准推)在主流情境下不會發生,不是邊角案例。
引句:「tier high 且 diff 命中棧 → 讀當前 sha 的 pass 記錄，逐問核對」
查證:`_pitfall_diff_collect`(file: `scripts/lumos:16472`)的 `tier` 完全由 `_PITFALL_DIFF_PATTERNS`(file: `scripts/lumos:16455`)算出,與 `stack_questions` 欄位完全獨立計算。`requests`/`httpx`/`threading` 是 Python 語法,Compose/Coroutine/SwiftUI/Vue 的典型改動不會命中這些正則;pre-push(file: `scripts/hooks/pre-push:187`)對 tier=high 才呼叫 `code-loop check`,`:223` 的 `elif` 只在 tier≠high 時走 advisory-only 分支。結果:一支只改 Compose remember/LaunchedEffect 的 diff,`stack_questions` 有值但 `tier=standard`,永遠落在不擋的 advisory 分支。

### B2 dispositions 只規劃寫進「治理帳事件」,但 CI 讀的是被裁過欄位的 ledger 重建
severity: blocker
blocking: 是——本專案已經真實發生過一次的同類事故,換了欄位重演機率高。
引句:「形狀壞 rc2 不寫帳；形狀好就寫進留痕記錄的 `dispositions` 欄與治理帳事件。」
查證:`governance/.gitignore:10` 排除 marker;CI 退回 `_codeloop_read_from_ledger`(file: `scripts/lumos:20135-20167`),重建 dict 只有 `status/head_sha/note/ts`;寫入端 `_codeloop_gov_log` 的 event dict(file: `scripts/lumos:20174-20182`)同樣沒有 `dispositions` 鍵;函式註解:「2026-08-22 實紅:CI 後盾 #5 上線後第一筆 tier=high 推送因 marker 不在 checkout 而假紅」(file: `scripts/lumos:20139`)。

### B3 docs/ 目錄不存在的消費專案,dispositions 在 CI 側完全沒有落地路徑
severity: major
blocking: 是——消費專案這條路徑直接失效而非降級。
引句:「留痕本來就綁 sha，改碼即失效，所以不需要日期式 grandfather。」
查證:`_codeloop_gov_log` 在 `docs` 不是目錄時直接 `return`(file: `scripts/lumos:20197-20198`);marker 被 gitignore、docs/ 又不存在時,dispositions 在 CI 上無從讀起。

### B4 test: 錨點驗證未提多平台前綴慣例
severity: major
blocking: 是——此案的計劃連結本身就指向一個多平台專案。
引句:「用該 repo 的 test profile 跑 `discover_test_methods`，名字要在集合裡」
查證:既有多平台合約測試綁定用 `<platform>:<name>` 前綴,由 `resolve_test_refs`(file: `scripts/lumos:3439-3456`)按前綴路由到各平台 `methods_for(plat)`(`_platform_test_index`,file: `scripts/lumos:8064-8085`)。

### B5 `.lumos/config.json` 解析失敗時的降級,會讓非 C# 專案的 test: 證據系統性誤判
severity: major
blocking: 是——降級後的預設 profile(csharp-xunit)與 Kotlin/Swift/Node 專案完全不合,是必然不是機率。
查證:`load_platforms` 解析失敗時走 legacy,`name = cfg.get("test_profile") or "csharp-xunit"`(file: `scripts/lumos:3374-3379`);`load_test_profile` 同一分支印「⚠ .lumos/config.json 解析失敗,用 csharp-xunit 預設」(file: `scripts/lumos:3313-3315`)。BLOCKED 訊息不會提這是設定檔壞掉。

### B6 唯一承認的補償機制(審查席反駁)結構上碰不到最後一輪表態
severity: major
blocking: 是——spec 自己承認 GIGO 天花板並指名這是唯一降低機率的手段,若對「最終那次 pass」不生效,承諾就是空話。
引句:「答對答錯不驗：派工鏡頭在 diff 模式把表態附進派工單，審查席可反駁（對稱辯方對發現的做法）。」
查證:dispositions 只在 pass 時寫入,而 pass 是審查收斂後的終審動作;決定放行的那一次 pass 之後沒有下一輪派工。

### B7 ⚠ `path:line` 證據字串怎麼切分沒有定義
severity: major
blocking: 是——若落地成「missing」而非提示格式錯,是把存在的證據判成不存在。
引句:「`path:line`：檔案存在且行號在範圍內（借 refcheck 的存在性核對，不驗內容）。」
查證:`_validate_repo_ref`(file: `scripts/lumos:14668-14697`)接收已切好的 `(token, line)`;既有切分 `_refcheck_scan` 用 `:([^/]+)$` 且要求 token 不含斜線(file: `scripts/lumos:14702-14713`)——為掃 markdown 反引號寫的,不是為 JSON 欄位寫的;反斜線路徑會 `missing`。

### B8 `na` 理由「≥10 字」用字元數,中英文門檻不對稱
severity: minor
blocking: 否——不影響閘擋不擋。
引句:「`na`（必附 `reason` ≥10 字）、`todo`（必附 `issue`：`Issues/<名>`）。」
查證:10 個中文字是一句完整理由,10 個英文字元幾乎不構成理由;spec 沒講單位。

### B9 `status` 三值大小寫未定義,打錯大小寫時錯誤訊息不會指出原因
severity: minor
blocking: 否——結果安全(未知 status 一律 rc2),只是診斷訊息品質。
引句:「`status` 三值：`satisfied`（必附 `evidence`：`path:line` 或 `test:<名>`）」

### B10 本專案主力語言 Python 不在 `_STACK_PERF_QUESTIONS`,對 `scripts/lumos` 自身的改動此閘永遠不會觸發
severity: minor
blocking: 否——繼承自更早的棧問題表計劃,非本案新增瑕疵。
引句:「- 不改問題表本身。」
查證:`_STACK_PERF_QUESTIONS` 的鍵只有 `kt/cs/vue/sql/swift/node`;`_stack_key_for_file`(file: `scripts/lumos:14852`)對 `.py` 回 `None`。

### B11 `--dispositions-template` 在零命中棧時的輸出格式未定(空字串 vs `{}`)
severity: minor
blocking: 否——只影響下游串接健壯性。
引句:「對命中各問各印一條骨架，含 `question` 原文與空 `status`；未命中棧不印」

### B12 BLOCKED 訊息在多棧多問情境下的長度沒有上限規劃
severity: minor
blocking: 否——純 UX。
引句:「→ 各自 BLOCKED 並列出該問；全部合法 → 照舊放行」
查證:本 repo 其他閘有截斷慣例(pre-push 測試失敗只列前 20 支)。

## 已讀無 finding
鍵多於/少於命中(S3 明文)、同鍵重複(JSON 語意)、多棧並存(dict)、只命中測試檔(既有排除)、package.json 兩 sha 間變動(非白名單即失效)、舊記錄相容(明文)、序號同 commit 穩定(表隨 sha 定版)、空物件 `{}`(check 逐問判缺,不構成繞過)。

## 總結
最嚴重 severity 為 blocker(B1、B2),blocking:是 共 6 條(B1–B7 中 B1–B6 為是;B7 為 ⚠ 是)。
