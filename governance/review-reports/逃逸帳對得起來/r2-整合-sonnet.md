severity: major

## F1 撤回紀錄本身混入沒帶 loop_id 的既有讀者,spec 沒交代要濾掉
severity: major
blocking: 是(照字面實作,撤回紀錄會被既有四個讀者當成一筆逃逸列去統計/去重,數字悄悄錯,不是措辭問題)

引句:「`_escape_rows_for` 加一個參數 `include_withdrawn`(預設否)」

現況:`_escape_rows_for(env, loop_id=None)` 目前的邏輯是「有給 loop_id 就比對 `d.get("loop")==loop_id`,沒給就整份回傳,不看 `d` 長什麼樣」(`scripts/lumos:7397-7415`)。spec 新增的撤回紀錄格式是 `{"kind":"withdraw","target":...}`(同份檔案,無 `loop`/`stage`/`severity` 欄),而且 spec 明講它跟一般逃逸列存在同一支 `.escape-log.jsonl`(「清單照樣列、標出來:`loop escape --list` 保留自己讀檔…列出所有列」)。

spec 全文只講「撤回**過的逃逸列**要不要算」(用 `include_withdrawn` 過濾),沒有任何一句講「撤回紀錄**這一筆本身**要不要算進去」。而現存 5 個呼叫點裡,有 4 個是不帶 `loop_id`(`loop_id is None`)的:
- `scripts/lumos:2301`(doctor S14「撤除條件分子」按門與階段分桶)
- `scripts/lumos:6303`(`_sc_history`,小改動閘查「近 N 天逃逸帳有沒有同落點」)
- `scripts/lumos:7082`(`_render_gov_stats` 治理帳統計)
- `scripts/lumos:9344`(`_auto_escape` 去重用的 `existing` 集合,spec 明講這裡要 `include_withdrawn=True`)

這 4 處只要 `include_withdrawn=True`(或函式本身沒把 `kind=="withdraw"` 的列濾掉),撤回紀錄就會被當成一筆真逃逸列處理:
- `scripts/lumos:2303-2309` 會對它跑 `_e.get("loop","")`(空字串)、`_e.get("stage")`(缺,印成 `?`),多出一個「風險不明:? N 筆」的假桶,每撤回一次分子就多一筆雜訊,而這正是這份計劃自己要修的那段(問閘尾的撤除條件分子)。
- `scripts/lumos:20230-20244`(`cmd_rule_gap`,規則缺口統計)是另一條自己讀檔、不經過 `_escape_rows_for` 的路,同樣會把撤回紀錄的 `ev.get("rule")` 讀成空 → 灌進 `unlabeled` 計數。spec 的 [S13] 只寫「並且不算被撤回的列」,同一個字面可以讀成「排除被撤回的原逃逸列」,沒有明講也要把 `kind=="withdraw"` 那一筆自己排除在外。

結論:spec 需要多一句話(或併進 [S1]/[S3] 的判準),明講「撤回紀錄自己(`kind=="withdraw"`)一律不當成逃逸列被任何讀者計數,不論 `include_withdrawn`」,而且這條要同時管到 `_escape_rows_for` 與 `cmd_rule_gap` 這兩條各自獨立的讀檔路徑(後者不經過前者,修 `_escape_rows_for` 救不了它)。目前 [S3]/[S13] 的字面缺這一句,照樣實作會在四個既有讀者身上長出新的雜訊桶。

## F2「排除測試留下的假紀錄」沒有可執行的判準,也沒有條款/測試綁定
severity: major
blocking: 是(沒有判準,實作者只能自己猜一個口徑,口徑猜錯分母就偏)

引句:「而且審查帳裡有它的列(排除測試留下的假紀錄)」

這句話在第四節「分母」定義裡,是唯一一次提到要排除測試污染,但通篇沒有:
- 定義什麼樣的紀錄算「測試留下的假紀錄」(id 前綴?vault 路徑?某個標記欄位?)
- 對應到 [S1]–[S13] 任何一條 [test:] 條款
- 對到程式碼裡任何既有機制——我用 `grep -n "測試留下的假紀錄\|假紀錄\|test.*fixture.*loop"` 掃過 `scripts/lumos`,repo 裡沒有任何既有函式在做這件事(唯一命中是無關的第 693 行註解)。`scripts/test_lumos.py` 裡建 `.canary-log.jsonl`/`.escape-log.jsonl` 測資都是寫進暫時目錄(每個測試自己的 vault),理論上不會混進真正的治理帳,但 spec 這句話暗示「真帳上仍可能混到測試留下的假紀錄」——如果真有這個現象,沒定義判準就無從排除;如果現象不存在,這句話應該刪掉,不該留一個查無實作對象的括號。

