severity: minor

這份 diff 在結構上對得上既有做法。`mech_only` 沿用 `keep_going` 的收集模式,判定走 `_lint_new_verdict` 和 `_codeloop_guard_verdict` 同一條路,新閘名也登進了 `_KNOWN_GATES`。我沒找到跨層直呼,也沒找到另寫一套判定。下面四條都是命名、輸出或記帳不一致。

**① 分層與依賴方向**

- 方向是對的。`cmd_lint_new` 呼叫既有的 `_lint_new_verdict`、`_lint_new_config`、`_anchor_repo_root`、`_diff_range_ends`。`_codeloop_pass_mech` 呼叫 `_codeloop_guard_verdict` 和 `_cl_say_block`,沒有繞過去。
- `mech_only` 是現成 `keep_going` 的做法再加一個旗標,沒有另開判定函式。對照 `scripts/lumos:71517` 的 `_codeloop_lint_new_step`,以及 `_CodeloopKg(keep_going or mech_only)`。
- 本節沒有 major 發現。

**② 命名與錯誤處理**

F1
severity: minor
blocking: 否
引句:「不認得的狀態一律當沒檢查到(rc3),不說乾淨」
- 新指令 `lint-new` 把退出碼 3 定義成「沒檢查到」。
- lumos 其他地方的 rc3 是「找不到知識圖譜」:`scripts/lumos:21677` 的 `_node_not_found` 回 3,`scripts/lumos:65638`、`scripts/lumos:68095` 也是。
- 同層的 `lint-check` 只用 0/1/2(`scripts/lumos:39172`)。
- diff 自己在 `_LINT_NEW_CLI_RC3` 和 `--help` 裡寫明了這個衝突,所以是有意的,但同一個數字在兩個指令裡意思不同。

F2
severity: minor
blocking: 否
引句:「_gate_event_or_warn(repo_root, "code-loop-pass", "blocked", "；".join(str(b.get("reason", ""))[:120] for b in blocks)[:300],」
- `code-loop pass` 被擋有兩條路,記在兩個閘名下:
  - 機械檢查擋下記 `code-loop-pass`。
  - 留痕驗證擋下記 `code-loop`,kind 是 `blocked`、note 是 `pass-refused:...`,在 `scripts/lumos:69590`。
- 既有慣例是同一個子指令共用 `code-loop` 閘名,靠 kind 或 note 分辨(`scripts/lumos:72375` 的 check 擋下也記 `code-loop`/`blocked`,並用 `extra={"blocks": kinds}`)。
- 這樣統計「pass 被擋幾次」要合併兩個閘名。diff 註解說撤除條件只數這個,但閘名分叉是新做法。

**③ 第二種做法**

F3
severity: minor
blocking: 否
引句:「print(f"擋下:{diff_range} 帶進了新的問題({lv.get('reason')})(狀態 blocked)", file=sys.stderr)」
- `lint_new` 擋下的訊息,既有路徑由 `_cl_say_block` 的 `lint_new` 分支交給 `_cl_say_lint_block` 印(`scripts/lumos:72387`)。
- 新指令 `cmd_lint_new` 另寫了一組印法:`_lint_new_cli_items`(逐條印、最多 20 條、附放行指令)。
- 同一個判定結果現在有兩套呈現:`lint-new` 一套,`code-loop check` 和 `pass` 另一套。
- 這是否合理要交編排者看:`_cl_say_lint_block` 需要 `branch`/`head_sha`,`lint-new` 沒有這兩個值,所以不能直接套用。⚠

F4
severity: minor
blocking: 否
引句:「bt = ({"status": "not-run", "reason": "只跑新增告警與表態兩道,合約測試沒跑"} if mech_only else」
- `_bound_tests_check` 既有的狀態詞是 `green`、`red`、`unfilterable`、`skipped`(`scripts/lumos:70360`、`scripts/lumos:70471`),跳過用的是 `skipped`。
- diff 為 `mech_only` 發明了 `not-run`。
- 後面的 `bt["status"] in ("red","unfilterable")` 檢查不受影響,但 `last_bound` 會帶出新詞。`scripts/lumos:22438` 和 `scripts/lumos:72698` 讀 `bt` 狀態的地方沒有處理 `not-run`,我沒追它們的行為。⚠
- 另外 `_lint_new_cli_missing` 自己用 `shutil.which` 判斷執行檔存不存在。我沒有確認既有程式裡有沒有現成的同類 helper,留給編排者查。⚠

**測試輔助**

測試端沒有另起一套。`_lnc_repo` 包 `_lng_repo` 和 `_lng_declare`,`_lcp_inproc` 沿用 `_ClkgFakes`。`_lnc_gov` 是讀 `.governance-log.jsonl` 的小輔助,範圍小,我不列為發現。

不對齊共 4 條,其中會擋的 0 條
