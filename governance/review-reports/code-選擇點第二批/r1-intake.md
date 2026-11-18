# r1 收貨紀錄

第一輪代碼審(tier high):正確性、邊界、通才、資源、合約與圖譜、架構對齊、資安,全 sonnet。材料凍在 `r1-snapshot.patch`(1468 行,範圍 `6857e3d60..eebb84593`),另拆 `r1-code.patch`、`r1-tests.patch`、`r1-docs.patch` 給各席。派審前新增告警 `lint-new` rc0 clean(中途把 `_choice_edits` 的分支移進 `_choice_anchor_edits` 才不超過複雜度上限);這次沒有要表態的效能檢核題。

## 收貨

- 七席全部交回才一次寫進卷證;報告從逐字稿取最後一則訊息存檔。
- report-normalize:七份都已是正規化格式。refcheck:七份引的路徑與行號全對得上。quote-check:六份全數錨定;合約席 k2 的一句引的是計劃本文(不在這次差異裡),下面重現表機械核對。
- 圖譜鏡頭:七席都回報「這次沒附固定席節點」(派工前一刻暖快取時外部碼表補選逾時);各席改用 diff 判讀。固定席內容的判讀這輪等於沒做,下一輪派工前先 `lumos dispatch-lens` 暖到完成再派。
- 席位臨時目錄 `/tmp/lumos-seat-work/code-選擇點第二批/` 收貨後已刪(刪前 lsof 確認沒有程序開著)。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| c1 | 樣本補 `if (c) x.let { show(it) }` 等五行標 MISS C-34,用原規則跑 `check.py --catalog-only --sg` | 原規則五行都命中(樣本核對報 MISS 卻命中);改規則後 0 問題 | HIT |
| c2 b1 | 原 S8 測試下把放行改「第一筆贏」、終態改「最後一筆贏」 | 兩種改壞 `t_gov_stats_choice_by_row` 都照綠 | HIT |
| a1 | 同一行兩筆放行 `2026-11-18T02:00:00+08:00`(不適用)與 `2026-11-17T20:00:00+00:00`(等價),原碼直接比字串 | 算成「不適用」(字串大的那筆其實較早) | HIT |
| b3 | `_render_gov_choice` 餵 row `C-²` | 原碼 `int("²")` 丟 ValueError | HIT |
| c3 | `!!` 位移改成字元數,跑原 `t_choice_points_nul_safecall` | 照綠(沒有多位元組案例) | HIT |
| b4 | 引數錨點改成不含右括號那行,跑原 `t_choice_points_compose` | 照綠 | HIT |
| b2 g1 | 型錄那行換成 `已撤列號：C-31`、`- 已撤列號:C-31`、多寫一行 | 原碼三種都回空、撤號守衛不報 | HIT |
| g2 c4 | 樣本補 `LaunchedEffect(-1)`、`LaunchedEffect('c')`、`remember(-1)` 標 MISS,用原規則跑 | 原規則三行都命中 | HIT |
| g3 | `grep -n literal-arg\|value-pos scripts/test_lumos.py` | 原本沒有比對三份照抄片段的測試 | HIT |
| r1 r2 | ast-grep 0.51.2 直接掃:巢狀 300 層 `remember(k) {`、1MB 每行 4 個 `?.` 2 個 `?:` 的檔 | 原規則 444MB、103MB;改雙重否定後 0.44MB、76MB(線性,每個命中 0.5 到 0.9KB) | HIT |
| k1 | 讀驗證筆記 REVISIT 與「上線日 2026-11-17」 | REVISIT 2027-01-15 早於滿兩個月 | HIT |
| k2 | `grep -n "補 WHY 行(第二批來源與不收理由)" 計劃`;`grep -c 不收 Systems/kotlin規則包.md` 的第二批行 | 計劃範圍 6 有這句;規則包筆記沒有對應 WHY 行 | HIT |

## 分組

1. **規則精度**(c1 major、g2、c4、g3):`.let` 的值用到判法照抄 `sbr.yml` 但方向相反;字面值清單漏負數與字元;照抄片段沒同步守衛。
2. **依列號統計**(c2、b1、a1 三條 major,b3):測試分不出放行取哪筆與終態;比時間沒走既有 `_loop_ts_newer`;排序鍵擋不住非 ASCII 數字。
3. **測試缺口**(c3 major、b4):多位元組位移、引數錨點右括號那行。
4. **已撤列號那行**(b2、g1):認不出的寫法被當成沒有、守衛靜默失效。
5. **輸出量**(r1、r2):新規則正面寫 inside,跟第一版 C-18 同一族。
6. **文件**(k1、k2)。

## 先查世界

