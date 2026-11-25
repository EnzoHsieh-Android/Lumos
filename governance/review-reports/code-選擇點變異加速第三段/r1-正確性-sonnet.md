severity: minor

我假設半開狀態機、量基準新估算、拒收代碼字串和新帳欄位各有一個壞輸入,逐條找過,沒找到會做出錯行為或弄壞資料的 bug。只有兩條 minor。

我在複製出來的 repo(`19e1f2c19`)跑了四支相關測試(`half_open`、`budget_edge`、`unclean_code`、`breaker`),都綠。再各改壞一道檢查,測試都會紅:

- 試探中不累計計數類原因:紅 1 項。
- 拿掉「只量一支」的保險:紅 2 項。
- 讓試探遇到沒跑乾淨也算恢復:紅 4 項。

1. 只量了一支就收手時,時限提示的「約需幾秒」用單價估,沒用剛量到的實測。
引句:「        c.merge_need = (len(uniq), avg * len(uniq) * _CHOICE_MERGE_BUDGET_K)」
- 場景:四支守衛測試,第一支冷編譯 27.7 秒,剩下時限 40 秒。`measured` 只有 1 支,`rest` 為空,`avg` 退回 `_CHOICE_MERGE_UNIT_SECS`(10 秒)。
- 結果:緊接著的「只量一支」保險回 False,印出的提示是「約需 60 秒」,而 `--max-seconds` 是照這個數算的。實際照單價估的值跟剛量到的第一支耗時脫節。
- 影響:只影響標準錯誤那行提示的數字,不影響合併與否的判定。
- 計劃 S7 的條款沒涵蓋這個分支。
file: `scripts/lumos:29010`
severity: minor
blocking: 否

2. 「只量一支」的保險拿第一支(含冷編譯)的耗時當門檻,跟計劃 WHY 的立場有一點矛盾。
引句:「        if len(measured) == 1 and mg.remaining() < measured[0] * _CHOICE_MERGE_BUDGET_K:」
- 場景:第一支 27.7 秒(冷編譯)、真正單支約 5 秒,剩下時限在 27.7×1.5≈41 秒以下。
- 結果:雖然 5 秒一支其實量得完,仍收手、這個平台組不合併。
- 影響:這是時限極緊時的邊界退化,實際影響很小。計劃已把這一條寫成實作補丁,測試也釘住了,所以只標 minor。
file: `scripts/lumos:29048`
severity: minor
blocking: 否

以下幾處我試過,判定沒問題:

- **半開狀態機:** 試探前要先累計滿 10 個、第 11 個才試。試探通過或有失敗才恢復,恢復時 `streak` 歸零、`reopen` 加一。編不過、計數類沒跑乾淨、非計數類沒跑乾淨都維持停用,不印恢復行、不再跳開。恢復後再跳開會重新數 5 次。時限不夠這類不合併原因在進迴圈前就整串交出,不會試探。
- **計數一致:** `tripped` 與 `trips` 在同一處設值,兩者一致。
- **試探途中收到中斷訊號:** `_kill_merge_screen` 會丟 `_KillHalt`,run 那筆不會被誤記。
- **拒收代碼對舊讀者:** 全 repo 沒有任何地方用「結果檔讀不出來」做字串相等比對。`_CHOICE_MERGE_BASE_WHY.get(why, why)` 找不到鍵就原樣印出。`merge_unclean`、`merge_off` 只是原樣記帳。
- **新舊互讀:** `_GOV_FIELD_TYPES` 已登記三個新欄位。`gov` 讀帳對缺欄的舊帳都補成空字典,按 `kind` 分在壞法那筆與 run 那筆,位置正確。
- **寫一半:** `merge_why` 每個壞法跑完就寫,中途停掉也留得下。`merge_trips`、`merge_reopen` 只在 run 那筆,中途停掉會遺失。計劃已寫明這個取捨。
- **`_secev_junit_facts` 的代碼:** 都是固定字串,代碼本身不夾路徑或任意文字。

圖譜鏡頭(固定席逐條):

- `bound-tests-gate`:不影響。這次改動沒碰 `code-loop check` 的跑綁定測試邏輯。
- `測試假綠形態`:不影響。新的翻紅測試都帶前置斷言,例如先確認「跑合併的壞法編號」。
- `lumos-cli-read`:不影響。`search` 沒被改。
- `pitfalls-code-loop`、`loop-convergence-recording`、`design-loop`、`lumos-cli-lifecycle`:不影響。改動不經過這些路徑。
- `guard-kill`:不影響。計劃寫明沒傳 `merge` 時行為不變。
  - rc 優先序(survived→rc1、drifted/abort/error→rc2)沒動。
  - `--json` 純度沒動:恢復那行與跳開那行都走 stderr。

暫存已清掉:`gctl-run-t4dv9658`、`gctl-run-1ey0makc`、`gctl-run-n07dayht` 與我的複製 repo(刪前 `lsof +D` 確認無程序開著)。

最嚴重等級 minor,blocking 0 條。
