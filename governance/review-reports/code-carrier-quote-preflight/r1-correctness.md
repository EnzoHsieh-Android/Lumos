severity: minor

### G1 — 新增圖譜敘述缺少機器可讀欄位

severity: minor  
blocking: 否  
引句:「PITFALL: 載體報告尾端非法 UTF-8 可被替換字元掩蓋」  
file: `docs/lumos-toolchain-knowledge/Systems/canary-audit.md:183`

輸入：新增的 `WHY:` 與 `PITFALL:` 敘述進入圖譜檢查或後續檢索。  
錯誤：第 181 行 `WHY:` 缺 `[出處:]`、`[因:]`；第 183 行 `PITFALL:` 缺 `[出處:]`、`[根因:]`，測試也只寫成反引號文字而非 `[test:]`。依本 repo 的圖譜格式合約，這些欄位必須機器可讀；目前形狀會被 lint／提交檢查提醒，且測試關聯無法被結構化消費。  
可運行證據：唯讀 PCRE 查詢實際命中且僅命中這兩條新增敘述；本席未執行可能寫治理帳的 `lumos lint`。

### 核對摘要

- 完整逐行讀完 `r1-source.patch` 331 行與 `r1-graph.patch` 314 行；兩者均與固定版本差異的 `-U10` 輸出精確一致。
- `cmd_canary` 的同份 raw bytes 解碼／hash、換檔拒收、LF/CRLF、`-O`、非載體 replace 策略及 literal `none` 路徑，未發現 delta 缺陷。
- 固定席逐條核對：
  - `design-loop`：未違反處置閘第五步合約。
  - `bound-tests-gate`：四個新測試名稱存在；本席未重跑測試。
  - `guard-kill`：無相關行為變更。
  - `授權與歸屬`：未改授權白名單或檔頭。
  - `測試假綠形態`：新測試具現場前置斷言；換檔測試另確認替換確實發生。
  - `lumos-cli-read`：無相關行為變更。
- 未跑全套或子集；測試數字僅按指定收據與程式結構核對，未重新宣稱通過。

最高級：minor；blocking：0。