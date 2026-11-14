# code-改動選擇點 r5 收貨紀錄

使用者 2026-11-14 看完第四輪攤人摘要後親口裁「加一輪」(第二筆 cap-decision extra-round)。派 7 席:正確性、邊界、資源、合約、架構對齊各看修補差異 r5-repair-code.patch 158 行;通才另加測試差異共 321 行;資安看整份 r5-snapshot.patch 14964 行(78 支檔),派工詞明寫逐檔看整份並列出讀過的檔,報告列了 78 支與各自結論(docs/ 筆記與 review-reports 散文為掃描式,席自述)。固定席這輪仍沒附上(派工鏡頭超時)。
編排者在修補提交後另於錨點提交 83ac95c8 重跑 `lumos loop fix-check code-改動選擇點 --round r4`:全部通過(144.9 秒,修正前 04b21d1f → 修正後 83ac95c8);附帶提醒重跑殺傷力配方 `lumos guard kill Systems/canary-audit --id 259cf76bb8ae`,推送前處理。
引句:正確性、資源、架構對齊、資安四份全數錨定;邊界、通才、合約 clean 零條。

## 重現表

| id | 核對 | 結果 |
|---|---|---|
| c1 a1 | 讀 `_choice_kill_report` 不唯一那行:修後為 `_kill_esc(_sh_quote(...))`,控制字元在引號內被換成字面 `\uXXXX`;修前 04b21d1f 為 `_kill_esc(x['file'])`,同樣換成字面。兩版照貼後都對不上原檔名、lint-waive 回找不到;不執行任何指令 | HIT |
| r1 | 資源席以 awk 抽 `_choice_test_blobs` 區段,兩版 md5 相同(f3047706…);編排者 `git diff 04b21d1f 83ac95c8 -- scripts/lumos` 只有 `_choice_kill_report` 一行 | HIT |
| s1 | 讀 `_render_gov_choice`:`decl`、`t` 過 `_kill_esc`,`waive` 的 label、`nores` 的 reason、乾節點 row 沒過;資安席附治理帳注入兩行與 `gov --stats` 輸出 | HIT |
| s2 | 讀 `_situation_rule_test_platform`:`lumos lint-waive {_sh_quote(_CHOICE_WAIVE_PREFIX + point)}` 有引號、沒 `_kill_esc`;換行與控制字元檔名被 git 加引號後 `_kt_sit_hunks` 先擋,只剩雙向字元這類能到這裡;席標推論、沒實跑 | HIT |

## 分組與處置

| 組 | 根因 | 條目 | 處置 |
|---|---|---|---|
| — | 照貼放行指令遇控制字元檔名,顯示用跳脫讓參數對不上原檔名 | c1 a1 | 放行(minor,附來源):修前同輸入同樣對不上,安全方向的失敗(lint-waive 回找不到、不誤放行、不執行);要 tab、換行或雙向字元檔名才碰到;兩席獨立判 minor |
| — | 點號名取最後一段後常見字輸出與記憶體無上限 | r1 | 放行(minor,附來源):與第三輪 r2、第四輪 r1 同一件事,前兩輪已放行;函式兩版逐位元組相同;只多跑不漏 |
| — | 治理帳欄位回顯到 `gov --stats` 沒過 `_kill_esc` | s1 | 放行(minor,附來源):lumos 威脅模型為單人自用、AI 依序操作,外來文字回顯屬已裁放行類(縱深防禦,無執行碼或繞過守衛);要先有人把惡意帳行寫進 repo |
| — | `situation-rule --point` 擋下訊息的放行指令檔名沒過 `_kill_esc` | s2 | 放行(minor,附來源):有 `_sh_quote`,不執行;只剩雙向字元檔名能到;席自標推論未重現 |

## 先查世界
- 本輪沒有折入,不需查做法;放行的四條都是顯示層縱深防禦或既有已放行的資源取捨。

## 回歸因果(第 5 輪)
- 修補差異的程式只有 `_choice_kill_report` 一行(加 `_sh_quote`)。
- 有證據的原有漏查:c1 a1(修前同樣對不上,正確性席兩版實跑)、r1(函式兩版相同)。
- 本分支既有、非本輪修補造成:s1(`_render_gov_choice` 不在修補差異內)、s2(`_situation_rule_test_platform` 不在修補差異內)。
- 判過且無修補回歸:regression-set none。

## 結論
本輪 7 席最高 minor、零 blocking;5 條全數附理由放行,0 條折入。修補(K1–K3)有修前紅、修後綠與改壞驗紅的兩版證據(通才、邊界、正確性、合約四席各自重現)。
