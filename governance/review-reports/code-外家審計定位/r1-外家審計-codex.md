codex
severity: major

## F1 對外安裝的精簡版仍注入舊定位，八檔守衛漏掉真正交付物
severity: major
blocking: yes
引句:「同一句規矩散在八個檔,漏掉任何一處就會有兩套互斥的第一步」
觀察到什麼：`slim/claude-block.md` 仍宣告「知識圖譜是唯一真相來源」及「第一個工具呼叫必須是 lumos」，而安裝器會把這份模板直接寫入消費專案；入口守衛的固定檔案清單沒有它。見 `slim/claude-block.md:6`、`slim/claude-block.md:10`、`slim/install.py:431`、`slim/install.py:439`、`scripts/test_lumos.py:17599`。
怎麼重現：以目前 `_merge_claude_md_text` 對不存在的 CLAUDE.md 做唯讀記憶體實驗，輸出為 `rc 0`、`old_unique_truth True`、`old_first_call True`。也就是輸入空專案 → 產物明確回到舊定位。
為什麼是問題而不是風格偏好：這是實際交付路徑，不是歷史文件。完整版與精簡版會給使用者互斥的工作順序，也直接證明「八個入口全改完、守衛釘住」不成立。

## F2 新設計的 RULE 無權推翻程式碼，最重要的外部限制會被裁掉
severity: major
blocking: yes
引句:「有結構、有出處的才能挑戰程式碼」
觀察到什麼：分類表把 `RULE:` 定義為程式碼看不到的相容性、法規、人工核可限制，但衝突裁決只授權 decisions、合約行、Issues、Verification；Systems 摘要中的 `RULE:` 不在清單內。見 `scripts/templates/graph-discipline.md:26`、`scripts/templates/graph-discipline.md:27`、`scripts/templates/graph-discipline.md:41`、`skills/lumos-project-notes/commands/INDEX.md:42`。
怎麼重現：輸入一篇 Systems 節點，摘要寫合格的 `RULE:[2026-09-21 起;退場:v2 下線]大額退款須人工核可`，而程式目前自動退款。按第 27 行的封閉權威清單，這條 RULE 不能挑戰程式碼；輸出會是依程式行為繼續自動退款，而不是守住人工核可。
為什麼是問題而不是風格偏好：這正是材料三唯一顯示正效益的 code-external constraint 類型。新格式即使證據、期限、退場條件全齊，也沒有決策效力，核心價值被自己的裁決規則取消。

## F3 lint 只驗裝飾字串，Evidence Integrity、Claim Validity 與 FLOW/DEP 都可直接繞過
severity: major
blocking: yes
引句:「規則是寫給人判斷的,機械只看形狀,判錯就擋會逼人繞過去」
觀察到什麼：WHY 的任意 `d999` 算來源；RULE 的任何日期形狀加「退場」算合格；PITFALL 的不存在測試名算防回歸；FACT 的任意六字反引號內容算可重跑查詢。程式不驗來源存在、測試存在、命令可執行或 evidence 是否支持 claim。`FLOW:`、`DEP:` 則完全不進規則表。見 `scripts/lumos:2763`、`scripts/lumos:2767`、`scripts/lumos:2770`、`scripts/lumos:2797`。
怎麼重現：直接執行目前的 `context_marker_warnings`，輸入 `WHY:虛構理由 d999`、`RULE:2030-99-99 退場:永不撤 假規則`、`PITFALL:沒有事故 [test:does_not_exist]`、`FACT:以程式碼為準 假值 \`這不是查詢指令\``，輸出是空陣列 `[]`；輸入 `FLOW:舊資料流 A→B` 與 `DEP:不存在的模組` 也輸出 `[]`。測試還把 FLOW/DEP 的無警告行為寫成必過，見 `scripts/test_lumos.py:3990`。
為什麼是問題而不是風格偏好：Evidence Integrity 要回答「證據是否真的存在」，Claim Validity 要回答「證據是否支持主張」。目前兩者都沒做，卻會把偽造內容顯示成合格；資料流與依賴又正是最容易過期、最需要治理的現況描述。

