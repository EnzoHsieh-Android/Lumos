severity: major

## F1 `spec-gate` 留痕會把未審計計劃錯分成 design
severity: major
blocking: 是 — 不改會污染 design/plan 分組，讓未進設計審的計劃進入設計審統計。
引句:「判法寫成一支函式,寫的一側與讀舊列都呼叫它,**只看兩個欄位:`loop` 與審查帳**:`loop` 以 `code-` 開頭 → `code`;否則審查帳裡有這個編號 → `design`;都不是 → `plan`。(代碼審記到 major 自動記的那種,`loop` 已經是去掉 `code-` 的計劃名,所以自然落在 `design` 或 `plan`,不用另看站名。)」
file: `scripts/lumos:5596` `spec-gate` 留痕本來就寫入 `.canary-log.jsonl`，並帶同一個 `loop` 欄。
file: `scripts/lumos:9896` 現有 `_loop_records` 明確排除 `kind=spec-gate`，因為它不是審查輪。
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:31` 相關節點也宣告 `spec-gate` 不是審查輪；本設計照字面會破壞該宣稱。現帳已有只含 `spec-gate`、沒有審查輪的編號，依本規則會被判成 design。

## F2 同時出現 converged 與 rewrite 時沒有唯一終態
severity: major
blocking: 是 — 不改會讓同一本帳依實作分支得到相反的分母判定。
引句:「分母:放行了的迴圈數。放行 = 治理帳有這個迴圈 `kind=converged` 的紀錄(處置閘過關時寫的;`cap-reached` 與 `rewrite` 都不算放行),而且審查帳裡有它的列(排除測試留下的假紀錄)。」
引句:「沒放行的迴圈:記在 `cap-reached` 或 `rewrite` 收尾的迴圈(或還開著的)底下的逃逸列,另列「未放行迴圈的逃逸」筆數,不進任何類別。」
file: `scripts/lumos:813` `cmd_loop_rewrite` 不檢查該編號是否已有 `converged`，會直接追加 `rewrite`。
file: `scripts/lumos:6760` 現有治理統計採「有 converged 就算通過，rewrite 只在沒有 converged 時生效」；第二段 spec 卻可讀成最後以 rewrite 收尾便算未放行。輸入為先 PASS、後執行 `loop rewrite` 時，兩條規則給出相反答案；S6、S8 也沒有釘住此混合事件序列。

## F3 共用讀取函式仍會被合法 JSON 非物件打崩
severity: major
blocking: 是 — 不改會讓 escape-stats、治理統計與問閘尾在遇到 `null` 或陣列行時直接例外退出。
引句:「`_escape_rows_for` 加一個參數 `include_withdrawn`(預設否):」
file: `scripts/lumos:7397` `_escape_rows_for` 只捕捉 JSON 解碼錯誤；`json.loads("null")` 或 `json.loads("[]")` 成功後，下一行呼叫 `d.get(...)` 會拋 `AttributeError`。
file: `scripts/test_lumos.py:33804` 現有合約已要求逃逸帳的 `null`、陣列與壞 JSON 要容錯，但只測了自行讀檔的 `loop escape --list`。修訂稿把更多讀者集中到 `_escape_rows_for`，卻未要求它驗證 `dict`、跳過並報告壞行。

## F4 空白佐證與空白豁免理由能繞過新規則
severity: major
blocking: 是 — 不改會繼續寫出沒有實質佐證、也沒有實質理由的新列。
引句:「新寫的列至少要有 `sha` 或 `defect_ref` 其中之一。手動記帳兩個都沒有時,要另給 `--no-defect-ref "<為什麼沒有>"`(理由用獨立旗標,跟既有旗標慣例一致),否則擋下。」
file: `scripts/lumos:9514` 現有 `defect_ref` 只做 truthy 判斷，`--defect-ref "   "` 會被寫入。
file: `scripts/lumos:30819` CLI 對 `--defect-ref` 沒有正規化。修訂稿與 S2 都沒列空字串、全空白 `defect_ref`、全空白 `--no-defect-ref` 的擋下條款；照現有模式加旗標即可用空白通過。

## F5 撤回寫入沒有承接既有帳本 symlink 防護
severity: major
blocking: 是 — 不改會新增一條可跟隨符號連結、把撤回紀錄追加到帳外檔案的寫入路徑。
引句:「**指令**:`lumos loop escape --withdraw <token> --reason "<理由>"`。」
引句:「**上鎖**:整段「讀帳確認目標→寫入」包在 `_vault_write_lock` 裡(手動記帳今天沒上鎖,這裡要明確加);拿不到鎖時照其他寫入指令一樣印「擋下:…」,不讓例外直接冒出來。」
file: `scripts/lumos:9520` 現有手動寫入在 append 前專門拒絕 `.escape-log.jsonl` 為 symlink。
file: `scripts/test_lumos.py:33791` 這項防護已有紅釘測試。修訂稿只要求鎖，沒有要求撤回分支經過相同的 symlink／安全建檔檢查；若撤回在現有手動記帳分支之前處理，`open(..., "a")` 會跟隨連結。

## F6 「每一列都有 loop_kind」與撤回列形狀互相衝突
severity: minor
blocking: 否 — 這是 schema 精度問題；撤回紀錄不是統計事件時可明訂例外，不會單獨造成錯誤統計。
引句:「新寫的列加 `loop_kind`:`design`(設計審迴圈)、`code`(代碼審迴圈)、`plan`(沒有審查帳的計劃,例如風險低直接實作)。」
引句:「**撤回紀錄長這樣**:`{"kind":"withdraw","target":"<被撤的 token>","reason":"…","by":"<git user.name>","ts":"…","token":"<新的 ESC- 編號>"}`——有自己的 token,不跟目標共用。」
前句涵蓋所有新列，後句的完整形狀沒有 `loop` 或 `loop_kind`，也無法依第一節函式推導。需明訂撤回紀錄是否豁免，或把目標的分類冗餘寫入。

## F7 `--withdrawn` 是 list 修飾旗標還是獨立模式未定義
severity: minor
blocking: 否 — 只影響 CLI 契約與測試寫法，不改核心撤回語意。
引句:「**清單照樣列、標出來**:`loop escape --list` 保留自己讀檔、對壞行寬容的寫法,列出所有列,被撤的標「已撤回(理由、誰、何時)」,撤回紀錄本身也列。另加 `--withdrawn` 只列撤回過的,給人查。」
未定義合法呼叫是 `loop escape --withdrawn` 還是 `loop escape --list --withdrawn`，也未定義它與記帳參數、`--withdraw` 的互斥。現有 `--list` 有嚴格互斥合約；照字面無法寫出唯一 parser 與測試。

已看,無: r2 與 LUMOS-SPEC 位元組完全一致；文件交叉引用與 refcheck 通過；`loop next`、`loop status --disposal`、`canary record`、`quote-check`、`loop escape`、`gov` 參數均以實際 `--help` 核對。帳本現況 25 列／6 列無佐證／17 列自動記、代碼審 146 個迴圈／33 個未定錨均重算相符。r1 的去重防復活、撤回目標驗證、同鎖序列化、清單保留撤回資訊、rule-gap standalone 佈局、push-gate 前綴、`_loop_anchor_tier`、`_plan_for_loop` 去前綴與 NFC、零分母、三份操作說明同步等修正已落入文字；除 F1、F2 所列者外，未再發現與 `Systems/loop-convergence-recording` 的宣稱或合約衝突。實務隱患逐類：併發核心序列已有同鎖設計；效能為手動/週報讀約 15MB 帳本，未進推送閘，範圍合理；守衛面仍有 F4、F5；帳損壞容錯仍有 F3；金流無，因只處理本機帳本；對外送出無，因沒有網路呼叫；不可逆無新增覆寫，因採 append-only 沖銷且回退代價已明載；舊版相容性已誠實標明只會多印可疑列。

最嚴重 severity: major；blocking 共 5 條。
