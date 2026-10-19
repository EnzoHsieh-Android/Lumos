preflight-4: ran

# 前端框架從vue分出 r1 前掃收貨

前掃四類:①未定義的詞 4 條、②壞引用 0 條、③範圍自相矛盾 1 條、④機械宣稱驗語意 1 條不成立(另附兩條附注)。①③與④全部直接修真檔 `docs/lumos-toolchain-knowledge/Projects/前端框架從vue分出_計劃.md`;沒有任何一條動到決策 d1 的裁定,所以沒有「升級為正式 finding」的項目。同時照編排者兩項指示修:vitest 一節由本計劃吸收(兩篇各補一句)、B10 角色判定翻案記成決策 d2。

## 修改對照

| 類 | 前掃說的 | 修改前 | 修改後 |
|---|---|---|---|
| ①-1 | `shape_only` 沒解釋 | 〈現況〉B10:「(標 `shape_only` 的 Spring 兩題與外部回應碼題除外)」 | 改成括號內說明 `shape_only` 是題目旗標:只在改動行真的寫出那種形狀時才亮,不因行數門檻整組亮、也不進改檔前推播的整組清單;現在標它的是 Spring 兩題與外部回應碼題 |
| ①-2 | `when_raw` 沒說跟 `when` 的差別 | 〈做法〉F2:「觸發字照 SOP 第 5 步「範式詞+反面詞」:」 | 後面補:`when` 先挖空字串字面、剝註解再比;`when_raw` 只剝註解、保留字串內容,只放要看字串才判得出的樣式 |
| ①-3 | 佔位符 `{method}`、`{LINT_SARIF_OUT}`/`{LINT_FILES}` 沒說來源 | 〈現況〉init 骨架:「run_cmd 一律 `npx jest -t {method}`;」;〈做法〉W7 範本括號只列指令 | `{method}`:設定檔 run_cmd 的佔位符,合約測試閘跑單支時換成測試名、經 shell 引號處理。`{LINT_SARIF_OUT}`:lumos 換成 SARIF 輸出檔路徑、缺了格式檢查會唸;`{LINT_FILES}`:新增告警閘換成改到的檔清單;指到 Systems/lint-declaration-health |
| ①-4 | 做法段引用「設計審 r1 資源併發 F1」等輪次代號 | 〈做法〉react-idioms 十一條後括號:設計審 r1 資源併發 F1、r2 資源併發 F1、r2 資源併發 F4、r2 資源併發 F3、代碼審 r1 正確性、合約席、代碼審 r1 正確性、設計審 r1 邊界 F7 | 全部改寫成現象(例:「輪詢的舊回應晚到蓋掉較新的庫存」「StrictMode 第一次掛載的請求晚到,把第二次掛載的在飛旗標清掉」),並指到 order-web 卷證路徑 `/Users/enzo/orca/workspaces/order-web/governance/review-reports/` 的 `搶購下單畫面/`、`code-搶購下單畫面/` |
| ③-1 | 八格表說 typescript 加 `.jsx`、S28 釘它,做法與提交方式沒有對應 | 只有八格表一格與 S28 | 〈做法〉新增「符號比對 profile 收 `.jsx`」一小節(改 `SYMBOL_PROFILES[\"typescript\"]` 的 code_exts、為什麼 `_stack_guess` 不用改);〈提交方式〉第一個提交寫明「程式(含符號 profile 收 `.jsx`)」 |
| ④-1 | 「`_RAN_EVIDENCE` 只有 node-jest 一條」不成立 | 「`_RAN_EVIDENCE` 只有 `node-jest` 一條(…)」 | 「`_RAN_EVIDENCE` 收了 swift-xctest、csharp-xunit、node-jest、python 四種;JS 系列只有 `node-jest` 一條(…),沒有 `node-vitest`」 |
| ④附注-1 | `_stack_key_for_file` docstring 寫純 .ts 前端檔回 None,程式回 "vue" | 計劃沒提 | 〈做法〉F2 的 `_stack_key_for_file` 那條補:實作時改正 docstring,照實寫 node/vue/react 三種回傳值,找不到或解析不了 package.json 才回 None |
| ④附注-2 | Vitest 5.0.4 摘要字樣與 eslint 9 預設行為是外部實測,要附佐證 | 〈現況〉只寫實測結果;PRIOR-ART 只寫「eslint 9 起預設 flat config」 | vitest:寫明指令 `NO_COLOR=1 npx vitest run -t <名>` 與原始輸出存在本檔附錄;eslint:引 order-web 的 eslint 9.39.5 原始碼 `lib/eslint/eslint.js` 判定函式回 `process.env.ESLINT_USE_FLAT_CONFIG !== "false"`。另順手把 F1 樣式描述補「行首前面可有空白」(原始輸出顯示摘要行是縮排的) |
| 編排者-1 | vitest 一節由本計劃吸收 | F1 末尾「實作提交時在那一節補一句指到本篇」 | 改成「吸收《逾期回頭條件立案清單2026-10_計劃》第 10 節」一條,寫明做完的判準;那篇第 10 節加一行「由誰做:2026-10-15 併進本計劃」 |
| 編排者-2 | B10 角色判定翻案要記決策 | 〈做法〉B10 角色那條寫「這回應…的理由」 | 新增決策 d2(context、三個不選、代價),做法那條改成「翻掉〈已知限制〉的設計取捨,理由見 d2」 |

