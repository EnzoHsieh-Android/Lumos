# r1 架構對齊審查——派工鏡頭注入 v1.2(固定席 0 篇備援段)

審查範圍:凍結審材 `派工鏡頭注入-v12-r1.md` 的「## v1.2」節(第 184-197 行)。只判這節設計跟本 repo 既有做法一不一樣,不找 bug、不評風格。

## 問題 1:分層與依賴方向

v1.2 明講「只改 `lumos dispatch-lens` 的輸出;hook 不動、閘不動」(第 187 行),這條邊界跟現有做法一致——`cmd_dispatch_lens` 本來就是靠 `redirect_stdout` 在製程內呼叫 `cmd_impact_diff` 拿 JSON 再解析(`scripts/lumos:16652-16654`:`buf = io.StringIO()` → `with contextlib.redirect_stdout(buf): rc = cmd_impact_diff(...)`),沒有另外開子行程呼叫自己的 CLI。v1.2 三格裡的「共改夥伴」明講沿用 `_cochange_mine`(第 189 行),而 `_cochange_mine` 本來就是回傳乾淨資料結構的純函式(`scripts/lumos:13455-13457`:回 `(rules, n_txn, n_files, err)`,`rules={(lhs,rhs):(conf,support)}`),不是印字串的 CLI 指令——直接呼叫這支 helper 跟現有「有 helper 就呼叫 helper」的分層一致,沒有問題。

但「受影響測試」這格只寫「`lumos testmap affected --diff <範圍> --repo <根> --json` 的測試名」(第 188 行),用的是 CLI 呼叫語法而不是像共改夥伴那樣點名內部 helper。查證後,testmap 這條路沒有 `_cochange_mine` 那種純資料 helper——`cmd_testmap_affected` 本身只把工作轉給 `_testmap_affected_inner`,而 `_testmap_affected_inner` 內部直接 `print(...)` 錯誤訊息並在多個 bail 分支各自組 JSON 印出,回傳值是 rc 不是資料(`scripts/lumos:14601-14618`)。也就是說,要在製程內拿到這格資料,唯一途徑是比照 `cmd_impact_diff` 那樣用 `redirect_stdout` 包住 `cmd_testmap_affected(as_json=True)` 再解析 JSON——這條路徑存在且已有先例,但 v1.2 文字沒寫死是走這條(製程內呼叫)還是真的另開一個 `lumos` 子行程執行 CLI 字串。同一份文件裡「消毒」段也只提「無任何 diff 文字」(第 192 行),沒有排除「另開子行程呼叫自己」這個可能性。這處判不準,標記見下方 f1。

## 問題 2:命名與錯誤處理

`bound_status` 是這支函式既有的機讀狀態欄位,值域走「ok / skipped-no-config」這種 `skipped-no-X` 命名慣例(`scripts/lumos:16689-16693`)。v1.2 新開的 `fallback: none|attached|skipped-no-testmap`(第 194 行)在**值域**上其實有沿用同一個 `skipped-no-X` 慣例(`skipped-no-testmap` 跟 `skipped-no-config` 是同一個構詞),這點是對齊的、不算問題。落差在**欄位命名**本身:同一個 `out` 字典裡已經有一個 `_status` 字尾的狀態欄位(`scripts/lumos:16731`:`"bound_status": bound_status`),`fallback` 沒有跟著這個字尾慣例命名成類似 `xxx_status` 的形式,是兩套命名風格並存在同一個 JSON schema 裡。另外查了全檔,`fallback` 這個詞目前只在註解/文件散文裡出現(例如 `scripts/lumos:26`「連結解析: 路徑優先,fallback basename」、`scripts/lumos:2178` 的行內註解),從未被當成 JSON 輸出的欄位名——`fallback` 在這個 codebase 是敘述性詞彙,不是既有欄位命名慣例的沿用。這是命名不一致,結構本身(在 `out` 字典裡加一個機讀狀態欄位)沒有問題,列 f2、severity minor。

錯誤處理面沒有發現落差:三格「皆缺資料就印固定字串」(testmap 未建印「testmap 未建,跳過」;第 188 行)跟既有 `_testmap_affected_inner` 的 fail-open 風格(缺 map 印訊息、`rc0` 照樣過,`scripts/lumos:14601-14618`)方向一致,都是不拋例外、印一句話續跑。

## 問題 3:第二種做法

