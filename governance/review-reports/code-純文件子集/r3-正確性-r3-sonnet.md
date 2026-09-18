severity: clean

沒發現(blocker/major/minor 都沒有)。逐一驗過鏡頭指定的六個懷疑點,結論都是「行為是對的、有守住」;細節如下。

## 驗過的路徑

1. **執行器 `--suite` 空片 rc0 會不會讓「全部片都空」也 rc0、逃過 rc3**:
   讀 `scripts/test_lumos.py` 的 `main()`(約 29391 行起)確認子集挑選(`_docs_suite_select`/`_keys_suite_select`)發生在 `--shard` 切片**之前**、且用同一份 `globals()` 排序清單、同一個 `$_shards`。因為切片是 `k % _n == _i - 1` 的模數分派,只要整體子集非空(已經過前面「`if _args.suite and not tests: return 3`」那關),必有某個 `_i` 分到至少一支——數學上不可能出現「子集非空但每片都空」。反過來,「整體子集為空」時,四片各自獨立算出同一份空子集,各自都在切片前就回 rc3,不會有片先分到東西。用 `git -C /tmp` 之外沒必要另起 worktree,直接讀原始碼 + 跑 `python3 scripts/test_lumos.py -k suite` 44 案例全綠(含 `t_runner_suite_flags` 的「子集配分片、這片沒分到 → rc0」與「keys 0 支:rc3」兩支)驗證了這條路。
   另外确认 pre-push 的 `run_group`(`scripts/hooks/pre-push:412-427`)聚合邏輯:`_any3=1` 只在「有子行程回 3 且沒有子行程回非 0/3」時才讓整體回 3;主要那組(docs/全套)是「非 0 就算紅」(`_grc -ne 0` → `_rc=1`,含 3 的情況——這是刻意的:文件子集/全套本來就不該選中 0 支),keys 那組才特別放行 rc3。兩組分開處理,語意一致,沒有互相污染。

2. **`[[ $_shards =~ ^[0-9]+$ ]]` 對 `"04"`、`"0"`、`" 4"`**:
   實跑驗證(bash 直接測):
   - `"0"` → regex 過但 `-ge 1` 為假(bash 算術把 `"0"` 當 0)→ 退回 `_shards=1`,安全。
   - `" 4"`(前導空白)→ regex 不過(`^` 錨定開頭)→ 退回 `_shards=1`,安全。
   - `"04"` → regex 過、`-ge 1` 為真(bash 算術把 `"04"` 當八進位 4)→ `_shards` 維持字串 `"04"`;後續 `seq 1 "$_shards"` 與組出的 `--shard "$_i/$_shards"`(例如 `1/04`)交給 Python 的 `int("04")` 解析一樣是 4,`python3 scripts/test_lumos.py --shard 1/04 --list` 實測 rc=0、正常跑。行為上沒有錯,只是字串沒被正規化成 `4`,不影響正確性,不構成 bug。

3. **mktemp 防呆放在 `impact_done` 的 trap 之前,exit 1 時 trap 還沒掛,前面 `impact_once` 建的檔會不會漏清**:
   讀了 `scripts/hooks/pre-push` 全檔用 `grep -n "impact_once\|impact_done\|^trap\|_PP_TMP="`:`impact_once` 的唯一呼叫點在第 220 行,晚於 mktemp 防呆與 `trap ... EXIT INT TERM`(第 64-69 行)。也就是說 mktemp 失敗要 `exit 1` 的那個時間點,`impact_once` 根本還沒被叫過,不存在「trap 還沒掛但已經有暫存檔」的窗口。這條懷疑不成立。

4. **`_range_base` 進 `_sc_churn` 後 `git show base:old` 對 merge-base 的行為**:
   讀 `_sc_changed_files`(`scripts/lumos:5660`)用的是 `git diff --numstat -z <git_range>`(不带 `--no-renames`,允许改名侦测),`_sc_churn`/`_small_change_check` 用同一個 `git_range` 字串。三點範圍 `a...b` 的 `git diff a...b --numstat` 本來就是相對 `merge-base(a,b)` 算的,所以 numstat 吐出來的「舊路徑」就是檔案在 merge-base 那個提交下的名字;`_range_base` 對三點範圍回傳的也正是同一個 merge-base——兩邊用的是同一個起點,`git show base:old` 讀到的內容跟 numstat 認定的舊路徑一致。兩點範圍 `a..b` 等價於 `git diff a b`,`_range_base` 回傳 `a`,同樣一致。測項 ⑪/⑪b(`t_test_suite_docs_only_judgement`)已經用「merge-base 時是 `#!` 腳本、左端點之後被改成純文字」的情境驗過這個差異,`python3 scripts/test_lumos.py -k suite` 全綠。

5. **`_KEY_OK_RE` 新正則對 `_x`、`a.b`、`.hidden`**:
   `re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{2,}")`(`.fullmatch`):
   - `_x`(2 字元)→ 第一類吃 1 個、`{2,}` 至少要再 2 個 → 總長最少 3,`_x` 長度 2 不夠 → 不匹配,被丟掉,跟文件字面「≥3 字」的宣稱一致。
   - `a.b`(3 字元)→ 第一類吃 `a`,`{2,}` 吃 `.b`(`.` 和 `b` 都在 `[A-Za-z0-9_.-]` 裡)→ 匹配,會被收進關鍵字清單。這是預期行為(允許帶點的檔名/模組名當關鍵字),不是漏洞。
   - `.hidden` → 開頭是 `.`,不在第一類 `[A-Za-z0-9_]` 裡 → 不匹配,被丟掉。順帶擋掉隱藏檔名這種邊界情況,沒有造成問題(若真的是隱藏檔改動,`_affected_test_keys` 抽檔名時 `b.rsplit(".",1)[0]` 也會得到空字串被 `_add` 的 `if k` 擋掉)。
   `python3 scripts/test_lumos.py -k suite` 內的 ⑤c(檔名含逗號/空白/`-` 開頭不當關鍵字)全綠。

6. **`run_group` 改名有沒有漏改呼叫點**:
   `grep -n "run_group\|_grc\|_krc\b" scripts/hooks/pre-push` 只有 1 個定義(第 412 行)、2 個呼叫點(439、442 行),都已改成新名字;另外 `grep -rn "_run_group" scripts/` 全 repo 掃描零命中,沒有殘留舊名字。

## 額外核對

- `python3 scripts/test_lumos.py -k suite` 44 案例全綠(含這批新增/折入的所有測試)。
- r1/r2 折入的四項(mktemp 擋、shards 正整數守衛、`_run_group`→`run_group` 改名、`_range_base` 收斂、`_KEY_OK_RE` 不准 `-` 開頭、子集配分片 rc0)在 `r3-delta.patch` 裡逐一核對過改動內容與對應測試,沒看到折得不對或折出新洞的地方。
- 沒發現「該跑全套卻跑了子集」或「合法推送被誤擋」的新路。
