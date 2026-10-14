severity: major

我載入掛鉤模組,用 `bypass_reasons(指令, cwd)` 實測了約 130 條正常寫法。沒有發現會讓閘整個失效的洞。有一個實作 bug 和〈範圍〉不一致:預篩漏掉〈S1〉明列要問的續行寫法。另有一組可低成本補上的缺口,和一組該在〈範圍〉承認的缺口。提交前閘只有 pre-commit 和 pre-push,下面都以這兩道為準。

1. 預篩漏掉「續行後 `-n` 頂在行首」的 `git commit`
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
