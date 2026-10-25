severity: major

## 1. 分層與依賴方向

結構大致對得上,但呼叫方向有一處跟鄰居相反。

- 鄰居的分工是範本腳本碰裝置、只產出檔案,lumos 事後讀檔判定。收集腳本自己的家節點寫明不負責判過不過、判定在 `lumos macrobench --stability`(`Systems/android-stability-collector` 的 responsibility)。本計劃在腳本最後呼叫 `lumos android-e2e judge`,是範本腳本反過來呼叫 lumos,依賴方向多了一條。計劃的 WHY 說「跟記憶體收集同一個分工」,這句只對一半。見 A5。
- `code-loop check` 新判定的位置合鄰居。安全證據那道排在放行早退之前(`scripts/lumos:64131`),判定本體在獨立函式 `_codeloop_security_step`(`scripts/lumos:64307`)。計劃要排在放行早退之前,這點一致。
- 計劃說「改到管的那支判定入口」,看起來是直接改 `cmd_code_loop`,沒提獨立的步驟函式。見 A6。

## 2. 命名與錯誤處理

- **子命令形狀:** `macrobench` 的設定檢查是旗標 `--check-config`(`scripts/lumos:66674`)。`code-loop` 用位置參數子命令(pass、skip、check)。`android-e2e` 取位置參數子命令,有前例,算對得上。
- **`check` 沒有定義:** 計劃列了 `check` 子命令,全文沒說它做什麼。它跟 `code-loop check` 同名,容易混淆。
- **放行指令形狀:**
  - 鄰居 `lint-waive <指紋> --note`(`scripts/lumos:37721`、`37748`)是頂層指令,擋下訊息會把指紋填好。
  - 計劃是 `android-e2e waive --note`,預設放行目前提交,沒有指紋參數。
  - 理由長度:`lint-waive` 只要求非空(`scripts/lumos:37764`);本專案其他人裁理由用 10 字(`scripts/lumos:22180`、`22236`)。計劃的 10 字跟後者一致,跟同類的 `lint-waive` 不一致。
  - 見 A3。
- **回傳碼:**
  - `check` 回 1 擋、`check-config` 回 2,跟 `macrobench --check-config` 一致。
  - 計劃說判定自己出錯時「照 code-loop check 既有做法回 2」,不太準。`check` 內部出錯其實走 `_gate_failopen` 記帳後放行(`scripts/lumos:63137`、`64129`),rc 2 在 docstring 裡是參數錯(`scripts/lumos:64759`)。
  - pre-push 對非 1 放行屬實(`scripts/hooks/pre-push:626`)。
  - CI 對任何非零都紅,不是「要實作時確認」(`.github/workflows/ci.yml:221`、`260`)。
  - 見 A6。
- **紀錄位置:** `.lumos/e2e-records/` 與既有的 `.lumos/receipts/<run-id>/` 並存,見 A2。

## 3. 第二種做法

有三處引入了專案已有同功能的另一種做法。

- **另一種綁版本的算法(A1):** 見 A1。
- **另一種紀錄格式與位置(A2):** 見 A2。
- **另一套放行與設定(A3、A4):** 見 A3 和 A4。

## 4. 落點合不合理

- 新開 `Systems/android-e2e-acceptance` 合理:它要管 `android-e2e-run.sh` 與新子命令,收集腳本的家不負責驅動與判定,放不進去。
- 另外三個落點有問題,見 A7。

## A1 紀錄綁內容指紋,是第二種「留痕綁版本」的算法
severity: major
blocking: 是
引句:「紀錄綁 App 程式目錄的內容指紋,不綁提交編號」
對照:
- code-loop 留痕與表態一律綁提交(同一個提交、或祖先且中間只動簿記檔),見 `Systems/pitfalls-code-loop` 的 PITFALL「壓提交或 rebase 之後留痕失效」。
- 安全證據閘已有「收據自帶的 sha256 對被推提交樹同一路徑的檔」的比法(`scripts/lumos:8946`、`8969`、`8980`),判的是「這份證據對不對得上被推的那棵樹」,功能同本計劃。
- 計劃自建「整批檔案路徑加內容算一個 sha256」,沒說為什麼不沿用逐檔比法。
- ⚠ 交編排者:計劃的壓提交理由是真的,鄰居也為此吃過虧。但它是推翻鄰居慣例,應寫成明確的決策,說明跟安全證據閘的逐檔比法為何不同。

