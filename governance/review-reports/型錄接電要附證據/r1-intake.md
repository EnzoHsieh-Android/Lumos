# r1 收貨紀錄(型錄接電要附證據)

preflight-4: ran

## 首輪前掃(派一席照固定清單掃,原始報告在 sweep 目錄外,摘要如下)

- ① 未定義的詞(批一、批四、通電批次、現成規則欄、情境欄、排除字表、擋得到、漏網帳):直接補進〈用詞〉,不算 finding。
- ② 壞引用:「漏網帳」沒給路徑 → 補 `docs/.escape-log.jsonl`;「四次、四種漏法」對不到卷證 → 改寫成逐次對應(r1、r2、r3 代碼審與事後審查),另寫明預設關與 Hint 兩種是全表核對才發現。
- ③ 範圍自相矛盾:預期值表 UI-49 那列前提是範圍 2 先做完 → 補前提;S3 只列 5 列 → 改成全表核對的 12 列;compose-rules 的列沒有自帶證據的寫法 → 〈用詞〉寫明全部要附證據。
- ④ 機械宣稱驗語意(修改前→後):
  - 「168 列」「39 列自帶」:實跑成立,不改。
  - 型錄自檢跑在哪:前→計劃沒寫;後→範圍 3 寫明跑在測試總檔的 `t_kt_catalog_*`,推送前掛鉤沒有另外呼叫(grep scripts/lumos、scripts/hooks、.github 無 `--catalog-only`)。
  - 自帶證據的列只看情境欄寫了檢查 id:前→沒驗跟現成規則欄一致;後→範圍 3 加「情境欄的檢查 id 要出現在現成規則欄」。
- 沒有動到核心裁定的條目。

## 全表核對(範圍 1 的依據)

六包代理各讀官方頁(sweep/p1.md 到 p6.md),判不出的 10 列再派一席讀檢查器原始碼(sweep/p7-src.md)。結果:129 列中擋得到 117、擋不到 9、預設關或 Hint 3。

## 四席收貨