## F4 有效期只剩任意日期字樣，逐 claim 的生命週期仍未實作
severity: major
blocking: yes
引句:「待設計:知識本身的時效欄位(Active / Superseded / Last-Confirmed / 適用版本),避免歷史決策被當成現行限制。」
觀察到什麼：材料一明說 Active、Superseded、Last-Confirmed、適用版本仍待設計；材料二卻把「脈絡三件套已交付」列為完成。實作只有日期正則與退場關鍵字，不解析日期、不判斷是否到期，也沒有逐 claim 狀態。見 `scripts/lumos:2763`、`scripts/lumos:2774`。
怎麼重現：輸入 `RULE:2030-99-99 退場:永不撤 假規則` 已實測無警告；之後即使前提消失，只要節點本身仍 active，該行沒有可被 `lint` 或 `doctor` 判成 superseded/stale 的狀態，錯誤輸出仍是合格現行規則。
為什麼是問題而不是風格偏好：材料三特別要求避免歷史 Decision 永遠充當現行 Constraint。退場條件散文不等於可執行的有效期；目前無法機械辨識規則何時已失效。

## F5 Context Strategy 沒有落地，code-contained 任務仍被強制檢索
severity: major
blocking: yes
引句:「H3 標頭/標籤當路由,不需要時近乎零成本」
觀察到什麼：計劃明載 H3 未測、路由版本仍需改推送機制；現行規則卻要求每次改 code 前至少執行一次 `lumos impact`，SessionStart 也固定注入同一要求。見 `scripts/hooks/claude/lumos-entry-hook.py:285`、`scripts/hooks/claude/lumos-entry-hook.py:287`、`skills/lumos-project-notes/commands/INDEX.md:42`。
怎麼重現：輸入一個完全能從程式碼回答的局部 rename；即使沒有任何 code-external 問題，規則輸出仍要求一次 impact retrieval，Edit 前 hook 也會推相關筆記。因此 retrieval 次數不可能是零，Context、Latency、Token 也不可能近乎零。
為什麼是問題而不是風格偏好：材料三的策略是 Agent 判斷需要後才看 header/tag，再 selective retrieval；目前只是把「先查」移到「讀 code 後但改 code 前」，沒有實作 on-demand router，H1 的成本問題結構上仍在。

## F6 三支文字守衛可假綠，且兩支明確 fail-open
severity: major
blocking: yes
引句:「改任一份複本的一個字(含全形半形標點) → 這條紅」
觀察到什麼：入口守衛只在範本含逐字「先讀程式碼」時執行，改同義詞便整支 skip；absence 守衛只查三個 token 是否出現在檔案任意位置；同步守衛只判完整區塊是不是某個 substring，HTML 註解也算。見 `scripts/test_lumos.py:17629`、`scripts/test_lumos.py:17634`、`scripts/test_lumos.py:17664`、`scripts/test_lumos.py:17685`、`scripts/test_lumos.py:17707`、`scripts/test_lumos.py:17720`。
怎麼重現：以目前守衛的精確 predicate 做記憶體變異實驗：把「先讀程式碼」改為「先看原始碼」並加入未列入黑名單的舊義同義句，得到 `entry_guard_skips_synonym_drift True []`；刪正文但留 `<!-- 換三次 乾淨 agent 新舊打架 -->`，得到 `absence_guard_dead_comment_passes True`；把完整規範藏進 HTML 註解、正文改壞，得到 `note_sync_dead_comment_passes True`。
為什麼是問題而不是風格偏好：三支測試宣稱保護可執行指示，實際只保護字串存在。順帶說明測試限制：環境拒絕在 `/tmp` 建目錄，`mktemp` 回 `Operation not permitted`，因此無法依要求跑隔離副本的完整 runner；上述為直接載入目前程式及逐字執行守衛 predicate 的唯讀實驗。

