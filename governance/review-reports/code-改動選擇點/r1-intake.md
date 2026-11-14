# code-改動選擇點 r1 收貨紀錄

派 11 席(正確性、邊界各按三段拆包;通才、資源、合約、架構對齊、資安各一席)。通才、資源、架構對齊、資安四席材料超過 1800 行軟上限,帳上標範圍過大(弱證據)。
派工鏡頭這輪算超時,各席尾端沒附圖譜固定席節點(各席報告都照實寫了),固定席沒有逐條判;合約席自行對照了 Systems/guard-kill 兩條 ★INVARIANT★。

## 重現表(引句錨不到的條目,編排者機械重現)

| id | 錨不到的引句 | 重現 | 結果 |
|---|---|---|---|
| c31 | `_raw = [r for r in rows if (not node) ...` | `grep -n` 在 scripts/lumos:18616 找到原句(既有未改行,不在 diff 內) | HIT |
| c32 | `if key in waived:` 跨兩行引句 | scripts/lumos:78132 找到;同一問題 k1、b31、g2 有錨定引句與獨立重現 | HIT |
| g6 | `_wl = {_k: _it for _k ...` | scripts/lumos:4217 找到原句(既有未改行) | HIT |
| k2 | 計劃「所以 situation-rule 會改計劃…」 | 計劃第 155 行原文是「situation-rule 會改計劃,所以 choice-kill 與處置在 `code-loop pass` 之前做;之後只有帳本提交…」,席位多寫一個「所以」;`_BOOKKEEPING_FILES`(scripts/lumos:40639)確實沒有 .lumos/lint-waivers.json | HIT |
| k4 | 計劃「略過的列不算進 `cmd_guard_kill` 自己的 rc…」 | 計劃第 110 行原文「「略過」列不算進 `cmd_guard_kill` 自…」,席位改寫引號 | HIT |

## 分組(依根因)與處置

| 組 | 根因 | 條目 | 處置 |
|---|---|---|---|
| G1 | 回報上限種子把放行過的行剔掉,放行一行就重抽 | k1 b31 g2 c32,訊息數字 b32 | 折:放行過的鍵也進種子集合,只在「要不要擋」排除;訊息印真的曾存活數 |
| G2 | 判定沒正確處理弱證據 | c21 b21 | 折:弱證據的 killed 不停組;帶弱證據的 survived 判 no_result |
| G3 | 重跑判斷只看測試名集合 | g1 c22 | 折:守的測試雜湊加入測試檔內容(blob);no_result 一律重跑 |
| G4 | 字串串接型別前提只看直接運算元 | g3 c13 b13 | 折:整條 + 鏈任一頂層運算元是字串字面值或樣板,鏈上每個 + 都排除 |
| G5 | 一次掃整批、命中全量做乾節點與 ERROR 比對 | r1 b12 c14 r2 | 折:按檔分開掃,一支檔算不出只標那支;只處理改到行的命中;C-18 規則不抓整個外層區塊 |
| G6 | 論文明寫的挑法沒有測試守 | c11 c12 k4 | 折:補會紅的測試(不同指紋挑到不同類別、節點排序、被排除換下一節點、guard kill 新選用參數) |
| G7 | 唯一判定用不重疊計數 | b11 | 折:改重疊計數;同族掃 guard kill 等同樣寫法 |
| G8 | 兩平台同名測試配方身分撞號 | b22 | 折:結果對回帶平台 |
| G9 | 主線判斷自寫一套 | a1 | 折:改用 `_note_reread_mainline_names` |
| G10 | 文件說提交放行檔不讓留痕失效,實際會失效 | k2 | 折(文件):計劃與 skill 改成 lint-waive 與 choice-kill 都在 `code-loop pass` 之前做、通過後只提交治理帳 |
| G11 | 統計口徑 | c31 g4 g6 | 折:統計用去重列;第一次跑只算 via run;doctor 放行計數排除 choice: |
| G12 | 零星 | k3 g5 a2 a3 r4 | 折:計劃名字改 stop_group_on;aborted 過 `_gate_event_fit`;帳寫失敗判法統一;--catalog-only 認 --sg;測試 blob 查詢共用時限 |
| — | 範圍內設計取捨 | s1 s2 r3 | 放行(minor,附逐條來源):s1 算不出來只提醒是計劃 S19 明訂(論文 §2.3 不讓工具壞掉擋開發);s2 環境變數覆寫會印「被環境變數關掉」那行、只在測試總檔設;r3 延後訊號是為了帳與工作樹一致(計劃 S12),第二次訊號立即收 |

## 先查世界

- PRIOR-ART:G3 Stryker 增量模式比對測試檔內容,只拿得到測試名的執行器承認抓不到「測試內容改了」並提供 --force(https://stryker-mutator.io/docs/stryker-js/incremental/ 、https://stryker-mutator.io/blog/announcing-incremental-mode/)。採用:雜湊加入測試檔 blob;既有 --only 當強制重跑。
- PRIOR-ART:G5 ast-grep 官方建議大量命中改用 `--json=stream` 逐筆輸出(https://ast-grep.github.io/guide/tools/json.html);論文 §2 也是逐檔分析改動。採用:按檔分開掃、逐筆讀。
- PRIOR-ART:G1 回報上限 ×7 出自論文 §2.3(https://arxiv.org/pdf/2102.11378);「已處置的仍算處置、集合變了才重抽」是計劃〈用詞〉自己的規定,程式放行路徑沒照做。這組是對齊規格。
- PRIOR-ART:G7 Python `str.count` 只算不重疊出現(https://docs.python.org/3/library/stdtypes.html#str.count);重疊計數用前瞻正規式。
- PRIOR-ART:G2 計劃 S9 本來就寫「沒有強 killed 而有弱證據記 no_result」,程式沒照做;這組是對齊規格,沒另查外部做法(論文對不穩定結果的處理節號編排者沒核對,不引)。
- G4、G6、G8、G9、G10、G11、G12 是本專案自己的邏輯或既有函式重用,沒有對應的外部做法可查。

## 回歸因果
第一輪,無上輪修補。
