severity: major

## 問1:分層與依賴方向

新函式呼叫關係都在正確層內、沒有跨層直呼:`_profile_stack_mismatch`/S4 迴圈只被 `run_doctor` 呼叫,`_init_config_skeleton` 只被 `_scaffold_project` 呼叫,`_bound_tests_filter_probe` 只被 `_bound_tests_check` 呼叫,參數走既有慣例(收 `repo_root` 而非 `env`/`vault`,同 `_stack_key_for_file(file_rel, repo_root)`、`load_test_profile(repo_root)`)。兩個結構性問題如下(f3、f4)。

### f1 冒煙測試自動嵌進推送擋關,不是既有的「宣告驗證/顯式 --smoke」兩階段分工
severity: minor
blocking: 否
file: `scripts/lumos:21273`(`_bound_tests_check`)對照 `scripts/lumos:15713`(`cmd_lint_check` 的 `smoke` 參數)
引句:「做法借既有 lint-check --smoke 的形狀:拿一個故意不存在的測試名跑一次。」
既有 lint-check 把「真的跑一次命令」隔成使用者顯式加 `--smoke` 才觸發的獨立步驟,跟恆跑的靜態驗證(`_lintcheck_validate`)分開。新的探針被自動塞進會決定推送擋不擋的 `_bound_tests_check` 本體,每次有綠結果就跑(靠快取降頻,不是靠使用者選擇),沒有保留它自稱借用的那個「使用者顯式同意才真跑」設計。bound-tests 這支本來就沒有獨立驗證階段可掛,所以是「新開先例」而非「破壞既有分工」,故列 minor。

### f2 `_init_config_skeleton` 與新 `governance/.gitignore` 寫入被套在只為保護既有 vault 而設的雙層早退 guard 底下,既有專案永遠碰不到
severity: minor
blocking: 否
file: `scripts/lumos:13274`(呼叫點)對照 `scripts/lumos:13244`(`if kg.exists(): return`)與 `scripts/lumos:13938`(`if existing is not None and not force: … return 0`)
引句:「_init_config_skeleton(kg.parent.parent)」
這行只在 `_scaffold_project` 通過 `kg.exists()` 檢查後才會跑到,而 `cmd_init` 又在更外層對「已有 vault 且未帶 --force」直接 `return 0`——兩層 guard 的設計初衷都是「保護既有 vault 內容不被覆寫」,新功能借用同一把鎖等於被連坐。結果是所有本來就有 vault 的既有消費專案(這份 diff 要修的正是這批專案的接入靜默),不論跑 `lumos init` 或 `lumos init --force`,都不會拿到新的 `.lumos/config.json` 骨架或 `governance/.gitignore`。這不是「第二種做法」也不是跨層呼叫,是既有 guard 的保護範圍被無意擴大到不相干的新產出上,故列 minor。

## 問2:命名與錯誤處理

`no-vault` 跟既有 `no-pins`/`no-bound`/`diff-unavailable` 同一種小寫連字號慣例;`unfilterable` 跟既有 `green`/`red`/`whole-suite-deferred` 同一種慣例。`gov_events` 的 `{"gate":…, "kind":"warned", "hard": False, "nodes": […]}` 形狀跟 Check S/S2 一致(`scripts/lumos:1343`、`1395`);S3 用 `"nodes": []` 有既有前例(`scripts/lumos:1847` 的 check-cascade,同屬專案級而非節點級提醒)。冒煙測試自己壞掉走 `_gate_failopen(repo_root, "bound-tests", …)`(`scripts/lumos:21374`),跟 `code-loop`/`pitfalls` 既有呼叫點(`scripts/lumos:22047`、`22056`、`22100`)同一種「except 裡呼叫、訊息截斷到 100~120 字」寫法,鄰居一致。快取讀寫失敗處理見問3 f-cache(獨立列,因為是「第二種做法」而非單純風格)。剩一條文件層級的不一致:

### f3 `_bound_tests_check` docstring 的 status 列舉沒跟著新狀態更新
severity: minor
blocking: 否
file: `scripts/lumos:21276`(`status ∈ green / red / skipped / no-config / no-pins / no-bound / range-unavailable / whole-suite-deferred`)
引句:「"status": "unfilterable"」
本檔案有明確慣例是在 docstring 開頭用「status ∈ …」列出該函式所有合法狀態值(同檔另三處:`153`、`12672`、`15188`),`_bound_tests_check` 自己也照這慣例寫了一份,但這次新增的 `no-vault`、`unfilterable` 兩個狀態沒有回頭補進那份列舉。純文件漂移,不影響行為,但跟既有慣例不一致。

## 問3:第二種做法

### f4 `_STACK_GUESS` 是第三份副檔名對照表,而且已經跟正典的 `SYMBOL_PROFILES` 對不上
severity: major
blocking: 是
file: `scripts/lumos:13279`(`_STACK_GUESS`)對照 `scripts/lumos:3171`(`SYMBOL_PROFILES` 只有 csharp/kotlin/python/swift/typescript 五個鍵)
引句:「".vue": ("playwright", "vue", "Vue"),」
`_STACK_GUESS` 把「副檔名→(test_profile, symbol_profile, 人話)」另開一張表,而不是從既有 `TEST_PROFILES`(profile→exts)與 `SYMBOL_PROFILES`(profile→code_exts)反查——這正是題目點名要查的第三份重複來源,而且已經漂移出真的錯值:`.vue` 與 `.dart`(`scripts/lumos:13284`)兩個條目的 symbol_profile 分別寫死 `"vue"`、`"dart"`,但 `SYMBOL_PROFILES` 沒有這兩個鍵。`_init_config_skeleton` 把這兩個值原封寫進 `.lumos/config.json` 後,`load_symbol_profile`(既有邏輯)每次都會判「未知 symbol_profile」印警告、退回 csharp——猜中語言,設定卻是壞的,而且不會有人告訴使用者為什麼一直有警告。

### f5 新增的 `~/.cache/lumos/bound-filter/` 繞過了本檔唯一的私有目錄信任檢查 `_trusted_private_dir`
severity: major
blocking: 是
file: `scripts/lumos:21157`-`21188`(`_bound_tests_filter_probe`)對照 `scripts/lumos:20263`(`_trusted_private_dir`,docstring 自稱「★私有目錄信任檢查(單一來源)★」)
引句:「Path.home() / ".cache" / "lumos" / "bound-filter"」
`_trusted_private_dir` 的 docstring 明講這是「這套工具在家目錄底下寫的暫存/標記目錄都走這支」的單一來源,起因是 2026-09-06 全 repo 審視抓到 dispatch-lens 的兩個消費者(`scripts/lumos:19940`、`20326`)各自檢查、其中一支漏了 symlink 防護;現在 `~/.cache/lumos/` 底下唯二既有子目錄(`dispatch-lens`、`dispatch-lens/armed`)都已改走這支共用檢查。新的 `bound-filter` 子目錄完全不用它——讀取只裸呼叫 `cache.exists()`/`read_text`,寫入只裸呼叫 `mkdir(parents=True, exist_ok=True)` + `_write_lf`,沒有 symlink 防護、沒有 owner/group-writable 檢查,是文件明講「別再各自漂」之後又長出的第三支各自漂的寫法。這支快取內容直接決定合約測試閘報不報綠(`trustworthy` 欄位),繞過信任檢查的風險不是裝飾性的。

---
不對齊共 5 條,其中 major 2 條
