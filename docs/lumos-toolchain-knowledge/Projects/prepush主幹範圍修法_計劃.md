---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Issues/code-loop守衛main-direct盲區]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/loop機械脊椎M1包_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:問題=pre-push 的 tier/code-loop 守衛以 merge-base(HEAD,main) 算 diff——main-direct 時 mb==HEAD,整段檢查(pitfalls tier/棧檢核/test-layers/code-loop check)直接跳過;code-loop check(scripts/lumos:9464-9477)同病回「無 branch diff→standard」。實證=[[Issues/code-loop守衛main-direct盲區]]:M1包 gate code 判 high 卻放行,事後補審三輪才還帳
  KEY:方案裁定=①機械修(本計劃):pre-push hook 改讀 **stdin 推送範圍**(githooks(5) 標準合約:每行 `<local_ref> <local_sha> <remote_ref> <remote_sha>`,範圍=remote_sha..local_sha)——push 什麼就檢什麼,分支與 main-direct 同軌;+②家規 advisory 一行(gate 類 code 建議 feature branch,落 lumos-code-loop skill 非 CLAUDE.md——避免動紀律區塊觸發 Check D 模板同步面)。③並行=①+②即是
  KEY:hook 改動——**stdin 必須最先讀**(讀進陣列再跑測試段,防後續指令吃掉);逐推送 ref 檢:刪除 ref(local_sha 全零)跳過;**無基準(新 ref/缺物件)→保守掃 `empty-tree..local_sha` 全部內容非 fail-open(r2 樞紐反轉:守衛算不出基準必倒向多掃,否則升格成穩定繞法);standard 放行/high 擋**;一般情形(remote_sha 有效)→`remote_sha..local_sha` 增量,含推 main 本身(r2:撤 self-base 特判,否則每個 main commit 永久 high);**逐 ref 獨立判非全域 high**;pitfalls/棧檢核/test-layers/code-loop check 全吃推送範圍
  KEY:code-loop check 改動——加選配 `--diff <a..b>`(r1 折入:名對齊全 CLI,原擬 --range 不一致)+`--at-sha`/`--branch`(r1 最重 major:留痕比對原讀 checkout HEAD,推非當前 checkout 分支時 tier 對 range 算、留痕卻查錯分支=誤放/誤擋;改由 hook 傳被推送 ref 座標);不給=現行為不變(向後相容)
  KEY:落地同步義務(r1 折入)——①anchor:scripts/hooks/pre-push 是錨點檔,改後落地 push 先卡自身 anchor verify→序含 `lumos anchor approve --note` ②既有 t_codeloop_guard_prepush(test_lumos.py:6494)餵 dummy sha,stdin 變 load-bearing 後失真→重寫真 sha ③Issue open→清償 ④code-loop必用守衛計畫「merge-base 同 pre-push」句失真同步 ⑤Verification
  KEY:★風險面★self-governance=high(動 pre-push 守衛本身)——spec 過 design-loop 非 light([[Issues/code-loop守衛main-direct盲區]] 排程時明裁);實作後本 hook 改動自己就會被新邏輯檢到(自舉驗證:改完 push 時新範圍演算法應對本 diff 判 high→要求 code-loop)
  TEST:見 body 測試策略——--diff CLI 格數/新舊相容/留痕座標(推非當前 checkout 分支查對 ref)/hook 假 stdin 模擬(main-direct/新 ref fallback/首推 main 空 diff/shallow 無物件/刪除 ref/空 stdin/多 ref 混合迴圈/stdin 先讀);既有 t_codeloop_guard_prepush 重寫(dummy sha→真 sha)
  DEP:scripts/hooks/pre-push｜scripts/lumos code-loop check(:9451-9479)｜[[Systems/pitfalls-code-loop]]
  PRIOR-ART:①最小解=hook 讀 stdin 是 git 原生合約,零新機制;code-loop check 加一選配旗標 ②世界解=githooks(5) 官方文件明定 pre-push stdin 格式,業界 hook(husky/lefthook)皆此模式——標準做法非發明 ③裁定=borrow(git 官方合約原生用)
