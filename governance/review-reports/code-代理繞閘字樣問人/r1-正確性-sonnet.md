severity: major

我把 `bypass_reasons` 實際載入跑了約 130 條指令,臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`。找到 2 條 major、4 條 minor。

1. 訊息 heredoc 裡有撇號時,指令替換後面的旗標整段漏判
引句:「"""i 指在 '(' 上;回傳配對的 ')' 之後的位置(找不到就回字串長度)。引號裡的括號不算。"""」
severity: major
blocking: 是
- 輸入:Claude 慣用的提交寫法,訊息含 `don't` 這類撇號,後面接 `-n`。
- 重現(`bypass_reasons(cmd, "/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass")`,指令用 `git commit -m "$(cat <<'EOF'\ndon't do it\nEOF\n)" -n`):輸出 `[]`,沒問。
- 走到哪:`strip_heredocs` 在雙引號內不剝 heredoc(`bare` 為 False)。`_replace_cmdsubs` 呼叫 `_skip_parens`,它用一個全新的 `_Quotes` 掃 `$(` 內文,把內文的 `'` 當成單引號開頭。於是括號永遠配不到,回傳字串長度,`)" -n` 整段被吞進佔位詞。
- 後果:被吞掉的部分,`-n`、`&& LUMOS_SKIP_X=1 git push`、`&& git -c core.hooksPath=/dev/null push` 都漏問。
- `--no-verify` 仍被 `literal` 兜住。`fix 1) thing` 這種訊息是因括號提早配對,碰巧也被抓到。
- 應該是:`_skip_parens` 要把內文的 heredoc 先剝掉,或是遇到找不到配對時不要吞掉到字串結尾。
- 測試缺口:`t_bypass_ask_flags_real_bypass` 沒有「`$(cat <<'EOF'` 含撇號 + 後綴旗標」這個案例,最常見的形狀沒有測試守。

2. `git config --global` 或 `--system` 從暫存目錄執行會被當拋棄式放行
引句:「if sub in ("commit", "merge", "config"):」
severity: major
blocking: 是
- 重現:`bypass_reasons("cd /tmp && git config --global core.hooksPath /dev/null", R)` 輸出 `[]`。
- 走到哪:`_exempt` 對 `config` 只看生效目錄是不是真 repo。`/tmp` 存在但不在任何 repo 裡,`_not_real_repo` 回 True。
- 錯在哪:`--global`、`--system`、`--file ~/.gitconfig` 寫的是使用者層設定,與生效目錄無關。結果等於關掉所有 repo 的閘,這正是 `config-hookspath` 理由文字說的後果。
- 實際會發生:session 的 cwd 本身常在 `/tmp/...`(例如暫存工作目錄),不必特地 `cd`。
- 應該是:`config` 帶 `--global`、`--system`、`--file` 或 `-f` 時不給拋棄式豁免。計劃〈拋棄式判定〉也沒提到這點。

3. 預篩的 `-n` 偵測在 JSON 跳脫的 `\n` 或 `\t` 之後會失效
引句:「_PRE_SHORT_N = re.compile(r"(?<![\w-])-[a-z]*n[a-z]*\b")」
severity: minor
blocking: 否
- 輸入:續行後沒有縮排的 `-n`,即 `git commit -m x \` 換行接 `-n`。
- 重現:`json.dumps` 後的原文裡 `-n` 前面是 `\n` 的 `n`,後視 `(?<![\w-])` 不成立。`prefilter()` 回 False,但 `bypass_reasons` 本身回 `['commit-n']`。同樣失效的還有 `\t-n`,以及 `git add .` 換行 `git commit -m x` 換行 `-n`。
- 縮排兩格就正常。只影響只靠短旗標那條預篩路徑。
- 應該是:預篩要處理 JSON 跳脫字元,例如前置字元排除 `\n`、`\t`、`\r`,或先 `json.loads` 再判。

4. 註解裡的撇號讓後面的 heredoc 內文沒被剝掉,造成誤問
引句:「"""逐字追蹤 shell 引號狀態,給下面幾個掃描器共用。"""」
severity: minor
blocking: 否
- 重現:`# it's fine\ngit commit -F - <<EOF\nnever use git push --no-verify\nEOF` 輸出 `['no-verify']`;`echo hi # it's\ncat <<EOF\ngit push --no-verify\nEOF` 也一樣。
- 原因:`_Quotes` 不認 `#` 註解,把註解的 `'` 當成開引號,之後的 heredoc 被當成引號內而不剝。shlex 稍後跳過註解,所以內文被當成指令。
- 這是計劃明說要放行的「heredoc 內容字面提到」,卻被誤問。