兩種情況都需要 spec 補一句可執行的判準(例如某個欄位、某個前綴、或乾脆說明「目前沒有已知污染源,這句先留著給未來,不算條款」),否則實作者只能自己編一個口徑,而這個口徑會直接影響 escape-stats 每一類的分母(進而影響率與 Wilson 區間),卻沒有任何測試盯著它。

## 已看,無:

- **寫入端(hook/pre-push/CI/代碼審)是否都被涵蓋**:四個自動記來源(`scripts/lumos:6383` 推送閘小改動、`scripts/lumos:8008` 代碼審、`scripts/lumos:25069` CI、`scripts/hooks/pre-push:305,311` 兩個 grep 分支)全部經同一支 `_auto_escape`(`scripts/lumos:9319-9377`)寫入,只有一處 `rec = {...}` 組列(`9363-9366`)。spec 要求的 `loop_kind`/`defect_ref` 邏輯只要動這一個函式就涵蓋全部四個自動來源,不需要逐一點名——這點沒有遺漏。手動記帳走另一條獨立路徑(`cmd_loop_escape` 非 `--auto` 分支,`9476-9539`),同樣只有一處 `rec = {...}`(`9511-9519`),也只需要改一處。
- **`_escape_rows_for` 加參數對既有呼叫點的影響**:5 個既有呼叫點(`2301`/`6303`/`7082`/`9344`/`18551`)裡,只有 `9344`(`_auto_escape` 去重)按 spec 該顯式傳 `include_withdrawn=True`,其餘 4 個不動、靠新參數預設值 `False` 自動拿到「排除被撤列」的正確行為,型別/位置皆相容(新參數放在既有 `loop_id=None` 之後,不影響任何已用位置或關鍵字傳法的呼叫)——這條除了 F1 講的「撤回紀錄本身混入」之外,加參數這件事本身不會弄壞任何既有呼叫點。
- **與 `[[Projects/逃逸自動記_計劃]]` 既有決定是否一致**:讀過該計劃全文,`_auto_escape` 的 fail-open、`_vault_write_lock`、去重鍵、`--auto/--range/--sha/--repo` 語意、`attribution: ledger|plan-file`、`_door_for_loop` 全部與 r2 spec 的敘述吻合,沒有找到牴觸;`_plan_for_loop` 目前唯一的既有呼叫點(`8010`)在呼叫前已經手動去掉 `code-` 前綴(`derived = str(loop)[len("code-"):]`),spec 要求把前綴/NFC 邏輯搬進函式本體不會讓這個呼叫點壞掉(等於對已去過前綴的字串再做一次 NFC,冪等)。
- **三份 skill 的逃逸記帳範例實際位置**:`skills/lumos-design-loop/SKILL.md:61`、`skills/lumos-code-loop/SKILL.md:54`、`skills/lumos-project-notes/commands/06-代碼審與推送.md:11,27`。三處現有範例都只示範 `lumos loop escape <編號> --stage … --severity … --desc …`,沒有 `--defect-ref`,新 [S2] 上線後照抄會被擋——但 spec 第二節已經明講「三份操作說明…同一次改動裡同步補上」,這是已規劃的工作項,不算本輪缺口。`lumos-code-loop/SKILL.md:54` 的「<編號>」在同檔第 14 行已定義為 `code-<主題>`,上下文夠清楚,不會跟 `loop_kind` 的 `code-` 前綴判準衝突。
- **與程式碼現況不符的宣稱**:`_loop_anchor_tier`(`17905`)、`_vault_write_lock`、`_jsonl_append_verified`、`--defect-ref` 旗標(dest `esc_ref`,`30819`)等 spec 引用的既有原語全部存在且用法與 spec 描述一致。
- **實務隱患分類**(逐類答):
  - 併發:spec 已答(撤回與自動記共用 `_vault_write_lock`),與現有寫入鎖用法一致(`9342`),無新增風險。
  - 效能:spec 已答(唯讀、手動/週報才跑),`.canary-log.jsonl` 現況約 1.7MB(`ls -la` 略)、`.governance-log.jsonl` 較大,量級與 spec 描述相符,不擋任何閘,無新增風險。
  - 守衛面:spec 已答(撤回會讓數字變好看,靠理由+清單標出+`--withdrawn` 單列因應),判斷合理,這期不做存取控管的決定也寫了 REVISIT。
  - 金流/對外送出/不可逆:spec 已排除,查證屬實(整份改動只碰本機 jsonl 帳本與治理帳,不呼叫外部服務,append-only)。

最嚴重 severity: major;blocking 共 2 條。