---
# prepush主幹範圍修法_計劃

> **狀態**：spec 完成，待 design-loop（self-governance=high）。緣起：[[Issues/code-loop守衛main-direct盲區]]（M1 包 gate code 判 high 卻從門下鑽過，事後補審三輪還帳——事前擋的價值實證）。

## 問題

`scripts/hooks/pre-push` 的代碼風險段以 `git merge-base HEAD main` 起算 diff：main-direct 時 mb==HEAD，`[[ -n "$mb" && "$mb" != "$head_sha" ]]` 為假 → **pitfalls tier／棧別檢核／test-layers／code-loop check 四件全部靜默跳過**。`lumos code-loop check`（scripts/lumos:9464-9477）同病：merge-base==HEAD → 回「無 branch diff」tier=standard → OK。

## 規格

### #1 hook 改讀 stdin 推送範圍（githooks(5) 標準合約）

- **stdin 最先讀**：hook 開頭（anchor verify 之前）把 stdin 逐行讀進陣列——防止後續任何指令（測試段等）繼承並吃掉 stdin。每行格式 `<local_ref> <local_sha> <remote_ref> <remote_sha>`。
- **逐 ref 推導檢查範圍**：
  - `local_sha` 全零（刪除遠端 ref）→ 跳過該行。
  - **★無基準＝保守掃全部，不 fail-open（r2 Codex 三席否決折入——樞紐反轉）★**：對守衛而言「算不出基準→跳過」是把盲區改成正式繞法（首推 main／`main:new-branch`／force-push 分岔未 fetch 全繞過，不需 --no-verify）。正確＝倒向**多掃**：以下情形一律用範圍 `<empty-tree-sha>..<local_sha>`（`git hash-object -t tree /dev/null` 得空樹 sha；scan 該 ref 引入的**全部**內容）跑 tier：
    - `remote_sha` 全零（新 ref，含首推 main——遠端無此 ref 故 remote_sha 全零，這條天然涵蓋，r2 修：不需 merge-base 自比特判）；
    - `git cat-file -e <remote_sha>` 失敗（shallow／force-push 分岔舊 tip 未 fetch，r1 s3＋r2 Codex#1）。
    只有連 empty-tree 掃描都跑不起來（git 環境壞）才 advisory 放行。**保守掃結果 tier=standard＝掃過且風險不高，正常放行（非 advisory）；tier=high＝擋**（r2 修：原植入「standard 亦 advisory 放行」是繞法換皮）。
  - **一般情形（remote_sha 非全零且物件在本地）→ 範圍 = `<remote_sha>..<local_sha>`——含推 main 本身**（r2 三席＋Codex 否決折入：原 v3「merge-base(local_sha,main)==local_sha → empty-tree」條件對**每次**推 main 都成立(main ref 本就指向 local_sha)，使每個 main commit 被 empty-tree 全掃抬成永久 high；實測 HEAD^..HEAD=standard vs empty-tree..HEAD=high/110 claims。**該 self-base 條件全撤**——remote_sha 有效即用增量 diff，空 diff 自然判 standard 正確放行，不需特判）。
- **聚合**：對每個有效範圍跑 `pitfalls --diff <range> --no-lint --json`；**逐 ref 獨立判——某 ref 判 high 即對「該 ref」走 code-loop check 硬擋（用其 --at-sha/--branch 座標，見 #2b）；非全域「整體 high」**（r1 修正：全域 high 會用一個 range 的判定套到別 ref 的留痕＝留痕脫鉤根源）。第一個 high ref 未過即擋、其餘 ref 可短路（成本＋明確性；r1 s3-F2 折入）。standard＋棧命中 → advisory；test-layers 逐範圍 advisory。多 ref push 常見於 `--all`/批次同步——逐 ref 迴圈變數每輪重置。
- **無 stdin 行**（無實際推送）→ 跳過代碼風險段（其餘 anchor/測試/doctor 照舊）。
- 原 merge-base 推導整段移除（被 stdin 範圍取代）。**git 語意誠實記（r2 Codex#3 minor）**：`remote_sha..local_sha` 是**增量 endpoint diff**（`git diff A..B` 比兩端 tree），與舊 `merge-base(main,HEAD)..HEAD` **不等價**——後續 push 前者只比 remote tip↔新 tip、更貼「只檢真正要推的」，但不宜稱「天然等價」或 force-push「只涵蓋新側」。行為＝改成增量端點 diff，明說。