## F7 Eval 結果尚不足以支持已擴散到十二個專案的架構反轉
severity: major
blocking: yes
引句:「所有結論來自單一受控專案、兩個模型、每格 25 場;只看得出大差距。」
觀察到什麼：材料一自己的數字是 H1 成本後半未過、H2 只靠一題、其餘三題無鑑別力、H3 未測、H4 只有弱化版；同一 patch 卻記錄第一階段已更新十二個消費專案，材料二又把寫法與 lint 宣告交付。
怎麼重現：把評測輸入按材料三要求分成四個假設，輸出分別是「部分失敗／單題支持／未測／弱化版」；治理決策輸出卻是跨十二專案改變預設工作順序。這不符合材料三所說先驗證核心假設、再決定架構的門檻。
為什麼是問題而不是風格偏好：原實驗刻意放入錯筆記，傷害只在較弱模型出現，強模型四組全對；這能支持「錯筆記有風險」，不能單獨支持把所有任務的預設流程反轉。至少要有真實分布、路由組、正確筆記組及 retrieval relevance 指標再推廣。

## F8 作者把建議中的主要依據升級成最終依據，且與既有記憶規則正面衝突
severity: major
blocking: yes
引句:「兩者不重疊,重疊處以程式碼為準。」
觀察到什麼：材料三只稱程式碼是 implementation 的主要來源，且前提是資訊能可靠地從 repository 得到；新規則升級成最終裁決。另一方面同一範本仍寫「事實與狀態一律歸圖譜」，但新分類又要求能從程式碼查到的現況不要寫入圖譜。見 `scripts/templates/graph-discipline.md:3`、`scripts/templates/graph-discipline.md:43`、`scripts/templates/graph-discipline.md:55`。
怎麼重現：輸入「目前 timeout 是多少」：第 43 行要求不要把可查現況寫入圖譜，第 55 行卻要求事實與狀態一律歸圖譜，無法同時遵守。再輸入「程式預設開啟，但部署設定或資料庫實際關閉」：最終依據規則會輸出開啟，實際運行狀態卻是關閉。
為什麼是問題而不是風格偏好：source code 並不包含部署設定、feature flag、資料庫狀態及生產觀測的全部現況。建議本身的 code-first 邊界可以成立，但「程式碼永遠終局」站不住；作者照單全收後還進一步絕對化，會把原本應調查的矛盾裁成錯誤答案。
tokens used
161,377
severity: major

## F1 對外安裝的精簡版仍注入舊定位，八檔守衛漏掉真正交付物
severity: major
blocking: yes
引句:「同一句規矩散在八個檔,漏掉任何一處就會有兩套互斥的第一步」
觀察到什麼：`slim/claude-block.md` 仍宣告「知識圖譜是唯一真相來源」及「第一個工具呼叫必須是 lumos」，而安裝器會把這份模板直接寫入消費專案；入口守衛的固定檔案清單沒有它。見 `slim/claude-block.md:6`、`slim/claude-block.md:10`、`slim/install.py:431`、`slim/install.py:439`、`scripts/test_lumos.py:17599`。
怎麼重現：以目前 `_merge_claude_md_text` 對不存在的 CLAUDE.md 做唯讀記憶體實驗，輸出為 `rc 0`、`old_unique_truth True`、`old_first_call True`。也就是輸入空專案 → 產物明確回到舊定位。
為什麼是問題而不是風格偏好：這是實際交付路徑，不是歷史文件。完整版與精簡版會給使用者互斥的工作順序，也直接證明「八個入口全改完、守衛釘住」不成立。

## F2 新設計的 RULE 無權推翻程式碼，最重要的外部限制會被裁掉
severity: major
blocking: yes
引句:「有結構、有出處的才能挑戰程式碼」
觀察到什麼：分類表把 `RULE:` 定義為程式碼看不到的相容性、法規、人工核可限制，但衝突裁決只授權 decisions、合約行、Issues、Verification；Systems 摘要中的 `RULE:` 不在清單內。見 `scripts/templates/graph-discipline.md:26`、`scripts/templates/graph-discipline.md:27`、`scripts/templates/graph-discipline.md:41`、`skills/lumos-project-notes/commands/INDEX.md:42`。
怎麼重現：輸入一篇 Systems 節點，摘要寫合格的 `RULE:[2026-09-21 起;退場:v2 下線]大額退款須人工核可`，而程式目前自動退款。按第 27 行的封閉權威清單，這條 RULE 不能挑戰程式碼；輸出會是依程式行為繼續自動退款，而不是守住人工核可。
為什麼是問題而不是風格偏好：這正是材料三唯一顯示正效益的 code-external constraint 類型。新格式即使證據、期限、退場條件全齊，也沒有決策效力，核心價值被自己的裁決規則取消。

