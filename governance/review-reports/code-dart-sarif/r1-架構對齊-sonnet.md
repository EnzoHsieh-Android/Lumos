severity: major

## 問一:分層與依賴方向

`cmd_dart_sarif` 放的位置、被誰呼叫、呼叫誰,三件事都跟鄰居一樣。函式緊接在 `cmd_stylelint_sarif`(`scripts/lumos:20923`)後面、`_dart_rel`/`_DART_LEVEL` 這兩個新增的小工具再往下才是 `cmd_dart_sarif`(`scripts/lumos:20978`),跟 `cmd_sqlfluff_sarif`(`scripts/lumos:20889`)同一個區塊、同一種「格式轉換器」定位。argparse 註冊接在 `stylelint-sarif` 那段之後(`p = sub.add_parser("dart-sarif", ...)`)、`main()` 裡的分派 `if args.cmd == "dart-sarif": return cmd_dart_sarif(...)` 也跟著接在 `stylelint-sarif` 分派後面,`HELP_WHEN["dart-sarif"]` 一行插進 `sqlfluff-sarif`/`stylelint-sarif` 中間——四個註冊點的次序完全對齊鄰居,沒有跳過或搶插隊。呼叫方向也乾淨:`cmd_dart_sarif` 只讀 `sys.stdin`、只寫 `--out` 或印 stdout,不去呼叫 `_lint_run_and_parse` 或任何圖譜/vault 函式,跟兩支鄰居一樣停在「橋接層轉格式」這一端,不越層去碰下游的 lint-adapter 解析邏輯,也不被下游反過來呼叫。測試 `t_dart_sarif_bridge` 接在 `t_stylelint_sarif_bridge` 正下面,呼叫鏈(`lumos dart-sarif` → 讀 SARIF → `_lint_run_and_parse`)跟另外兩支測試同一個三段式。**唯一在分層上站不住的是新增的 `_dart_rel` 這個輔助函式本身在做什麼**,細節見 F1——它不是「跨層直呼」,而是把本來該由下游共用層做的事,搬到橋接層自己重做一次。

## 問二:命名與錯誤處理

命名完全比照鄰居:`cmd_dart_sarif` 跟 `cmd_sqlfluff_sarif`/`cmd_stylelint_sarif` 同一個 `cmd_<工具>_sarif` 樣式;argparse 的 `--out` dest 叫 `dart_out`,跟 `sqlfluff_out`/`stylelint_out` 同構;函式內部參數統一叫 `out`,三支逐字一樣。輸出方式(`out` 給了就寫檔、沒給就 `print(text)`)三支共用同一段程式碼形狀,沒有走樣。錯誤訊息開頭用「擋下:」,這是整支 `scripts/lumos` 幾十處 `print(..., file=sys.stderr)` 的既有起頭慣例(例如 `scripts/lumos:591`、`4328`、`5719` 等),`cmd_dart_sarif` 這裡用法(`f"擋下:{why}——不產出結果檔,免得一條沒跑的檢查被當成乾淨。"`)沒有創造新格式。rc2 用來表達「輸入讀不懂/壞輸入」也不是新語意——這支 CLI 本來就把 rc2 廣泛當「錯誤/壞輸入」用(argparse 缺必要引數是 rc2,`guard kill` 的 drifted/abort/error 也歸 rc2),`dart-sarif` 讀不懂輸入時回 rc2 落在既有的分類裡,不是替它單獨發明一條 rc 規則。真正跟鄰居不一樣的是「讀不懂就不寫結果檔」這個行為本身,這條留到問三判。

## 問三:第二種做法

**先判任務點名的第一題:rc2 不寫檔 vs 另兩支吐零條告警。** 這條差異是有意留下的,而且三個條件都在:①理由寫在 docstring 裡且是量出來的真實現象(dart 沒裝時 stdout 是空的、給不存在的檔印的是用法說明,這兩種輸入用舊寫法都會被解析成「跑完了、乾淨」,正好是 2026-09-13 新增告警閘要修的假綠洞);②有專門測試 `t_dart_sarif_bridge` 逐一釘住三種讀不懂輸入都是「rc≠0 且不寫結果檔」,還往下釘了 `_lint_run_and_parse` 拿到這種輸出時判「跑不動」而不是「乾淨」;③寫回了圖譜(`docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md` 新增一節、`linter精選目錄.md`、`reference.md`、`commands/07-安裝維運.md` 都同步),而且明講「那兩支的舊行為沒動,改它們要另外評估」——不是沒發現不一致,是講清楚為什麼現在刻意不動舊的兩支。三條都滿足,判**正當的刻意差異**,不需要現在回頭把三支統一。

