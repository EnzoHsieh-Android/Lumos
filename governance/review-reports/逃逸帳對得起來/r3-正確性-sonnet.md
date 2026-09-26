severity: major

## F1 歸因不明的判定沒有限定在分母母體內,會誤扣真正應算數的設計/代碼迴圈
severity: major
blocking: 是(照 spec 字面實作,「同一個佐證出現在兩個以上迴圈的列」不分 loop_kind、不分該迴圈是否真的在分母母體裡就一律判歸因不明——會把明明只有一個統計候選迴圈的真實逃逸,誤判成「兩個以上迴圈共用」而從它自己的分子裡踢掉,率被系統性低估,不是邊界巧合而是 `--auto`/CI 的常態寫法)
引句:「同一個佐證(同一個 sha 或 defect_ref)出現在兩個以上迴圈的列,不算進任何迴圈的分子,另列筆數」

第四節「歸因不明」只用「同一個佐證出現在幾個不同 `loop` 字串」判定,完全沒有先過濾成只看第一節定義下真正屬於 `design`/`code` 且在分母母體(治理帳有 converged、審查帳有審查紀錄)裡的迴圈。而 `--auto`(`scripts/lumos:9422-9432`)與 CI 掛勾(`scripts/lumos:25069`)的實際寫法是「一次提交範圍碰到幾個計劃,就對每個計劃各寫一筆逃逸列、共用同一個 sha」(`_auto_escape` 的 `for loop_id, plan_rel in loops:` 迴圈,`scripts/lumos:9346`),所以同一個 sha 綁到 2、3 個不同 `loop` 名是**正常且高頻**的情況,不是例外。

實測 `docs/.escape-log.jsonl`(3 個 sha 有跨迴圈共用):
- `9bfa759f1fc269a9f89c568cf2437de2fe151d75` → `{規格落成可驗收條件, 逃逸自動記, 雙向門放行}`
- `a2d7726b9464a12ff877ce6af4a512adf603c5df` → `{規格落成可驗收條件, 逃逸自動記, 雙向門放行}`
- `696709b4ace01f3118de203069433a91824d7d6d` → `{Codex行為精修, 規格落成可驗收條件, 雙向門放行, 逃逸自動記}`

而這幾個 `loop` 名裡,`逃逸自動記` 在 `docs/.canary-log.jsonl` 完全沒有任何列(kind 空集合)、`雙向門放行` 只有 1 筆 `kind=spec-gate`(spec-gate 依 spec 第一節規定不算審查紀錄)——照 spec 第一節,這兩個 `loop_kind` 都判成 `plan`,天生沒有分母、永遠不進任何率。也就是說,前兩個 sha 實際上只有 `規格落成可驗收條件` 一個 `design`/`code` 候選,並不存在「該算給哪個統計迴圈」的真ambiguity;但字面規則仍會把它列入「歸因不明」,把 `規格落成可驗收條件` 這個本應算進分子的逃逸排除掉。第三個 sha 才是真正的雙迴圈 ambiguity(`Codex行為精修` 與 `規格落成可驗收條件` 都有真實審查紀錄)。

修法方向(供編排者判):應先把候選迴圈過濾成「屬於分母母體(loop_kind ∈ {design, code} 且該迴圈有 converged 記錄與審查紀錄)」之後,再判斷是否還有 2 個以上——只剩 1 個時直接算進那 1 個迴圈的分子,不算歸因不明。

## 已看,無:

- S1 loop_kind 判法(`code-` 前綴、審查帳 kind ∈ {none,caught,missed} 排除 spec-gate)與 `docs/.canary-log.jsonl` 實際 kind 值域(`caught:338, missed:67, none:1474, spec-gate:19`,無第五種)一致,判法可執行。
- S2 手動記帳 `--sha` 現況確實沒寫進帳列(`scripts/lumos:9511-9519` 的 `rec` 只放 `loop/stage/severity/desc/defect_ref/rule`,`sha` 參數在手動分支完全未被引用,只在 `--auto` 分支用),與計劃 FACT 一致,不影響本次「率」的邏輯(是資料完整性問題,已有 S2 條款覆蓋)。
- 第四節分母定義裡「設計審與代碼審過處置閘都寫在 `gate=design-loop` 這個閘名下」與 r2 重現表（`r2-intake.md` r2a-F1)一致:`_loop_gov_mark`(`scripts/lumos:549-559`)被 disposal/panel gate 各條路徑(`scripts/lumos:8392,8396,8495,8500,9244,9684,9797,10673,18584`)共用呼叫,不分設計或代碼迴圈,一律 `gate="design-loop"`;而「`gate=code-loop, kind=passed` 不帶迴圈編號」也屬實(`scripts/lumos:28320-28324` 固定 `nodes: []`,程式碼裡的 `LOOP_CLOSE_EVENTS_BY_DETAIL` 註解也明載「148 筆全空」)。spec 正確地指出「不用它」,這處沒有問題。
- `_plan_for_loop`(`scripts/lumos:9293-9298`)現況確實沒有去 `code-` 前綴、沒有 NFC,S10 要求的改動方向與現況缺口一致;唯一既有呼叫者(`scripts/lumos:8005-8010`)確實已經自己先算好 `derived = str(loop)[len("code-"):]` 再傳進去,回退段「不受影響」的說法可重現。
- `_loop_anchor_tier`(`scripts/lumos:17905-17908`)「帳上第一筆帶 tier 的值」與計劃描述一致,無另需驗證的分歧。
- `_escape_rows_for`(`scripts/lumos:7397-7415`)現況遇到合法 JSON 但非物件的列(如 `null`)會在 `d.get("loop")` 那行因為 `d` 是 `None` 而丟未捕捉的 `AttributeError`(只包了 `OSError`),S15 修這個缺口方向正確、且是真缺口(`--list` 路徑在 `scripts/lumos:9452-9454` 已經有防護,但統計會用到的 `_escape_rows_for` 沒有)。
- S7 站名清單(`實作`、`code-loop`、`push-gate*`)與帳上實際出現過的站名一致(`實作:4, code-loop:7, push-gate:1`,另有 `push-gate-unreviewed` 用於別處 `scripts/lumos:9356`、`2314-2317`),沒有杜撰站名。
- 第三節撤回機制(token 形狀、上鎖、擋下條件、`--by` 明講、`_jsonl_append_verified` 共用)與 `cmd_loop_escape`/`_auto_escape` 現有的鎖、寫入、NFC 慣例一致,沒有找到新的內部矛盾或壞引用;`_vault_write_lock`(`scripts/lumos:13757`)、`_jsonl_append_verified`(`scripts/lumos:8017`)確實存在且簽名符合描述。
- 反引號路徑、指令、欄位名逐一核對(`_escape_rows_for`、`_vault_write_lock`、`_loop_anchor_tier`、`_plan_for_loop`、`loop canary-stats`、`gov`)均存在於 `scripts/lumos`,無壞引用。
- r1/r2 的折入項目(撤回紀錄形狀、分母只認 converged、`push-gate` 前綴、`_plan_for_loop` NFC 等)在本輪重讀中未發現「說已解決但其實沒解決」的落差。
- 實務隱患欄(併發、效能、守衛面)描述與程式現有的鎖/檔案大小/唯讀性質相符,已排除三項(金流/對外送出/不可逆)確實適用(本功能只讀寫本機 JSONL、不呼叫外部服務、append-only)。

最嚴重 severity: major;blocking 共 1 條。
