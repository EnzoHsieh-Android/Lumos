preflight-4: ran

# r1 收貨紀錄

## 前掃(首輪四項)

前掃報告原文:`r1-preflight.md`(便宜代理,只讀;①未定義詞 4、②壞引用 2、③範圍矛盾 6、④語意宣稱 11)。①②③與存在類直接修真檔、不算 findings。④語意類逐條修真檔,改前→改後如下;編排者親自對程式驗過標「驗」的幾條。沒有動到核心裁定(第二批收哪幾列的取捨只拿掉頂層 combine,理由是編不過的事實,不是裁定改向),所以不升格成正式 finding。

| # | 宣稱 | 改前 | 改後 | 編排者驗 |
|---|---|---|---|---|
| ④1 | elvis 列錨點 | 沒寫錨點(照慣例會填「運算子」) | 錨點「運算元起始」,不改 `_CHOICE_OP_RE` | 驗:`_CHOICE_OP_RE` 只有比較/邏輯/算術記號,不含 `?:` |
| ④2 | `$A!!` 括號 | 整節點替換,外層是運算式時加括號 | `$A` 不是單一記號先包 `($A)` 再接 `!!`;預期值表加 `f(a + b ?: c)`→`f((a + b)!!)` | 驗:`_choice_edits` 通用路徑括號包在整個替換文字外 |
| ④3 | `?.`→`!!.` 走哪個錨點 | 一句帶過 | 新錨點「安全呼叫符」與 `_choice_edits` 新分支 | 驗:錨點「方法名」一律走 `_choice_api_edits` 換識別字 |
| ④4 | `(Unit)` 替換 | 引數清單換成 `(Unit)` | 錨點「引數」樣板直接覆蓋,不經加括號 | 驗:通用路徑會包成 `((Unit))` |
| ④5 | 頂層 combine→zip | 收、預期值表給 `zip(a, b)` | 不收,改成預期「不產生」;PRIOR-ART 與〈不做〉寫理由 | 驗:kotlinx.coroutines 的 `zip` 只有擴充函式 |
| ④6 | 新錨點「函式名」與 `_choice_also` | 要新增函式名錨點 | 隨④5 拿掉函式名錨點;`zip` 只走接收者寫法,`_choice_also` 不用放寬 | — |
| ④7 | LaunchedEffect 常數 key 等價 | 沒處理 | 規則排除單一 `Unit`/`true`/`false` 引數;預期值表加一列 | — |
| ④8 | S6 綁的測試 | `t_kotlin_rulepack_samples` | 新測試 `t_choice_samples_batch2` | — |
| ④9 | S7 綁的測試與範圍 | 第一版各列壞法不變、綁 `t_choice_points_stable` | 縮成「只含第一版語法的行」、新測試 `t_choice_points_batch2_stable`;〈實務隱患〉補換壞法一條 | — |
| ④10 | `--stats` 依列號 | RETIRE-IF 假設已有 | 範圍 5 新增「依列號」小節、S8 與預期值表;寫明不加它為什麼不夠 | 驗:`gov --stats` 選擇點段沒有依列號的比例 |
| ④11 | 白名單位置 | 範圍 3 寫 lumos 讀表加白名單 | 移到範圍 4 check.py;NUL 加在 `CHOICE_CATEGORIES` 尾端 | 驗:`CHOICE_CATEGORIES`、`CHOICE_ANCHORS` 只在 check.py |

①②③ 直接修:〈用詞〉補接收者寫法、NUL 命名、各列類別、跑不出結果;RETIRE-IF 指〈回退〉第 1 項並給〈回退〉編號;`lands_in` 拿掉 guard-kill 改 規格閘(範圍 5 落在規格閘);S1 與〈實務隱患〉的型別前提矛盾改成 elvis 列用「運算元有 null 字面值」、預期值表 `x ?: null` 說明改正;範圍 1 補說明段錨點清單與〈統計〉列數同步。

## 席報告收貨(六席,2026-11-16)

六份報告從各席逐字稿取最後回覆原文存檔;report-normalize --write 只把列表縮排裡的 `severity:` 搬成獨立行(正確性 8、邊界 7、整合 5、資源併發 2、回滾 7 處),等級不變。quote-check 六份全錨、refcheck 六份全對、seat-check 因派工單材料寫在各席欄位而判 vacuous。repo 收貨時 `git status` 沒被席位改動。

finding 編號:正確性 c1–c8、邊界 b1–b7、整合 i1–i5、資源併發 r1–r2、回滾 h1–h7、架構對齊 a1–a5(照各報告條目順序),共 34 條。

## 編排者重現

| id | 重現 | 結果 |
|---|---|---|
| c1、b1 | ast-grep 解析 `val n = a⏎    !!.b` 與 `val m = a!!⏎    .b` | HIT:前者第 3 行 ERROR 節點,後者無 |
| b2、c3 | `kind: elvis_expression` 與 pattern `$A ?: $B` 對 `a ?: b` 取後設變數 | HIT:前者 None,後者 A、B |
| b3 | 讀 `_choice_anchor` 與選行 `line_of(anchor) in want` | HIT:運算元起始回節點開頭,續行改動選不到 |
| r1 | 讀 `_choice_push_judge`、`_CHOICE_MAX_MUTANTS` | HIT:回報上限只限存活 |
| h2 | 讀 check.py `--catalog-only` 與 `_choice_rules_match` | HIT:規則多出或缺列會報;樣本核對要帶 --sg |
| 其餘 | 讀報告附的程式行號與計劃原文核對 | HIT(全部成立,沒有判假陽性) |

## 先查世界