5. `cd` 的追蹤把失敗或背景的 `cd` 當成成功
引句:「if not os.path.exists(eff):」
severity: minor
blocking: 否
- 重現 A:`cd /tmp/nonexist; git commit -n -m x` 輸出 `[]`。`cd` 失敗後 git 仍在真 repo 跑,但「目錄不存在」被當成「同一條指令裡才建的」。
- 重現 B:`cd /tmp & git commit -n -m x` 輸出 `[]`。`&` 讓 `cd` 在子殼層執行,不影響後面的 git,`_Walker` 卻讓它生效。
- 應該是:目錄不存在要求同一條指令裡有 `mkdir`、`git init` 或 `mktemp` 建過它,`&` 後的 `cd` 不改目錄堆疊。
- `git remote add o /tmp/foo; git remote set-url o git@…; git push --no-verify o` 也是類似的追蹤缺口:`added` 不認 `set-url`,輸出 `[]`。

6. 切詞後失去引號資訊,以及 ANSI-C 引號讓切詞失敗
引句:「return bool(tok) and all(c in "();|&\n" for c in tok)」
severity: minor
blocking: 否
- 重現 A:`git commit -m "(" -n` 輸出 `[]`。shlex 去掉引號後,詞 `(` 與分隔符號無法分辨,被切成兩段。`";"` 與 `"|"` 同理。
- 重現 B:`git commit -m $'it\'s' -n` 輸出 `[]`。shlex 不認 `$'…'`,丟 `ValueError`。`_literal` 只認 `--no-veri`,所以 `-n`、`LUMOS_SKIP`、`hooksPath` 全放行。
- 兩種都很罕見。B 與計劃的字面判口徑一致,只是 `-n` 等代號沒有後備。

確認沒問題的路徑,我走過、沒找到會判錯的輸入:
- 未跳過的 `<<<` 與 `$((…))`。
- 多個 heredoc 同一行。
- 續行與子殼層括號的 push 與 pop。
- `export` 後的 `LUMOS_SKIP_*`。
- 未 export 的 `LUMOS_SKIP_X=1;` 不問,這個判斷正確。
- `commit` 短旗標的吃值規則(`-mn`、`-m -n`、`-Sn`、`-uno -n` 皆符合計劃)。
- `config` 讀與寫的分辨。
- mktemp 變數展開。
- worktree 的共用 git 目錄判斷。

新舊互讀與寫一半的檢查:
- `enforcement_summary` 把 `stale` 排除在分母外,繞閘問人的新列不會拖垮摘要。
- `gov --stats` 讀 `hook-events.jsonl` 只按 hook 名彙總,新事件名讀得對。
- `merge-claude-settings.py` 的 `_equivalent` 以 matcher 加腳本檔名比對,重跑安裝不會重複註冊,也不會被 `_prune_dangling` 剪掉(前提是 `_GLOBAL_CLAUDE_HOOKS` 先複製檔案,這次已加)。
- Codex 目標在 `_codex_entries` 被跳過。
- 掛鉤被逾時砍掉只可能留下一行未完成的追加,與鄰居掛鉤同型,沒有新風險。

測試品質:
- `t_bypass_ask_*` 斷言的是 `decide` 的實際輸出,預期值來自計劃條款,沒有用實作重算,不是純結構測試。
- 缺口就是第 1、2 條所指的案例。第 1 條的 heredoc 加撇號是最常見形狀,卻沒案例。
- `t_bypass_ask_registered` 只驗註冊與列存在,沒驗重跑安裝的冪等性。我讀程式碼判斷冪等,沒另外實測。

角色卡:
- be-api-compat:不影響。這次沒有對外 API。掛鉤的 stdin 與 stdout 形狀沿用既有 PreToolUse 契約,事件帳欄位沒改名也沒刪。
- be-authz:不影響。沒有新增或改動端點,也沒有資料存取。

最嚴重 severity: major,blocking 共 2 條。
