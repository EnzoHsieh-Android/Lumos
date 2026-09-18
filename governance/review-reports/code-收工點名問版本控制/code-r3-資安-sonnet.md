severity: blocker

## Finding 1:清單外的第三項——`diff.<任意驅動器名>.command`/`.textconv`,經 `.gitattributes` 掛載,完整繞過 `_GIT_UNSAFE_CONFIG` 清單,端到端重現成功

severity: blocker
blocking: 是

`_harden_git_env()` 只神隱化了兩個**固定名字**的設定鍵(`core.fsmonitor`、`diff.external`)。但版本控制的 diff 驅動器機制允許被打開的資料夾用一份 `.gitattributes`(★不需要被提交,工作樹上未追蹤的檔就生效★)把任一路徑指到一個**攻擊者自己命名**的驅動器,再用 `diff.<那個名字>.command`(或 `.textconv`)設定該驅動器要跑的指令——這個設定鍵的名字本身就是攻擊者選的,不是固定字串,原理上不可能被一份具名清單窮舉。主程式 `scripts/lumos` 裡「逐檔比對差異」那個呼叫(閘門 3 會呼叫到,就是 r2 資安複審抓到 `diff.external` 觸發的同一個呼叫點)完全沒有帶 `--no-ext-diff`/`--no-textconv`,而它依賴的防護只有繼承來的 `GIT_CONFIG_PARAMETERS` 環境變數,那個變數裡沒有這個攻擊者自訂的鍵名可以中和。

引句:「這是★列舉法★,不是完備防護。清單上的擋得住,清單外的擋不住。」

引句:「★子行程一律繼承★,所以主程式內部的呼叫也涵蓋得到(實測驗過)。」

file: `scripts/lumos:25261-25262`(被主程式 `cmd_impact_diff` 用來逐檔取 hunk 文字的呼叫:`["git", "-C", str(repo_root), "-c", "core.quotePath=false", "diff", diff_range, "--", f]`,未帶 `--no-ext-diff`/`--no-textconv`,不在本次改動範圍內,但這支 hook 引入的環境變數防護聲稱涵蓋到它)

**最小重現(端到端跑完整支 hook,不是只跑查詢函式)**:

```
# 1. 造惡意倉庫:一個提交、docs/x-knowledge、scripts/code.py
git init -q repo && cd repo && git add -A && git commit -qm base

# 2. 攻擊者資料夾裡放一份未追蹤的 .gitattributes
echo "scripts/code.py diff=pwn" > .gitattributes

# 3. 攻擊者設定一個自訂命名的 diff 驅動器(名字任意,不在任何清單裡)
git config diff.pwn.command 'sh -c "touch /tmp/PWNED2" #'

# 4. 造出「工作樹有未提交的程式碼檔 + 未提交的圖譜筆記」這個會走到閘門3、
#    再去呼叫主程式 impact 的現場(改 scripts/code.py、改 docs/x-knowledge/Systems/s.md)

# 5. 端到端跑收工 hook(HOME 換乾淨目錄、LUMOS_STOP_BLOCK_OFF=1 只是為了不擋停,
#    _harden_git_env() 仍照常在 main() 第一行跑)
python3 check-graph-sync.py --budget 40 < payload.json
```

實測輸出:

```
rc= 0
PROOF exists(舊清單項核對用): False
```
```
$ ls -la /tmp/sec-textconv-work/PWNED2
-rw-r--r--@ 1 enzo  wheel  0 Sep 18 13:17 /tmp/sec-textconv-work/PWNED2
```

`/tmp/PWNED2` 被建出來,代表攻擊者指定的指令在完整跑過收工 hook(含 `_harden_git_env()`)之後仍然執行了。對照組:把 `.gitattributes` 換回綁 `diff.pwn.textconv`(不掛 `.command`)在直接呼叫 `git diff` 時也一樣觸發,只是 `diff.external=` 的空字串在**沒有 `.command`、只有 `.textconv`** 時剛好會讓 git 整條路徑失敗(rc128「external diff died」)而不是執行——★這只是巧合的副作用,不是設計出來的防護★:一旦攻擊者改用 `diff.<name>.command`(第 3 步驗過的版本),防護完全失效,rc=0、無錯誤訊息、指令照跑。