## 附錄:vitest 5.0.4 實測原始輸出(2026-10-15,order-web 工作樹,兩次都回 0)

`NO_COLOR=1 npx vitest run -t '偏移與倒數用同一個注入時鐘'`:

```

 RUN  v5.0.4 /Users/enzo/orca/workspaces/order-web


 Test Files  1 passed | 8 skipped (9)
      Tests  1 passed | 33 skipped (34)
   Start at  17:06:22
   Duration  760ms (environment 78%, setup 14%, import 3%, transform 2%, tests 2%, worker 1%)
```

`NO_COLOR=1 npx vitest run -t 'zz_no_such_test_xyz'`:

```

 RUN  v5.0.4 /Users/enzo/orca/workspaces/order-web


 Test Files  9 skipped (9)
      Tests  34 skipped (34)
   Start at  17:06:23
   Duration  650ms (environment 81%, setup 14%, import 3%, transform 2%, worker 1%)
```

## 六席收貨與處置

收貨:正確性 6 條(major 2)、邊界 9 條(major 2)、整合 7 條(major 1)、資源併發 3 條(major 1)、回滾 4 條(major 0)、架構對齊 9 條(major 0),共 38 條:major 6、minor 32,blocking 6(正1、正2、邊1、邊2、整1、資1)。四類:折入 38 條;駁回 0 條;升級為正式 finding 0 條(架9 原本列為要人裁,2026-10-15 編排者裁定加題後改成折入);附注 1 則(架構對齊 ⚠ .java 與 .kt 兩套判法,不計條數,已在計劃 B10 角色那條寫明刻意的理由)。每條都回程式或真帳核對過,席位的觀察全部重現得出來,所以沒有駁回;折法是我自己定的過關條件,沒有照抄席位開的藥。