## F3 lint 只驗裝飾字串，Evidence Integrity、Claim Validity 與 FLOW/DEP 都可直接繞過
severity: major
blocking: yes
引句:「規則是寫給人判斷的,機械只看形狀,判錯就擋會逼人繞過去」
觀察到什麼：WHY 的任意 `d999` 算來源；RULE 的任何日期形狀加「退場」算合格；PITFALL 的不存在測試名算防回歸；FACT 的任意六字反引號內容算可重跑查詢。程式不驗來源存在、測試存在、命令可執行或 evidence 是否支持 claim。`FLOW:`、`DEP:` 則完全不進規則表。見 `scripts/lumos:2763`、`scripts/lumos:2767`、`scripts/lumos:2770`、`scripts/lumos:2797`。
怎麼重現：直接執行目前的 `context_marker_warnings`，輸入 `WHY:虛構理由 d999`、`RULE:2030-99-99 退場:永不撤 假規則`、`PITFALL:沒有事故 [test:does_not_exist]`、`FACT:以程式碼為準 假值 \`這不是查詢指令\``，輸出是空陣列 `[]`；輸入 `FLOW:舊資料流 A→B` 與 `DEP:不存在的模組` 也輸出 `[]`。測試還把 FLOW/DEP 的無警告行為寫成必過，見 `scripts/test_lumos.py:3990`。
為什麼是問題而不是風格偏好：Evidence Integrity 要回答「證據是否真的存在」，Claim Validity 要回答「證據是否支持主張」。目前兩者都沒做，卻會把偽造內容顯示成合格；資料流與依賴又正是最容易過期、最需要治理的現況描述。

## F4 有效期只剩任意日期字樣，逐 claim 的生命週期仍未實作
severity: major
blocking: yes
引句:「待設計:知識本身的時效欄位(Active / Superseded / Last-Confirmed / 適用版本),避免歷史決策被當成現行限制。」
觀察到什麼：材料一明說 Active、Superseded、Last-Confirmed、適用版本仍待設計；材料二卻把「脈絡三件套已交付」列為完成。實作只有日期正則與退場關鍵字，不解析日期、不判斷是否到期，也沒有逐 claim 狀態。見 `scripts/lumos:2763`、`scripts/lumos:2774`。
怎麼重現：輸入 `RULE:2030-99-99 退場:永不撤 假規則` 已實測無警告；之後即使前提消失，只要節點本身仍 active，該行沒有可被 `lint` 或 `doctor` 判成 superseded/stale 的狀態，錯誤輸出仍是合格現行規則。
為什麼是問題而不是風格偏好：材料三特別要求避免歷史 Decision 永遠充當現行 Constraint。退場條件散文不等於可執行的有效期；目前無法機械辨識規則何時已失效。

## F5 Context Strategy 沒有落地，code-contained 任務仍被強制檢索
severity: major
blocking: yes
引句:「H3 標頭/標籤當路由,不需要時近乎零成本」
觀察到什麼：計劃明載 H3 未測、路由版本仍需改推送機制；現行規則卻要求每次改 code 前至少執行一次 `lumos impact`，SessionStart 也固定注入同一要求。見 `scripts/hooks/claude/lumos-entry-hook.py:285`、`scripts/hooks/claude/lumos-entry-hook.py:287`、`skills/lumos-project-notes/commands/INDEX.md:42`。
怎麼重現：輸入一個完全能從程式碼回答的局部 rename；即使沒有任何 code-external 問題，規則輸出仍要求一次 impact retrieval，Edit 前 hook 也會推相關筆記。因此 retrieval 次數不可能是零，Context、Latency、Token 也不可能近乎零。
為什麼是問題而不是風格偏好：材料三的策略是 Agent 判斷需要後才看 header/tag，再 selective retrieval；目前只是把「先查」移到「讀 code 後但改 code 前」，沒有實作 on-demand router，H1 的成本問題結構上仍在。