四席(通才、正確性、證據可信、架構對齊)交回後一次存檔,取自逐字稿;四份已是正規化格式。引句:通才、證據可信、架構對齊全數錨定;正確性 7 句有 1 句錨不到(第 2 條寫成「每列一筆,型錄列編號」,快照是冒號),那條與通才 a2 同一件事,下表機械重現。編號:通才 a、正確性 b、證據可信 c、架構對齊 d。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| a1 | 通才 | major | 自帶證據的列只驗檢查 id 出現,不驗預設開與等級,抄一句「形狀:由 Android Lint X 判」就繞過 | HIT:讀快照範圍 3,只有 id 比對 | 折:取消自帶證據豁免(G4) |
| a2 | 通才 | major | 證據表以列編號為鍵,同列兩個標籤一筆就全放行 | HIT:python 數到 21 列同時標兩個標籤 | 折:證據以(列,標籤)為單位(G2) |
| a3 | 通才 | major | 證據的「檢查」欄沒跟現成規則欄比,佔位字也過、型錄改了證據不失效 | HIT:讀快照範圍 3 的驗證項 | 折:檢查欄要是該列該標籤接電段抽出的規則碼(G2) |
| a4 | 通才 | major | 證據表沒有預設開、等級欄,自己定義的兩種漏法沒守衛 | HIT:讀〈用詞〉證據表欄位 | 折:證據加等級、預設、套件版本欄並驗(G3) |
| a5 | 通才 | minor | 推送前子集的觸發沒點名證據檔 | HIT:讀範圍 3 | 折:證據改放型錄內(G1),觸發同型錄 |
| a6 | 通才 | minor | TSV 重複列編號、欄位數沒規定 | HIT:讀範圍 3 | 折:改 markdown 表、重複編號報(G1) |
| b1 | 正確性 | major | 只在一段補註記不足以退回:API-23、TEST-25、UI-11 多段各自判 | HIT:python 實跑 API-23 只改最後一段仍回 Android Lint | 折:退回不再靠註記字,改由判定表決定(G5) |
| b2 | 正確性 | major | 同 a2(兩標籤列一筆證據) | HIT:同 a2;此條引句錨不到,以 a2 的機械重現採信 | 折:同 a2 |
| b3 | 正確性 | major | 同 a3(檢查欄與規則欄漂移) | HIT:同 a3 | 折:同 a3 |
| b4 | 正確性 | major | 39 列自帶證據跳過預設關與 Hint 核對;id 比對是不是整詞沒寫 | HIT:讀快照;DATA-79、DATA-83 帶「只看」範圍限定 | 折:同 a1(G4),規則碼整詞比對 |
| b5 | 正確性 | major | 情境欄多個 id、帶括號時怎麼解析沒寫 | HIT:讀型錄情境欄三種寫法 | 折:G4 取消豁免後不再解析情境欄 |
| b6 | 正確性 | minor | TSV 含 tab、重複列編號 | HIT:同 a6 | 折:同 a6 |
| b7 | 正確性 | minor | 查證日期只驗格式,官方改版不會被發現 | HIT:讀快照 | 折:〈天花板〉寫明,回頭條件改成真跑重驗 |
| c1 | 證據可信 | major | UI-96 唯一檢查是 Hint 卻判擋得到;UI-13 要寫 Warning 那條 | HIT:curl ArcAnimationSpecTypeIssue 頁 Severity: Hint | 折:G3 欄位擋下、兩列資料改(待真跑先導確認) |
| c2 | 證據可信 | major | Slack 四條有版本門檻,範本在 AGP 9.2.0 以下裝 1.4.2 沒有這幾條 | HIT:Slack CHANGELOG 1.5.0、1.6.0 New 條目;Systems/linter精選目錄 版本對照 | 折:G3 套件最低版本欄,Slack 跟範本最低版本比 |
| c3 | 證據可信 | major | UI-92 ConflictingOnColor 只管 Material 2,壞例是 M3 colorScheme | HIT:官方頁 Artifact 是 androidx.compose.material | 折:UI-92 判擋不到(待真跑先導確認) |
| c4 | 證據可信 | major | 同 a4(證據表沒有定義需要的欄位) | HIT:同 a4 | 折:同 a4 |
| c5 | 證據可信 | minor | 「環境沒有」跟型錄 2026-11-05 實跑紀錄衝突;UI-11 實測欄寫實跑命中 | HIT:本機 Gradle 快取有 AGP 8.13.2、Gradle 8.13、compose 與 Slack lint | 折:派真跑先導,計劃改寫成真跑優先(G6) |
| c6 | 證據可信 | minor | UI-100 壞例沒帶 @Preview,照字面不會被報 | HIT:讀型錄 UI-100 壞寫法欄 | 折:壞例補 @Preview |
| d1 | 架構對齊 | major | 證據另放 TSV 是第二種做法(型錄已有〔查證〕欄與〈待查證〉節) | HIT:repo 沒有任何 .tsv;check.py 的 _pending_table、pending_problems | 折:證據改成型錄裡的一節表格,照〈待查證〉的讀法(G1) |
| d2 | 架構對齊 | minor | 網址日期格式另寫一套驗證,_VERIFIED_RE 已有 | HIT:check.py 的 _VERIFIED_RE | 折:重用 |
| d3 | 架構對齊 | minor | 型錄側沒說要用 main_rows | HIT:讀快照 | 折:寫明用 main_rows 與 _cells |

--refuted-set none。

## 依根因分組

- G1 證據放哪(d1、d2、d3、a5、a6、b6)
- G2 證據粒度與檢查比對(a2、b2、a3、b3)
- G3 判準欄位(a4、c4、c1、c2、c3)
- G4 自帶證據豁免(a1、b4、b5)
- G5 退回靠註記字(b1)
- G6 真跑環境(c5、b7)
- 單列資料:c6

## 先查世界

- PRIOR-ART:G3、G6——Android Lint 自己就印得出每條檢查的等級與預設開關:`lint --show <Id>` 印 Severity 與「disabled by default」,`lint --list` 列全部(https://googlesamples.github.io/android-custom-lint-rules/usage/flags.md.html);檢查頁的 Severity 欄也是固定格式。採用:等級與預設欄以這兩個來源填,不靠讀說明文字。最可靠的是真跑:Lint 的 lint.xml 可用 `checkAllWarnings` 一次跑全部檢查、報告帶每筆的 severity(https://developer.android.com/studio/write/lint),本機快取有 AGP 8.13.2 能離線建專案,先導驗證可行性。
- PRIOR-ART:G1——同一份檔裡的逐列附表照型錄既有〈待查證〉節的做法(check.py 的 _pending_table 與 pending_problems 雙向比對);不新開資料格式。
- PRIOR-ART:G2——lint baseline 檔(lint-baseline.xml)以「issue id + 位置」為單位記每筆,不以檔案為單位(https://googlesamples.github.io/android-custom-lint-rules/usage/baselines.md.html);採用同樣的粒度:以「列 + 標籤 + 檢查 id」為單位。
- PRIOR-ART:G4、G5——不靠字面判斷的現成做法就是 G3 的欄位與真跑;所以退回與豁免都改成看判定表,不再補排除字。
