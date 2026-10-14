severity: major

以下是對照〈做法〉各點與 [S1]–[S6] 的合規結果。大部分已實作,縮水 2 條(都是照 spec 字面該問卻放行)、多做 3 條、未實作 0 條。重現用掛鉤模組直接呼叫 `bypass_reasons(指令, "/Users/someone/work/repo")`,實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/t.py`。

## 一、已實作

| 項目 | 裁定與佐證 |
|---|---|
| 讀輸入與預篩 | 已實作。`prefilter` 與 `__main__` 在 `guard` 之外:`stdin.buffer.read().decode("utf-8","replace")`、三個字樣加「git+commit+含 n 短旗標」,外包 try/except。沒過預篩 `sys.exit(0)`,不記事件、不跑子程序。 |
| guard 與事件名 | 已實作。`_guard("pretooluse-bypass-ask-hook", __file__, lambda: main(_raw), swallow=True)`。`decide` 內部吞例外時有 `mark("error", …)`,存活事件不帶「問了」的備註。 |
| 逾時預算 | 已實作。我用 awk 抽出 `_BUDGET_RATIO` 到 `return max(_BUDGET_FLOOR` 那段,與 `impact-hook.py`、`dispatch-lens-hook.py` 的 md5 三份相同。git 子程序用 `_inner_budget(default=5.0)` 當逾時。 |
| 長度上限與字面判 | 已實作。`bypass_reasons` 在 `len(command) > MAX_LEN` 或 shlex 丟 ValueError 時走 `_literal`,同時含 git、push 或 commit、`--no-veri` 才回 `literal`。 |
| heredoc 剝除 | 已實作。`strip_heredocs`、`_heredoc_action`、`_find_terminator`、`_drop_bodies` 涵蓋:`<<<` 與 `$((` 排除、多個 heredoc 依序配對、`<<-` 前置 Tab、找不到結束字不剝、運算子保留。 |
| 切詞切段 | 已實作。`_join_continuations` 處理續行;`_tokens` 用 `punctuation_chars="();<>|&\n"` 加 `whitespace_split`,空白字元不含換行;`_is_sep` 與括號堆疊 `stack` 追蹤子殼層。 |
| 找 git 指令 | 已實作。`_command` 用 `basename == "git"` 找段內第一個 git 詞;`_parse_git` 處理全域選項與值選項,記下 `-C`、`-c`。`--no-verify` 縮寫判斷在 `_hit_codes`。 |
| 命中規則 | 大致已實作。`no-verify`、`commit-n`、`c-hookspath`、`config-hookspath`、git 前的 `lumos-skip`、`export` 後接 git 或 lumos 都有。`lumos-skip` 接 lumos 指令縮水,見下。 |
| 拋棄式判定 | 大致已實作。`_temp_roots`(TMPDIR 為空不加)、`_under_temp`(realpath)、`_not_real_repo`、`_push_target_temp`、`_remote_add`(實作期補充的 `git remote add` 本機遠端),`_exempt` 對 rebase、am 等不給豁免。mktemp 部分有偏離,見下。 |
| 命中輸出與介面 | 已實作。`decide` 印出 `permissionDecision: "ask"`,理由只用 `_REASON_TEXT` 固定文字、三段式齊;`decide(event)`、`bypass_reasons(command, cwd)`、`main(raw)` 簽名與職責相符。 |
| `merge-claude-settings.py` | 已實作。PreToolUse 加 `matcher: "Bash"` 並註冊,`HOOK_BUDGET` 為 5,`_codex_entries` 對 PreToolUse 的 Bash 一律 `continue`。 |
| `scripts/lumos` | 已實作。`_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 新列、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 都已加。`governance/anchor-baseline.json` 已含 `bypass-ask-hook.py`(我 grep 計數為 1)。列數測試 24 改為 25。 |
| Systems 節點與計劃 | 已實作。新增 `Systems/代理繞閘問人`(`about_code` 列了掛鉤檔),`Systems/lumos-cli-lifecycle` 加了 WHY 行。計劃現檔有兩條「實作期補充」,實作也有(`remote add`、`$VAR/子路徑`)。 |
| [S1]–[S5] | 已實作。五支測試 `t_bypass_ask_flags_real_bypass`、`ignores_mentions`、`throwaway_targets`、`fallbacks_and_budget`、`registered` 都在 diff 裡,案例涵蓋條款列舉。S3 的缺口見下面縮水第 1、2 條。 |
| [S6] | 已實作(manual 條款)。此條按設計無程式,diff 只保留條款文字,等使用者回報。⚠ 交編排者確認 manual 條款待驗不算未實作。 |

## 二、縮水

1. [S3] mktemp 賦值變數的子路徑可用 `..` 繞出暫存根,仍被當成拋棄式放行。
severity: major
   blocking: 是
   引句:「路徑以 `..` 繞出暫存根」
   - 哪個輸入:`S=$(mktemp -d); cd $S/../../Users/x && git commit -n -m x`。走到 `_expand`:`head and variables.get(...) is _MKTEMP` 就直接 `return _MKTEMP`,沒有解析子路徑。`_not_real_repo` 對 `_MKTEMP` 直接回 True。
   - 重現:`bypass_reasons` 回 `[]`(放行);`S=$(mktemp -d); cd $S/.. && git commit -n -m x` 同樣回 `[]`。
   - 應該是:S3 要求「路徑以 `..` 繞出暫存根」照問。實作期補充只放寬「`$VAR/子路徑`」,`$S/..` 不是子路徑。`_expand` 該拒絕含 `..` 的子路徑,或正規化後確認仍在暫存目錄底下。

2. [S1] `lumos-skip` 接 lumos 指令,只認程式詞位置的第一個詞,前面有 `timeout` 等前綴就漏問。
severity: major
   blocking: 是
   引句:「或寫在 lumos 指令前面(段裡有檔名為 `lumos` 的詞當程式,或 `python*` 的第一個參數檔名是 `lumos`)」
   - 實作:`_command` 只呼叫 `_is_lumos_cmd(seg, i)`,其中 `i` 是跳過賦值與 `_KEYWORDS` 之後的第一個詞,只容許 `env`(加賦值)、`lumos`、`python*` 三種。對照 git 是「段裡任何一個詞」。`_skip_before(seg, i+4)` 的 4 字視窗也讓 `env` 後多個賦值時漏掉。
   - 重現(都回 `[]`):
     - `LUMOS_SKIP_FIX_CHECK=1 timeout 600 lumos code-loop check`
     - `LUMOS_SKIP_FIX_CHECK=1 sudo lumos code-loop check`
     - `timeout 600 env LUMOS_SKIP_X=1 lumos code-loop check`
     - `env -i A=1 B=2 LUMOS_SKIP_X=1 lumos x`
   - 對照:同樣前綴接 git 會命中,`command lumos` 因為 `command` 在 `_KEYWORDS` 裡也命中。S1 明列 `env`/`timeout`/`time` 等前綴要涵蓋「上述指令」,其中含 lumos。

## 三、多做

3. [S3] `cd $(mktemp -d)` 與 `git -C $(mktemp -d)`(指令替換直接當目標,沒經變數)被當拋棄式放行。
severity: minor
   blocking: 否
   引句:「目標含 `$(`、反引號或展開不了的變數 → 目前目錄變成「判不出」」
   - 實作:`_replace_cmdsubs` 把 mktemp 替換記成 `subs[key]=True`,`_expand` 對 `word in subs` 回 `_MKTEMP`。
   - 重現:`cd $(mktemp -d) && git commit -n -m x` 回 `[]`。
   - spec 只讓「`VAR=$(mktemp …)` 賦值後以該變數為目標」豁免;S3 也寫明「`cd $(…)` 之後」照問。這是 diff 有、spec 沒有的放寬。⚠ 方向偏安全且合理,交編排者裁決要放進 spec 還是收回。

4. [S1/S2] `git config set core.hooksPath x` 與 `git config unset core.hooksPath`(新語法子命令)判為 `config-hookspath`。
severity: minor
   blocking: 否
   引句:「if pos and pos[0] in ("set", "unset"):」
   - spec 的寫入形狀只列「帶值、`--unset`/`--unset-all`/`--replace-all`/`--add`」。
   - 重現:兩條都回 `['config-hookspath']`。⚠ 屬合理延伸,建議補進 spec 或標為刻意。

5. [S2] 兩處未在 spec 的行為變更。
severity: minor
   blocking: 否
   引句:「elif a in _COMMIT_VALUE_LONG:」
   - `_commit_short_n` 對長選項(`--message`、`--file`、`--author` 等)吃下一個詞,另加 `a == "--"` 就停止判定。重現:`git commit --message -n`、`git commit -- -n` 都回 `[]`。
   - `_not_real_repo` 對「存在但不在任何 repo 裡的暫存目錄」(`rev-parse` rc 非 0)回 True。重現:`cd /tmp && git commit -n -m x` 回 `[]`。spec 只說「共用 git 目錄也在暫存根底下才算拋棄式」,沒定義這種情形。⚠ 同上,交編排者決定是否補 spec。

## 四、未實作

無。

縮水+未實作共 2 條

severity: major
(最高)。blocking 共 2 條(縮水 1、2),多做 3 條都是 minor、非 blocking。
