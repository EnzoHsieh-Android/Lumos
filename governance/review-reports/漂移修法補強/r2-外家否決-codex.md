severity: major

## F1 模糊名稱交集仍會把別案卷證自動寫成驗證依據
severity: major
blocking: 是
引句:「範本句「代碼審見 …」只自動填標「兩者」的目錄」
file: `scripts/lumos:27935`

1. 現有 `_drift_c4_evidence` 的「計劃名比對」是子字串判斷：`k in _drift_c4_key(d.name)`，不是目錄名的邊界或精確比對。
2. 例：`plan_refs` 指向 `API_計劃`，同一批提交碰巧加入另一案的 `governance/review-reports/code-rapid/...`；正規化後 `"api" in "code-rapid"` 成立。
3. 該目錄因此同時取得「同提交」與「計劃名」兩種來源，被標成「兩者」，自動填入 `valid_under` 的「代碼審見」句，並隨 `--values` 寫入筆記與修復帳。
4. 「兩者」目前只是兩個相關啟發式的交集，不足以當成可自動落盤的證據。至少要把名稱比對改成有邊界的 token/prefix 規則，或仍要求人選定後才寫入。

## F2 兩個以 `-` 開頭的值會被 argparse 覆蓋，可能靜默少寫一項
severity: major
blocking: 是
引句:「`--values` 的單一項以 `-` 開頭時 argparse 會當成選項:寫成 `--values=-x` 的形式」
file: `scripts/lumos:37589`

1. Spec 只要求 `add_argument("--values", nargs="+")`，沒有 `action="append"`/`"extend"`；argparse 預設採最後一次出現的值。
2. 若合法的新欄位需要兩項 `-x`、`-y`，單次寫成 `--values=-x -y` 時，第二項會被當成選項；自然改寫成 `--values=-x --values=-y` 時，後一次會覆蓋前一次。
3. 若原欄位兩項都含 c4 關鍵詞，既有項目保存檢查不會保護它們；工具最後可只寫入 `-y`，靜默遺失使用者提供的 `-x`。
4. 應定義可無損接收重複 `--values=` 的解析方式，並加入「至少兩個 `-` 起首值」的測試。

## 其餘逐節結果

- 範圍：已讀，無其他 finding。
- 做法 1「c4 卷證目錄」：除 F1 外已讀，無其他 finding。
- 做法 2「c4 走 drift fix 寫入」：除 F2 外，乾淨檢查、鎖內指紋、寫後驗證與修復帳鏈無其他 finding。
- 做法 3「c1 與 settle 訊息」：已讀，無 finding。
- 做法 4「c3 理由」：已讀，無 finding。
- 做法 5「刪除守衛跳過工具自裝檔」：已讀，無 finding。
- 做法 6「文件與測試同步」：已讀，無 finding。
- 條款與回退：已讀；F1 影響 S1，F2 影響 S2，其餘無 finding。
- 實務隱患：不可逆、金流、對外送出、守衛面、資安、效能、併發均已讀；除上述兩項資料正確性問題外，無新增 finding。
- 誠實界線：已讀；`-` 起首值的界線未涵蓋 F2 的多值情境。
- 合約：`Systems/guard-kill` 的兩條 `★INVARIANT★` 分別管 kill 的 rc 優先序與 JSON stdout，本設計未改 kill 執行路徑，判定不影響；`lumos-cli-write` 的原子寫入與寫後自驗仍沿用，判定不影響；其餘 lands_in 未見被破壞的正式合約行。

最高等級:major;blocking 共 2 條