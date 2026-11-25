severity: clean

這份 diff 我沒找到能被利用的洞。

**① 提示注入:已看,無。**
- 新增印字有三處:`_kill_merge_off` 的標準錯誤行、斷路器跳開行「最後一次:{why}」、時限提示。
- 這三處的原因字串全是固定字串或固定代碼。來源是 `_choice_merge_classify` 的固定字樣,以及 `_secev_junit_facts` 回的 `report_unparseable`、`report_too_deep`、`report_malformed`、`evidence_too_large`、`e.code`。
- 結果檔裡的測試名、案例名沒有流進印字。
- 平台名進印字前都過 `_kill_esc`。
- 帳欄位 `merge_kind`、`merge_unclean`、`merge_off` 和 `single_runs` 也是固定詞、平台名、次數或整數。`merge_unclean` 的鍵是固定原因,所以記的是固定詞而非外來文字。
- `_choice_merge_base_cap` 一類的數字欄位只有整數。

**② 讀寫與執行越界:已看,無。**
- 合併失敗名單 `failed` 是 `[m for m in names if _choice_merge_hits(bad, m) > 0]`。它只從原本的 `names` 清單篩,不會把結果檔裡的名字加進去。
- 它只用來排逐支順序,沒有進指令組裝。指令仍由 `_choice_merge_cmd` 用已過 `_test_name_ok` 與名稱碰撞檢查的名字組出。
- 新程式沒有新增檔案讀寫、`shell=True`、下載網址或環境變數覆蓋。
- 測試檔部分:對 patch 內 `_test_` 部分搜過 `shell=True`、`os.system`、密鑰、信箱、網址,沒有可用的憑證。唯一的 `os.environ` 用途是測試內的 `CK_MARK` 標記檔,屬測試自用。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 「一個壞法也合併」只改合併門檻。快篩通過時交出的是 `survived` 列,survived 會擋推送,所以這步只會多擋、不會多放。
- 快篩失敗、沒跑乾淨或編不過都走 `single`,由逐支流程重判。
- 先紅順序只重排 `_kill_merge_failed_first` 交出的順序,不判任何事。名單空或一支都對不到時維持原順序。
- 逐支判定靠 `rows` 的 `recipe_id` 與平台對回,不依賴順序。
- `single_runs` 的 `_single` 標記只影響統計。
- 新增的 `_single` 鍵已加進 `--json` 輸出要濾掉的鍵,不會漏到輸出。
- 沒看到按一次 Ctrl-C、檔名帶空白或殘留 `LUMOS_SKIP_*` 就走過守衛的新路徑。

**涵蓋範圍:**
- patch 全部 8 個 diff 區塊的程式部分:`scripts/lumos` 完整讀過;`scripts/test_lumos.py` 只對 patch 內該部分做了關鍵字掃描,沒有逐行細讀。
- 筆記與計劃文件(`Projects/*_計劃.md`、`guard-kill.md`、`規格閘.md`)只看了 diff 區塊的位置與標題,沒有細讀內容。
- 真代碼只讀了 `scripts/lumos` 裡 `_secev_junit_facts` 的回傳值與 `_CHOICE_MERGE_BASE_WHY` 的定義。

最高 severity:clean