### #2 `lumos code-loop check --diff <a..b> [--at-sha <sha>]`（選配；r1 折入：旗標改名＋留痕座標）

- **旗標名＝`--diff`（r1 s4-F3 折入，原 `--range` 與全 CLI 不一致）**：對齊 `pitfalls --diff`/`cochange --diff`/`test-layers --diff`/`impact --diff` 全用 `--diff <A..B>`。給了 → 跳過 merge-base 推導（:9464 段），直接以該範圍跑 pitfalls 算 tier。不給 → 現行為分毫不變（向後相容）。格式非 `<sha>..<sha>`／git 解不開 → 沿 fail-open（unknown tier、不 blocked）＋stderr 一句。
- **★留痕座標脫鉤（r1 最重 major，三席互證＋r2 Codex 確認）★**：現行留痕比對讀「**當前 checkout** 的 branch/HEAD」（:9502-9517）；hook 逐 ref 檢的是**被推送 ref 的 local_sha**（可非當前 checkout）→ 借錯分支留痕誤放/誤擋。修法：`code-loop check` 加 `--at-sha <sha>`＋`--branch <name>`，hook 傳被推送 ref 座標。
- **★`--branch` 鍵正確性（r2 Codex#3 折入——原「取 local_ref 末段」是實作 bug）★**：marker 鍵＝完整 branch 名把 `/`→`__`（`feat/x`→`feat__x.json`，:9395）——取末段查 `x.json` 錯、且會名稱碰撞。修法：**只認 `refs/heads/*`**——去 `refs/heads/` 前綴後的**完整** branch 名（沿 :9395 的 `/`→`__` 轉換）作 `--branch` 值。`local_ref` 非 `refs/heads/*`（tag／`HEAD~`／raw revision，git 合約允許）→ 無對應 branch marker，走保守掃描判 tier：**high → 硬擋（r2 s3-F2＋Codex 折入：原「advisory 放行」是 `push sha:refs/tags/x` 的穩定繞法，與本 spec 宗旨相悖；非分支 ref 無留痕通道故不給 pass，要推走 branch 或 `--no-verify` 自負）**；standard 放行。**`--branch` 鍵大小寫（r2 s3-F1＋Codex）**：現行 marker 寫入側（:9395 `_codeloop_branch_filename`）只做 `/`→`__` **不轉大小寫**——`--branch` 值**保留原大小寫**（原植入「先 lower-case」會與寫入側不對稱、大寫分支誤擋）。

### #2b hook 逐 ref 傳留痕座標
hook 對每個 `refs/heads/*` 範圍呼叫 `code-loop check --diff <range> --at-sha <local_sha> --branch <去前綴的完整 branch 名>`；非 heads ref 走保守掃描 tier 判定但不綁留痕。

### #3 家規 advisory（純散文，一行）

`lumos-code-loop` SKILL `## 一眼看懂` 的「**何時**:」條末補一句（r1 s4-F5 折入落點精確化）：「gate/守衛類 code **建議** feature branch（pre-push 對 branch 與 main-direct 現已同軌檢查，此為縱深建議非機械強制）」。不動 CLAUDE.md 紀律區塊（避免觸發紀律區塊漂移守衛 Check D 的模板同步面——範圍刀）。

## 落地同步義務（r1 s4-F1/F6 折入，同一 commit）

