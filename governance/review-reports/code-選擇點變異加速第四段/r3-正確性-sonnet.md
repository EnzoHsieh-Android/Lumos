severity: minor

我逐 hunk 讀完 1197 行快照,挑了具體輸入走過。在這個鏡頭下找不到會做出錯行為、破壞合約或損壞資料的洞,只找到兩條測試覆蓋缺口,都是 minor。

**Finding 1:`merge_init_off` 的治理帳讀回路徑沒有任何測試守**
severity: minor
blocking: 否
- 引句:「"merge_init_off": d.get("merge_init_off") or {}} if d.get("kind") == "run" else {}))}」
- file: `scripts/lumos:18571`、`scripts/lumos:18473`
- 規格閘筆記的 WHY 寫「gov 讀帳 merge_init_off 放 run 那筆的 ck、缺欄讀成空字典」,綁的測試是 `t_choice_kill_merge_events_cmd`。這支測試只用 `_ck_gov` 讀原始 jsonl,不經 `cmd_gov`。
- 重現:在 /tmp 副本同時拿掉 `scripts/lumos:18571` 的 `merge_init_off` 那一項,以及 `scripts/lumos:18473` 型別登記裡的 `merge_init_off`。跑 `-k choice_kill_merge_events_cmd` 得 17 passed、0 failed,跑 `-k choice_kill_merge_unclean_code` 得 6 passed、0 failed。
- 沒驗到:我沒跑 `-k gov_` 和全套,不排除別處有測試碰到型別登記。
- 這是觀測欄位,沒有行為後果,所以只算 minor。
- 同族的 `merge_trips`、`merge_reopen` 在 `t_choice_kill_merge_unclean_code` 有「舊帳缺欄讀成空字典」的案例,這個欄位沒有。
- 歸因:有證據的修復回歸不成立。兩版 `scripts/` 完全相同,這條是原有漏查。

**Finding 2:SKIPPED 進通過層沒有測試**
severity: minor
blocking: 否
- 引句:「elif "PASSED" in evs or "SKIPPED" in evs:」
- 我讀了新測試,`SKIPPED` 在 `t_choice_kill_merge_events_order` 的程式與案例裡出現 0 次。
- 把「or SKIPPED」拿掉,被 `@Ignore` 的測試會從通過層掉進未知層,逐支順序跟著變,而測試照綠。我讀碼推得,沒實跑變異。
- 計劃〈用詞〉四層明文寫 SKIPPED 算通過層。影響只限順序,不改判定。
- 歸因:原有漏查。

**三問**
1. 修復(squash 提交,`scripts/` 兩版相同、只改計劃與守檔筆記)有沒有回歸:沒有。文件改動與程式對得上:`_CHOICE_MERGE_HANG_BREAKER=15`、`_kill_merge_trip` 兩計數歸零、重試上限 `min(cap, max(remaining, 1))`、`merge_unclean` 記掛住字樣,都逐項對過。
2. 整份快照有沒有上一輪沒人看的角落:只有上面兩條覆蓋缺口。基準途中逾時會用掛住字樣,`_CHOICE_MERGE_BASE_WHY` 沒有對應鍵,所以印出的字樣少了「合併基準」前綴。這只影響印出的字,記帳的 `merge_off` 仍帶前綴,不夠格標 finding。
3. 新發現修前、修後各是什麼結果:兩條在修前、修後都是同一個狀態,因為程式相同。

**已驗主張**
- **事件行解析效能**
  - claim:事件解析在大輸出上不會爆量。
  - input:500 個測試名、8000 行事件。
  - expected:幾秒內完成。
  - before/after:同一份程式,實測 0.62 秒。
- **參數尾巴被截掉**
  - claim:守檔筆記 PITFALL 的 repro 成立。
  - input:`x.V > foo (bar) FAILED`,名單 `["foo (bar)"]`。
  - expected:failed 為空。
  - before/after:實測 failed 為空,對得上。
- **同名事件**
  - claim:SKIPPED 收尾會進通過層,同名事件只進一層。
  - input:`a STARTED` 接 `a SKIPPED`;`A.t PASSED` 加 `B.t FAILED`。
  - expected:前者在 passed,後者在 failed。
  - before/after:實測符合。
- **逾時判類**
  - claim:逾時有無 STARTED 事件行,分別走另外計數或舊的計數。
  - input:有 STARTED 的輸出和空輸出。
  - expected:`("unclean","逾時(跑到測試後掛住)",False)` 與 `("unclean","逾時",True)`。
  - before/after:實測符合。
- **三個計數路徑**
  - claim:不跳開、第 6 個跳開、恢復後從頭數,三種情形都成立。
  - 依據:讀 `_kill_merge_breaker` 與 `_kill_merge_trip` 的每個分支(啟用中、試探中、跳開、恢復),另核對新測試的 6 個直接呼叫案例。計劃的 S3 條款跟程式一致。
- **重試只在特定條件觸發**
  - claim:只有「找不到 JUnit 結果檔」才重試。
  - 依據:`_KILL_COMPILE_RE` 的 `Compilation error` 區分大小寫,Gradle 的 `Script compilation error` 不會被誤判成編不過,所以拒收腳本會走重試。
- **舊帳與欄位型別**
  - claim:舊帳缺 `merge_init_off` 時讀成空字典。
  - 依據:讀碼確認讀回路徑有 `or {}`,型別登記是 dict。
- **暫存與例外路徑**
  - claim:暫存和例外路徑收得乾淨。
  - 依據:讀 `_isolated_worktree` 的 `scratch=parent` 與 `rmtree(parent)`,腳本寫在工作樹外。`_KillHalt` 在重試前的 `hk.between()` 和 `_kill_merge_base_run` 裡都會往外丟。

**未驗範圍**
- 真 Gradle 的實際輸出格式,只信計劃裡的實測 FACT。
- Windows 的 8191 字元上限:`_kill_merge_ready` 把 init 路徑算進過長判斷,但沒有測試守這一條。
- 全套測試與 `-k gov_`。
- 圖譜固定席節點的合約:沒有一條被這次改動破壞。`bound-tests-gate`、`guard-kill` 和其他固定席宣稱的行為(rc 優先序、`--json` 純度、綁定測試逐支真跑)都不在改動路徑上。
- 這輪沒附「這次新增的殘留」段,也沒附角色卡,所以沒有要逐條答的項目。

我自己建的 /tmp 副本(含 `repo` 目錄)已刪。`/tmp/lumos-seat-work/code-選擇點變異加速第四段/正確性-sonnet/` 底下的 `p.py`、`q.py`、`w` 不是我建的,沒動。

最高 minor,blocking 0 條