## 第 2 點:清單上的每一項實際試過的結果

- `core.fsmonitor`(r1 資安席原始發現,查工作樹狀態觸發):**擋得住**。用 `test_lumos.py -k sync_nudge` 跑 `t_sync_nudge_git_call_disables_fsmonitor`(直接測查詢函式)與 `t_sync_nudge_hardens_git_for_all_subprocesses`(端到端跑整支 hook、現場逼它走到會呼叫主程式那條分支)兩支測試,兩支都通過(`PWNED` 之類的證據檔沒被建出來)。另外我自己在 `/tmp/sec-de-work` 造了一個獨立現場(不重用測試碼),`git config diff.external "…touch PWNED_DE…"`,端到端跑完整支 hook,`PROOF exists: False`——確認擋得住。
- `diff.external`(r2 資安複審發現,主程式逐檔比對差異觸發):**擋得住**。同上,`t_sync_nudge_blocks_every_listed_unsafe_git_config` 逐項跑過這一項(見第 4 點驗證),端到端不執行。我自己額外用直接設定 `diff.external` 為惡意指令(不透過任何驅動器、最單純的攻法)造了獨立現場,端到端跑完整支 hook,`PROOF exists: False`,同樣確認擋得住。
- 兩項都親自端到端跑過,不是只驗第一項。

## 第 3、4 點:機制與測試本身——已驗證,未發現額外洞(非獨立 finding)

環境變數同名鍵覆蓋語意(後值優先)、清單驅動的逐項端到端測試、子行程繼承路徑三項都自行重現過,沒有另外的洞。

引句:「同名鍵已存在時採後值優先,所以附加在尾端是安全的(r2 資安複審實測驗過)。」

- 「後值優先」:自己造了一個場景,先在環境裡預埋一個惡意的 `core.fsmonitor` 值,再模擬 `_harden_git_env()` 把中和值接在尾端,跑 `git status --porcelain -uall`,`PWNED_LASTWINS` 沒被建出來——後值優先屬實。
- 「逐項端到端跑,不是寫死」:讀了 `t_sync_nudge_blocks_every_listed_unsafe_git_config`(`scripts/test_lumos.py`,對應本次 patch 新增段落)——它真的是 `for key in list(getattr(m, "_GIT_UNSAFE_CONFIG", ())):` 逐項迭代,不是寫死兩支獨立測試函式;清單加一項這支測試會自動多驗一項。這部分機制是真的。
- 「子行程自己清掉環境變數 / 繞過進入點直接呼叫內部函式」:查了 `check-graph-sync.py` 與 `scripts/lumos` 裡所有呼叫 git 的 `subprocess.run`/`_sp.run`,在 impact/status 這條路上沒有任何一處帶 `env=` 覆蓋(會丟掉繼承來的 `GIT_CONFIG_PARAMETERS`);`_harden_git_env()` 是 `main()` 的第一行,這支 hook 沒有繞過 `main()` 直接呼叫內部查詢函式的路徑。這部分沒找到洞。

## 第 5 點:檔名注入與狀態檔路徑——未發現額外洞(非獨立 finding)

送給模型的 reason 字串仍全部經過既有的 `_safe_path()`(本次 diff 沒有改動這道消毒,新增的「(已刪除)」標記只出現在 stderr 除錯訊息裡,不進模型的 `decision:block` reason)。

file: `scripts/hooks/claude/check-graph-sync.py:937`(`stop_block_reason()` 組 reason 仍是 `[f"  • \`{_safe_path(r)}\`" for r in rel[:10]]`,消毒呼叫沒被本次 diff 動過)

`_printed_mark_path(session_id)` 的路徑組法:`re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)[:120]`,再擋 `""`/`.`/`..` 三個特例。試了 `session_id` 內含 `/`、`..`、`../../etc` 三種輸入(本地跑過 regex,不需要真的起 hook):`/` 會被規則換成 `_`,`../../etc` 整段因為含 `/` 也會被打散成 `_.._.._etc` 這種單一路徑段,沒有任何組合能跳出 `_printed_dir()` 這一層,沒找到路徑穿越洞。

## 總結

最嚴重等級:blocker。blocking 共 1 條(Finding 1)。
