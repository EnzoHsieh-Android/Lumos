preflight-4: ran

# r2 收貨紀錄

第二輪是使用者 2026-11-16 回「再派」:r1 已過處置閘,計劃幾乎整份重寫,加一輪只看改過的部分(仍整份讀)。材料:`r2-snapshot.md`(spec-freeze 凍結)與 `r2-delta.diff`(r1 快照到 r2 快照)。首輪四項前掃已在 r1 跑過(`r1-preflight.md`),本輪沿用第 2 步的機械排乾:refcheck 2/2 對得上、prose-lint 0、pitfalls --check 有節。

## 收貨

- 六席(正確性、邊界、整合、資源併發、回滾、架構對齊,全 sonnet)全部交回後才一次寫進卷證;報告從逐字稿取最後一則訊息存檔(完成通知會把 `<`、`>`、`&` 轉成跳脫字)。
- 正確性、整合、資源併發、回滾四席初交時每條 finding 沒有獨立的「引句:」行,quote-check 抽不到;退回原席只補引句、其餘不改,重交後六席 quote-check 全數錨定。
- report-normalize:六份都已是正規化格式。refcheck:六份引的路徑與行號全對得上。seat-check:派工單材料格式讓它判 vacuous(與 r1 相同)。
- 收貨時 `git status` 看過 repo 沒被審查席動過;審查席臨時目錄 `/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/` 已刪。

## 重現表(編排者自己跑,不照抄席位)

| finding | 指令 | 輸出 | 判 |
|---|---|---|---|
| c1 b1 i1 r1 a1 | 載入 `scripts/lumos`,`_choice_top_prec('flag ?: false')`;再把 `_CHOICE_OP_RE` 前面加 `\?:` 重跑 | 現況 `0`;加入後 `KeyError('?:')` | HIT |
| c2 i2 r4 b6 a2 a3 | 讀 `_gov_row` 的欄位白名單與 `_gov_choice_counts` | `ck` 欄位沒有 `new_sha`;`ck_waive` 有 `row` 且現行形狀計數已用它;註解寫 `ts` 是 HEAD 提交時間 | HIT |
| r4 i2 b6 | `grep -n 基準不綠沒跑 scripts/lumos` | 實際字串是「基準不綠沒跑」,計劃寫成「基準沒綠所以沒跑」 | HIT |
| r2 b5 | `lumos choice-points --help` | 只收 `--diff` 範圍;整個專案一次掃會撞整次共用的 15 秒時限,計劃原量法做不到 | HIT |
| 其餘 | 席位自帶 ast-grep 實測(YAML 引號、註解兄弟節點、remember 排除、value-pos)與檔案行號,refcheck 驗過存在 | — | 採信(機械佐證) |

## 分組

1. **`?:` 進共用運算子正規式會當掉**(c1 b1 i1 r1 a1,五席獨立):major。
2. **依列號統計的資料來源與終態判法**(c2 i2 r4 b6 a2 a3 r6):major。
3. **上線前量法做不到、門檻擋不到真成本**(r2 r3 b5 b7 i8 c4):major。
4. **列號不重用沒有機械保證、回退清單漏項**(h1 h2 h3 h4 h5 h6):h1 major。
5. **規則細節**(c3 b3 b8 b9 i4 i7 r5 c5):minor。
6. **測試分工與既有測試**(b2 i5 b4 i3):minor。
7. **錨點出處與文件同步**(a4 i6):minor。

## 先查世界

