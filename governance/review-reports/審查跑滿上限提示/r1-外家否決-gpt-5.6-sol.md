severity: major

## F1 新制 light 迴圈被錯送到處置閘
severity: major
blocking: 是；照字面以日期決定閘種，合法 light 迴圈會套到不同的收斂規則而無法正常放行。
引句:「2026-08-25 之後開的迴圈(帳首日期在舊閘退役日之後)」
file: `scripts/lumos:9557` `--disposal` 與 `--light` 是互斥的獨立閘；light 自有 severity/findings/hash 謂詞。
file: `scripts/lumos:9644` light 輪允許 `minor` 且 `findings ≥ 1` 通過。
file: `scripts/lumos:18367` disposal 輪有 findings 卻沒有 `findings_set` carrier 時判「無處置帳」失敗。
file: `docs/.canary-log.jsonl:807` 新制真帳已有 tier=light、無 round、無 carrier 的合法帳形。
重現：2026-08-26 後的 light 輪記一條 minor finding、hash 與留痕皆正確；現行 light 閘可過，照 spec 改問 disposal 則因沒有 carrier 失敗。日期只能決定新舊 panel 路由，不能取代 tier／帳形分流。

## F2 跑滿後仍建議再一輪，反轉硬上限出口
severity: major
blocking: 是；工具會在明令停止的狀態指示使用者繼續燃燒下一輪。
引句:「其他(在下降、但還有 major 以上) → **再一輪還有進展**。」
file: `scripts/lumos:10675` 現行 cap 分支明定跑滿後停止並交人裁決。
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:175` 相關節點宣稱「到頂未收斂 → 停、攤給人、別無限燒」。
重現：standard 第三輪後折入數由 5 降到 2、最高 severity=major、閘仍未過；spec 會印「再一輪」，與 cap 的終止合約相反。這破壞 `Systems/design-loop` 宣稱的上限行為。

## F3 severity 低不代表處置閘可以附理由放行
severity: major
blocking: 是；照建議操作會把不可由 accepted reason 消除的證據鏈失敗誤當成 minor finding。
引句:「最後一輪最高嚴重度 ≤ minor → **附理由放行**(代碼審照舊只准放行 minor)。」
file: `scripts/lumos:18265` 處置閘實際是 G3、處置集合、全席留痕、quote-check、條款、資安席與落點的七步合取。
file: `scripts/lumos:18574` 任一合取失敗都維持 FAIL；`accepted_set` 只處置 finding，不能豁免 hash、留痕、條款、資安席或落點。
重現：最後兩輪折入 3→1、席位最高 minor，但最後一輪 report sha 被改；閘因 G3／留痕失敗而未過，跑滿報告卻會建議「附理由放行」。正確建議必先看實際 fail reason，不能只看 severity。

## F4 單輪超過 20 條時兩條規則互相否定
severity: major
blocking: 是；同一輸入沒有唯一合法輸出，實作者必須任意違反其中一條條款。
引句:「有任何一輪沒記處置、或只有一輪」
引句:「同一個審查編號,各輪彙總帳的折入條數累計超過 20」
file: `docs/.canary-log.jsonl:916` 真帳「主session鏡頭利用率」第一輪 carrier 已折入 62 條，單輪即觸發此衝突。
規則一要求只有一輪時「不給建議」，提早熔斷與 S7 卻要求同一輪印「建議拆小改動」。需定義 breaker 是否覆蓋一般建議、是否能與「判不了」並列，以及對已 PASS 的第一輪是否仍觸發。

## F5 無 spec 的 cap 快路會繞過壞帳 fail-closed
severity: major
blocking: 是；帳本損壞時仍會宣告跑滿並寫入 cap-reached，輪數可能是跳過壞行後的假值。
引句:「輪數已達上限而沒帶 --spec 時,不再先回」
引句:「處置閘因為帳本壞行等原因先擋下時,這段不印」
file: `scripts/lumos:9896` `loop next` 使用的 `_loop_records` 對 JSON 壞行直接跳過。
file: `scripts/lumos:18279` disposal 閘對任何壞行回 rc2，理由正是無法確定最後一輪。
重現：帳本放三輪有效記錄，再放一行截斷 JSON，執行未帶 `--spec` 的 `loop next`。照 spec 直接走 cap 時會以三輪有效記錄宣告跑滿；同一本帳交 disposal 會因壞行拒判。S2 必保留壞行 fail-closed，不能只把 `--spec` 檢查移到 cap 之後。

## F6 JSON 輸出沒有欄位合約或驗收條款
severity: minor
blocking: 否；不影響核心判定，但不同實作者會產生不相容的機讀格式。
引句:「`loop next` 回跑滿上限時:文字輸出與 `--json` 都要有」
file: `scripts/lumos:10419` 現行 JSON schema 由 `emit` 的明確鍵集合形成。
file: `scripts/lumos:10561` 文字模式另有固定白名單，不會自動跟 JSON 新鍵同步。
S3 只驗「文字輸出」，未定義 JSON 的欄名、每輪資料結構、缺 carrier 的表示法或 advice code。實作者只補文字仍可通過全部列出的相關條款。

已看,無: 完整讀過 frontmatter、PRIOR-ART、一句話、四段做法、S1–S9、回退、實務隱患與誠實界線；所有 repo 內交叉引用目標存在。LUMOS-SPEC 與送審副本逐字一致，該計劃本身沒有登記合約；`Systems/loop-convergence-recording` 也沒有登記形式合約，但其 light/disposal 分閘與壞行 fail-closed 宣稱分別受 F1、F5 影響；`Systems/design-loop` 的 cap 停手宣稱受 F2 影響。`folded_set`、`severity`、`--spec`、`--json`、`--disposal` 等旗標與欄位均已由程式、help 與真帳核對存在；quote-check、escape 與 gov 的既有資料模型不需修改。實務隱患逐類：併發／帳本 torn-write 風險見 F5；守衛面見 F1、F2、F3、F5；效能無新增凍結審材讀取，沿用已載入帳列後計數；金流無，因無付款或計費；對外送出無，因無網路或外部服務；不可逆無新 schema 或資料搬移，但既有治理帳仍是 append-only；資源、async、秘密與 shell 注入均無，因功能是同步本機讀帳與格式化輸出。

總結: 最嚴重 severity major，blocking 共 5 條。
