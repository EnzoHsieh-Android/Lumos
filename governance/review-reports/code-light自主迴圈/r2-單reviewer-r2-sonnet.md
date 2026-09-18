severity: clean

## 驗過的路徑

①掛鉤多 ref 推送:`_AUTOLOOP_FULL` 的賦值(`scripts/hooks/pre-push:255`)只在
`if [[ "$_suite_this" == "full" ]] && grep -q '改動風險分級:light' ... && light_ok...`
這個區塊裡(`scripts/hooks/pre-push:251`),而 docs 那個 ref 在更早的地方(`scripts/hooks/pre-push:226`:
`printf '%s' "$pf_json" | grep -q '"suite": *"docs"' && _suite_this="docs"`)已經把 `_suite_this`
改成 `"docs"`,所以 251 行的 `"$_suite_this" == "full"` 對 docs ref 恆假,255 行的區塊不會跑,
docs ref 的 `pf_json`(其 `autoloop_full` 因 affected_keys 空而必為 true)根本不會被讀進
`_AUTOLOOP_FULL`。實際追過整個 for 迴圈(`scripts/hooks/pre-push:170-321`),`_AUTOLOOP_FULL` 只可能被
某個被判成 light 的 ref 設成 1,不會被 docs ref 誤觸發。多 ref 混合(一個 docs、一個 light)也手動推演過:
docs ref 那輪不進區塊、light ref 那輪照它自己的 pitfalls json 判,兩者互不干擾,結論保守正確——沒有發現。

②`_autoloop_full_for`(`scripts/lumos` 新增函式)讀的是 `Path(repo_root)/scripts/test_autonomous_loop.py`
(工作目錄磁碟上的內容),不是 `git show <_lsha>:scripts/test_autonomous_loop.py`。但確認過整支掛鉤本來就是這樣設計:
真正被執行的 `"$PY" "$REPO_ROOT/scripts/test_autonomous_loop.py"`(`scripts/hooks/pre-push:362`)本身也是讀磁碟、
不是先 checkout 到 `_lsha` 再跑——`_range`(sha-based)只用來讓 `pitfalls`/`impact`/`code-loop check` 精準算受影響範圍,
但「要不要整支跑」這個判斷的目的正是「磁碟上這支即將被執行的檔案,有沒有提到這些關鍵字」,跟磁碟版一致才是它該比對的對象。
這跟既有的 `_is_code_file`(`scripts/lumos:5636`,同樣磁碟優先、找不到才 fallback 到 git show base)是同一套既有慣例,
不是這次改動新引入的落差——沒有發現。

③`_keys_suite_select`(`scripts/test_lumos.py:71`)改成 `_mentioned = _load_lumos_inproc()._keys_mentioned` 在
`for k in keys` 迴圈外先拿一次(只載入模組一次,不是每個 key 都重載),迴圈內 `_mentioned(src, [k])` 用的正規表達式
跟原本行內 `_re.compile(r"(?<![A-Za-z0-9_])" + _re.escape(k) + r"(?![A-Za-z0-9_])")` 逐字相同,只是搬到 `scripts/lumos`
共用一份定義,`cap=0.3` 那段「太泛就丟掉」的邏輯完全沒動——實際跑了 `t_test_suite_docs_only_judgement`(內含
⑩a/⑩b/⑩c 三條新案例)全線 25 passed;沒有發現行為差異。

④`_pitfall_diff_collect` 的兩個回傳路徑(`scripts/lumos` 裡 `if config is None:` 早退與函式結尾的完整路徑)
都各自算了 `_ak = _affected_test_keys(...)` 並塞進 `"autoloop_full": _autoloop_full_for(repo_root, _ak)`——
兩處都有,沒有漏掉哪一條路徑。

⑤`--list` 路徑會不會每支測試都重載一次 lumos 模組:`_load_lumos_inproc()`(`scripts/test_lumos.py:225`)
是模組級單例快取(`_LUMOS_INPROC` 全域變數,`if _LUMOS_INPROC is None:` 才真的 `exec_module`),而
`_keys_suite_select` 只在迴圈外呼叫一次、賦值給 `_mentioned`,不是每支測試各呼叫一次——只有第一次真的付
載入整支 `scripts/lumos` 的成本,之後(含同一次 `--suite keys --list` 呼叫裡的每支測試)都是拿快取。

另外實跑驗證(在 `git worktree add --detach /tmp/seat-單reviewer-r2-sonnet HEAD` 的隔離工作目錄,跑完已
`worktree remove --force`,沒動過正式 repo):
- `python3 scripts/test_lumos.py -k t_prepush_docs_and_light_run_subset` → 17 passed, 0 failed
- `python3 scripts/test_lumos.py -k t_prepush_and_ci_wired_for_docs_suite` → 10 passed, 0 failed
- `python3 scripts/test_lumos.py -k t_test_suite_docs_only_judgement` → 25 passed, 0 failed
- 手動在該隔離目錄跑 `lumos pitfalls --diff HEAD~1..HEAD --no-lint --json` 確認 JSON 序列化真的印成
  `"autoloop_full": true`(有空格),掛鉤的 `grep -q '"autoloop_full": *true'`(`scripts/hooks/pre-push:255`)
  抓得到,不是憑讀碼猜格式。

另外查了兩個延伸點(非派工詞指名,但屬同一批改動的鄰接風險):
- CI(`.github/workflows/ci.yml`)確認過**沒有**跟進 light/keys/autoloop_full 那套縮減,`suite` 一律被
  `[ "$suite" = docs ] || suite=full` 收斂成 docs 或 full 兩種——light 的縮減只在本機掛鉤生效,CI 對非文件
  改動照樣整支跑,符合掛鉤註解裡「CI 那邊照樣跑全套當後盾」的設計意圖,不是遺漏。
- 兩組子集真平行(`scripts/hooks/pre-push:461-467`:`( run_group s ... ) & _gpid=$!` 與
  `( run_group k ... ) & _kpid=$!`,分別 `wait`)手動推演過:`run_group` 用的暫存檔名帶 `_pfx`(s/k)區分,
  不會互相覆寫;`_grc`/`_krc` 各自從對應 pid 的 `wait` 取值,沒有被吞掉的路徑;兩個 `wait` 都在同一個(非子殼)
  主 shell 依序執行,不是各自子殼裡讀寫共用變數,沒有競態。

沒有找到派工詞五個重點裡任何一個構成 bug,也沒有另外找到獨立的新問題。
