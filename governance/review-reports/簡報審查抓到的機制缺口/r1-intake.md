# r1 收貨紀錄:簡報審查抓到的機制缺口

preflight-4: ran

## 首輪前掃(固定清單四項,sonnet 一席,2026-11-09)

命中 12 條:未定義 3、壞引用 1、範圍矛盾 5、機械宣稱語意 3。未定義、壞引用、範圍矛盾直接修真檔;語意類三條逐條留修改前→後。

### 語意類(修改前 → 修改後)

1. 「推送閘、代碼審、pitfalls 共用同一支分級函式,所以三處同時生效」
   - 查到:`_pitfall_tier` 只在 `_pitfall_diff_collect` 呼叫;推送閘經 `_codeloop_pitfalls_tier` 開子程序跑 pitfalls;`loop next` 不算分級,只收 `--tier`,第一筆定錨後不准換;`spec-gate --push-check` 的 light 是另一套。
   - 修改前:三處同時生效。
   - 修改後:生效處是 pitfalls 輸出與推送閘 `code-loop check`;`loop next` 由編排者照 pitfalls 帶、已定錨迴圈不會事後升級;`spec-gate --push-check` 的 light 不受影響,推送以 `code-loop check` 為準。
2. 「分級函式讀這次範圍內每個提交訊息」(範圍沒定義,三點範圍會把對面分支的提交算進來)
   - 修改後:用詞節新增「這次範圍」:先用 `_diff_range_ends` 拆起點終點(三點取共同祖先),再讀 `git log 起點..終點`;測試加三點範圍那一條。
3. 「本 repo 先前 [[Projects/進度從提交推導_計劃]] 也選 trailer(Lumos-Task)」
   - 查到:那篇的 trailer 決策已翻案(d7):「trailer 寫錯的輸出跟沒寫一樣,會靜默失敗」。
   - 修改前:人工標記照 git trailer 格式認,值第一個字是 high 才算。
   - 修改後:訊息裡任何地方出現 `Lumos-Risk` 字樣(正規式 `lumos[-_ ]?risk`,不分大小寫)就判 high,值寫什麼都照 high;寫錯格式的結果是多審,不是靜默沒作用。測試照改(寫 low、寫在內文、底線寫法、只改文件都要 high)。

### 其餘直接修真檔的

- 認工具的方法補成正規式與字的邊界;掛點寫明在命令真的跑完之後。
- 範圍 1、S1、預期值表補 `launchIn` 分支。
- 回退補型錄 STATE-5 與 README 中英兩版。
- S4 與預期值表補英文版、補「回到 20/25」「筆記正確時還沒量」。
- README 拿掉「5 題各 5 場」(repo 內找不到出處,改寫「每組 25 場」)。
- 實務隱患補「同一行改字留著 noqa 會算新增」「讀不到提交就不升」「順手提到也算」。
- 天花板補推送閘兩種直接當 standard、讀不到標記的情況。

## r1 席報告收貨(四席,2026-11-09)

四份報告從逐字稿存檔;正確性席只做了 report-normalize 的格式搬移;整合席第一次交回沒有引句,退回補引句後重交(內容與條數未變)。四份 quote-check 全數錨定、refcheck 全部對得上。repo 收貨時 `git status` 只有審查卷證與治理帳在動,席位沒有改 repo。

編號:正確性 c1–c10、邊界 b1–b17、整合 i1–i16、架構對齊 a1–a4(架構對齊席另有兩條 ⚠ 交編排者裁,不計條數,一併處理)。

## 先查世界

PRIOR-ART: 人工指定高風險 → GitHub CODEOWNERS 用路徑指定敏感區要誰審(https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners);第三方整理指出 CODEOWNERS 寫錯的行會被靜默略過,所以採用時加「對不到任何檔的路徑要印出來」。採用:路徑清單,不採:提交訊息標記(r1 四席實測被合併主線、空樹起點、壞編碼、壓提交四種情況打穿)。
PRIOR-ART: ruff 的抑制寫法 → 官方文件 https://docs.astral.sh/ruff/linter/#error-suppression :inline `#noqa` 不分大小寫、`#` 後可有空白;檔案層級 `# ruff: noqa`、`# flake8: noqa`;另有 `ruff: ignore`、`ruff: file-ignore`、`ruff: disable`。採用:對照表照文件改成不分大小寫並補這幾種。
PRIOR-ART: detekt 的抑制寫法 → 官方文件 https://detekt.dev/docs/introduction/suppressing-rules :規則名放在 @Suppress 的字串裡,可帶 detekt: 或規則集前綴,也接受 @SuppressWarnings。採用:括號裡全是全大寫底線的(Kotlin 編譯器警告名)不算,其餘算;use-site 前綴(@get:、@field:)一併認。
PRIOR-ART: 命令裡認工具 → 本 repo 已有 detekt 判定的命令切段(`_detekt_walk_segments`、`_cmd_basename`),架構對齊席指出整串正規式是第二套做法。採用:沿用切段、取每段第一個詞,外加套件執行器(npx、uv run、python -m 等)往後看一個詞。

## 不加新機制的最小解為什麼不夠

範圍 2 新增設定鍵 `risk_high_paths`。最小解是「讓人自己開高風險審查迴圈」,但推送閘不會因此要求高風險審查(整合席 i1,另開 Issue);另一個最小解「提交訊息寫標記」被 r1 四席實測打穿。路徑清單是能讓推送閘機械判出 high 的最小入口,比對沿用實機驗收 shared_paths 的既有函式,不另寫。

## 處置表

