severity: minor

我只讀了 repo,沒改動。實驗都在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/文件一致3-sonnet/` 下的兩份 `git clone --shared` 副本裡跑:`repo` 在修後版本 59f8f92b,`before` 在修前版本 88322e46。

## F1 守檔筆記計劃第 106 行還教人把整個紀錄資料夾加進提交
severity: minor
blocking: 否

引句:「`git add governance/reread-verdicts && git commit` → 推。」

- 位置:`docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md:106`。
- 這句描述手冊「推送前回頭重讀守檔筆記」小節該寫什麼,還叫人整個資料夾加進去。
- 修補把同一篇的第 82 行、手冊 `skills/lumos-project-notes/commands/06-代碼審與推送.md:98`、`_note_reread_add_cmd`(`scripts/lumos:34925`)都改成列具體檔名,這行漏了。
- 照這行重寫手冊的人,會把「夾帶殘檔與別的會談的紀錄」的舊寫法寫回去。
- 歸因:有證據的原有漏查。這不是修復造成的回歸,而是修補掃描同句散落時漏掉。
- 證據(claim / input / expected / case_source / before / after):
  - claim:提交提示改列具體檔名後,別處不再留下整個資料夾的說法。
  - input:對兩版跑 `git show <sha>:<該檔> | grep -c 'git add governance/reread-verdicts && git commit'`。
  - expected:修後為 0。
  - case_source:本席補的同句散落掃描。
  - before(88322e46)= 1。
  - after(59f8f92b)= 1。
  - 結果:兩版一樣,未修到。

## F2 舊句兩道轉擋計劃的治理帳欄位描述沒跟上修補
severity: minor
blocking: 否

引句:「detail 記兩層各幾篇、第一層要重判幾篇、第二層要處理的前 50 行(路徑、引句前 80 字、判定紀錄指紋)」

- 位置:`docs/lumos-toolchain-knowledge/Projects/舊句兩道轉擋_計劃.md:67`。
- 修後真碼(`_note_reread_ledger_found`,`scripts/lumos:35505`)是這樣:
  - `note` 只剩兩層篇數、範圍終點和來源。
  - 第一層沒對照的路徑與指紋,另放在頂層欄位 `layer1_fps`(前 50 篇)。
  - 第二層點出的行放在 `rows`。
  - `head_sha` 記被推頂端。
  - 超過 4 KB 先丟 `rows`、再丟 `layer1_fps`,各記 `_truncated`。
- 同篇第 65 行寫「warn 時回 0、記 `skipped`」,也沒提修補新加的 `state=undecidable`。
- 這一篇正是 REVISIT 2026-12-04 量帳的依據。
- 照這段文字去找清單欄位的人,不知道有 `layer1_fps`、`layer1_fps_truncated`,也不知道 skipped 帳帶 state。
- 歸因:有證據的原有漏查。修補日誌聲稱帳欄位文件跟真碼一致,這兩行實際沒改。
- 證據:
  - claim:帳欄位描述與真碼一致。
  - input:對兩版跑 `grep -c 'detail 記兩層各幾篇'`。
  - case_source:本席補的文件對碼核對。
  - before = 1、after = 1,兩版相同。
  - 真碼行為證據:修補後的測試 `t_reread_block_ledger_fits_4k` 在修前碼上紅 5 條斷言、在修後碼上綠。
  - 所以欄位確實變了,而這段描述沒跟上。

## F3 帳本家節點的 `_gate_event_fit` 說明仍寫兩個使用者
severity: minor
blocking: 否

引句:「_gate_event_fit 是跨閘共用的 4 KB 裁法,舊句檢查帳與筆記形狀擋的 relaxed 帳共用、不另寫第二支」

- 位置:`docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:29`。
- 修補把 `list_key` 改成可收一串鍵,新增 `_gate_event_fit_drop`(`scripts/lumos:1594,1602`)。
- 回頭重讀那筆帳現在傳 `("rows", "layer1_fps")`(`scripts/lumos:35523`),成了第三個使用者。
- 改共用函式的人,只看家節點會漏掉回頭重讀這個使用者,以為只有兩個消費者可以放心動。
- 歸因:未判定。
  - 回頭重讀使用它早於修補,但多鍵語意是修補新增的。
  - 兩版該行都是 1 次,說明沒更新。
  - 嚴格說是原有漏查加上修補新增語意都沒補,無法單歸一邊。

---

## 三問回答

### ① 原問題的修復效果

我把修後的測試總檔放進修前碼(88322e46)跑 `-k reread`,結果 237 通過、19 條斷言失敗,分布在 6 支測試。紅的都對應修補主張:

| 測試 | 修前紅的內容 |
|---|---|
| `t_reread_block_ledger_fits_4k` | 整行超過 4096,最大 4946 位元組;note 帶「路徑=指紋」清單;head_sha 不是被推頂端 |
| `t_reread_wt_records_guarded` | 13 萬層巢狀 JSON(不到 256 KB)讓 prepare 與 `drift ack --kind reread` 崩;提交指令列整個資料夾 |
| `t_reread_record_refuses_unreadable_size` | 上限加 1 位元組時印出「256 KB,超過 256 KB」;提示只怪最長那行 |
| `t_reread_block_undecidable` | warn 下判不了的 skipped 帳沒有 state;已提交的巢狀太深紀錄被當成沒預料的錯誤 |
| `t_reread_block_hook_and_ci_wiring` | 帳的來源判斷只看 `CI`,設了 `GITHUB_ACTIONS` 沒記成 ci |
| `t_note_audit_reread_prepare_skips_uncommitted_records` | prepare 與 check 的提交指令列整個資料夾 |

- 修後版本跑同一組測試:`-k reread` 256 通過、0 失敗。
- 我另外只對 `_isolate_environment` 的清變數那段做了一次改壞:清除範圍縮成只清 `LUMOS_SKIP_REREAD_CHECK`。`t_runner_drops_inherited_skip_env` 紅 2 條,與筆記「防回歸」描述吻合。
- 作者聲稱的 17 種改壞,我只重現了這一種。其餘未驗。

### ② 正常、錯誤與相鄰路徑

修後版本實跑,全綠:

| 子集 | 結果 |
|---|---|
| `-k gate_event` | 5 通過 |
| `-k long_line` | 12 通過 |
| `-k old_sentence` | 41 通過 |
| `-k command_index` | 14 通過 |

- 舊句檢查帳、筆記形狀擋放寬帳沿用同一個 `_gate_event_fit`,行為仍成立。
- `t_command_index_complete` 轉綠,索引仍提到 `--kind reread`。
- 索引縮字後是 4498 字,上限 4500,只剩 2 字餘裕,但我讀不出會讀錯的場景,所以不當 finding。
- 工作目錄紀錄的正常路徑(提交 + `provenance_ok` 為真,算只差提交)有對照組測試通過。

### ③ 新發現在修前、修後的結果

三條都是兩版相同(F1 查證命令的結果、F2 同一個命令的結果、F3 同一個命令的結果,都是 1 次)。沒有發現由修補引入的新文件錯誤。

## 鏡頭逐項結論

**1. 文件與真碼一致**
- 已逐句對照,語意相符:
  - `layer1_fps`、4 KB 從尾端截。
  - `_in_ci()` 同看 `CI` 與 `GITHUB_ACTIONS`。
  - 工作目錄紀錄的「還沒提交」口徑(符號連結、不是一般檔、256 KB、巢狀太深都略過)。
  - 走訪守門只有 `_note_reread_wt_verdicts` 一份,`drift ack --kind reread` 共用。
  - 提交指令三處走 `_note_reread_add_cmd`。
  - 超長行判準:`_drift_m1_line_names` 的條件是「每段 ASCII 詞是完整詞、整個名稱是子字串」。
  - README 中英的名稱範圍:函式、類別、模組層或類別層的變數與常數、旗標;`_drift_m1_assigns` 確實收模組層與類別層。
  - CHANGELOG 的「判不了在 block 回 1,CI 那步一樣紅」:`_DRIFT_M1_UNKNOWN` 的四種狀態,block 下 rc 1。
- 筆記說「13 萬層」,碼註解是 125000 層。我實測 125000 與 130000 層都會丟 RecursionError,兩者都小於 256 KB,不算錯。

**2. 同句散落變體**
- 超長行「純子字串」的舊說法、`_note_reread_committed`、「只比檔名」都已清乾淨。
- 只有 F1 一處留下舊說法。

**3. 手冊索引與 README**
- 索引縮字只改了 3 行,沒有刪指令。
  - `drift ack` 的 `--name` 與 `--kind reread` 都保留。
  - `reread-prepare/record/check` 在第 38 行仍在。
  - 「推送時」三字被移走,但第 17 行還有。
- 中英 README 對齊。

**4. 圖譜筆記格式**
- 修補新寫或改寫的摘要行:
  - `測試假綠形態` 的 PITFALL 有 `[出處]` `[根因]`,以及 `[防回歸]` 與 `[test:]`。
  - Issue 的 DECISION 與 PITFALL 格式沿用既有寫法。
- 7 篇被改的筆記跑 `lumos lint`,0 個 error。
- 只有 `存量漂移守衛` 有 2 條 warning,來自第 83 行已標 superseded 的舊 RULE。那行在修補範圍之外,不報。
- 修補新增文字沒有會過期的「還沒/尚未」承認句,出現的都是描述「尚未提交」這個狀態。

**5. 圖譜鏡頭(固定席節點)**
- 這份文件修補不改任何行為,所以對下列節點都不影響:
  - `Issues/code-loop守衛main-direct盲區`
  - `Systems/guard-kill`
  - `Systems/lumos-cli-read`
  - `Systems/lumos-cli-lifecycle`
  - `Systems/pitfalls-code-loop`
  - `Systems/筆記內容閘`
- `Systems/存量漂移守衛`:新文字與真碼一致。
- `Systems/reversibility-governance-ledger`:有 F3 的小缺口。

## 未驗範圍
- 沒有跑全套測試。
- 沒有重跑作者聲稱的 17 種改壞,只驗了其中一種。
- CHANGELOG 的「CI 永遠是冷快取」是絕對說法,但我給不出具體的讀者失敗場景,所以沒列。

最高等級:minor

相關檔案(絕對路徑):
- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block/docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block/docs/lumos-toolchain-knowledge/Projects/舊句兩道轉擋_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone-reread-block/docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md`