- 第 1 組:PRIOR-ART: Kotlin 文法運算子優先層級表裡 Elvis 介於 infix 與比較之間(https://kotlinlang.org/docs/reference/grammar.html;JetBrains 文法檔鏡像 https://pigweed.googlesource.com/third_party/github/JetBrains/kotlin/+/0801cc12da5af28d8009eb66d070f37079ab755d/grammar/src/expressions.grm),所以 `?:` 綁得比 `&&`、比較緊,席位的輸入成立。採用「`?:` 只在那一列比字面,不進共用正規式」:`_choice_top_prec` 對表外運算子一律加括號本來就安全,不必替 `?:` 補優先層級。排除「把 `?:` 補進 `_CHOICE_PREC`」:要改一張多處共用的表又得新增測試面,比不碰它大。
  方向:對 — 照語法樹節點位置定錨、只為新列加專用比對,沿用 ast-grep 結構比對(https://ast-grep.github.io/guide/pattern-syntax.html)與文法優先層級(上列文法頁);r1 也在這一組(錨點)折過,這輪是共用常數的副作用,不是方向錯。
- 第 2 組:PRIOR-ART: PIT 與 Stryker 每個壞法只有一個終態(killed、survived、no coverage 等),報表依壞法種類彙總(https://pitest.org/quickstart/basic_concepts、https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/)。採用「每個壞法一個終態、依列號彙總」;終態不靠時間先後(統計列的時間是提交時間,同提交打平),改成曾殺掉優先;放行用事件自帶列號,不另造歸屬規則。
  方向:對 — 上列兩個工具都是「壞法一個終態+依種類彙總」;r1 已在這組折過口徑,這輪是資料欄位跟程式對不上,方向不變。
- 第 3 組:PRIOR-ART: 論文的差異式做法只變異改到的行、每行與每次審查限量,成本以每次改動計(https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/;論文 https://arxiv.org/pdf/2102.11378)。採用「固定最近 10 個真實提交逐一跑 `choice-points`、量每次改動的成本」,不量整個專案(那不是推送會遇到的量,也會撞時限)。
- 第 4 組:PRIOR-ART: ESLint 規則停用政策——停用的規則留著標停用、不刪(https://eslint.org/docs/v8.x/use/rule-deprecation)。採用「說明段一行已撤列號、check.py 擋再出現」。沒查到 SonarQube 規則鍵的重用政策(查詢詞:static analysis rule id deprecated never reused SonarQube rule key),不引。
- 第 5 組:PRIOR-ART: Kotlin coding conventions 與 ktlint `chain-wrapping` 規則寫明換行時 `.`、`?.` 放下一行(https://kotlinlang.org/docs/coding-conventions.html、https://pinterest.github.io/ktlint/0.48.0/rules/standard);計劃依據表原本把這條掛在文法頁,改掛這兩個出處(i8)。YAML 引號與 value-pos 照席位在 ast-grep 0.51.2 的實測。
- 第 6、7 組:專案內部約定(測試分工、錨點單一出處),不需外部依據。

## 處置

全 38 條折入計劃(第 1 組改〈用詞〉`?:` 的錨點與範圍 3;第 2 組改範圍 5、S8 與預期值表;第 3 組改範圍 7、S9、實務隱患;第 4 組改範圍 1、4、〈回退〉、S5、RETIRE-IF;第 5–7 組改範圍 2、6、測試做法、S2–S6)。沒有放行、沒有重現不到的。新增機制只有「已撤列號」一行與 check.py 兩條檢查,不加它的最小解為什麼不夠寫在計劃範圍 4。

| id | 去向 | 種類 |
|---|---|---|
| c1 c2 c3 c4 c5 | 折 | spec |
| b1 b2 b3 b4 b5 b6 b7 b8 b9 | 折 | spec |
| i1 i2 i3 i4 i5 i6 i7 i8 | 折 | spec |
| r1 r2 r3 r4 r5 r6 | 折 | spec |
| h1 h2 h3 h4 h5 h6 | 折 | spec |
| a1 a2 a3 a4 | 折 | spec |

## 鏡像核對(折完派 haiku 只看本輪差異+席報告目錄)

核對代理指出的沒跟上處,全部補進計劃:
- 部分上線:範圍 1 加一條總規則(NUL、安全呼叫符、引數、`$A!!` 各在哪些列上線時才加),範圍 2、4 改成照總規則;「新增第二批六列」改「最多六列」。
- 預期值表補 S6 四種不命中(完整套件名 combine、註解後的 `?.`、`LaunchedEffect()`、具名 `block =`);「前一行結尾是註解」統一成「前一個兄弟節點是註解」。
- 放行「最後一筆」:寫明取提交時間最大那筆,同一個提交的重複放行去重時已併成一筆(放行事件鑑別子是 `檔:行指紋`);choice-kill 事件鑑別子是事件隨機碼,同提交先存活後殺掉不會被去重併掉(a3)。
- 範圍 7 拿掉列的規則改成對超標的那一項(a、b、c)各自量單獨增量;b 的牆鐘寫明含掃描(i8);驗不了檔數涵蓋整批退回逐檔(r3);不設「每 20 行平均壞法數」門檻的理由寫進範圍 7(r2);編不過壞法每個花幾秒一併記(r6);深層巢狀 elvis 輸出平方成長寫進實務隱患(b5)。

席位建議裡沒照做的子項與理由(那條 finding 的主問題已折):
- h4 建議 RETIRE-IF 改機器式寫法:RETIRE-IF 是撤除條件不是 REVISIT,門檻要讀 `gov --stats` 的印出數字,沒有現成的機器式寫法可用;補了上線日寫進 Verification、REVISIT 最晚日、分母口徑。
- h4 建議統計印「已撤」:要讓 `gov --stats` 讀型錄,多一條依賴;改成撤列時把數字抄進 Verification(證據不會過窗消失)。