- 第 1 組:PRIOR-ART: Kotlin 編譯器的 unused return value checker 把 `let` 這種回傳 lambda 結果的高階函式列為要另加 `returnsResultOf()` 契約才查(https://kotlinlang.org/docs/unused-return-value-checker.html );沒查到 Detekt 有「let 結果被丟掉」的規則(查詢詞:detekt rule unused return value let scope function result ignored)。語法樹沒有型別,只能照語法位置近似:採用「不確定是不是值就不收」(跟 `sbr.yml` 的「不確定就不刪」方向相反),另排除沒大括號的 if/for/while/when 分支;必然等價的壞法事前排除照計劃原依據 Trivial Compiler Equivalence。
- 第 2 組:PRIOR-ART: Python 文件寫明帶時區的 datetime 比較時先減掉 UTC 偏移,字串字典序不看偏移(https://blog.ganssle.io/articles/2018/02/a-curious-case-datetimes.html 、https://dev.to/inesp/what-are-utc-iso-time-format-and-unix-time-and-how-does-python-handle-them-22bg )。採用專案既有的 `_loop_ts_newer`(解得動就比 UTC 秒數,否則退回字串)而不另寫一份。終態判法照計劃原依據 PIT、Stryker 每個壞法一個終態。
- 第 3 組:專案內部測試缺口,照 lumos-project-notes〈實作測試品質〉補「現場成立 + 翻紅」案例,不需外部依據。
- 第 4 組:PRIOR-ART: 照計劃原依據 ESLint 規則停用政策(https://eslint.org/docs/v8.x/use/rule-deprecation ,停用的規則留著不另作他用);讀法改成「認不出就報、不當成沒有」(fail closed),這是本專案守衛的既有原則(第一版讀表壞就擋並指出哪一列)。
- 第 5 組:PRIOR-ART: ast-grep 的關聯規則(inside、has)命中的外層節點會成為命中的次要標記並寫進 JSON 輸出的 labels(https://ast-grep.github.io/guide/rule-config/relational-rule.html 、https://ast-grep.github.io/blog/new-ver-38.html 、https://ast-grep.github.io/guide/tools/json.html )。採用第一版 C-18 已驗過的「not inside not X」雙重否定寫法(Systems/kotlin規則包 的 PITFALL),命中集合不變、外層不進輸出;剩下的單行超長鏈是每個命中都附整行原文造成,跟第一版長串 `+` 同一類,照計劃落成驗不了、只提醒。
- 第 6 組:文件,不需外部依據。

## 處置

全 16 條折入,沒有放行、沒有重現不到的。

| id | 去向 | 種類 | 改了哪裡 |
|---|---|---|---|
| c1 | 折 | code | api.yml C-34 value-used 排除 control_structure_body 直接子節點(if/when 當值用除外);樣本補五行 MISS、一行 HIT |
| g2 c4 | 折 | code | api.yml C-36、C-37 literal-arg 補 character_literal 與帶正負號的數字;樣本補三行 MISS;計劃範圍 2 字面值定義同步 |
| g3 | 折 | code | `t_choice_samples_batch2` 比對 C-36 與 C-37 的 literal-arg、C-34 與 sbr.yml 的 value-pos 一字不差 |
| a1 | 折 | code | `_gov_choice_counts` 放行取最後一筆改用 `_loop_ts_newer` |
| c2 b1 | 折 | code | `t_gov_stats_choice_by_row` 加混時區兩筆放行、字串順序一致的兩筆放行、先殺掉後存活的壞法、C-9 與 C-32 排序;測試說明的翻紅釘改成實跑過的 |
| b3 | 折 | code | 排序鍵改 `isascii() and isdecimal()`;測試加 `C-²` |
| c3 | 折 | code | `t_choice_points_nul_safecall` 加多位元組案例(假命中與真 ast-grep 各一) |
| b4 | 折 | code | `t_choice_points_compose` 加只改右括號那行 |
| b2 g1 | 折 | code | check.py `_choice_retired`:冒號半形全形都認;提到「已撤列號」的行不是恰好一行頂格就報看不懂;`t_choice_table_batch2` 加四種怪寫法 |
| r1 r2 | 折 | code | nul.yml C-33、api.yml C-34 到 C-37 的父節點條件改雙重否定;計劃〈實務隱患〉寫入實測門檻;規則包筆記補 PITFALL |
| k1 | 折 | spec | 驗證筆記 REVISIT 改 2027-01-17(滿兩個月) |
| k2 | 折 | spec | Systems/kotlin規則包 補第二批來源與不收理由的 WHY 行 |

修完逐一改壞驗證(先改壞再跑對應測試):放行直接比字串、放行取第一筆、終態取最後一筆、排序照字串、排序用 isdigit、`!!` 位移用字元數、引數錨點不含右括號行、`.let` 不排除沒大括號分支、負數兩份都拿掉、字元常數只拿掉一份、已撤列號不認全形、已撤列號容許前綴——12 個全部翻紅。「`?.` 拿掉父節點條件」沒紅:語法上 navigation_suffix 只會出現在 navigation_expression 底下,那個條件是防衛性寫法,不是守衛。
