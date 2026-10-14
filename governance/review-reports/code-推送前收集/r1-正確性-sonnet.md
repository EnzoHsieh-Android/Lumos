severity: minor

正確性席結論:沒找到「某道擋下被吞掉、變成放行」的路徑,只有 1 條 minor。

我做了三件事驗證。
- 讀了掛鉤、主程式兩份 patch,並對照工作樹 `a9362d4c`。
- 用 `/bin/bash`(3.2.57)搭假 `scripts/lumos`,實跑整支掛鉤。測了:簽名擋下(AV=1)、代碼審 rc1 並帶 `LUMOS-BLOCKS:`(CL=1)、全過(AV=0)、`push-summary` 回非零(PS=3)、兩者並發(AV=1 CL=1)。除全過回 rc0 外全是 rc1。
- 單獨實跑 `push-summary`(正常、暫存檔不存在、`--count` 非整數)與 `code-loop check --help`。

severity: minor
blocking: 否 — 只改變「pitfalls 自己壞掉」這種罕見情境的結果,而且是往更嚴的方向
引句:「keep_going 下 pitfalls 失敗:表態要它的資料、代碼審留痕要 tier,照現在 fail-open 不判;新增告警閘只看範圍,照跑;前面記下的擋下照算」
問題:掛鉤只要認得 `--keep-going` 就一律帶上它,所以掛鉤實際走的路徑跟不帶旗標的路徑不一樣。不帶旗標時,`pitfalls` 失敗(回非零、沒吐 JSON、例外)會在跑到新增告警閘之前就 fail-open 放行。帶旗標時,同樣情境會多跑新增告警閘(`_lint_step`),它判擋就整體擋下。
失敗情境:`pitfalls` 暫時失敗(逾時、環境壞)且這次改動帶進新告警。舊掛鉤放行;新掛鉤擋下,`LUMOS-BLOCKS: lint_new`。直接跑 CLI 不帶旗標則仍放行。
補充:這是有意的設計,註解寫得很清楚,方向也是更嚴而非放行。問題是計劃與測試有沒有明講這個差異。我沒找到能把行為釘住的測試,但沒逐條對 tests patch。
佐證:file: `scripts/lumos:51395-51399`

## 逐項檢查(已讀,無 finding)

- **9 道閘的記錄點**:anchor、anchor-baseline、doctor、home、note-shape、spec-gate、code-loop、drift、reread 全都改成記錄後繼續。全套測試之前的 `exit 1` 只剩缺 python3.14、缺暫存目錄(早於所有閘),另一處在統一判斷點之後(`pre-push:682`)。
- **`_PP_BLOCKED` 旗標**:所有 `pp_record_block` 呼叫都在主 shell,沒有管線或子 shell,旗標和筆數不會被吞。判斷點只看這兩個記憶體純量,寫暫存檔失敗不影響擋下。判斷點之前沒有 `exit 0` 能繞過它(早期的 `exit 0` 都在 anchor 之前)。
- **統一判斷點的位置**:在 ref 迴圈之後、建全套測試 log 檔之前。迴圈內的 `continue` 只會跳過該 ref 後面的閘,不會跳過判斷點。
- **`_fin` 與 8 個放行站點**:逐一對過 `return`。放行站點是 `HEAD sha` 取不到、`merge-base == HEAD`、`merge-base` 算不出、`_lens_push_base` 為 None、pitfalls 失敗、`tier != high`、有效留痕(兩處)。擋下站點(合約測試、表態、告警、審查留痕兩處)也都經 `_fin`。env 跳過與合併側放行是 `_codeloop_review_block` 的回傳,最終也經 `_fin`。八個站點在 `blocks` 非空時都會回擋下,蓋不掉前面記下的擋下。合約測試第二次(advisory 遇到 tier=high)與第一次互斥,不會重複記。
- **`LUMOS-BLOCKS:` 解析**:rc1 時不論該行在不在、解析出幾筆,至少記一筆,實跑確認。空欄、逗號後空格都有處理。stdout 與 stderr 合流時,該行是整行輸出,`grep '^…'` 抓得到。
- **版本探測**:新版 `code-loop check --help` rc0 且含 `--keep-going`。舊版不帶旗標,rc1 時退回通用原因記一筆。
- **`push-summary` 退路**:回非零或不存在都走 `pp_plain_summary`,之後一律 `exit 1`。暫存檔不存在時,`--count` 仍會顯示總筆數並說明有幾筆沒寫進暫存檔,實跑確認。`--count` 非整數回 rc2,走退路。
- **中斷陷阱**:INT/TERM 已拆開,先收背景工作再 `exit 130/143`,EXIT 陷阱照常清暫存。實測 TERM 後背景 `sleep` 被收掉、rc=143。12 個 `pp_stop_if_signaled` 清單與實際呼叫點一致。
- **bash 3.2**:`${1//[$'\t\n']/ }` 在 3.2.57 實測可用,未使用空陣列展開。
- **資料狀態五問**:
  - 空:無暫存檔或空欄寫 `-`,正常。
  - 舊:暫存檔每次推送用新的 `mktemp -d`,不會讀到上次的內容。
  - 重複:同一道閘多個 ref 各記一筆,閘數去重。
  - 並行:每次推送各用各的暫存目錄,不互相碰。
  - 損毀:欄位數不對的行 Python 端略過,筆數以 `--count` 為準。

## 附帶觀察(不算 finding)

- 擋下改成收集後,簽名沒過或 home 擋下時仍會往下跑合約測試等昂貴的步驟,等待時間變長。這是設計取捨;`pp_plain_summary` 對 anchor 有提示。

最高等級 minor,blocking 條數 0。

我的暫存實驗目錄已刪。