1. **anchor baseline（最重）**：`scripts/hooks/pre-push` 是錨點檔（`governance/anchor-baseline.json`＋`ANCHOR_FILES`）——改 hook 後 sha 變，落地 push 自己會先卡在 hook 內的 `anchor verify`（:29）。落地序：改完 → `lumos anchor approve --note "prepush 範圍修法落地"` → 再 push（否則進不到新 tier 邏輯）。
2. **既有測試重寫**：`t_codeloop_guard_prepush`（test_lumos.py:6494 起）餵的 stdin 是字面 `dummy` sha——現行不讀 stdin 故無妨，但 stdin 變 load-bearing 後 `dummy..dummy` 會讓 pitfalls 報錯靜默 fail-open、既有斷言失真。改餵真 sha（`git rev-parse HEAD`/`main`）。
3. `Issues/code-loop守衛main-direct盲區` status open→改（修法落地即清償主軸）。
4. `Projects/code-loop必用守衛_實作計畫`「merge-base 取法同 pre-push」句落地後失真——同步。
5. Verification 節點（plan_refs 回指）。

## 明確不做（範圍刀）

- 不做 push 範圍的 doctor/測試段範圍化（那兩段本來就是全量語意，與範圍無關）。
- 不動 pass/skip 留痕的 sha 語意。
- 不做 CLAUDE.md 紀律區塊改動。
- 不做 force-push 的**特殊路徑**——但缺舊物件時走保守掃描（見 #1 樞紐反轉），非跳過。

## 測試策略

1. `code-loop check --diff`：合法範圍算 tier（造含 .py 變更的範圍→tier 判定跑通）／不給 --diff 現行為不變（既有測試不紅）／壞格式 fail-open 不 blocked／`--at-sha`/`--branch` 使留痕查指定座標非 checkout。
2. hook 模擬（臨時 git repo＋假 stdin，沿 `t_codeloop_guard_prepush` subprocess＋input 模式）：main-direct push（remote_sha 有效）→增量範圍風險段執行／**新 ref（remote_sha 全零，含首推 main）→empty-tree 保守掃，掃出 high 擋、standard 放（r2 反轉，非 fail-open）**／**缺物件（shallow/force-push 未 fetch）→empty-tree 保守掃（r2）**／刪除 ref→跳過／空 stdin→風險段跳過其餘照舊／多 ref 混合（一刪＋一推＋一新）→逐 ref 迴圈各自處理／stdin 先讀不被後段吃。
3. **留痕座標（r1 最重）**：checkout 在 main、push featB→`--at-sha`/`--branch` 使留痕查 featB 非 main（誤放/誤擋雙向案例）。
4. 迴歸：一般分支 push 新舊範圍等價；`t_codeloop_guard_prepush` 重寫後仍綠。

## 審計修正紀錄

**pre-flight（2026-07-21）**：1 命中——新 ref fallback 分岔缺測試項＋空 stdin 跳過缺測試項，補測試策略。

**r1（2026-07-21，high panel W=4 sonnet 異鏡頭＋Codex 帶餌 finder＋無餌否決席）**：canary s2/s3/s4 caught、**s1 missed（summary↔body「空 stdin 提前 exit0 vs 只跳風險段」矛盾未抓，通才席漏鏡像面）→ 輪無效**；s1 findings 剔除（其主 finding＝留痕脫鉤已由 codex-finder＋s2＋s4 獨立三席互證浮回，無損）。canary token（--push-base/PUSH_RANGE_MAX/hook-sync.log）溯源排除不折。真 findings 折入 v2：
- **★留痕座標脫鉤（major，三席互證，本輪最重）★**：pass/skip 留痕讀 checkout HEAD、tier 讀被推送 range——非當前 checkout 分支 push 時借錯分支留痕誤放/誤擋 → `--at-sha`/`--branch` 由 hook 傳；聚合改逐 ref 獨立判非全域 high。

**r2（2026-07-21，Codex 帶餌 finder＋無餌否決席；復核 v2）**：finder canary caught；**否決席 VETO 3 major——全指向 v1/v2「無基準＝fail-open」的方向性錯誤**（我 r1 折入時把 shallow/首推都改 fail-open，反而把盲區升格成正式繞法）。全折 v3：
- **★樞紐反轉（major×2，Codex 否決#1#2）★**：無基準（新 ref／self-base 空 diff／force-push 缺物件）一律 **`empty-tree..local_sha` 保守掃全部**，非跳過——守衛「算不出基準」必須倒向多掃。原 fail-open 條全撤。
- **`--branch` 鍵 bug（major，Codex#3）**：取 local_ref 末段與 marker 鍵（完整名 `/`→`__`，:9395）不符＋非 heads ref 無綁定 → 限 `refs/heads/*` 用完整名，tag/raw 走保守掃描不綁留痕。
- **git 語意誠實（minor，Codex）**：「天然等價」「只涵蓋新側」改「增量 endpoint diff」。

