severity: minor

## 代碼審查席報告:整合(合約與圖譜一致/知識同步)r2

**席名:** code-資安護欄唯讀盤點/r2/整合-sonnet
**範圍:** 修前 20293afe,修後 aadf6b07

派工詞指到的共用派工詞 `scratchpad/code-seat-common.md` 當時找不到,我先只照整合.txt 與 r2-intake.md 做。這份報告是補回該檔後,只依其〈輸出格式〉重排的版本,內容不變。

### 結論

- **阻擋推送的 finding 沒有。**
- 本席實測的合約與行為(S1 到 S13、d1 七處、d2、d3、錯誤種類對照表、母計劃 d8 與 d9 的敘述)都和程式一致。
- 抓到 4 條知識同步上的落差,都是文字沒跟上程式,不影響程式行為。
- **範圍外的觀察(補一條):** `scripts/lumos` 在 `_secinv_select_vault` 之後留了連續 25 個空行(修前最多連續 5 行,修後 26 行)。專案 ruff 設定沒選 E3,不會被擋,是重構刪碼後的殘留。

### 實測指令與結果(修後 aadf6b07)

| 指令 | 結果 |
|---|---|
| `python3.14 scripts/lumos doctor --ci` | rc 0,「圖譜健康 0 issues (907 篇)」 |
| `python3.14 scripts/lumos note-shape --diff 20293afe..aadf6b07` | rc 0 |
| `lumos lint` 對子計劃、母計劃、`Systems/lumos-cli-read`、Verification 四篇 | 都是 0 問題 |
| `lumos spec-gate 資安護欄唯讀盤點_計劃` | 13 條全綁、全綠,相依回歸 `t_search_forget_superseded` 綠 |
| `test_lumos.py -k seclist` | 280 passed、0 failed |
| `-k fence` | 49 passed |
| `-k search` | 177 passed |

- **`doctor` 提醒但與本案無關:** 它提醒 `lumos-cli-read` 的 `self_audit` 比 `updated` 舊,也有一條連到 stale 驗證的連結。
- **search 合約沒被破壞:** `Systems/lumos-cli-read` 的 search 合約(不排除 stale)沒被碰,`search` 相關測試全綠。
- **`load_vault` 本體沒動:** `load_vault` 只多了一段 docstring。

### Finding

**F1 子計劃「實務隱患」沒寫列舉總項目 50000 的新上限**
severity: minor
blocking: 否
引句:「_VAULT_SAFE_ENTRIES_MAX = 50000                 # 列舉的總項目數上限(含非 .md 與目錄;代碼審 r1 資源席:只限 .md 時 30 萬個 .txt 吃掉 260MB)」
file: `scripts/lumos:634` 錯誤種類 `enumeration_failed`;子計劃 `Projects/資安護欄唯讀盤點_計劃.md` 的〈資源與效能〉只寫「單檔 2MiB、64MiB、Markdown 檔案數 10000」。
- 失敗場景:cli-read 說上限值「單源是計劃」。三個月後接手的人只讀計劃,不知道存在這道上限。含大量非 .md 項目的圖譜會被擋下並退出 2,看起來像莫名其妙的錯誤。這個上限也沒有對應的 S 條款。
- 歸因:有證據的修復新增項。修前 `grep 50000` 沒有這個常數,修後有。

**F2 子計劃說「schema 與 S1 到 S13 條文未改」,但輸出契約其實加了東西**
severity: minor
blocking: 否
引句:「schema 與 S1–S13 條文未改，既有凍結卷證保持原樣」
file: `docs/lumos-toolchain-knowledge/Projects/資安護欄唯讀盤點_計劃.md:56`(同一句在子計劃該段)。
- 失敗場景:實測修後 JSON 多了 `references_valid`、每個入口列上的 `invalid_reference_control_ids`、錯誤種類 `vault_selection_failed`,並改了「已登記」的語意(d3)。這些新行為只寫在 `lumos-cli-read` 的 WHY 與子計劃「輸出補充」段,S1 到 S13 都沒有條款。`invalid_reference_control_ids` 實際放在 `coverage.surfaces[]` 的每列,補充段沒講位置。
- 歸因:有證據的修復新增項。
- 修前修後對照(探針 P7,引用的決策不存在):

| 版本 | `coverage.unmapped` | 入口列 `invalid_reference_control_ids` | `references_valid` |
|---|---|---|---|
| 修前 | `[]`(入口顯示已映射) | null | null |
| 修後 | `["S-pay"]` | `["C1"]` | `[false]` |