| 根因組 | 條目 | 折法 |
|---|---|---|
| B10 伺服端訊號會把 Android 判成伺服端 | 正1、邊1 | 改成「Android 跡象優先」:檔內 android 匯入、建置檔的 `com.android.`、版本目錄 `libs.plugins.android`、`android {` 任一 → Android;只認伺服端外掛(`org.springframework.boot`、`io.ktor.plugin`、`ktor-server`),不認一般 `io.ktor`;判錯只准往「判不出」。新 S31;決策 d2 的 content、why_chosen 同步改寫 |
| B10 讀法、批次預取、版本、上限、快取 | 正2、邊4、資1、架1 | 判定函式收 `reader`;pitfalls 與推播讀工作樹、角色路讀起點版;建置檔候選併進 `_review_role_wanted`,受 `_ROLE_READ_CAP`/`_ROLE_MAX_BYTES`/時間預算管;檔頭 64KB;快取存建置檔文字、鍵含讀取來源;pitfalls 一次最多判 300 支,超過算判不出。S26 改成派工路徑;新 S34 |
| B10 過濾沒收齊、集合範圍、旗標形狀 | 正3、邊2、邊3、架2 | 旗標改布林 `android_only`;一支共用過濾函式套在 `_stack_applicability`、`stack_qs` 整組欄、改檔前推播整組、張力候選四處;集合定義成「跟 `_by_stack` 同一份的非測試 .kt 檔」,讀不到、超上限都算判不出。新 S32、S33 |
| S23 字面與 shape_only 現況不符 | 正6 | S23 改成「四題整組列出、shape_only 三題照舊不因門檻亮」 |
| 跑過證據樣式的錨定、雙讀者、二次方回溯 | 正4、邊6、資2 | 樣式定成 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed`:不錨行首、不加旗標(兩個讀者共用、逐行讀者不去色),中段限長。我重現:現行 jest 樣式 2 萬字 2.71 秒、4 萬字 11.08 秒;新樣式同輸入 0.0 秒,五種真實摘要判定正確。fix_hint 補 vitest reporter。新 S35 |
| vitest 每支測試的成本 | 資3 | F1 加「成本要知道」一條,指到既有 `bound_tests.parallel` |
| 第 10 節判準沒人驗、中文測試名與不做項目沒有落點、比對表代號 | 整1、整5 | 判準拆兩半:單元層 S4–S7;實地綠燈寫成 S30(manual),並在摘要 REVISIT 加「測試名收自由字串計劃做完就跑 S30,過了才算第 10 節做完」;〈不做〉指到 `Projects/測試名收自由字串_計劃`、`Projects/前端知識與風險詞_計劃`;〈現況〉開頭說明代號只是簡稱、每節先寫現象 |
| eslint 偵測細節 | 正5、邊7、架3、架6 | 只有 `.eslintrc*` 時範本帶 `ESLINT_USE_FLAT_CONFIG=false`;lint.json 已存在 init 不印;兩種都有時列全部、給新式;init 用 `⚠` 前綴、指令獨立一行;`_LINT_CONFIG_GLOBS` 補 mts/cts 並互相註明。新 S36、S37 |
| 前端判定的混合依賴與重複表 | 邊8、架4、架5、整7 | react 只在「沒有其他任何前端框架」時判;收依賴鍵抽共用(三類);慣例 skill 改查既有 `_ARCH_IDIOM_SKILL`(補 node、react 兩列),既有守衛自動涵蓋。新 S38 |
| react 觸發字寫法 | 邊5 | 七題觸發字改寫成可直接編譯的 regex 原文;react-key 兩條改放 `when` 並給出具體樣式 |
| react-idioms 機檢代號沒有守衛 | 邊9 | S29 改成機械測試 `t_react_idioms_rule_names_known`(代號限固定名單、標已實跑或未實跑) |
| 散落清單漏項 | 整2、整6 | 散落清單擴成七項:題數串與鏡像表、表態閘那句、SOP 三處、兩支測試、templates 兩處、ONBOARDING 與 ARCHITECTURE、node-idioms description;lands_in 加 Systems/補新語言SOP |
| lands_in、提交分法、被翻的原筆記 | 整3、整4、架7、架8 | 改成一功能一提交(六個);效能檢核目錄跟程式同提交、只有 linter精選目錄另提交;角色鏡頭與 Java/Kotlin 判法說明寫進 Systems/pitfalls-code-loop;代碼審前後端角色鏡頭計劃的兩處原文各補一句指到 d2 |
| 回退與在途表態、撤除條件量不到 | 回1、回2、回3、回4 | 〈回退〉加三件事(重表態、vitest 證據樣式退回會被擋、其他刪檔);新 S39(題組換了的擋下訊息);RETIRE-IF 改成帳上量得到的口徑(人答全是 na,同 `lumos stats` 死題候選) |
| react 題組缺「並行等待」題 | 架9 | 折入(2026-10-15 編排者裁:使用者只裁「走 React 專屬題」,加一題不算翻裁定):新增 `react-parallel`,`when` 只收賦值式 await、迴圈裡 await、`forEach(async`、`Promise.all` 這類具體寫法,不收裸詞 await;題目帶 `min_lines: 2`(至少兩行命中才亮,近似連續兩個 await);決策 d1 記一句;新 S40–S42,S17 與題數、鏡像表改成八題 |

另依編排者指示折入(不是席位條目):跟 `Projects/前端知識與風險詞_計劃` 的交界——related 回指、infra 判定排在 react/vue 之前、後合者補 `t_infra_before_react_stack_key`。

駁回重現表:無(0 條)。
