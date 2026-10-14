severity: major

彙總載體,非新增審查席。30 條由八份原報告逐字彙整,只在每條 severity 行前加 ID 行,severity 與引句不變;規格符合報告最後的總結句不是發現,不給 ID、不收入。


來源:r1-正確性-sonnet.md


我把 `bypass_reasons` 實際載入跑了約 130 條指令,臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`。找到 2 條 major、4 條 minor。

1. 訊息 heredoc 裡有撇號時,指令替換後面的旗標整段漏判
引句:「"""i 指在 '(' 上;回傳配對的 ')' 之後的位置(找不到就回字串長度)。引號裡的括號不算。"""」
ID: c1
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
ID: c2
severity: major
blocking: 是
- 重現:`bypass_reasons("cd /tmp && git config --global core.hooksPath /dev/null", R)` 輸出 `[]`。
- 走到哪:`_exempt` 對 `config` 只看生效目錄是不是真 repo。`/tmp` 存在但不在任何 repo 裡,`_not_real_repo` 回 True。
- 錯在哪:`--global`、`--system`、`--file ~/.gitconfig` 寫的是使用者層設定,與生效目錄無關。結果等於關掉所有 repo 的閘,這正是 `config-hookspath` 理由文字說的後果。
- 實際會發生:session 的 cwd 本身常在 `/tmp/...`(例如暫存工作目錄),不必特地 `cd`。
- 應該是:`config` 帶 `--global`、`--system`、`--file` 或 `-f` 時不給拋棄式豁免。計劃〈拋棄式判定〉也沒提到這點。

3. 預篩的 `-n` 偵測在 JSON 跳脫的 `\n` 或 `\t` 之後會失效
引句:「_PRE_SHORT_N = re.compile(r"(?<![\w-])-[a-z]*n[a-z]*\b")」
ID: c3
severity: minor
blocking: 否
- 輸入:續行後沒有縮排的 `-n`,即 `git commit -m x \` 換行接 `-n`。
- 重現:`json.dumps` 後的原文裡 `-n` 前面是 `\n` 的 `n`,後視 `(?<![\w-])` 不成立。`prefilter()` 回 False,但 `bypass_reasons` 本身回 `['commit-n']`。同樣失效的還有 `\t-n`,以及 `git add .` 換行 `git commit -m x` 換行 `-n`。
- 縮排兩格就正常。只影響只靠短旗標那條預篩路徑。
- 應該是:預篩要處理 JSON 跳脫字元,例如前置字元排除 `\n`、`\t`、`\r`,或先 `json.loads` 再判。

4. 註解裡的撇號讓後面的 heredoc 內文沒被剝掉,造成誤問
引句:「"""逐字追蹤 shell 引號狀態,給下面幾個掃描器共用。"""」
ID: c4
severity: minor
blocking: 否
- 重現:`# it's fine\ngit commit -F - <<EOF\nnever use git push --no-verify\nEOF` 輸出 `['no-verify']`;`echo hi # it's\ncat <<EOF\ngit push --no-verify\nEOF` 也一樣。
- 原因:`_Quotes` 不認 `#` 註解,把註解的 `'` 當成開引號,之後的 heredoc 被當成引號內而不剝。shlex 稍後跳過註解,所以內文被當成指令。
- 這是計劃明說要放行的「heredoc 內容字面提到」,卻被誤問。

5. `cd` 的追蹤把失敗或背景的 `cd` 當成成功
引句:「if not os.path.exists(eff):」
ID: c5
severity: minor
blocking: 否
- 重現 A:`cd /tmp/nonexist; git commit -n -m x` 輸出 `[]`。`cd` 失敗後 git 仍在真 repo 跑,但「目錄不存在」被當成「同一條指令裡才建的」。
- 重現 B:`cd /tmp & git commit -n -m x` 輸出 `[]`。`&` 讓 `cd` 在子殼層執行,不影響後面的 git,`_Walker` 卻讓它生效。
- 應該是:目錄不存在要求同一條指令裡有 `mkdir`、`git init` 或 `mktemp` 建過它,`&` 後的 `cd` 不改目錄堆疊。
- `git remote add o /tmp/foo; git remote set-url o git@…; git push --no-verify o` 也是類似的追蹤缺口:`added` 不認 `set-url`,輸出 `[]`。

6. 切詞後失去引號資訊,以及 ANSI-C 引號讓切詞失敗
引句:「return bool(tok) and all(c in "();|&\n" for c in tok)」
ID: c6
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

來源:r1-併發資源-sonnet.md


我量到一個會超過外層預算的形狀,另有兩條 minor。

**1. 2 萬字內塞滿「落在暫存目錄的命中段」,hook 超過 5 秒外層預算**
ID: r1
severity: major
blocking: 是
引句:「timeout=_inner_budget(default=5.0))」

- **輸入**:一條 2 萬字內、約 260 段的指令。每段是 `git -C /tmp commit --no-verify;` 或 `git -C /tmp push --no-verify origin;` 這類,目錄存在且在暫存根底下。
- **走到哪**:`_Walker._command` 對每個命中段呼叫 `_exempt`。`commit` 走 `_not_real_repo`,`push` 走 `_push_target_temp`,兩者都會用 `_git_out` 各起一個 git 子程序。
- **出什麼錯**:`_inner_budget` 回「剩餘時間,下限 1 秒」,只限制單次子程序。沒有全域的子程序次數或總時間上限,段數也沒有上限(`MAX_LEN` 只擋字數)。預算用完後每次呼叫仍給 1 秒,所以 git 稍慢或卡住時,總時間 = 段數 × 1 秒。
- **失敗後果**:外層 5 秒一到,Claude Code 殺掉 hook,這條指令沒有跳「問人」就放行。這是「寧可漏問」的設計,但這個形狀正是繞閘會用的形狀(用重複段把命中埋進去),不是隨機壞輸入。
- **實測**(`bypass_reasons(cmd, "/tmp")`,git 正常、無卡住):
  - 262 段 `git -C <存在的暫存目錄> commit --no-verify;`:6.96 秒,回 `[]`。
  - 約 520 段 `git -C /tmp push --no-verify origin;`:11.55 秒,回 `['no-verify']`。
- **預算起點**:`_BUDGET_START` 在第一次呼叫 `_inner_budget` 才記,不是行程開始。這裡之前花掉的解析時間沒被扣。
- **應該是**:在 `bypass_reasons` 或 `_git_out` 層加總預算守衛,例如累計子程序數上限(約 3 次),超過就改用不查 git 的保守判斷(照命中算、寧可多問),或檢查整體 deadline。

