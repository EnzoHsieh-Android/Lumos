# Code Review r2 — code-dloop-redesign r1 修復批 delta 審查

審查對象:`code-dloop-redesign-r2-s4.patch`（governance/eval/canary_calibration.py、scripts/lumos、scripts/test_lumos.py、skills/lumos-design-loop/SKILL.md）。逐 hunk 讀完整份 diff，並對照 `scripts/lumos` 現行原始碼／實際跑 CLI 驗證關鍵行為。

---

## Finding 1 — `n_badlines` 未按 loop 域隔離：任一無關 loop 的一行壞行會永久癱瘓全庫 disposal 閘

**severity: blocker**
**file:line**: `scripts/lumos:8138-8141`（`_loop_status_disposal` 新增區塊；對應 patch 第 175-178 行,`@@ -8144,55 +8192,72 @@`）

**引句**：「canary-log 含 {n_badlines} 行不可解析——disposal 閘 fail-closed」

**問題**：`n_badlines` 是在 `cmd_loop_status`（scripts/lumos:3590-3600）掃**整份 `.canary-log.jsonl`**（該 vault 下所有 loop 共用同一檔）時累計的壞行數——壞行連 JSON 都解不了，自然也讀不出 `"loop"` 欄，所以這個計數天生無法按 loop_id 過濾。這份 r2 diff 把它新接到 `_loop_status_disposal`（全新程式碼，r1 之前完全不存在這道檢查），只要 `n_badlines>0` 就整體 rc2——**不論這行壞行是不是屬於正在查的這個 loop**。

已實測驗證（用真的 `scripts/lumos` 二進位跑，非臆測）：

```
loop A：record 一筆完整帶 findings-set/report/snapshot
loop B：另一筆完全獨立、完整、乾淨的 record
→ loop status B --disposal ...  rc=1（正常判定，非壞行問題）
→ 手動把「與 loop B 毫無關係」的一行垃圾字串附加進共用帳尾（不含 "loop":"B"，甚至不是合法 JSON）
→ 再跑同一條 loop status B --disposal ...  rc=2
   ERROR: canary-log 含 1 行不可解析——disposal 閘 fail-closed
```

也就是說：只要這個 vault 曾經（甚至是很久以前、別的 loop）留下一行壞掉的 JSONL，**之後所有 loop 的 `--disposal` 硬閘就永久 rc2**，直到有人手動修帳，且錯誤訊息「判定輪=最後一輪不可信」還會誤導查的人以為是「本 loop」帳面問題（其實壞行可能屬於毫不相關的另一個 loop）。`.canary-log.jsonl` 是整個 vault 一路累積、跨所有 design-loop 共用的帳本（見 CLAUDE.md 引用的 `lumos-design-loop` skill），這代表任一過去事故都能把「進實作前」的硬閘對全團隊癱瘓。

備註：同一個 `n_badlines` 也餵給既有的 `--settle` 路徑（scripts/lumos:3451-3454），該處訊息明確自承「fail-closed 及於整個共用檔」，是既有、已知的權衡；但 `_loop_status_disposal` 這段是本輪全新加上去、且訊息文字暗示問題出在「本 loop 判定輪」，掩蓋了實際上是「共用檔任意處」的事實——把既有的粗粒度機制直接套進一個新的強制合並閘，是這輪修復自己引入的新問題。

---

## Finding 2 — `cmd_loop_verify_progress` 的 streak 計算新增「丟最後一筆」，與真正 K-streak 閘邏輯不一致（off-by-one）；且現行 working tree 未實際套用此改動

**severity: major**
**file:line**：`scripts/lumos`，`cmd_loop_verify_progress`（patch hunk `@@ -3374,8 +3392,8 @@`）

**引句**：「for r in reversed(rounds[:-1]):   # dsp_streak_trim: 末筆常為進行中未定案輪,不計入 streak」

**問題**：`cmd_loop_verify_progress` 自我定位是「獨立進度驗證器」，其存在意義就是要跟真正的 K-streak 閘（`cmd_loop_status` 主路徑，scripts/lumos:3672-3681：`for r in reversed(rounds):`，**沒有**丟最後一筆）算出同一個 `clean_streak`，供編排者對照。這個 diff 只改了 verify-progress 這一份，卻沒有同步改真正的閘，兩邊從此結構性不一致。