- 多行與 `!!` 位置(c1、b1、b3):PRIOR-ART: Kotlin 文法 https://kotlinlang.org/docs/reference/grammar.html 與 SonarSource 解析 Kotlin 換行規則 https://www.sonarsource.com/blog/the-challenges-of-parsing-kotlin-part-i-newline-handling/ :換行只能出現在特定運算子前(`.`、`?.` 可以),後置 `!!` 不行;官方慣例建議 `?.` 換行寫在續行。採用:`!!` 插在前一行最後一個非空白字元之後、`?.` 換 `.`;`?:` 改用運算子錨點落在 `?:` 那一行;引數錨點看節點範圍內任一改動行。
- 等價與必定編不過的壞法(c2、b4、b7、c4、c5、c6、a3):PRIOR-ART: Trivial Compiler Equivalence(Papadakis 等 ICSE 2015)https://discovery-pp.ucl.ac.uk/id/eprint/1499169/1/Jia_Trivial_Compiler_mutation-testing-papadakis-icse15.pdf 編譯後比對抓等價約三成;ISSTA 2024 https://homes.cs.washington.edu/~rjust/publ/equi_mutants_ems_issta_2024.pdf 指出等價壞法多來自常見寫法、可用便宜的靜態分析抓。採用:在規則裡用 `not:` 排除可由語法判定的必然等價(回傳值沒人用的 `.let`、全常數 key)與必定編不過(沒尾隨 lambda、具名 block)——第一版 C-18 已有同做法。不採 TCE 本身:要編譯每個壞法,本機成本跟殺傷力同量級。
- 依列號統計口徑(i1、i2、h6、c8、a4):PRIOR-ART: PIT 壞法狀態 https://pitest.org/quickstart/basic_concepts 與 Stryker 指標定義 https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ :每個壞法一個終態、沒涵蓋與存活分開計、分數只算有涵蓋的。採用:以 (檔, 行指紋, new_sha) 為一個壞法取最新終態;基準沒綠的不算進該列;放行用 (檔, 行指紋) 接最近存活、接不上另計。
- 回退與混合行(h1–h5、h7):查了「mutation testing mutant identity across versions」類做法,論文 2.3 與第一版舊否決已裁「處置鍵不帶壞法」(型錄一改整批作廢的代價更大),本計劃不翻案,改成如實寫進〈回退〉第 3 項與〈天花板〉第 5 條;單列撤的完整清單靠既有 check.py 自檢守。
- 推送負擔(r1、r2):沒有找到可直接套的業界門檻;論文 2.3 用每檔上限 7 控制回報量,本計劃用上線前實測門檻(範圍 7、S9)取代「兩個月後才看」。
- 文件同步與命名(i3、i5、a1、a2、a5、i4、b5、c7、b6):照專案鐵則 5(每支檔有家)與第一版一個類別一個規則檔的慣例,不需外部依據。

## 處置

| id | 去向 | 改了計劃哪裡 |
|---|---|---|
| c1、b1 | 折 | 範圍 3 安全呼叫符兩處編輯;S2;預期值表 S2 第二列 |
| b2、c3 | 折 | 範圍 2 `?:` 用 pattern |
| b3 | 折 | 〈用詞〉`?:` 錨點與引數錨點;範圍 3 選行;S1、S4;預期值表 S1 續行列 |
| c2 | 折 | 範圍 2 `.let` 排除單獨陳述;S3;預期值表 |
| b4、c4 | 折 | 範圍 2 LaunchedEffect 要尾隨 lambda 與至少一引數;S4 |
| b7、c5 | 折 | 範圍 2 全字面值 key 排除;S4;預期值表 |
| c6 | 折 | 範圍 2 combine 排除完整套件名;S3 |
| b6 | 折 | 〈實務隱患〉同名一條;〈天花板〉2 |
| b5、c7 | 折 | 〈用詞〉單一記號定義;預期值表 S1 `repo.load()` 列 |
| c8、i1、i2、h6、a4 | 折 | 範圍 5 口徑;S8 與預期值表 S8;RETIRE-IF 最少筆數與「接上存活的放行」 |
| r1 | 折 | 範圍 7 上線前實測門檻;S9;〈實務隱患〉推送負擔 |
| r2 | 折 | 範圍 7 最大檔挑壞法 ≤10 秒;〈實務隱患〉挑壞法時限 |
| h1 | 折 | 〈回退〉3;〈天花板〉5;〈實務隱患〉換壞法與不可逆兩行改寫(不再宣稱回到第一版行為) |
| h2 | 折 | 〈回退〉1 完整清單與 check.py --catalog-only --sg;〈實務隱患〉守衛面 |
| h3 | 折 | 〈驗收條款〉前的測試做法:S1–S4 用合成型錄列 |
| h4 | 折 | 〈回退〉3 抽樣種子重洗 |
| h5 | 折 | 範圍 1 說明段與〈回退〉1:列號不重用 |
| h7 | 折 | 〈回退〉3 人裁寫回的條款留在計劃 |
| i3、a5 | 折 | 範圍 6 about_code 與過期句子逐條列 |
| i4 | 折 | S7 釘成常數;測試做法說明 ast-grep 沒裝時跳過 |
| i5 | 折 | 範圍 1 各列對應決策表;說明段兩句同步;〈統計〉說明一起改;範圍 3 刪掉多餘的 `_choice_anchor` 改動 |
| a1 | 折 | 範圍 2 四條 API 規則都進 api.yml,一個類別一個檔 |
| a2 | 折 | 〈用詞〉第二批各列類別補理由(第一版 API 已有拿掉呼叫) |
| a3 | 折 | 範圍 2 寫明照 C-18 先例 |

鏡像核對:這輪是整份重寫,編排者自己逐節對過〈用詞〉〈範圍〉〈驗收條款〉〈預期值表〉〈回退〉〈天花板〉的同一件事寫法一致;沒有另派代理(下一輪全新席會再審整份)。
