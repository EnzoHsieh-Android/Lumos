severity: major

審查範圍:整份 diff 逐 hunk 讀過,並在真 repo 實跑。ast-grep 用 `/Users/enzo/lumos-scratch/android-checks/venv/bin/ast-grep`(釘版 0.51.1,pip 上也查得到)。圖譜鏡頭見最後一節;角色卡沒附,略過。

### Finding 1
severity: major
blocking: 是

`t_kotlin_rulepack_samples` 在有 ast-grep 的機器(含 CI,CI 這次新裝了 ast-grep)一定噴 EXCEPTION。測試把 `'**/src/test/**'` 改成 `'**/test/**'` 想造一個「路徑過濾沒錨在 src/」的壞版本。真規則檔裡的寫法其實是 `'**/src/test*/**'`,`_ktpack_edit` 的 `assert old in t` 先炸掉。「祖先目錄叫 test 的正式碼不准命中」這道守衛因此沒有任何綠燈的測試保護。

重現:
```
PATH=/Users/enzo/lumos-scratch/android-checks/venv/bin:$PATH python3.14 scripts/test_lumos.py -k kotlin_rulepack
```
輸出:
```
✗ t_kotlin_rulepack_samples EXCEPTION: .../rules/coroutines.yml 找不到要改的字:'**/src/test/**'
17 passed, 1 failed
```
file: `scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples`(diff 內 `_ktpack_edit(f, "'**/src/test/**'", "'**/test/**'")` 那行)。真規則:`configs/ast-grep/kotlin-android/rules/coroutines.yml:362` 與 `rules/testing.yml:204` 等,寫的是 `src/test*/**`。

引句:「_ktpack_edit(f, "'**/src/test/**'", "'**/test/**'")」

即使把字串改對,`t_rules[0]` 取到的是第一條只掃測試碼的規則。之後 `if t_rules:` 才跑的斷言「祖先目錄叫 test」,能不能翻紅要在修正後再驗一次。

### Finding 2
severity: major
blocking: 是

`catalog_ids()` 號稱只收「型錄主表」編號,實際收的是 `〈待查證〉` 之前整段文字。這段包含情境決策表的 `| D-1 |` 列,以及來源索引表的 `| KX-1814 |` 這類列。結果規則訊息寫 `[D-1]` 或 `[KX-1814]` 會通過 S2「訊息要引用型錄裡真的有的編號」。實跑已證實:`'D-1' in ids` 為 True,`message_problems([{"id":"kt-z",...,"message":"[D-1] x;改用 y"}], ids)` 回傳 `[]`。

測試用的假編號是 `NOPE-9`,這種格式的壞引用才抓得到。D-n 與來源索引編號這條路測試抓不住:把 `catalog_ids` 的範圍放寬,所有測試照綠。

file: `configs/ast-grep/kotlin-android/check.py:109-114`(`catalog_ids`),對照同檔 `_MAIN_ROW_RE`(只認 API/FLOW/STATE/CO/UI/ARCH/DATA/TEST/PERF)。

引句:「return set(re.findall(r"^\|\s*([A-Z]+-\d+)\s*\|", main, re.M)), text」

建議 `catalog_ids` 改用 `_MAIN_ROW_RE`,並只切主表那一段(`\n## 情境決策表` 之前)。測試補一個 `[D-1]` 的壞例。

### Finding 3
severity: minor
blocking: 否

樣本歸屬用 `parts.index(kind)`,取路徑裡第一個叫 `good` 或 `bad` 的目錄。ast-grep 收到絕對路徑就回絕對路徑。repo 若放在祖先目錄叫 `good` 的位置,好例的命中全被歸到錯的 owner(例如 `configs`)。好例誤報變成漏報,檢查假綠。

重現:把規則包與型錄複製到 `/tmp/.../good/configs/ast-grep/...`,在 `samples/good/kt-test-thread-sleep` 的 kt 檔尾加 `fun extraSleepy() { Thread.sleep(5) }`,跑 `check.py`。輸出「規則 208 條,問題 0 個」(應報好例誤報)。祖先叫 `bad` 的情形則是壞例全判不足而假紅。

file: `configs/ast-grep/kotlin-android/check.py:289-291`

引句:「owner = parts[parts.index(kind) + 1] if kind in parts and parts.index(kind) + 1 < len(parts) else ""」