「呼叫者」這格寫「在 base 樹的 code 檔裡反查誰提到(識別字比對,`grep -F -w` 等級,不做語法解析——三輪代碼審的教訓)」(第 190 行)。本 repo 對「掃全部 code 檔找內容比對」這類工作已有統一慣例:`build_code_haystack`(`scripts/lumos:2886-2898`)與 `discover_test_methods`(`scripts/lumos:2902` 起)都是 `os.walk` 走全 repo、用 `CODE_SKIP_DIRS` 濾目錄、`CODE_EXTS_T`(或 profile 的 exts)濾副檔名,再用 `Path.read_text` 讀檔內容、Python `re` 比對——全程製程內完成,不曾對外開 `grep`/`ripgrep` 之類子行程。連 `cmd_dispatch_lens` 自己所在的 `_lens_*` 家族,唯一的子行程包裝是 `_lens_git`(`scripts/lumos:16511-16519`),而且明確只包 `git` 指令,沒有「任意跑外部工具」這種通用子行程 helper。「頂層識別字」抽取(python `def`/`class` 名,不做語法解析)這件事本身也有現成先例可比——`PYTHON_TEST_RE`(`scripts/lumos:2473`)就是同一種「行首錨定 regex、不解語法」的抽取法,跟 v1.2 說的「不做語法解析」精神一致,這部分沒有問題。

問題出在「反查誰提到」這一步。文字明寫 `grep -F -w` 而不是「像 `build_code_haystack` 那樣 `os.walk` 建 haystack 再用 Python regex 找」,這是在既有「全 repo code 掃描一律製程內 `os.walk`+`re`」的慣例之外,另立一條「叫外部 `grep` 二進位」的路——同一類工作(掃 code 檔找字串命中)出現第二種做法,而且會把依賴從「純 Python + git 子行程」擴大到「假設環境裝了 GNU/BSD grep 且旗標語意一致」,跨出這個模組原本的邊界。列 f3、severity major、blocking。

三格全空時仍印「三格皆空」一行而非完全靜默(第 197 行)不算違例:本 repo 對「查完是空的」有兩種並存慣例——`cmd_cochange_check` 這種提醒式檢查在無警告時全靜默(沒有 else 分支印總結句),但 `cmd_contracts` 這種給人看的審計/列表式輸出在空的時候會明講「這篇沒有登記任何……」而不是沉默。v1.2 這段本來就是給審查員看的審計性列表(跟 `cmd_contracts` 同一類),選擇「皆空也講一句」貼著 `cmd_contracts` 那條先例走,沒有另立第三種慣例,不列為不對齊。三格各上限 8(第 187 行)也對齊——`cmd_dispatch_lens` 既有的 `cap=8` 參數預設本身就是同一個數字沿 `_print_sync_nudge` 預設值來的(文件第 90 行自陳),v1.2 三格沿用同一個 8,沒有另開新上限。

## 不對齊清單

### f1

分層與依賴方向:「受影響測試」格只寫成 CLI 呼叫字串「`lumos testmap affected --diff <範圍> --repo <根> --json`」,沒指明是製程內 `redirect_stdout` 包 `cmd_testmap_affected(as_json=True)`(比照 `cmd_impact_diff` 現有做法,`scripts/lumos:16652-16654`)還是另開子行程執行 `lumos` CLI 本身。testmap 這條路沒有像 `_cochange_mine` 那樣的純資料 helper 可直接呼叫,只能靠 JSON-stdout 這條既有路——文件沒排除第二種(子行程)讀法。

引句:「`lumos testmap affected --diff <範圍> --repo <根> --json` 的測試名」

severity: ⚠
blocking: 否

### f2

命名與錯誤處理:新欄位 `fallback` 跟同一個輸出字典裡既有的 `bound_status`(`scripts/lumos:16731`)命名風格不一致——`bound_status` 是 `<主體>_status` 字尾,`fallback` 沒有跟進;值域本身(`skipped-no-testmap` 沿用 `skipped-no-config` 的構詞)是對齊的,只有欄位名不對齊。

引句:「`fallback: none|attached|skipped-no-testmap`」

severity: minor
blocking: 否

### f3

第二種做法(跨層直呼):「呼叫者」反查明寫用 `grep -F -w` 等級比對,另立一條掃 code 檔的路,跟既有 `build_code_haystack`/`discover_test_methods` 的 `os.walk`+`CODE_EXTS_T`+`CODE_SKIP_DIRS`+製程內 `re` 比對慣例(`scripts/lumos:2886-2933`)不同形態,也超出 `_lens_*` 家族目前唯一的子行程包裝 `_lens_git`(`scripts/lumos:16511-16519`,只包 `git`)的邊界,新增一個外部二進位依賴。

引句:「識別字比對,`grep -F -w` 等級,不做語法解析」

severity: major
blocking: 是

## 小結

不對齊共 3 條,其中 major 1 條。
