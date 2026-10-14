severity: major

我把規格組的〈做法〉與 [S1]–[S6] 逐條對照,版本取 9b8ce146(工作目錄 HEAD 是 0b3933d9,只多了派工材料提交)。我用 `SourceFileLoader` 載入掛鉤,另外呼叫 `entry()` 實際走了預篩。

## 做法逐點裁定

| 規格點 | 裁定 | 佐證 |
|---|---|---|
| 讀輸入與預篩 | 縮水,見 finding 1 | `-$'n'` 的預篩輸出 False |
| 預篩不記事件、不跑子程序 | 已實作 | `entry()` 預篩為 False 時直接 `return 0` |
| `guard`、事件名、`swallow` | 已實作 | `_guard("pretooluse-bypass-ask-hook", …, swallow=True)` |
| 逾時預算與 git 子程序上限 | 已實作 | `_remaining_budget`、`MAX_GIT_CALLS=4`、cache;沒有 1 秒下限 |
| 長度上限與字面判 | 已實作 | 引號不成對回 `['literal']`;超長走 `_literal` |
| 前處理(註解、遮罩、ANSI、續行、heredoc) | 已實作 | 詞中的 `#` 不當註解、`$(cat <<'EOF'` 內的撇號、續行切開長選項、`$'n'` 解碼,抽測皆符合 |
| 切詞切段、導向剝除 | 已實作 | `2>&1 -n` 仍命中 `commit-n`;`config core.hooksPath 2>/dev/null` 放行 |
| 找 git 指令與全域選項 | 已實作 | `timeout`、`env`、`sudo`、`!`、`if…then`、括號前綴都命中 |
| `no-verify` 與縮寫 | 已實作 | `--no-veri` 命中;merge、rebase、pull 放行 |
| `commit-n` | 已實作 | `-m -n`、`-F -n`、`-mnote`、`-uno` 不命中;`-m x -S -n` 命中 |
| `c-hookspath` | 已實作 | `-c`、`--config-env`、`GIT_CONFIG_KEY_0=…`、`export GIT_CONFIG_KEY_0` 都命中 |
| `config-hookspath` | 已實作 | 帶值、空字串、`--unset`、`set`、`--remove-section core` 命中;只給鍵或加導向放行 |
| `lumos-skip` | 已實作 | 前綴、`env`、`export`、`declare -x`、先賦值再 `export 名稱`、`+=` 命中;`export -n`、`grep` 參數放行 |
| 拋棄式判定(生效目錄、`cd` 追蹤、暫存根、git 確認) | 已實作 | 見下方 S3 |
| 拋棄式判定中 GIT_DIR 一族一律不豁免 | 縮水,見 finding 2 | push 加本機路徑時仍豁免 |
| 命中輸出與三段式 | 已實作 | 理由只用固定文字,不嵌入指令內容 |
| `decide` 與 `bypass_reasons` 拆分 | 已實作 | `main` 只解析、叫 `decide`、印出 |
| `merge-claude-settings.py` 註冊 | 已實作 | Bash matcher、`HOOK_BUDGET` 5 秒、`_codex_entries` 跳過 Bash |
| `scripts/lumos` 註冊 | 已實作 | `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`ANCHOR_FILES` 都有 |

「多做」沒發現。

## S1–S6 裁定

- **S1 縮水:** 只有 `$'…'` 這一項不成立,見 finding 1。其餘抽測都命中:前綴、跨行與續行、詞中 `#`、跳脫字元、`$(cat <<'EOF'` 帶撇號、私用區字元。
- **S2 已實作:** 引號裡的字樣、heredoc 內容、`echo` 與 `grep` 參數、吃值旗標、`HUSKY=0`、merge/rebase/pull、`git config` 讀值都放行。
- **S3 縮水:** 只有 GIT_DIR 加 push 一項不成立,見 finding 2。抽測項目的結果如下:
  - **已存在的暫存 repo:** 放行,包括 `-C`、`cd`、`config`、push 到本機 bare repo 或 `file://`、以及 `cd A && cd B &&` 這種緊接 `&&` 的條件式 `cd`。
  - **仍然問人:**
    - `mkdir`/`git init`、`$(mktemp)`;
    - `cd exp && git -C 真目錄`、`cd` 在子殼層、管線或背景裡、`cd -`、`cd ~`;
    - 符號連結指回真 repo;
    - `config --global`;
    - 網路遠端、`host:path`、沒寫遠端;
    - 同指令 `remote set-url`;
    - 暫存目錄裡的 `lumos-skip`;
    - 缺 `cwd` 或 `cwd` 不是字串。
  - **放行:** 暫存根底下、git 明說不是 repo 的目錄。