**F3 Verification 的舊段落沒標成已被取代,數字也對不上**
severity: minor
blocking: 否
引句:「實作後:`python3.14 scripts/test_lumos.py -k seclist` 14 支、203 條斷言全綠」
引句:「新測試 8 支(g1_field_type_fuzz」
- 檔案:`Verification/2026-10-19_資安護欄唯讀盤點實作.md`。
- 失敗場景:
  - `git diff` 只新增 7 支 `def t_seclist_*`,第 8 支是改寫,不是新增。
  - 目前 `-k seclist` 是 280 條斷言通過。
  - 故障變體表標「最終版程式」,病態輸入的數字也是第一版程式量的。
  - frontmatter 的 `valid_under` 仍釘「起點 Lumos/main 7d38774c」。
  - 接手的人會把舊表當現況。
  - 新增段落裡「32 種變體」「八席 34 條」我沒有重跑,也沒讀 r1 卷證核對,**未判定**。
- 歸因:有證據的原有漏查,是文件沒跟著更新。

**F4 母計劃有一處過期句,`updated` 沒更新**
severity: minor
blocking: 否
引句:「Q3已依d8核可，OD-01／OD-02的P1故障與還原證據已收」
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:378` 的 P0 步驟清單「解 Q1–Q3；確認真正隔離環境…」(這一行不在審材 diff 內)。
- 失敗場景:
  - 該處的 Q3 已依 d8 決定,但這句沒改成歷史語氣。
  - frontmatter `updated: 2026-10-18` 沒跟上 10-19、10-20 的修改。
  - d8、d9 的敘述本身都和程式與決策欄位一致。
  - P1 證據只寫「order-demo 的 Verification/2026-10-19_訂單所有權故障翻紅與還原」,引用方式合規,我沒跨 vault 去猜內容。
- 歸因:未判定。

### 三問回答

**① 原問題的修復效果有何行為證據**

我把修後的 `test_lumos.py` 複製到修前的臨時工作樹,對修前的 `scripts/lumos` 跑,再同樣跑修後,算同一案例的修前修後對照:

- **G1、G2、G3、G7、整合①(`t_seclist_integration_gaps`):**
  - 修前紅、修後綠。
  - 整合①的修前斷言訊息是「撤銷決策的護欄」仍顯示 `mapped`,修後不再。
  - 用我自己的探針腳本再驗(case_source:本席獨立造的,input/expected 取自計劃與 d3 條文):空登記塊加 `flag/security-relevant` 標籤的節點,在修前不在 `unregistered_nodes`,在修後有出現。
- **`--vault` 指向非圖譜目錄(`--json`):** 修前 rc 0、`errors` 為空;修後 rc 2、`errors` 為 `vault_selection_failed`,頂層欄位與正常輸出一致。
- **JSON 輸出遇孤立代理字元:**
  - 修前 rc 1,traceback 是 `UnicodeEncodeError`。
  - 修後 rc 2,並輸出單一可解析 JSON。
  - 另造 `\u202e`、`\u2028`、`\u0007`:修後 JSON 原文逐字是 `\u202e` 之類的跳脫,rc 0,符合文件說法。
- **`t_seclist_g4_read_guards`、`g8_read_request_bound`、`s03`、`s08`:**
  - 這四支在修前是紅的,但原因是舊程式沒有 `_vault_safe_read_rel`(AttributeError),不是行為證據。
  - G4 行為面的修前證據:非圖譜目錄 rc 0(上一條)。
  - 圖譜根是捷徑時,修後 rc 2、`vault_selection_failed`;**修前我沒有對照**,**未判定**。
  - 中間目錄被換成捷徑的修前行為我沒測,**未判定**。
- **`t_seclist_g8_key_rules`:** 修前在舊程式上綠,和 Verification 說的「G8 本來就對」一致,這支是補測試判準,不能當修前紅。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立(preserve)**

preserve 的修前證據在 intake 全標未判定,以下是我獨立補的:

- **正常登記(探針 P9):** 修前修後都 rc 0、`evidence_check` 是 `declared_only`、`security_verdict` 是 `not_assessed`。
- **d1 七處保守做法:** 修前修後的輸出一致,修前修後都用同一組探針:
  - 零登記:rc 0,`registration_complete` 為 false。
  - 只有候選的入口:同時列在 `unmapped` 與 `candidate_only`。
  - 圖譜內有捷徑:rc 2、`symlink_rejected`。
  - 例外過期:rc 0,記 `exception_expired` 問題。
  - 例外引用的決策作廢:rc 2、`reference_error`。
  - 決策路徑大小寫不同(`systems/slpay#d1`):沒有錯誤。
- **錯誤種類對照表:** 對照表列的種類和程式實際會發出的種類完全一致(我用正則抽出,沒有表有程式沒有、也沒有程式有表沒有的)。`not_utf8` 因為含數字沒被正則涵蓋,靠 `t_seclist_s02` 綠。
- **相鄰路徑:** `load_vault` 其他指令行為不變(`-k search`、`-k fence` 全綠,`_visible_lines` 本體沒動)。

**③ 新發現同一案例的修前修後**

F1 到 F4 都是文字落差,不是行為回歸,所以沒有「修後才壞」的案例。F2 的修前修後對照在上面的表。

未驗範圍:

- 非 macOS 平台。
- Verification 內的耗時與記憶體數字、「32 種變體」。
- 修前對圖譜根捷徑的行為。
- 沒讀上輪席報告,所以「放行 2 條、34 條」這類統計沒核對。

### 暫存清理

- 臨時工作樹 `r2-整合-sonnet-before`、`r2-整合-sonnet-after` 和席工作目錄都已刪除。
- 探針用的 `seat-probe-*` 和我自己跑出來的 14 個 `gctl-run-*` 現場,用字面絕對路徑清掉了。
- 其他會談的 `gctl-run-*`(約 101 個)沒碰。
- 本 repo 留下的 `?? r2-dispatch.json` 是編排者的,不是我產生的,我沒動。

相關檔案(皆在 `/Users/enzo/orca/workspaces/lumos-toolchain/security-list/docs/lumos-toolchain-knowledge/`):
- `Projects/資安護欄唯讀盤點_計劃.md`
- `Projects/消費專案產品安全Brief與證據驗收_計劃.md`
- `Systems/lumos-cli-read.md`
- `Verification/2026-10-19_資安護欄唯讀盤點實作.md`

最嚴重 severity: minor,blocking 共 0 條