**再判任務點名的第二題:`_dart_rel` 這種路徑正規化,專案裡是不是已經有同功能的工具函式。** 有,而且這次判定跟上一條不一樣。`_lint_run_and_parse`(`scripts/lumos:17499`)裡本來就有一段明講「共用 uri 正規化」的邏輯(`scripts/lumos:17590`–`17598`):剝 `file://`、unquote、絕對路徑就對呼叫端傳進來的 `repo_root` 取 `relpath`、反斜線轉斜線。`sqlfluff`/`stylelint` 兩支橋接完全不自己碰路徑——`cmd_sqlfluff_sarif`(`scripts/lumos:20889`)、`cmd_stylelint_sarif`(`scripts/lumos:20923`)把工具回報的 `filepath`/`source` 原樣塞進 `uri`,路徑數學整段下放給這個共用函式在解析階段一次做完(`t_sqlfluff_sarif_bridge`/`t_stylelint_sarif_bridge` 的樣本本身就用相對路徑,印證這兩支從不在橋接層自己算路徑)。`dart-sarif` 沒有走這條線:它在**產出**那端就自己用新寫的 `_dart_rel`(`scripts/lumos:20960`–`20975`)把絕對路徑轉成相對路徑,而且用的是第三套演算法——拿 `os.getcwd()` 的 `realpath` 分別去跟原始路徑、`os.path.realpath(path)` 兩個候選比對,挑不帶 `..` 的那個。專案裡其實已經有對付同一個「macOS `/var`→`/private/var`」symlink 問題的既有寫法:`rel_vault = os.path.relpath(str(Path(env.vault).resolve()), str(root.resolve()))`(`scripts/lumos:11505`,註解就寫著 `# macOS /var→/private/var`)——兩邊都先 `.resolve()` 再取 `relpath`。`_dart_rel` 沒有沿用這個既有慣用法,也沒有把「共用正規化要不要處理 symlink」這個需求回饋進 `_lint_run_and_parse`,而是在橋接層另外生出第三種路徑轉換邏輯。這正是「之後接手的人要在兩套之間猜」的情況——以後要接第四支橋接時,是照 sqlfluff/stylelint「路徑丟給下游共用層處理」,還是照 dart「自己先轉成相對路徑」?没有任何註解或筆記回答這個問題,也沒有测试证明兩条路径数学在同一份 SARIF 上会得到一致结果。這條判 major。

另外一處同類但沒被任務點名、順手看到的地方:`cmd_dart_sarif` 解析 stdin JSON 時比鄰居多一輪重試——整段解一次失敗就從第一個 `{` 開始再解一次(`scripts/lumos:20991`);`sqlfluff`/`stylelint` 兩支都是單純 `json.load(sys.stdin)` 失敗就當空清單處理,沒有這層。這個重試分支目前三個測試輸入(空字串、用法說明文字、`{"hello": 1}`)沒有一個會真的走到「重試後解析成功」那條路,測試沒覆蓋到它想解決的情境(stdout 混了非 JSON 前綴、JSON 本體在後面),程式裡也沒有註解說明是為了處理哪種真實遇過的輸出。這是多出來的一條沒被驗證過的輸入判斷邏輯,但只影響 `dart-sarif` 自己內部、不涉及共用邏輯被繞過或跨層,判 minor。

## F1 `_dart_rel` 另立一套路徑正規化,繞過既有共用 uri 正規化

severity: major
blocking: 是
引句:「★兩邊都要比真實路徑★:macOS 的暫存目錄是符號連結(/var → /private/var),」
file: `scripts/lumos:20962`

`_lint_run_and_parse` 已有「共用 uri 正規化」段落(`scripts/lumos:17590`–17598)專門把橋接層吐出的絕對路徑轉成相對路徑,`sqlfluff`/`stylelint` 兩支橋接都仰賴它、自己不碰路徑。`_dart_rel` 在橋接層自己重做一次同性質的轉換,用的是另一套「兩候選比對」演算法,也沒有沿用專案裡已經在用的「兩邊 `.resolve()` 再 `relpath`」寫法(`scripts/lumos:11505`)。第四支橋接接進來時,沒有任何文件講清楚該照哪一套。

## F2 stdin JSON 解析多一輪未測試的重試邏輯

severity: minor
blocking: 否
引句:「for text in (raw, raw[raw.find("{"):] if "{" in raw else ""):」
file: `scripts/lumos:20991`

`sqlfluff-sarif`/`stylelint-sarif` 讀不到合法 JSON 就直接當空清單處理;`dart-sarif` 多了「整段失敗就從第一個 `{` 開始重解一次」的分支,但三個既有測試案例都測不到這條路徑真正生效的情境,程式與筆記裡也沒交代它是為了應付哪種觀察到的實際輸出。範圍侷限在這支函式內部,不涉及跨層或共用邏輯被繞過。

不對齊共 2 條,其中 major 1 條。