| 編號 | 席 | 嚴重 | 去向 | 說明 |
|---|---|---|---|---|
| c1 | 正確性 | major | 折 | 改成路徑清單,不讀提交訊息,合併主線的提交不再相關 |
| c2 | 正確性 | major | 折 | 同上,空樹起點不再讀訊息 |
| c3 | 正確性 | major | 折 | 壞例檔加 Service 類別,整檔豁免的錯誤實作會讓壞例命中歸零;S1 改寫 |
| c4 | 正確性 | minor | 折 | 範圍 1 定為「任何一層外圍類別」,並寫明兩種巢狀的結果 |
| c5 | 正確性 | minor | 折 | 拿掉 ProcessLifecycleOwner 例外,列進不做 |
| c6 | 正確性 | minor | 折 | ruff 寫法不分大小寫,補 ruff: disable 等 |
| c7 | 正確性 | minor | 折 | 提交訊息正規式整個拿掉 |
| c8 | 正確性 | minor | 折 | RETIRE-IF 改成可用 git log 離線算;@Suppress 排除編譯器警告名 |
| c9 | 正確性 | minor | 折 | 回退改寫,d7 補「後來再翻案但理由沒被推翻」 |
| c10 | 正確性 | minor | 折 | 不再讀提交範圍,單一版本範圍不相關 |
| b1 | 邊界 | major | 折 | 同 c2 |
| b2 | 邊界 | major | 折 | 不再解碼提交訊息;設定讀不出改成往 high |
| b3 | 邊界 | major | 折 | 同 c7 |
| b4 | 邊界 | minor | 折 | 同 c10 |
| b5 | 邊界 | minor | 折 | 同 c1 |
| b6 | 邊界 | minor | 折 | 生效處列出合約測試硬擋、表態閘、掛鉤提醒改印理由 |
| b7 | 邊界 | major | 折 | 同 c6 |
| b8 | 邊界 | minor | 折 | 對照表補 use-site 前綴與 kotlin. 前綴 |
| b9 | 邊界 | minor | 折 | 改用命令切段取第一個詞,路徑裡的工具名不算 |
| b10 | 邊界 | minor | 折 | 實務隱患寫明對照表用正規式字串、不會被自己認到 |
| b11 | 邊界 | major | 折 | 同 c3 |
| b12 | 邊界 | minor | 折 | 同 c4 |
| b13 | 邊界 | minor | 折 | 只認建構子呼叫形式 Name(,可帶套件前綴 |
| b14 | 邊界 | minor | 折 | 同 c5;launch(Dispatchers.IO) 寫法補進 Service 樣本 |
| b15 | 邊界 | minor | 折 | 同 c9 |
| b16 | 邊界 | minor | 折 | 同 c8 |
| b17 | 邊界 | minor | 折 | 依據改指原始紀錄(被測 claude-haiku-4-5),d7 補註 |
| i1 | 整合 | major | 放行 | 既有缺口,自然判出的 high 一樣存在,不是這份計劃帶進來的;另開 Issues/高風險改動用輕量審查通過也能推送 追蹤 |
| i2 | 整合 | major | 折 | 同 b6 |
| i3 | 整合 | major | 折 | README 拿掉加註後回到 20 場,Opus 改寫成在天花板;S4 改對照原始紀錄 |
| i4 | 整合 | major | 放行 | 放行綁指紋是既有放行規則,工具本身的告警一樣;另開 Issues/放行綁指紋同檔複製貼上的同一行不再擋 追蹤。同一行被多條命令重複算那一半已折(同一行只算一次) |
| i5 | 整合 | major | 折 | 只在推送範圍模式數,工作樹模式列進不做 |
| i6 | 整合 | major | 折 | 同 c3 |
| i7 | 整合 | major | 折 | 新增範圍 5 列出要一起改的文件;lands_in 補 pitfalls-lint-adapter |
| i8 | 整合 | minor | 折 | 同 c7、c9 |
| i9 | 整合 | minor | 折 | 順序寫成殘留索引、高風險路徑、風險型樣,理由用分號串 |
| i10 | 整合 | minor | 折 | 對照表補 ruff 其他寫法、mypy、bandit、biome、ktlint;REVISIT 與菜單核對 |
| i11 | 整合 | minor | 折 | 同 c8 |
| i12 | 整合 | minor | 折 | 同 c8 |
| i13 | 整合 | minor | 折 | 天花板補拿不到分級的情況;壓提交那條隨提交訊息做法一起消失 |
| i14 | 整合 | minor | 折 | 同 c5 |
| i15 | 整合 | minor | 折 | 同 c9 |
| i16 | 整合 | minor | 折 | 範圍 3 寫明訊息與 source 欄;預期值表不再寫行號 |
| a1 | 架構對齊 | major | 折 | 同 b9 |
| a2 | 架構對齊 | minor | 折 | 讀不出改成往 high,跟殘留索引一致 |
| a3 | 架構對齊 | minor | 折 | 理由列最多 3 支檔、經 _plain_label 清洗 |
| a4 | 架構對齊 | minor | 折 | 同 i7 |

架構對齊席 ⚠A(為什麼不併進作弊比對那條):它不知道哪條命令跑了哪個工具,而忽略寫法只對有跑的那個工具有意義,所以掛在跑命令那一步;規則名改用帶命名空間的 lumos/inline-suppression。⚠B(外圍類別看哪一層):定為任何一層,照同包 kt-register-without-unregister 的既有寫法。

重現表:本輪沒有編排者重現不到、要列進 refuted 的發現。i1 由編排者讀 `_codeloop_pass_shape` 確認屬實(輕量帳回輕量放行)。