## F6 三支文字守衛可假綠，且兩支明確 fail-open
severity: major
blocking: yes
引句:「改任一份複本的一個字(含全形半形標點) → 這條紅」
觀察到什麼：入口守衛只在範本含逐字「先讀程式碼」時執行，改同義詞便整支 skip；absence 守衛只查三個 token 是否出現在檔案任意位置；同步守衛只判完整區塊是不是某個 substring，HTML 註解也算。見 `scripts/test_lumos.py:17629`、`scripts/test_lumos.py:17634`、`scripts/test_lumos.py:17664`、`scripts/test_lumos.py:17685`、`scripts/test_lumos.py:17707`、`scripts/test_lumos.py:17720`。
怎麼重現：以目前守衛的精確 predicate 做記憶體變異實驗：把「先讀程式碼」改為「先看原始碼」並加入未列入黑名單的舊義同義句，得到 `entry_guard_skips_synonym_drift True []`；刪正文但留 `<!-- 換三次 乾淨 agent 新舊打架 -->`，得到 `absence_guard_dead_comment_passes True`；把完整規範藏進 HTML 註解、正文改壞，得到 `note_sync_dead_comment_passes True`。
為什麼是問題而不是風格偏好：三支測試宣稱保護可執行指示，實際只保護字串存在。順帶說明測試限制：環境拒絕在 `/tmp` 建目錄，`mktemp` 回 `Operation not permitted`，因此無法依要求跑隔離副本的完整 runner；上述為直接載入目前程式及逐字執行守衛 predicate 的唯讀實驗。

## F7 Eval 結果尚不足以支持已擴散到十二個專案的架構反轉
severity: major
blocking: yes
引句:「所有結論來自單一受控專案、兩個模型、每格 25 場;只看得出大差距。」
觀察到什麼：材料一自己的數字是 H1 成本後半未過、H2 只靠一題、其餘三題無鑑別力、H3 未測、H4 只有弱化版；同一 patch 卻記錄第一階段已更新十二個消費專案，材料二又把寫法與 lint 宣告交付。
怎麼重現：把評測輸入按材料三要求分成四個假設，輸出分別是「部分失敗／單題支持／未測／弱化版」；治理決策輸出卻是跨十二專案改變預設工作順序。這不符合材料三所說先驗證核心假設、再決定架構的門檻。
為什麼是問題而不是風格偏好：原實驗刻意放入錯筆記，傷害只在較弱模型出現，強模型四組全對；這能支持「錯筆記有風險」，不能單獨支持把所有任務的預設流程反轉。至少要有真實分布、路由組、正確筆記組及 retrieval relevance 指標再推廣。

## F8 作者把建議中的主要依據升級成最終依據，且與既有記憶規則正面衝突
severity: major
blocking: yes
引句:「兩者不重疊,重疊處以程式碼為準。」
觀察到什麼：材料三只稱程式碼是 implementation 的主要來源，且前提是資訊能可靠地從 repository 得到；新規則升級成最終裁決。另一方面同一範本仍寫「事實與狀態一律歸圖譜」，但新分類又要求能從程式碼查到的現況不要寫入圖譜。見 `scripts/templates/graph-discipline.md:3`、`scripts/templates/graph-discipline.md:43`、`scripts/templates/graph-discipline.md:55`。
怎麼重現：輸入「目前 timeout 是多少」：第 43 行要求不要把可查現況寫入圖譜，第 55 行卻要求事實與狀態一律歸圖譜，無法同時遵守。再輸入「程式預設開啟，但部署設定或資料庫實際關閉」：最終依據規則會輸出開啟，實際運行狀態卻是關閉。
為什麼是問題而不是風格偏好：source code 並不包含部署設定、feature flag、資料庫狀態及生產觀測的全部現況。建議本身的 code-first 邊界可以成立，但「程式碼永遠終局」站不住；作者照單全收後還進一步絕對化，會把原本應調查的矛盾裁成錯誤答案。