具體失敗場景：3 筆 record，最近 2 筆皆 `kind=caught` 且 `severity` 為 clean/minor、`auditor` 非空，最舊 1 筆是 major。
- 真正的閘（3672-3681）：`reversed(rounds)` 從尾算回去,連續 2 筆合格才停 → streak=2。
- 這次改法：`reversed(rounds[:-1])` 先丟最後一筆，剩下只看舊的那 2 筆之一，只算到 streak=1。

「末筆常為進行中未定案輪」這個前提本身也站不住腳——`.canary-log.jsonl` 的每一筆 record 都是 `canary record` 一次性寫入時就帶著確定的 `kind`/`severity`，沒有「先寫個半成品、之後再補完」的資料模型，所以末筆不會是「未定案」的草稿,無條件丟掉會系統性低估 streak。

再者：現有測試 `t_loop_verify_progress`（scripts/test_lumos.py:2943-3007）只斷言 `rounds==2`、`findings_trend`，完全沒斷言 `clean_streak` 的值，所以這個 off-by-one 目前沒有任何測試會抓到。

**額外要點（需與作者核對，非我臆測）**：我直接對照了目前 `scripts/lumos` 的 git working tree（`git diff -- scripts/lumos`），這個特定 hunk（`dsp_streak_trim`）並**沒有**出現在現行未提交的改動裡——`cmd_loop_verify_progress` 目前實際檔案內容仍是舊的 `for r in reversed(rounds):`（scripts/lumos:3397，未變）。我把 patch 檔的 scripts/lumos 內容行與現行 `git diff` 逐行比對，唯一的差異就是這一個 hunk——patch 其餘所有變更都與現行 working tree 完全吻合。也就是說：這份要審的 diff 裡「唯一」對不上現行程式碼的地方,恰好就是我抓到 bug 的這一段。不確定是這段修法被人事後撤掉了（若是,此 finding 可視為已處理,不需再動作）,還是這份 patch 檔本身跟真正要進版的內容有落差——但無論哪種情況都值得跟出這份 patch 的人核對一次,免得「以為修了其實沒修」或「本來沒問題卻被重新引入」。

---

## Finding 3 — calibration-log 讀回自驗只比對「檔案最後一行」，並發寫入下會誤判自己的成功寫入為失敗

**severity: minor**
**file:line**：`governance/eval/canary_calibration.py:85-86`

**引句**：「tail = log.read_text(encoding="utf-8").splitlines()[-1]」

**問題**：這段程式碼的註解自稱「沿 lumos `_jsonl_append_verified` 慣例」,但實際做法不同:`_jsonl_append_verified`(scripts/lumos:2865-2893)是重開檔**逐行掃描、找自己那把唯一鍵**(token)是否存在;calibration 這裡只抓**檔案最後一行**去比對自己的 `ts`。

具體失敗場景:兩次 calibration 執行時間相近(例如排程跑批 + 有人手動補跑,或平行環境)。行程 A 寫完自己那筆(ts=T1)後,行程 B 緊接著把自己那筆(ts=T2)也 append 進同一個共用檔,搶在 A 讀回檢查之前完成 —— A 讀回時 `splitlines()[-1]` 抓到的是 B 的行,`json.loads(tail).get("ts")`(T2)!= A 自己的 `entry["ts"]`(T1),於是 A 印出「calibration-log 讀回自驗失敗」並 rc2 —— 但 A 自己那筆其實已經成功寫入、只是不再是檔案最後一行。這是一次假陽性:把「別人剛好晚一點點寫入」誤報成「自己的寫入失敗/半行」,與註解宣稱要抓的「中斷/併發可留半行」剛好是相反的失敗模式——真正該抓的是「自己那筆到底有沒有出現在檔案裡」,不是「自己那筆是不是最後一行」。

---

## 未列入的觀察(未達回報門檻,附註供參考)

- `cmd_canary` 落帳路徑正規化(`_pr.relative_to(env.vault.parent.resolve())`,scripts/lumos:~2822-2830)在本 repo 實際佈局下(`env.vault.parent` = `docs/`,而 `governance/review-reports/<loop-id>/` 是 `docs/` 的手足目錄、不在其下)幾乎必然 `relative_to` 拋 `ValueError`,退回存絕對路徑——沒有錯誤行為,只是「相對路徑」這個優化在本專案真實佈局下形同沒用到;因為退回路徑仍是絕對路徑、跨 cwd 仍正確,查不到具體會壞的場景,故未列為 finding。

---

max severity: blocker
