severity: major

這份報告的 major 是 finding 1。我用 SourceFileLoader 載入 `scripts/hooks/claude/bypass-ask-hook.py`,直接呼叫 `bypass_reasons`,共跑約 130 條邊界輸入。臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/`。

## Finding

1. 單詞中間的 `#` 被 shlex 當成註解,後面整行(含 `--no-verify` 與接著的 git 指令)被吞掉,不問。
引句:「lex = shlex.shlex(cmd, posix=True, punctuation_chars="();<>|&\n")」
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