建議改成相對 `HERE / "samples"` 取第一段。

### Finding 4
severity: minor
blocking: 否

祖先目錄檢查那段 `scan(sg, cfg, TEST_ONLY_ANCESTOR) or []`:ast-grep 跑失敗(`scan` 回 `None`)時被吞成空清單,這道檢查無聲通過。其他兩處呼叫失敗都會記問題,只有這裡不會。例如 hints 設定載入錯誤導致 rc 2,「祖先目錄命中」就永遠查不到。

file: `configs/ast-grep/kotlin-android/check.py:315`

引句:「for (i, f) in scan(sg, cfg, TEST_ONLY_ANCESTOR) or []:」

建議 `None` 時同樣加一條 `<pack> 掃 ancestor 樣本跑不起來`。

### Finding 5
severity: minor
blocking: 否

型錄來源欄的「有來源縮寫」判斷太鬆:`\b[A-Z][A-Z0-9-]{1,}\b` 任何兩個大寫字母(`TODO`、`TBD`、`OK`、`AI`)都算。來源寫「待補 TBD」會過 S3 的「來源沒有網址或來源縮寫」。這道檢查要擋的是出處沒查證,卻放行了這類佔位詞。

file: `configs/ast-grep/kotlin-android/check.py:172`

引句:「if not re.search(r"https?://|\b[A-Z][A-Z0-9-]{1,}\b", src):」

### 看過、判無問題
- `include_test_paths` 設定解析:`[]`、`[""]`、`".kt"`、`"KT"` 的正規化都對。非清單值有警告,預設是不可變的 `frozenset`,不會被共用污染。`cfg` 沒被 `json.dumps`,所以 frozenset 沒有序列化問題。
- 新鍵不會破壞舊設定檔(沒設就是空集合)。舊程式讀到新鍵,屬於它不認得的鍵。
- 閘的行為驗證有效:`-k lint_new_include` 26 passed,`-k astgrep_kotlin` 4 passed,`-k lint_block_message` 2 passed,`-k kotlin_catalog` 7 passed。
- `_RULEPACK_SAMPLE_RE` 用 `.match` 錨在 repo 相對路徑開頭,測試也有一般 kt 檔與 `app/samples/` 的對照組。擋下訊息 120 字與 `scripts/lumos:39234`、`39246` 的 SARIF 截斷一致,測試用 71 到 120 字之間的訊息,回到 70 會翻紅。
- CI 裝 `ast-grep-cli==0.51.1`:套件版本存在。另一個 docs-only 子集的 CI 工作不跑這些測試,不需要它。
- `test_only` 判定的正則用了 DOTALL,規則檔若在別處(註解或訊息)提到 `src/test`,理論上會誤判成只掃測試碼。目前 17 條實際判定合理,沒有具體失敗輸入,所以不單列。

### 圖譜鏡頭
我跑的是 `check.py` 與測試,沒有跑 `lumos impact --diff`。`scripts/lumos` 的改動點是:
- `_stack_changed_ok` 新增預設為空的 `keep_test_ext`。
- 新增 `_RULEPACK_SAMPLE_RE`。
- `_cl_say_lint_block` 的截斷從 70 字改為 120 字。
- `_lint_new_config` 新增 `include_test_paths` 鍵。

其他三個呼叫端(`scripts/lumos:61831`、`61840`、`61847`、`65924`)沒傳新參數,行為不變,只多排除規則包樣本路徑。沒有發現行為或合約遭破壞,但沒有逐篇對過節點宣稱的行為。`.lumos/config.json` 新增的 `node_home.ignore` 是既有鍵(`scripts/lumos:44327`),語意相容。

### 清理
我跑 `-k kotlin_rulepack` 時留下測試紅時保留的現場 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/gctl-run-8ck5jv42`。我已用字面絕對路徑刪除,另外刪掉自己在 `/tmp/lumos-seat-work/code-kotlin規則包/正確性-sonnet/good` 建的暫存。

總結:2 條 major 要修,測試因子字串寫錯而紅,以及 `catalog_ids` 範圍錯誤讓 S2 守衛漏放;3 條 minor,都是自檢程式的路徑歸屬和判斷過鬆。新增告警閘本身(`include_test_paths`、120 字、樣本排除)行為正確、測試有效。