- **S4 已實作(⚠ 部分只抽測):** 引號不成對走字面判,`-$'n'` 之外的拆字寫法(`-"n"`、`--no-\⏎verify`、續行後的 `-n`)都過預篩。1000 段和 8000 個 `$(` 在 0.002 秒內判完。1500 個未閉合 heredoc 在 0.019 秒內判完。⚠ 未實測:git 卡住的 5 秒上限、非 UTF-8 輸入。
- **S5 已實作:** 註冊、timeout 5、Codex 跳過、`_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列,對照 `merge-claude-settings.py` 與 `scripts/lumos` 原文都有。
- **S6:** 人工條款,不判。

## Findings

1. 預篩把 ANSI 引號包住的旗標漏掉,[S1] 不成立。
   - 〈做法〉預篩規定「先拿掉引號與反斜線」,但沒有解 `$'…'`。
   - 輸入 `git commit -$'n' -m x`:`bypass_reasons` 會判 `['commit-n']`,但 `prefilter` 回 False,`entry()` 直接放行不問。
   - `-$'\x6e'` 結果相同。
   - [S1] 明列「`$'…'` 之後或包住旗標」必須 ask,實際整支掛鉤端到端放行。
   - 引句:「`$'…'` 之後或包住旗標、跳脫的反引號夾著指令」
   - 預篩該用與 `_Normalizer` 相同的 ANSI 解碼,或在看到 `$'` 時直接放行進分類。
   - 歸因:未判定。
   - 重現:`python3.14 t.py` 與 `t2.py` 在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`。`entry()` 的輸出是「pass」。修前版本沒有跑。

severity: major
blocking: 是

2. GIT_DIR 一族加 push 到本機暫存路徑時仍被豁免,與規格不符。
   - 〈做法〉與 [S3] 規定,整條指令任何地方設過 `GIT_DIR`、`GIT_WORK_TREE`、`GIT_COMMON_DIR` 或用了 `--git-dir`/`--work-tree`,之後的命中一律不給豁免。
   - 輸入 `GIT_DIR=/x/.git git push --no-verify /tmp` 與 `git --git-dir=/x/.git push --no-verify /tmp`:`bypass_reasons` 回 `[]`。
   - 原因:`_git` 把 `eff` 設成 `_UNKNOWN`,但 `_push_target_temp` 對絕對路徑參數不看 `eff`,仍然豁免。
   - 同樣的 commit 與 config 形狀會正確問人。
   - 影響面小:目標已存在且在暫存根底下的本機 bare repo,影響也受限。
   - 引句:「`self.gitdir_seen = True          # 賦值、export、declare、env 前綴都算`」
   - 歸因:未判定。

severity: minor
blocking: 否

縮水+未實作共 2 條

## 回答三問

1. **原問題的修復效果:** 此席只對規格,不做修前修後比較。拋棄式推論類(同指令 `mkdir`、`mktemp`、`set-url`、符號連結、`..`)修後抽測全部照問。
2. **相鄰路徑:** 同類的 push、commit、config 在 GIT_DIR 下並不一致,見 finding 2。
3. **新發現的修前修後:** finding 1、2 都沒跑修前版本,歸因標未判定。

實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`,含 `w/` 與 `h/` 副本,由編排者刪。