**r2-panel（2026-07-21，delta 審 v3 樞紐反轉；3 sonnet＋Codex 否決復核）**：canary s2/s3 caught、**s1 missed（自植「standard 亦 advisory 放行」矛盾未抓）→ 連 2 輪無效**（r1 亦 s1 missed；護欄→r3 升 opus）；s1 findings 剔除但兩條經 Codex 獨立浮回。真 findings 折入 v4：
- **★self-base 過度反轉（major×3，s1+s2+Codex 實測）★**：`merge-base==local_sha` 對每次推 main 都成立→每 main commit empty-tree 全掃永久 high → **該條件全撤**，remote_sha 有效即用增量 diff（空 diff 自然 standard）。
- **★summary/測試策略未跟樞紐（major，s1+Codex#1）★**：frontmatter KEY 與測試策略 items 仍寫 fail-open（`lumos context` 攤 summary 會誤導、TDD 會把繞法測回去）→ 同步反轉。
- **非 heads ref high→硬擋（major，s3+Codex）**：原 advisory 放行是 `push sha:refs/tags/x` 繞法 → 改硬擋。
- **`--branch` 保留大小寫（major，s3+Codex）**：marker 寫入側不轉大小寫，`--branch` 值不得 lower-case（原植入會使大寫分支誤擋）。
- **既有債記（Codex minor，不折）**：marker 鍵 `feat/x` vs `feat__x` 碰撞、marker 綁 local_sha 不綁 range——屬既有 marker 設計面，出本 spec 範圍，指 [[Projects/code-loop必用守衛_計劃]] 待另案。
- **首推 main mb==local_sha 空 diff（major，s2）**：重現盲區 → 併入 fail-open+advisory。
- **shallow/remote_sha 本地無物件（major，s3）**：cat-file -e 探測 → fail-open+advisory（原不對稱靜默）。
- **既有 t_codeloop_guard_prepush 崩（major，s3）**：dummy sha 在 stdin load-bearing 後失真 → 重寫真 sha，列同步義務。
- **anchor baseline 落地卡關（major，s4）**：改 hook 先卡自身 anchor verify → 落地序含 anchor approve，列同步義務。
- **聚合成本/多 ref 迴圈無測試（s3）**：短路＋逐 ref 迴圈重置＋多 ref 混合測試格。
- **自舉驗證因果不成立（minor，codex-finder）**：glob claim 保底 high 與新邏輯對錯無關 → 誠實改。
- **--diff 命名/advisory 落點/同步清單（minor，s4）**：全折。

## 實務隱患

- **自舉面（r1 s?-誠實修正）**：本改動落地 push 時會判 high——但 tier=high **來自 `pitfall_when: glob:scripts/hooks/pre-push` 既有 claim 保底命中**（碰該檔即 high），**與新範圍演算法對錯無關**。故「有觸發 high」不能當「新邏輯正確」的自舉證據——真驗證靠 hook 模擬測試（測試 2/3），不靠落地那次 push 的 tier 值。
- **保守掃描的殘餘（r2 反轉後）**：無基準改掃 `empty-tree..local_sha`＝掃該 ref 全部內容——對「大量既有內容首推」會判 tier=high（保守；寧誤擋不誤放，守衛正確方向）；真需放行走 `code-loop skip --note` 留痕。只有 git 環境壞到 empty-tree 都掃不動才 advisory 放行（極窄）。
- **非分支 ref（tag/raw）**：走保守掃描判 tier，但無 branch marker 可綁留痕 → advisory 不硬擋（另訂策略前的誠實預設，記為待辦）。
- **stdin 消費順序**：bash 中若測試段先跑會吃掉 stdin——spec 明定最先讀；測試 2 有專門格。