## A2 另一份進版控的查證紀錄,與既有收據目錄重疊
severity: major
blocking: 是
引句:「同一個指紋再跑一次就覆蓋成新的那份」
對照:
- 既有收據是 `.lumos/receipts/<run-id>/`,含 `manifest.json`、`report.md` 等,進版控(`skills/lumos-android-evidence/reference.md:3`、`SKILL.md:23`)。
- 計劃另開 `.lumos/e2e-records/<指紋>.json`,用 run-id 以外的鍵,還用覆蓋寫。
- 計劃在 `related` 與 PRIOR-ART 都沒提收據,也沒說為什麼不把 E2E 摘要放進收據、再讓判定去找。
- ⚠ 兩者用途不同(診斷證據對閘的輸入),可能有理由分開,請計劃寫出來。

## A3 放行指令與記帳用了跟 lint-waive 不同的形狀
severity: minor
blocking: 否
引句:「治理帳記一筆 `android-e2e-waive` 事件」
對照:
- 鄰居記帳是 `_gate_event_or_warn(repo_root, gate名, "waived", note, hard=False)`(`scripts/lumos:37773`),閘名加事件種類兩欄。計劃的 `android-e2e-waive` 把兩欄併成一個字串。
- 放行人鄰居取 `$USER`(`scripts/lumos:37768`),計劃取 git 設定的使用者。
- 鄰居放行存在獨立的 `.lumos/lint-waivers.json`;計劃把放行寫進被覆蓋的紀錄檔,同指紋重跑就沒了。這一點是行為問題,留給別的審查員。

## A4 另開設定檔,且 package 與 adb_serial 跟 macrobench.json 的 stability 段重複
severity: minor
blocking: 否
引句:「App 套件名(只收英數字、底線與點,跟收集腳本同一個規則)」
對照:
- 鄰居把記憶體與穩定性做成 `.lumos/macrobench.json` 的 `stability` 段,不另開檔。
- `stability` 段已要求 `package`(`scripts/lumos:39452`、`39455`)與選填 `adb_serial`(`scripts/lumos:39475`)。
- 計劃的 `android-e2e.json` 又定義一份 `package`、`adb_serial`,同一個值有兩處來源,容易不一致。
- 另開一個檔當開關,結構上可接受,`lint.json` 也是這樣。重複欄位才是不一致。

## A5 範本腳本反過來呼叫 lumos
severity: minor
blocking: 否
引句:「腳本最後呼叫 `lumos android-e2e judge <run 目錄>`」
對照:
- 收集腳本只寫 `stability.json`,不呼叫 lumos,見 `Systems/android-stability-collector` 的 responsibility 與 `scripts/templates/android-stability-collect.sh`。
- 這是新的依賴方向:範本腳本要求裝置那台機器裝有相容版本的 lumos。
- ⚠ 不算跨層直呼(judge 只判定,不碰裝置),所以標 minor。

## A6 code-loop check 新判定:接線清單不全,出錯路徑描述與既有做法不符
severity: minor
blocking: 否
引句:「改到 [[Systems/pitfalls-code-loop]] 管的那支判定入口」
對照:
- 安全證據那道是獨立函式,經 `kg.hit(..., reason_kind=...)`、`_cl_say_block` 的種類分支(`scripts/lumos:64877`)與 `--keep-going` 的 LUMOS-BLOCKS 機讀行(`scripts/lumos:64869`)接進去。
- pre-push 有一張寫死的「LUMOS-BLOCKS 種類對照表」(`scripts/hooks/pre-push:135`),CI 擋下訊息列了原因清單(`.github/workflows/ci.yml:224`)。
- 計劃只說改「判定入口」,沒列新種類、`_cl_say_block`、pre-push 對照表、`ci.yml` 訊息、docstring 與 help 裡的「五道」(`scripts/lumos:64758`、`66855`),漏改會讓新擋下查不到原因句。
- 出錯路徑見第 2 問。

## A7 lands_in 兩個落點沒有對應的改動,且把判定細節塞進一個很大的節點
severity: minor
blocking: 否
引句:「`code-loop check` 多一道判定,排在放行早退之前:改到 [[Systems/pitfalls-code-loop]] 管的那支判定入口。」
對照:
- `Systems/pitfalls-code-loop` 已有 290 行、約 20 行 KEY、沒寫負責範圍,管 `scripts/lumos`。鄰居的做法是閘的細節放自己的節點:`Systems/安全證據閘` 的 responsibility 明寫包含「code-loop check 的安全證據那一道」,`Systems/棧別提問表態閘` 同樣獨立。本計劃應照做:判定細節寫進新的 `android-e2e-acceptance`,`pitfalls-code-loop` 只加一句連結。
- `Systems/macrobenchmark-adapter` 與 `Systems/android-stability-collector` 列在 lands_in,但計劃明說「既有判定的程式碼不改」。換 Maestro 驅動只是設定,收集腳本照舊。除非計劃寫出這兩篇要補哪些說明(例如 Maestro 驅動、`stability_unjudged` 被當成「沒判到」),否則不該列。

不對齊共 7 條,其中重大 2 條