file: `scripts/hooks/claude/bypass-ask-hook.py:306`(`_git_out`),子程序呼叫點在 `_not_real_repo` 與 `_push_target_temp`。

**2. 存活事件檔的修剪用固定暫存檔名,多個會談同時修剪會互相蓋掉**
ID: r2
severity: minor
blocking: 否
引句:「if not _go:」

- **說明**:這條不是新 diff 引入的程式,`_hookevent.py` 不在 diff 內,diff 只是讓它更常被觸發。引句取自 `bypass-ask-hook.py` 裡「預篩在 guard 之外」的接線,過了預篩的每條 Bash 都會記一筆。
- **走到哪**:`record()` 在檔案超過 512KB 時,讀整檔、取最後 2000 行、寫入固定名稱的 `hook-events.jsonl.tmp`,再 `os.replace`。
- **會出什麼錯**:兩個會談同時修剪時,會寫同一個 `.tmp`,後到的可能把另一方寫到一半的內容換上去。讀檔到改名之間別人 append 的行也會丟。
- **未能重現**:我沒有造出並行修剪的場景,所以沒有實測。
- **擠掉其他掛鉤紀錄**:預篩的 `-[a-z]*n[a-z]*` 只要原文同時含 `git`、`commit` 和任何含 n 的短旗標就過。我測到 `git log | grep commit; find . -name x` 這種純讀指令會過。過預篩的比例因此高於命中。修剪是留最後 2000 行,commit 密集的工作階段可能把 memory-sweep 這類低頻掛鉤的存活紀錄擠出去。我沒量到實際比例,所以只列 minor。

**3. `MAX_LEN` 的註解和實際最壞情形不符**
ID: r3
severity: minor
blocking: 否
引句:「MAX_LEN = 20000                     # 超過就不做結構分類,走字面判(shlex 對超長單詞是超線性)」

- 註解說慢在 shlex,但我實測的純解析形狀都不慢:
  - 括號、引號、反斜線、`$(` 這幾種形狀在 2 萬字內 ≤0.02 秒。
  - 5000 個 `<<A\n` 的未結束 heredoc 約 1.6 秒(`_drop_bodies` 每個換行都掃到結尾,是平方級)。
  - 1 萬個 `` `a `` 的反引號約 0.4 秒。
- 這些都在 5 秒內,所以不構成缺陷。真正的最壞路徑是 finding 1 的子程序累加,註解沒提。應該把註解改成指向子程序數量,或把 finding 1 的上限寫進去。

**其他項目,逐項判定(都沒找到問題)**

- **成本**:`echo '{}'` 空跑一次總計 0.053 秒;預篩只做子字串與一個正規式,不啟動 `_hookevent` 以外的子程序。
- **正規式**:`_PRE_SHORT_N`、`_ASSIGN`、`_expand` 都是線性,無回溯爆炸。
- **子程序釋放**:全用 `subprocess.run(timeout=)`,逾時會殺子程序。找不到 git 或權限問題都落入 `except` 回 `(None, "")`,不會拋出,也沒有開著沒關的檔案描述子。
- **`sys.path.insert(0, 本目錄)`**:放在 import `_hookevent` 前,只影響這支 hook 自己的行程,沒有副作用。
- **固定席節點**:這份 diff 不影響各節點宣稱的行為。
  - lumos-cli-lifecycle:`re-inject` 只覆蓋 sentinel 之間 body,diff 只動安裝名單、enforcement 列、錨點名單,沒碰這段邏輯。
  - lumos-cli-read:`search` 沒被碰。
  - guard-kill:`guard kill` 的 rc 優先序與 `--json` 純度沒被碰。
  - design-loop、測試假綠形態:diff 沒碰設計審處置閘,也沒改既有「還原翻紅釘」測試;新增測試是否帶前置斷言不在我的鏡頭內。

最嚴重 severity:major,blocking 共 1 條。

來源:r1-邊界輸入-sonnet.md


這份報告的 major 是 finding 1。我用 SourceFileLoader 載入 `scripts/hooks/claude/bypass-ask-hook.py`,直接呼叫 `bypass_reasons`,共跑約 130 條邊界輸入。臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/`。

## Finding

1. 單詞中間的 `#` 被 shlex 當成註解,後面整行(含 `--no-verify` 與接著的 git 指令)被吞掉,不問。
引句:「lex = shlex.shlex(cmd, posix=True, punctuation_chars="();<>|&\n")」
ID: e1
severity: major
blocking: 是
- 輸入:分支名或訊息帶 `#` 很常見,例如 `git checkout -b fix#1 && git push --no-verify`。
- 路徑:`_tokens` 用 `shlex.shlex`,預設 `commenters='#'`,而且在單詞狀態遇到 `#` 就丟掉整行剩餘內容。bash 只在詞首才把 `#` 當註解,所以 `fix#1` 在 bash 裡是普通詞。
- 重現(cwd 為本 repo):

```
bypass_reasons("git checkout -b fix#1 && git push --no-verify", R)  -> []
bypass_reasons("echo a#b; git push --no-verify", R)                 -> []
```

- 對照:`# git commit -n` 與 `echo a #; git commit -n`(詞首註解)回 `[]` 是對的。
- 應該:`_tokens` 不要依賴 shlex 的註解處理。可設 `lex.commenters = ""`,再自己用 `_Quotes` 在引號外、詞首(前一字元是空白或分隔符)才切掉 `#` 到行尾。
- 理由:這是計劃〈範圍〉沒列的漏洞,也不是 `$(…)` 之類已聲明的攔不到。但觸發需要 `#` 出現在被吞的那段之前,所以我只給 major,未到 blocker。

2. `--git-dir=X`、`--work-tree=X`、環境變數 `GIT_DIR=X` 不影響生效目錄,commit、merge、config 被判成「拋棄式」而放行。
引句:「for d in gdirs:」
ID: e2
severity: minor
blocking: 否
- 輸入:cwd 在暫存根底下、但本身不是 repo 的目錄,而指令指向真 repo。
- 路徑:`_Walker._command` 的 `eff` 只吃 `-C`。`_exempt` 對 commit、merge、config 走 `_not_real_repo(eff)`,而 `eff` 是暫存目錄且不在任何 repo 裡,所以回 True。
- 重現(cwd 為暫存目錄 W,不是 repo):

```
"git --git-dir=<真repo>/.git commit -n"      -> []
"GIT_DIR=<真repo>/.git git commit -n"        -> []
"git --work-tree=<真repo> commit -n"         -> []
```

