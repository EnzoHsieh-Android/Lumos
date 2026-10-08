severity: minor

## Findings

### delivery-資安-security-archives-codex-F1

severity: minor  
blocking: 否

引句:「+{"event": "header", "ts": "2026-10-06T17:47:06+00:00", "root_decision_id": "Systems/guard-kill.md#d1", "node": "Systems/guard-kill.md"}」

觀察：`archive-index.txt` 第 968 筆把這支檔分類為「historical fixed research or audit receipt」，但它其實是有效中的 `rel-cascade` 治理帳。`doctor` 會枚舉並解析所有 `governance/rel-cascade/*.jsonl`；這筆合法 header 且沒有 transition，會進入「尚未處理的連鎖單」狀態。CI 又會執行 strict doctor。因此它不是靜態封存證物，而是 active control input；將它放入封存索引會讓封存驗收錯誤地宣稱全數資料皆為惰性歷史材料。

是否本批新增：是，凍結 patch 顯示 `new file mode 100644`。

file: `scripts/lumos:2583`  
file: `scripts/lumos:2591`  
file: `scripts/lumos:2595`  
file: `.github/workflows/ci.yml:170`

影響：目前內容沒有秘密或命令注入，也不會直接執行程式；問題是分類與責任邊界錯誤。應從 archive index 移除並交由 active-controls 鏡頭驗收，或把分類改成「CI/doctor 會消費的 active governance ledger」。

## 四條攻擊路徑

1. 秘密外洩

   - 入口：1,131 支新增封存檔。
   - 解析：逐檔大小及 SHA-256，並掃描 private key、AWS、GitHub、Slack、Bearer 與含密碼 URL 樣式。
   - 敏感落點：版本庫、CI log 或後續散布。
   - 結果：文字及原始位元組掃描沒有命中；但 9 支 Git bundle 的壓縮物件未解包，不能宣稱 bundle 內完整秘密掃描已完成。

2. 結構化資料注入

   - 入口：`.json`、`.jsonl` 與派工／修正紀錄。
   - 解析：`json.loads`、loop roster、fix-check、rel-cascade reader。
   - 敏感落點：治理狀態、測試選擇與 CI doctor。
   - 結果：發現 F1；`rel-cascade` 被錯列封存資料。其目前值合法且沒有命令字串。

3. 命令或程式執行

   - 入口：`.patch`、`.diff`、`.bundle` 及 fix-record 測試名稱。
   - 解析：檢查 source/CI 是否呼叫 `git apply`、`git am`、bundle import 或直接執行封存檔；另讀 fix-check 的測試名稱驗證與執行路徑。
   - 敏感落點：shell、Git 工作樹及測試 runner。
   - 結果：未找到 CI 自動套用 patch、匯入 bundle 或執行封存檔的路徑；fix-check 是人工子命令，測試名稱須先通過索引與方法名驗證，方法參數會 shell quote。無 finding。

4. 終端與紀錄注入

   - 入口：派工 JSON、報告文字及帳本欄位。
   - 解析：roster/status 訊息輸出到本機終端或 CI log。
   - 敏感落點：ANSI 控制、偽造行或終端控制序列。
   - 結果：非 bundle 檔未發現 NUL、ESC 或其他異常控制位元；9 個有控制位元的檔案全部是二進位 Git bundle。無實際注入 finding。

DoS 依派工要求未列報。

## 封存完整性

- 1,131 筆索引皆為唯一相對路徑。
- 全部存在、為一般檔，工作樹權限 `0644`、Git mode `100644`。
- 大小與 SHA-256：1,131/1,131 相符。
- 無 symlink、路徑穿越、shebang、`.py/.sh/.js/.ts` 或可載入設定副檔名。
- 1,130 筆對應本批 `governance/review-reports/**` 或研究封存根。
- 唯一越界項是 F1 的 `governance/rel-cascade/*.jsonl`。
- 個別封存檔未逐字全文閱讀；不能把上述 inventory、雜湊及機械掃描視為全文語意審查。

## 圖譜固定席

- `Issues/canary-record未落盤事件`：不影響；F1 走 `rel-cascade` reader，沒有寫入或改變 canary-record 落盤路徑。
- `Systems/lumos-cli-read`：不影響；沒有改變 search 的 superseded/stale 篩選。
- `Systems/design-loop`：不影響；沒有改變設計審材格式或條款綁定判定。
- `Systems/pitfalls-code-loop`：不直接影響；封存副檔名沒有被當程式碼掃描，F1 是 archive 分類錯誤，不是 tier 計算錯誤。
- `Systems/bound-tests-gate`：不影響；沒有改變合約測試的選取、執行或 rc。
- `Systems/guard-kill`：間接影響；F1 的 `root_decision_id` 指向 `Systems/guard-kill.md#d1`，使它成為尚待處理的連鎖帳，但未改變 guard-kill 的 rc 優先序或 JSON stdout 合約。
- `Systems/授權與歸屬`：不影響；封存檔均非 vendored toolkit，沒有 LICENSE 刪除或 SPDX 執行邊界。
- `Systems/測試假綠形態`：不影響；本席沒有依封存測試收據主張測試殺傷力，僅核對檔案與消費路徑。

鏡頭第 32–52 行只列節點名稱、沒有合約內容；依鏡頭規則未把它們冒充已讀合約。

## 閱讀量與限制

- 規則：265 行（兩份 skill 164 行、`CLAUDE.md` 101 行）；另已讀使用者內嵌派工與 AGENTS 規則，但其無本地行號，未混入精確計數。
- graph lens：57/57 行完整。
- 凍結 patch：直接語意閱讀約 35/323,633 行；全檔僅做 diff 邊界機械掃描。
- archive index：1,131/1,131 筆均由解析器核對；原文只抽讀前段及第 968 筆，不能算逐字全文。
- 上下游 source/CI：直接閱讀約 916 行。
- 搜尋輸出：約 765 行。
- 重讀：約 177 行。
- 保守合計約 2,300 行，超過 1,800 行上限；原因是兩次搜尋輸出意外膨脹並遭工具截斷。超限後已停止擴大範圍，未宣稱完整覆蓋。
- 未讀：`full-branch.patch` 其餘約 323,598 行、1,130 支封存檔的逐字全文，以及 9 支 Git bundle 的解包物件內容。指定席工作目錄不存在且環境唯讀，因此未建立工作樹解包 bundle。