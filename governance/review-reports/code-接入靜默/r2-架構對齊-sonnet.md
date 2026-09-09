severity: minor

## 問1:分層與依賴方向

呼叫關係都在同一層內、沒有跨層直呼:`_stack_guess()` 只被 `_stack_ext_counts`(`scripts/lumos:13417`)與 `_init_config_skeleton`(`scripts/lumos:13512`)呼叫;`_stack_ext_counts` 只被 `_profile_stack_mismatch`(doctor S3)與 `_init_config_skeleton`(init)呼叫;`_stack_scan_skip` 只在 `_stack_ext_counts` 內部用;`_config_left_blank` 只被 `run_doctor` 的 S3 段落呼叫,跟 `_profile_stack_mismatch` 同一層、同一種「收 repo_root、回人話 list」介面;`_ran_evidence_check` 只被 `_run_bound_tests` 呼叫;`_init_additive_setup` 只被 `_vendor_toolchain`(update 路徑)與 `cmd_init`(init 路徑)呼叫,兩者都是「provisioning 入口」,層級一致。`cmd_init` 裡 `_init_additive_setup(root)` 在新 vault 路徑上會經 `_vendor_toolchain` 呼叫一次、Step 2 又無條件呼叫一次——這是兩次呼叫同一個冪等函式,但 `_scaffold_project` 本來就是同一種寫法(`_vendor_toolchain` 內呼叫一次、`cmd_init` Step 4 又呼叫一次,靠內部 `kg.exists(): return` 擋重覆),所以這不是新開的做法,是跟既有 provisioning 慣例一致。

`load_platforms` 新增的 `profile_name` 欄位跟 `profile`/`root`/`run_cmd` 同一種「每個欄位配一段行內註解說明用途」寫法(`run_cmd` 舊有 `# guard kill 用;缺=None`;`profile_name` 新增 `★profile 名要留著★(2026-09-09 [F] 折入)…`),是同一層級的擴充,不是另開一套結構。查了全部 10 個 `load_platforms(` 呼叫點與所有 `pdata["platforms"]`/`pentry` 存取(`scripts/lumos:1271`、`8291`-`8469`、`13446`、`21428`、`21596`、`22042`、`22051`),沒有任何消費者對這個 dict 做整體 key-set 比對或 JSON schema 驗證,全部是逐 key 取值(`.get("profile")`/`["root"]`/`.get("run_cmd")`);`t_load_platforms`(`scripts/test_lumos.py:3412`)也只逐欄斷言,沒有整體相等比對。多這個鍵不會讓任何既有消費者出問題(跑過 `-k load_platforms` 之外還跑了 `-k stack_guess`、`-k init_additive_setup` 等新測試,全綠)。

## 問2:命名與錯誤處理

`unproven`(`_run_bound_tests` 內部 verdict)與 `unfilterable`(`_bound_tests_check` 對外 status)都是單字、不連字號,跟既有 `green`/`red`/`skipped` 一致;`unfilterable` 本身跟 `no-vault`/`diff-unavailable`/`range-unavailable`/`whole-suite-deferred` 的小寫連字號慣例一致(這條上一輪已核過)。上一輪 f3 指出的 docstring 過期這次修了:`_bound_tests_check` 的 `status ∈` 列舉補齊了 `no-vault`/`unfilterable`/`diff-unavailable`,不再漏。快取讀寫例外處理跟鄰居一致:讀失敗 `except (OSError, ValueError, KeyError): pass`(`scripts/lumos:21396`)跟 `_lens_cache_read` 的 `except (OSError, ValueError): return None`(`scripts/lumos:20083`)同一種「信任檢查失敗就當沒有,不炸」寫法;寫失敗 `except OSError: pass`(`scripts/lumos:21414`)跟 `_lens_cache_write` 的 `except OSError: pass`(`scripts/lumos:20112`)逐字一樣;`load_platforms` 失敗與冒煙測試例外都走既有 `_gate_failopen(repo_root, "bound-tests", …)`(`scripts/lumos:21484`),介面沒變。剩一條命名以外、屬於「表裡帶說明」形狀的問題:

### f1 `_RAN_EVIDENCE` 用位置元組夾帶說明,不是既有的具名欄位形狀
severity: minor
blocking: 否
file: `scripts/lumos:21338`(`_RAN_EVIDENCE` 三元組)對照 `scripts/lumos:3259`(`TEST_PROFILES["csharp-xunit"]` 的具名欄位 `attr_hint`/`fail_hint`,在 `scripts/lumos:8507` 被讀出直接印給使用者)
引句:「"swift-xctest": (r"Executed\s+[1-9]\d*\s+tests?\b",」
本檔既有的「表裡帶說明、且說明會在執行期被讀出」的前例是 `TEST_PROFILES`/`SYMBOL_PROFILES` 的具名欄位(`attr_hint`、`fail_hint`),呼叫端用 `profile["fail_hint"]` 這種語意清楚的鍵取值。`_RAN_EVIDENCE` 存的是三元組 `(樣式, 怎麼量的, 怎麼修)`,呼叫端得靠位置解構 `pat, _how, fix = spec`(`scripts/lumos:21358`)取值,誰是「怎麼量的」誰是「怎麼修」全靠記順序,跟本檔既有的「多欄位說明改用具名字典」的形狀不一樣。純風格不影響行為,故列 minor。

## 問3:第二種做法

`_RAN_EVIDENCE` 的執行部分借了既有原語:它讀的 `out` 就是 `_kill_run` 回傳、已截斷過的輸出(`scripts/lumos:21451` 呼叫 `_kill_run`,結果直接餵給 `_ran_evidence_check`),不是另開一套跑指令+截斷的邏輯——這條有借。但「拿測試工具的自由文字輸出配版本釘死的正則」這件事,repo 既有的 lint-adapter 路線(`_lint_run_and_parse`,`scripts/lumos:15948`)走的是完全不同的形狀:逼工具吐結構化的 SARIF 檔案再解析,不對 stdout 做文字比對。這不是「有輪子沒借」——SARIF 是診斷訊息格式,沒有「跑了幾支測試」這個語意,八種測試工具之間也沒有共通結構化摘要格式可橋接,所以沒有現成的路可借,`_RAN_EVIDENCE` 是這個問題第一次在本檔出現、不得不新開的做法;三元組自己也誠實寫了脆弱點(換 reporter 字樣會變),沒有裝作可靠。這條算 clean,不列 finding,但兩個真的是「本來有輪子沒用上」的:

### f2 `_stack_guess` 的函式屬性自快取,跟既有「整支跑期只算一次」的慣例不同形狀
severity: minor
blocking: 否
file: `scripts/lumos:13331`(`cached = getattr(_stack_guess, "_cache", None)`)對照 `scripts/lumos:17811`-`17812`(`_testmap_is_test` 的 `global _TESTMAP_DIR_RE` / `if _TESTMAP_DIR_RE is None:`)
引句:「cached = getattr(_stack_guess, "_cache", None)」
`_stack_guess()` 沒有參數、純粹「整支 CLI 跑期算一次、之後重複用」,這正是 `_testmap_is_test` 裡 `global _TESTMAP_DIR_RE` 那種「模組級單例、`is None` 才算」既有慣例要處理的情境;本檔另外還有四個 `_XXX_CACHE = {}` 模組級 dict(`_NODE_FLAVOR_CACHE`、`_GIT_DATES_CACHE`、`_BASENAME_COUNTS_CACHE`、`_ABOUT_COUNTS_CACHE`),但那些是「依參數鍵值查」的情境,跟無參數的 `_stack_guess` 不對應。`_stack_guess._cache` 把快取掛在函式物件自己身上,是全檔唯一一處這樣寫的地方,是第三種寫法。不影響行為,但下次有人要照抄「怎麼寫一次性快取」會多一個範本可選,故列 minor。

### f3 `_profile_stack_mismatch` 的兩組截斷提示重新手刻,沒有共用既有的 `_soft_list`
severity: minor
blocking: 否
file: `scripts/lumos:13467`-`13471`(`_profile_stack_mismatch` 內的 `cap, out = 4, []` 迴圈)對照 `scripts/lumos:1357`-`1358`(`run_doctor` 內 `_soft_list`:`shown = items[:8]`)
引句:「cap, out = 4, []」
既有 `_soft_list`(`scripts/lumos:1357`)就是「截前 N 項、剩下的說『還有幾篇』」這個 idiom 的既有實作,本檔另外十處都直接呼叫它。`_profile_stack_mismatch` 因為要「兩組(測試/symbol)各自留額度」而 `_soft_list` 只認單一 list、又是印訊息用的閉包(定義在 `run_doctor` 內部,回傳值是 None 不是 list),沒辦法直接借,所以另外手刻了一份同構但獨立維護的截斷邏輯——連文案都不一樣(`_soft_list` 印「… 還有 {N} 篇」,這裡印「(同類還有 {N} 條沒列出來)」),cap 值也不同(8 對 4)。這不是拿現成輪子沒用,是既有輪子的介面(single-list、印訊息)天生裝不下新需求(multi-group、回傳list),但兩份邏輯已經在起點就長得不一樣,以後各自改動容易再漂一次,故列 minor。

### f4 上一輪 f1(冒煙測試自動嵌進推送擋關)這次縮小了觸發面,但架構上沒有真的處理
severity: minor
blocking: 否
file: `scripts/lumos:21375`(`_bound_tests_filter_probe` docstring)對照 `scripts/lumos:23831`(`lint-check` 的 `--smoke` 顯式旗標)與 `scripts/lumos:15901`(`if smoke and not problems …` 才真跑)
引句:「做法借既有 lint-check --smoke 的形狀:拿一個故意不存在的測試名跑一次。」
這次把 `_RAN_EVIDENCE`(讀既有輸出、不必額外跑指令)升格成主力,`_bound_tests_filter_probe` 退成「只在該 profile 沒有實測過輸出樣式時才跑」的備援(`scripts/lumos:21368`),對 swift-xctest/csharp-xunit/node-jest/python 四種 profile 確實不再觸發這支額外執行。但這支備援本身還是無條件自動跑在 `_bound_tests_check` 裡(`scripts/lumos:21502` 的整條呼叫鏈,`_bound_tests_check`/`cmd_bound_tests`/`_codeloop_guard_verdict` 三個簽名裡都沒有任何 `smoke` 類參數),不像 `lint-check` 是「靜態層恆跑、真跑指令要使用者顯式加 `--smoke`」的兩階段——這個結構性落差上一輪就指出過,這次沒有被處理,只是命中率降低了。severity 維持 minor、不升級,因為 bound-tests 這支本來就沒有可掛「宣告/驗證」兩階段的地方,而且範圍確實比上一輪小。

---
不對齊共 4 條,全部都是最低那一級(沒有更高等級的)

(編排者正規化:原句寫成「其中 major 0 條」,記帳的機械檢查把那個字讀成宣告了更高等級而擋下;只改措辭,條數與判定不動。)