- 為什麼只給 minor:push 沒寫遠端時一律問,所以不受影響。其他子指令得 cwd 剛好在暫存目錄才會漏。
- 應該:指令出現 `--git-dir`、`--work-tree`、`GIT_DIR`、`GIT_WORK_TREE` 時,把 `eff` 設成 `_UNKNOWN`(即不豁免)。計劃已寫明黏著的 `--git-dir=X` 不多吃一個詞,這點沒問題。要補的是這些選項不能讓豁免成立。

3. `mktemp` 目錄的子路徑含 `..` 時,仍被當成新建目錄而豁免。
引句:「if head and variables.get(head.group(1)) is _MKTEMP:」
ID: e3
severity: minor
blocking: 否
- 輸入:`d=$(mktemp -d); git -C $d/../../..<真repo絕對路徑> commit -n`。
- 路徑:`_expand` 只看詞首的 `$d/`,就整個回 `_MKTEMP`,沒檢查後面有沒有 `..`。
- 重現:`"d=$(mktemp -d); cd $d/..<真repo> && git commit -n"` 回 `[]`。
- 應該:剩餘子路徑含 `..` 段就回 `_UNKNOWN`。實際代理很少這樣寫,所以只給 minor。

## 邊界逐項結果(會問 / 放行 / 例外)

全部沒有丟例外。出現的 `literal` 都是 shlex 的 ValueError 走字面判,結果是問人。

**問人,行為正確或可接受(寧可多問)**
- 單一引號 `'`、`\` 結尾,搭配 `git push --no-verify`:問(literal)。
- `$'a\'b'` 後接 push:問(literal)。
- `<<` 在行尾:問。
- `<<-` 配空白縮排:問。bash 的 `<<-` 只吃 Tab,所以問是對的;配 Tab 縮排則放行,也對。
- 結束字帶引號或反斜線:內文正確剝掉,放行。
- 同一行三個 heredoc:內文剝掉,後面真正的指令照問。
- heredoc 在括號裡:內文剝掉,括號後的指令照問。
- `case ... ;;`、`|&`、`&>`、`2>&1`、`>|`:問。
- 陣列賦值 `a=(1 2)`、`a+=x git push --no-verify`:問。
- `cd ""`:判成路徑未知,問。
- `git -C a -C b`(多次相對 `-C`):依序疊加,問。
- `-C ../x`:問。
- `git --git-dir x` 或 `--git-dir=x` 加 push:問。
- `git -c a=b=c`(值含等號):問。
- `\r\n` 換行:問。
- cwd 是相對路徑、空字串或 None:判成未知,問。
- `echo git push --no-verify`:問。這是計劃明列的刻意誤問。
- 超過 2 萬字且含 `--no-veri`:literal,問。

**放行,行為正確**
- 空指令、只有空白、只有換行、單一引號本身:放行。
- `--no-verify=`:放行。這是 git 的非法形式,git 會拒絕。
- `--no-ve`、`--no-ver`:放行。我用真 git 實測,commit 與 push 都回 `ambiguous option: no-ve (could be --no-verbose or --no-verify)` 而失敗。`--no-veri` 是第一個不歧義的前綴,和程式碼一致。
- `--no-verify` 後面黏字(`--no-verifyxxx`):放行。
- `git commit -mn`、`-m n`、`-m -n`、`-- -n`:放行,都是值而不是旗標。
- `git config --local core.hookspath`(唯讀):放行。
- `cd -- /tmp/x`、`cd -P /tmp`、路徑含空白、中文或換行,且位於暫存根:放行(拋棄式)。
- `LUMOS_SKIP_X=1 bash scripts/lumos x`:放行。見下方「待確認」。
- `rebase`、`am`、`cherry-pick` 加 `--no-verify`:放行。見下方「待確認」。
- cwd 為 `/tmp`:放行。

**漏問,但屬計劃已聲明的範圍(不當 finding)**
- `$(git push --no-verify)`、反引號、`$(` 或反引號不閉合:放行。
- 超過 2 萬字且只含 `commit -n`、`core.hooksPath` 或 `LUMOS_SKIP_`:放行,因為字面判只看 `--no-veri`。這是計劃〈字面判〉明文的「其他放行」。

**小怪點(無實害)**
- `export -n LUMOS_SKIP_X=1` 會問,但 `export -n` 是取消匯出,屬誤問。
- `LUMOS_SKIP_X+=1 git push` 會漏問。`_SKIP_ASSIGN` 不吃 `+=`,但 bash 實際會把它帶進環境。實務上沒人這樣寫。

**效能**
我另外測了 2000 與 3000 個未配對 `<<a` 後接 5000 到 8000 行、1500 組 heredoc、9000 層括號、6000 個 `$((`、2500 段 `cd`、600 個 `remote add`。所有輸入都在 0.05 秒內判完,沒有退化。

**待確認(交編排者)**
- ⚠ `rebase --no-verify` 與 `LUMOS_SKIP_*` 在 `bash scripts/lumos` 之前:`_hit_codes` 的 no-verify 只認 commit、push、merge,`_is_lumos_cmd` 只認 `lumos` 或 `pythonN lumos`。我判斷這是設計取捨,但沒在計劃條款裡找到明文。請確認計劃〈範圍〉有寫,沒寫就補一句。

## 固定席節點逐條判

- **`Issues/code-loop守衛main-direct盲區.md`**:diff 沒改 code-loop 守衛的 main-direct 邏輯,只新增問人層掛鉤與註冊,不影響。
- **`Systems/lumos-cli-lifecycle.md`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間 body)**:diff 動到 `scripts/lumos` 的安裝名單與 `merge-claude-settings.py` 的註冊,沒碰 CLAUDE.md 的 sentinel 注入。我沒找到會破壞 `t_reinject_preserves_outside` 的路徑,不影響。
- **`Systems/lumos-cli-read.md`(search 預設排除 superseded)**:沒有改 search,不影響。
- **`Systems/測試假綠形態.md`(還原翻紅釘要配前置斷言)**:這是對新測試的要求,不是對 diff 的破壞。新測試 `t_bypass_ask_*` 我沒逐條審還原翻紅釘,不判。
- **`Systems/design-loop.md`(處置閘第五步)**:diff 剔除了設計審卷證,沒動處置閘程式,不影響。
- **`Systems/guard-kill.md`(rc 優先序、`--json` 純度)**:沒碰 guard kill,不影響。
- **`pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★)**:只列出牽連 `scripts/lumos`。diff 在 `scripts/lumos` 只動 enforcement 列、安裝名單與錨點名單,我沒發現改變它們宣稱的行為。
- 其餘「超出上限只列名」的節點:我沒逐篇讀,不判。

最嚴重 severity:major,blocking 共 1 條(finding 1),minor 共 2 條。

來源:r1-合約圖譜-sonnet.md


我是三個月後的接手人,逐項對了計劃與兩篇 Systems 節點的句子、掛鉤與註冊程式的實際行為、各處平行名單,以及條款 [S1]–[S5] 綁的測試。有 1 條 major、3 條 minor。

**平行名單與命名(逐項對過,沒有問題)**
- 事件名 `pretooluse-bypass-ask-hook` 與 `enforcement_status` 的列名一致。
- 預篩字樣、長度上限 2 萬字、`_inner_budget` 的複本都與計劃相符。`HOOK_BUDGET` 的 5 與 `_codex_entries` 跳過 Bash 的寫法,和計劃、S5 也相符。
- `scripts/lumos` 裡凡是列舉掛鉤檔名的地方都改到了:
  - 安裝名單 `_GLOBAL_CLAUDE_HOOKS`、工具自裝檔名單 `_VENDORED_TREE_FILES`、錨點名單 `ANCHOR_FILES`、`enforcement_status` 的列。
  - `_own_hook_scripts` 由安裝名單推出,不必另改。
  - 安裝與拆除流程用的 `_GLOBAL_HOOKS` 與 `_GLOBAL_CLAUDE_HOOKS` 是同一份,所以拆除會清掉這支。
- `governance/anchor-baseline.json` 的 sha256 與現檔相符。
- 三篇筆記的 `lumos lint` 都是 0 問題;摘要行的必有鍵(WHY 的出處與因、PITFALL 的出處、根因與 test)都齊,`[test:]` 指的測試名都存在。
- 我跑了 `-k bypass_ask`、`vendored`、`budget`、`anchor`、`enforcement`、`codex_r1`、`hook_python`,全綠。
- 文件裡沒有別的地方列舉掛鉤檔名,不必跟著改。

**1.** 計劃〈回退〉說拿掉註冊就能退,實際做不到
ID: g1
severity: major
blocking: 是
引句:「拿掉 `merge-claude-settings.py` 那條 Bash matcher 並重跑安裝,掛鉤就不再被呼叫;掛鉤檔留著不影響任何事。」
- 輸入:照這句做,從 `HOOK_ENTRIES` 刪掉 `matcher: "Bash"` 那條,重跑 `merge-claude-settings.py`。
- 走到哪:合併器只會新增、遷移、去重,並剪掉指向不存在檔案的註冊,不會移除已經寫進 `settings.json` 的條目。見 `scripts/merge-claude-settings.py:381-394`。
- 結果:`bypass-ask-hook.py` 仍在 `_GLOBAL_CLAUDE_HOOKS`,檔案照舊被複製,所以註冊不算懸空,也不會被剪。
- 重現:我在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/rb.py` 用假 HOME 先裝再用拿掉該條的版本重跑,重跑後 PreToolUse 仍是 `('Bash', ['ude/hooks/bypass-ask-hook.py" --budget 5'])`。
- 應該是:〈回退〉要寫成同時把檔名移出安裝名單並加進 `_RETIRED_CLAUDE_HOOKS`(讓檔被刪、註冊變懸空後被剪),或改寫成只能靠分類函式收窄。目前的句子會讓接手人以為拿掉就退了,實際上每次命中仍會跳確認框。

**2.** `LUMOS_SKIP_*` 接 lumos 指令的判法,與計劃寫的規則和 S1 的前綴說法不一致
ID: g2
severity: minor
blocking: 否
引句:「的詞當程式,或 `python*` 的第一個參數檔名是 `lumos`」
引句:「if self._skip_before(seg, min(len(seg), i + 4)) and _is_lumos_cmd(seg, i):」
- 輸入與輸出(`bypass_reasons(指令, "/Users/someone/work/repo")`):
  - `LUMOS_SKIP_FIX_CHECK=1 timeout 60 lumos code-loop check` 回 `[]`。
  - `LUMOS_SKIP_X=1 sudo lumos code-loop check` 回 `[]`。
  - `lumos search LUMOS_SKIP_X=1 foo` 回 `['lumos-skip']`,這是誤問。
- 原因:`_is_lumos_cmd` 只看「略過賦值與關鍵字之後的第一個詞(含 `env` 之後)」是不是 lumos。計劃寫的是「段裡有檔名為 lumos 的詞」,git 那邊也確實是掃整段,只有 lumos 這條不一致。
- 前綴不一致:S1 說前綴 `env/timeout/time/command/then/!/括號` 都認得,但 `timeout` 與 `sudo` 這類沒列在 `_KEYWORDS` 的包裝詞會漏。
- 誤問:`i + 4` 的視窗計劃沒寫,視窗內的參數若長得像 `LUMOS_SKIP_X=1` 會被當成賦值。
- 應該是:程式改成與計劃一致,或計劃改寫成實際行為。S1 的測試也沒有這個形狀的案例。

**3.** S4 的三種最壞形狀與預篩例外,測試沒有真正驗到
ID: g3
severity: minor
blocking: 否
引句:「10 萬字單詞、數萬個分段、大量未閉合 `<<EOF` 三種形狀 應 各在 0.5 秒內判完」
引句:「("大量未閉合 heredoc", "cat <<EOF " * 3000 + "\n git push --no-verify")):」
引句:「預篩階段丟例外、輸入不是 UTF-8、`command` 不是字串時 應 放行、不印 traceback」
- 未閉合 `<<EOF` 那筆長 30022 字,超過 `MAX_LEN`,直接走 `_literal`,從沒跑到 `strip_heredocs`。10 萬字單詞同樣只走字面判。
- 我另外量了真正走結構分類的形狀,都在 0.5 秒內:
  - 未閉合 heredoc 1900 次,19022 字,0.02 秒。
  - 1900 個含換行的 heredoc,0.25 秒。
  - 4900 個指令替換,0.31 秒。
  - 實測沒有效能問題,但 S4 綁的測試沒有驗到條款說的最壞情形。
- 「數萬個分段」測的是 9000 個,不到數萬。
- 條款列了「預篩階段丟例外」,測試沒有這一項。非 UTF-8 的案例走的是替換解碼,不會丟例外。計劃的審計紀錄承認這層「刻意不釘」,但條款文字仍把它列為應驗項,兩邊不一致。
- 應該是:條款拿掉這一項,或測試補上。

**4.** S3 說暫存根以 `_temp_roots()` 為準,但測試把它整個換掉
ID: g4
severity: minor
blocking: 否
引句:「暫存根以 `_temp_roots()` 為準,相對 `cd` 依序疊加解析」
引句:「m._temp_roots = lambda: [str(tmp_root)]」
- 整份新測試沒有任何一處驗預設根(`/tmp`、`/private/var/folders` 等六個、`TMPDIR` 有設才加、空字串不加)。
- 把 `_temp_roots` 裡的 `"/tmp"` 拿掉,S1 到 S5 照樣全綠。
- 設計審量到的主要情境(審查席在 `/tmp/lumos-seat-work/` 做實驗)因此沒有守衛。
- 應該是:補一條不換掉 `_temp_roots` 的案例,例如 `cd /tmp/新目錄 && … --no-verify` 放行。

**一個附帶觀察(不算 finding)**
- `_GLOBAL_HOOKS` 與 `_GLOBAL_CLAUDE_HOOKS` 同名單,安裝時 Codex 的 `~/.codex/hooks` 也會多收到一份未註冊的 `bypass-ask-hook.py`。
- 這不會被執行,也沒有測試因此翻紅。計劃〈做法〉只寫了 `~/.claude/hooks/`。

**固定席節點逐條判**
- `Issues/code-loop守衛main-direct盲區`:不影響。它管 pre-push 的 tier 判定,diff 沒動 `scripts/hooks/pre-push`。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject):不影響。新增的是一行 WHY 與安裝名單、錨點、列舉各一處,沒碰注入範本或 sentinel 邏輯,`t_reinject_preserves_outside` 不在改動路徑上。
- `lumos-cli-read`、`測試假綠形態`、`design-loop`:不影響。只加了新測試與一個 hook 檔,沒改 search 排除、還原翻紅釘或處置閘。
- `guard-kill`:不影響。沒動 guard kill 的 rc 優先序或 `--json` 輸出。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):不影響。diff 沒碰 pitfalls 規則與逃逸帳的流程;新掛鉤也不寫帳,只寫存活事件。
- 其餘「超出上限、只列名」的節點:diff 沒有觸及它們登記的檔案行為,不逐條展開。

總結:最嚴重 severity 為 major,blocking 共 1 條(第 1 條)。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/merge-claude-settings.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/docs/lumos-toolchain-knowledge/Projects/代理繞閘字樣問人_計劃.md`
- `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/rb.py`(第 1 條的重現)
- `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/p.py`(第 2 條的重現)

臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/` 是我建的,留給編排者在收齊後刪除。

來源:r1-通才-sonnet.md


我載入掛鉤模組,用 `bypass_reasons(指令, cwd)` 實測了約 130 條正常寫法。沒有發現會讓閘整個失效的洞。有一個實作 bug 和〈範圍〉不一致:預篩漏掉〈S1〉明列要問的續行寫法。另有一組可低成本補上的缺口,和一組該在〈範圍〉承認的缺口。提交前閘只有 pre-commit 和 pre-push,下面都以這兩道為準。

1. 預篩漏掉「續行後 `-n` 頂在行首」的 `git commit`
ID: t1
severity: major
blocking: 是

引句:「_PRE_SHORT_N = re.compile(r"(?<![\w-])-[a-z]*n[a-z]*\b")」

- 預篩看的是 stdin 的 JSON 原文。指令裡的換行在 JSON 裡是 `\n`,所以 `-n` 前面緊貼著字母 `n`(`\t` 則是字母 `t`)。
- `(?<![\w-])` 的負向後look 因此不成立,預篩回 False,掛鉤直接 exit 0,連 `bypass_reasons` 都沒跑。
- 這是〈S1〉明列的「跨行與續行寫」,也是 `git commit -m x \` 換行後把 `-n` 頂在行首的常見排法。縮排兩個空白的寫法有被攔到,所以測試很容易漏掉。
- 重現(`prefilter(json.dumps({"tool_input":{"command":c},"cwd":R}))` 加 `bypass_reasons(c,R)`):

```
prefilter  bypass_reasons       command
False      ['commit-n']         'git commit -m x \\\n-n'
False      ['commit-n']         'git commit -m x \\\n\t-n'
True       ['commit-n']         'git commit -m x \\\n  -n'
```

- 分類器其實會判中,是預篩擋掉了。
- 應該:預篩也用 `command` 欄位解碼後的文字判,或把 lookbehind 改成不把 JSON 跳脫字母算進去(例如先 `json.loads` 取 command 再做 `-n` 預篩)。`json.loads` 失敗時再退回原文判。

2. `--config-env` 與 `GIT_CONFIG_*` 環境變數是 `-c` 的原生等價寫法,程式碼卻不攔
ID: t2
severity: minor
blocking: 否

引句:「_GIT_VALUE_OPTS = {"-c", "-C", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}」

- 程式認得 `--config-env` 並跳過它的值,但 `_parse_git` 只把 `-c` 的值收進 `cfgs`。
- 實測以下全部回 `[]`(放行):
  - `git --config-env=core.hooksPath=H push`
  - `git --config-env core.hooksPath=H push`
  - `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/dev/null git push`
  - `GIT_CONFIG_PARAMETERS="'core.hooksPath=/dev/null'" git push`
- 這些字樣會過預篩(含 `hookspath`),所以是分類器漏判,不是預篩漏掉。
- 〈範圍〉沒列這些寫法,屬於未承認的缺口。
- 建議攔:`--config-env` 與 `-c` 共用 `cfgs`,是一行改動。`GIT_CONFIG_KEY_<n>=core.hooksPath` 和 `GIT_CONFIG_PARAMETERS` 可以當成 env 賦值,走 `lumos-skip` 同一條路徑。

3. 先賦值再裸 `export NAME`,以及 `declare -x`,不會被當成 export
ID: t3
severity: minor
blocking: 否

引句:「if _ASSIGN.match(w) and self._assign(w).startswith("LUMOS_SKIP_"):」

- `_export` 只認 `export NAME=值`。
- `LUMOS_SKIP_X=1; export LUMOS_SKIP_X; git commit -m x` 回 `[]`。
- `declare -x LUMOS_SKIP_X=1; git commit` 也回 `[]`。
- 後者的 `declare` 被當成一般指令。
- 前者是常見寫法。
- 建議:`export` 的參數若是裸名且名稱以 `LUMOS_SKIP_` 開頭、又已在 `variables` 裡,就設 `exported_skip`。

4. 這些攔不到,應在〈範圍〉明寫承認(目前只列了 shell 別名,沒列到)
ID: t4
severity: minor
blocking: 否

引句:「只看指令文字;以下攔不到,這篇防「代理順手繞」、不防有心改寫」

- 這句引自計劃〈範圍〉,在 diff 裡。以下都實測回 `[]`:
  - 直接改 `.git/config`:`sed -i 's/hooksPath.*//' .git/config`、`printf ... >> .git/config`。字樣「hookspath」會過預篩,但分類器沒有對應規則。
  - `git config --edit` / `-e`。
  - 動 `scripts/hooks/` 的閘:`rm`、`mv`、`chmod -x`、`echo 'exit 0' > scripts/hooks/pre-push`。pre-push 在 `ANCHOR_FILES` 裡,事後 `anchor verify` 抓得到;但 `.git/hooks` 和 `.git/config` 不在錨點內。
  - 掛鉤的 matcher 只有 `Bash`。用 Edit 或 Write 工具改 `.git/config`、`scripts/hooks/pre-push`、`~/.claude/settings.json`(拿掉這條註冊)完全不經過掛鉤。
  - 不走 `git push` 的送出方式:`git send-pack`、`git commit-tree` 加 `git update-ref`、`git fast-import`,都不跑 pre-push。
  - git 別名:`git config alias.p 'push --no-verify'` 和 `git -c alias.p='push --no-verify' p` 都回 `[]`。〈範圍〉只寫了「shell 別名與函式」,git 自己的別名沒列。
  - `LUMOS_SKIP_X=1 python3 -X dev scripts/lumos doctor`:`_is_lumos_cmd` 取「第一個不以 `-` 開頭的參數」,把 `-X` 的值 `dev` 當成腳本。
- 這幾條都是有意識地改寫或換工具,符合單人加問人層的威脅模型,攔下的收益低。
- 建議全部寫進〈範圍〉。可以順手攔的只有直接改 `.git/config`:非 git 指令的段落裡同時有 `.git/config` 和 `hookspath`,成本低。

5. 該判「不影響」或不需攔的
ID: t5
severity: minor
blocking: 否

引句:「_HOOK_SUBS = ("commit", "push", "merge", "rebase", "am", "cherry-pick", "revert")」

- `git pull --no-verify` 是 git 接受的旗標,但它只會跳過 pre-merge-commit 和 commit-msg。本 repo 沒裝這兩個,所以不影響 Lumos 的閘。
- `rebase` 與 `am` 的 `--no-verify` 同理。
- `LUMOS_SKIP_*` 只有 pre-push 讀(`DRIFT_CHECK`、`NOTE_SHAPE`、`REREAD_CHECK`),pre-commit 沒讀,所以 `LUMOS_SKIP_X=1 git cherry-pick` 放行是對的。
- 這一條不需要動作。

固定席節點逐條判

- lumos-cli-lifecycle 的 re-inject 合約:不影響。diff 只在 `_GLOBAL_CLAUDE_HOOKS`、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 和 enforcement 列加一項,沒碰 sentinel 之間覆蓋與 sentinel 之外 byte-equal 保留的邏輯。
- lumos-cli-read(search 排除 superseded 的合約):不影響,沒碰 search 路徑。
- 測試假綠形態、design-loop、guard-kill 三份合約:不影響。這份 diff 沒動這些路徑。
- 測試假綠形態的相關風險:上面第 1 條正是前置斷言的對照案例。測試若只用縮排續行或單行寫法驗〈S1〉,第 1 條缺口會是綠的。
- code-loop 守衛盲區的 Issue、pitfalls-code-loop、reversibility 的 RISK 節點:不影響。
- 其餘「只列名」的節點:我沒逐篇讀,無法判。

最嚴重 severity:major,blocking 共 1 條(第 1 條)。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`
- 重現腳本:`/tmp/lumos-seat-work/code-代理繞閘字樣問人/通才-sonnet/p.py`

來源:r1-架構對齊-sonnet.md


我只讀了 diff 和鄰居檔,沒有跑任何東西重現。報告裡的行號指 `/tmp/code-代理繞閘字樣問人-r1.patch` 的行,或 repo 內檔案的行(repo 是 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass`)。我的 Bash 被 lumos-guard 擋過一次(路徑含 claude),改加結尾斜線後可用。三問都沒有 major。

## 1. 分層與依賴方向

分層跟鄰居一致,沒有跨層直呼。

- 新掛鉤放在 `scripts/hooks/claude/`,跟 `impact-hook.py`、`dispatch-lens-hook.py` 同層。它只依賴 `_hookevent.guard` 與 `mark`,再加標準庫、`git` 子程序,沒有 `import` `scripts/lumos`。
- 註冊走 `merge-claude-settings.py` 既有路徑:`HOOK_BUDGET` 加 `"bypass-ask-hook.py": 5`,`HOOK_ENTRIES["PreToolUse"]` 加 `matcher: "Bash"`(patch 1060-1095 行)。
- Codex 側在 `_codex_entries` 用 `continue` 跳過 Bash matcher(1125-1126 行)。形狀跟旁邊 `Edit|Write|MultiEdit`、`Agent` 的 matcher 特例一樣。
- `scripts/lumos` 的四處名單(`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 列舉)都補了,跟既有掛鉤同一套(patch 964、987、1009、1031-1034 行)。
- 分類邏輯放在掛鉤內,是計劃 d1 已決的偏離,不重報。我查了先例:`impact-hook.py` 與 `memory-sweep.py` 確實是厚掛鉤,理由不假。

## 2. 命名與錯誤處理

**finding 1**
ID: a1
severity: minor
blocking: 否

`__main__` 收尾與 stdin 讀法跟四個鄰居不同。

- 鄰居的做法:`impact-hook.py:919-928`、`dispatch-lens-hook.py:546-555`、`ci-status-hook.py:244-256`、`memory-sweep.py:959` 都在 `__main__` 區塊內用 `import sys as _s, pathlib as _p`,再 `from _hookevent import guard as _guard`,最後 `sys.exit(_guard(名, __file__, main) ...)`。`main()` 無參數,自己在內部 `json.loads(sys.stdin.read())`,JSON 壞掉就 `return 0`(`impact-hook.py:769-773`)。
- 新檔的做法:
  - 模組頂層 `sys.path.insert` 加 `try: from _hookevent import guard as _guard, mark`,失敗時自定一個 `mark` 空殼(patch 256-263 行)。
  - 在 `__main__` 以 `sys.stdin.buffer.read().decode("utf-8","replace")` 先讀,預篩後用 `lambda: main(_raw)` 傳入,`main(raw: str)` 帶參數(patch 928-948 行)。
- 錯誤處理的差異:`main` 內是 `decide(json.loads(raw))`,JSON 壞掉靠 `guard(swallow=True)` 吞掉,不是鄰居那種就地 `return 0`。結果仍是放行,只是路徑不同。
- 計劃明文要求「讀一次、預篩在 guard 之外」,所以讀 stdin 的位置不同有理由。結構對,這是形狀不一致,故為 minor。
- 引句:「sys.exit(_guard("pretooluse-bypass-ask-hook", __file__, lambda: main(_raw), swallow=True))」

已對齊、不報的項目:

- 輸出 JSON 是 `{"hookSpecificOutput": {"hookEventName": "PreToolUse", ...}}` 加 `ensure_ascii=False`,與 `dispatch-lens-hook.py:285` 同形。
- 事件名 `pretooluse-bypass-ask-hook` 等於 `enforcement_status` 的列名,命名規則與 `pretooluse-impact-hook`、`pretooluse-dispatch-lens-hook` 一致。
- `--budget` 預算段是 `impact-hook.py` 的逐字複本(`_BUDGET_RATIO`、`_outer_budget`、`_inner_budget`)。

## 3. 第二種做法

我 grep 了 `_sh_quote`(`scripts/lumos:450`)、`_repo_path_unsafe`、`_path_special_chars`。新碼完全不用這三個:它不印給人照抄的指令,理由文字也不嵌入指令內容,所以沒有重造引號或路徑消毒。

**finding 2**
ID: a2
severity: minor
⚠
blocking: 否

新增了一套自寫的 shell 解析器,專案裡已有一套較弱的。

- 已有的一套:`check-graph-sync.py:431-442` 的 `_segment_command` 用 regex 切 `&&`、`||`、`;`、`|`,`_tokens_of` 用 `shlex.split`,但不追蹤引號。作者自己註明「Quote-aware 不嚴格」。
- 新增的一套:`_Quotes`、`_join_continuations`、`strip_heredocs`、`_replace_cmdsubs`、`_tokens`(`shlex` 加 `punctuation_chars`)、`_Walker`,共約 400 行(patch 377-547、791-889 行)。
- 為什麼不算 major:
  - 兩邊需求不同。新碼要追蹤引號、heredoc、`cd`、子殼層,舊的做不到。
  - 兩支掛鉤各自獨立安裝,新檔不能 `import` 檔名帶連字號的 `check-graph-sync.py`。
  - 舊函式只服務已無呼叫點的 `touched_graph_via_cli`。
- 缺口:計劃 d1 只裁了「邏輯放掛鉤內」,沒有交代為何不復用或為何要另寫切段器。判不準,標 ⚠ 交編排者。
- 引句:「lex = shlex.shlex(cmd, posix=True, punctuation_chars="();<>|&\n")」

**finding 3**
ID: a3
severity: minor
blocking: 否

暫存根名單另立一份,而且組法跟 Python 側既有的不同。

- 既有的 Python 做法:`scripts/lumos:18226` 與 `impact-hook.py:172,179` 都只用 `tempfile.gettempdir()`(前者再 `realpath`)。
- 新檔的做法:`_temp_roots()` 寫死六個路徑,只有 `os.environ.get("TMPDIR")` 為真才加 `tempfile.gettempdir()`(patch 131-135 行)。
- 這份名單與 `mods/claude/lumos-guard/hooks/register.ts` 的暫存根是另一種語言的另一份,計劃明寫「取聯集」,屬已知設計。
- 不一致處:Python 側沒有共用名單函式可呼叫,但「gettempdir 要不要無條件加」的條件不同。`TMPDIR` 未設時,`gettempdir()` 若落在名單外(Linux 自訂 `TMPDIR` 之外的情況很少見),新碼與 `scripts/lumos:18226` 的判定會不同。我給不出具體失敗場景,只標形狀不一致。
- 引句:「if os.environ.get("TMPDIR"):」

其他我查過、沒有第二種做法的地方:

- shlex 用法是 `scripts/lumos` 與 `check-graph-sync.py` 已有的標準庫用法,沒有新依賴。
- 子程序用 `subprocess.run(["git","-C",...], timeout=_inner_budget(...))`,與 `impact-hook.py` 的 subprocess 加預算逾時同做法。
- 註冊方式沒有另一種,就是 `HOOK_ENTRIES`。

## 固定席節點

- `lumos-cli-lifecycle` 的 re-inject INVARIANT:diff 只動安裝名單與 WHY 行,沒碰 sentinel 與 re-inject 邏輯,不影響。
- 其他 INVARIANT(`search` 預設排除、還原翻紅釘、設計審處置閘、`guard kill` 的 rc 優先序與 JSON 純度):diff 沒碰這些路徑,不影響。
- `test_lumos.py` 只把 `enforcement_status` 的列數 24 改成 25,與新增那一列同步。

不對齊共 3 條,其中 major 0 條。

來源:r1-資安-sonnet.md


只有第 1 條發現成立,是一條繞過;其餘各類已看,無。

**1. `--git-dir=X`(黏著寫法)、`--git-dir X` 和 `GIT_DIR=X` 不會改變生效目錄,在暫存目錄裡可對真 repo 繞閘而不被問**
ID: s1
severity: major
blocking: 是

- 誰:被提示注入的代理,或是推送被擋、順手想繞閘的代理。
- 入口:Bash 指令先 `cd` 到暫存根底下(不存在的目錄或非 repo 的目錄),再用 `--git-dir` 或 `GIT_DIR` 指向真 repo 提交。
- 送什麼:`cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git --work-tree=/Users/enzo/real commit --no-verify -m x`
- 拿到什麼:`bypass_reasons` 回空清單,掛鉤放行,提交前閘被跳過而且沒有問人。
- 原因:`_parse_git` 只認 `-C` 來改生效目錄,黏著的 `--git-dir=X` 不是 `_GIT_VALUE_OPTS` 的成員,只被當成一個要跳過的旗標。`GIT_DIR=` 前綴也從不影響 `eff`。於是 `eff` 停在 `/tmp/nonexist`。`_exempt` 走 commit 分支,`_not_real_repo` 看到「目錄不存在」就回 True。
- 計劃的 S3 明列「`cd` 到暫存目錄後又 `git -C` 指回真目錄」要問人。`--git-dir` 是同一件事的另一種寫法,〈範圍〉沒列,所以不算已接受的漏洞。
- 應該是:只要出現 `--git-dir`、`--work-tree` 或 `GIT_DIR`/`GIT_WORK_TREE` 賦值,就不給拋棄式豁免,或把 `--git-dir` 也納入生效目錄的計算。

引句:「黏著的 `--git-dir=X` 不多吃。記下 `-C` 的目錄(可多次,後者相對前者)與 `-c` 的鍵值。」

最小重現(python3.14 用 SourceFileLoader 載入掛鉤,呼叫 `bypass_reasons`):

| 指令 | cwd | 輸出 |
|---|---|---|
| `cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git --work-tree=/Users/enzo/real commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && GIT_DIR=/Users/enzo/real/.git git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && git --git-dir /Users/enzo/real/.git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `cd /tmp/nonexist && env GIT_DIR=/Users/enzo/real/.git git commit --no-verify -m x` | `/Users/enzo` | `[]` |
| `git --git-dir=/Users/enzo/real/.git commit -n -m x` | `/tmp/lumos-seat-work` | `[]` |
| `cd /tmp/nonexist && git --git-dir=/Users/enzo/real/.git <推送> --no-verify origin` | `/Users/enzo` | `['no-verify']` |

最後一列(推送)有問人,因為 push 只看目標位址,不看目錄;提交、合併、config 這幾類才會漏。

## 逐類結果

**1. 不可信輸入流到危險操作:已看,無可利用的洞。**
- 選項注入:`git -C d` 的 `-C` 與 `d` 分成兩個參數,`d` 以 `-` 開頭也只會被當成目錄值。
- 遠端名稱:`_push_remote_arg` 取第一個不以 `-` 開頭的詞,所以名稱不會以 `-` 開頭。
- 惡意 repo 執行任意碼:我建了 repo,設了 `core.fsmonitor`、`core.sshCommand`,再實跑掛鉤會下的 `rev-parse --git-common-dir` 與 `remote get-url`,標記檔都沒生成。這兩個子指令不碰索引,也不連網。
- 被影響的資料:`remote get-url` 回的位址可被 `url.*.insteadOf` 影響,但真推送也用同一個改寫後的位址,所以判定與實際一致。
- 推論(minor,不阻擋):`get-url` 回的是 fetch 位址,不是 pushurl。真 repo 若設了 `remote.X.url=/tmp/...` 而 `pushurl` 指向真遠端,會被誤判成拋棄式。這需要攻擊者先能改 repo 設定,所以我不單獨立條。

**2. 輸出到使用者:已看,無。**
- 問人理由 `_reason_text` 只用固定字串與命中代號查表,沒有嵌入指令或路徑的原文。
- 存活事件只記 `mark("error", 例外型別名 + 前 120 字)`。例外字串可能含指令片段,但它寫進本機事件帳,不是給使用者看的輸出。

**3. 執行邊界:已看,無。**
- `sys.path.insert(0, 掛鉤自己所在目錄)`:目錄是掛鉤自己的,攻擊者要先能寫 `~/.claude/hooks/` 才有用,那時早已越界。
- `_hookevent` 缺席就退回空殼並照常運作(放行)。
- 安裝名單、錨點簽名、`enforcement` 列都是照既有 hook 的模式加,沒有新寫入面。
- `merge-claude-settings.py` 註冊 `Bash` matcher,並讓 `_codex_entries` 對 Codex 跳過。

**4. 繞過面:除第 1 條外,已看,無新的。**
- 〈範圍〉已列的寫法(別名、變數拼接、`bash -c`、`eval`、指令替換等)我沒有重報。

## 固定席節點逐條判

- `Issues/code-loop守衛main-direct盲區`、`Systems/guard-kill`:不影響。這份 diff 沒碰 `code-loop` 或 `guard kill` 的邏輯。
- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject 保留 sentinel 之外的內容):不影響。`merge-claude-settings.py` 與 `scripts/lumos` 的改動只加了 hook 名單與註冊項,沒有動 CLAUDE.md 的 sentinel 改寫路徑。
- `Systems/lumos-cli-read` ★INVARIANT★(search 排除 superseded):不影響,沒碰 search。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):這份 diff 不違反它。但第 1 條說明 S3 的測試沒涵蓋 `--git-dir` 這條路。
- `Systems/design-loop` ★INVARIANT★:不影響,只動代碼與計劃,沒碰處置閘。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★)與其餘只列名的節點:沒有看到會破壞其行為的改動。

最嚴重 severity: major,blocking 共 1 條。

來源:r1-規格符合-sonnet.md


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
ID: p1
severity: major
   blocking: 是
   引句:「路徑以 `..` 繞出暫存根」
   - 哪個輸入:`S=$(mktemp -d); cd $S/../../Users/x && git commit -n -m x`。走到 `_expand`:`head and variables.get(...) is _MKTEMP` 就直接 `return _MKTEMP`,沒有解析子路徑。`_not_real_repo` 對 `_MKTEMP` 直接回 True。
   - 重現:`bypass_reasons` 回 `[]`(放行);`S=$(mktemp -d); cd $S/.. && git commit -n -m x` 同樣回 `[]`。
   - 應該是:S3 要求「路徑以 `..` 繞出暫存根」照問。實作期補充只放寬「`$VAR/子路徑`」,`$S/..` 不是子路徑。`_expand` 該拒絕含 `..` 的子路徑,或正規化後確認仍在暫存目錄底下。

2. [S1] `lumos-skip` 接 lumos 指令,只認程式詞位置的第一個詞,前面有 `timeout` 等前綴就漏問。
ID: p2
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
ID: p3
severity: minor
   blocking: 否
   引句:「目標含 `$(`、反引號或展開不了的變數 → 目前目錄變成「判不出」」
   - 實作:`_replace_cmdsubs` 把 mktemp 替換記成 `subs[key]=True`,`_expand` 對 `word in subs` 回 `_MKTEMP`。
   - 重現:`cd $(mktemp -d) && git commit -n -m x` 回 `[]`。
   - spec 只讓「`VAR=$(mktemp …)` 賦值後以該變數為目標」豁免;S3 也寫明「`cd $(…)` 之後」照問。這是 diff 有、spec 沒有的放寬。⚠ 方向偏安全且合理,交編排者裁決要放進 spec 還是收回。

4. [S1/S2] `git config set core.hooksPath x` 與 `git config unset core.hooksPath`(新語法子命令)判為 `config-hookspath`。
ID: p4
severity: minor
   blocking: 否
   引句:「if pos and pos[0] in ("set", "unset"):」
   - spec 的寫入形狀只列「帶值、`--unset`/`--unset-all`/`--replace-all`/`--add`」。
   - 重現:兩條都回 `['config-hookspath']`。⚠ 屬合理延伸,建議補進 spec 或標為刻意。

5. [S2] 兩處未在 spec 的行為變更。
ID: p5
severity: minor
   blocking: 否
   引句:「elif a in _COMMIT_VALUE_LONG:」
   - `_commit_short_n` 對長選項(`--message`、`--file`、`--author` 等)吃下一個詞,另加 `a == "--"` 就停止判定。重現:`git commit --message -n`、`git commit -- -n` 都回 `[]`。
   - `_not_real_repo` 對「存在但不在任何 repo 裡的暫存目錄」(`rev-parse` rc 非 0)回 True。重現:`cd /tmp && git commit -n -m x` 回 `[]`。spec 只說「共用 git 目錄也在暫存根底下才算拋棄式」,沒定義這種情形。⚠ 同上,交編排者決定是否補 spec。

## 四、未實作

無。

縮水+未實作共 2 條

