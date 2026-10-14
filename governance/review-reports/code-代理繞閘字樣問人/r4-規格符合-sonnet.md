severity: minor

**逐條對照結果:已實作、縮水、未實作都是 0 條;多做 1 條,規格自己前後不一致 1 條。**

驗法:用 `SourceFileLoader` 載入固定版 465736e9 的掛鉤,呼叫 `bypass_reasons`。跑了約 200 個案例,分三輪:S1/S2、S3 拋棄式、S4 效能與進入點。掛鉤實際以子程序執行,餵 stdin。測試腳本在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/` 的 `p.py` 到 `p6.py`。

## 一、發現

1. 多做:`git remote` 把「不是 `-v`、`--verbose`、`show`、`get-url`」的子指令一律當成改了推送位址。
引句:「return bool(args) and args[0] not in ("-v", "--verbose", "show", "get-url")」
spec 〈做法〉拋棄式判定寫的是「`git remote` 的寫入子指令」。唯讀或不改 URL 的 `-vv`、`update`、`prune` 也被算進去,後面的 push 於是失去拋棄式豁免,多問一次。
重現:cwd 在只有本機遠端的暫存 repo 時,`git remote -vv; git push --no-verify origin` 回 `['no-verify']`。`remote -v` 與 `remote show origin` 則回 `[]`。
方向是多問,不是漏問,所以是 minor。
歸因:未判定。這是規格與實作的落差,兩版沒做對照。
severity: minor
blocking: 否

2. ⚠ 規格自己前後不一致,實作照〈做法〉字面做,結果跟 [S2] 的字面衝突。
引句:「lk = next((k for k in range(i, len(seg)) if os.path.basename(seg[k]) == "lumos"), None)」
〈做法〉明寫「段裡有檔名為 `lumos` 的詞」就算 lumos 指令。[S2] 卻說「`LUMOS_SKIP_*` 設在 git 與 lumos 以外的程式前……放行」。
重現:`LUMOS_SKIP_X=1 cat scripts/lumos` 和 `export LUMOS_SKIP_X=1; grep foo scripts/lumos` 都回 `['lumos-skip']`。〈做法〉那句本意是涵蓋 `python3 scripts/lumos`,但同一條規則也會把 `cat scripts/lumos` 判成 lumos 指令。
照〈做法〉判為已實作。要不要收窄由編排者裁,所以標 ⚠。
歸因:未判定。
severity: minor
blocking: 否

## 二、逐條裁定

**〈做法〉**
- 讀輸入與預篩:已實作。
  - `entry(bytes)` 進場就起算預算。
  - 先解析 JSON,再套同一套前處理,拿掉引號與反斜線,不分大小寫比三個字樣和 `-n` 短旗標。
  - 預篩自包 try/except。
  - 抽測 `--no-ver''ify`、`-$'n'`、續行加 Tab 的 `-n`、續行切開的 `--no-verify` 與 `core.hoo\⏎ksPath`,都過預篩並輸出 ask。
  - 非 UTF-8、`command` 不是字串、`ls` 都放行,沒有 traceback。
- `guard`、事件名、`swallow=True`:已實作。事件名是 `pretooluse-bypass-ask-hook`,guard 呼叫不帶備註。
- 逾時預算:已實作。
  - 與 impact-hook、dispatch-lens-hook、memory-sweep 三支的逐字複本比對,三支都一致。
  - 假 git 睡 30 秒,300 段全要查 git,整支 4.09 秒結束,結果照問。
  - `MAX_GIT_CALLS=4`,300 段實測跑了 4 次。
- 長度上限 2 萬字走字面判:已實作。10 萬字單詞回 `literal`,0 秒。
- 前處理逐項:已實作。
  - 詞首才算註解,`a#b` 不算。
  - `$(` 重開引號層,內文有撇號的 heredoc 提交訊息仍判出 `-n`。
  - 引號遮罩。
  - ANSI 引號:`\156`、`\u006e` 都解得出。
  - `$"…"`。
  - 反斜線跳脫。
  - 續行。
  - 檔案代號:`-m 1 >x -n`、`2>&1 -n`、`{fd}>x -n` 都命中。
  - `)>` 拆分:`(cd X)>/dev/null` 問人。
  - 指令本身含私用區字元也只還原成普通字。
  - heredoc:多個、`<<-`、`<<<` 不算、算式 `<<` 不算、找不到結束字就不剝。
- 切詞與切段:已實作。指令替換佔位詞、換行當分隔、括號子殼層、`$(` 與 `$((` 大量不配對。最壞形狀在 2 萬字內都低於 0.1 秒。
- 找 git:已實作。`sudo`、`!`、`time`、`nohup`、`command`、`then`、`env` 都命中。
- 全域選項:已實作。
  - `-c`、`-C`、`--config-env` 分開寫與黏著都認得。
  - `-C` 可多次。
  - `--git-dir`、`--work-tree` 會記下。
  - 縮寫 `--no-veri` 必須帶到 `--no-veri` 才認(spec 就是 `--no-veri` 開頭),`--no-ver` 不認。
- 命中規則:已實作。
  - no-verify:僅限 commit 與 push,`merge`、`rebase`、`cherry-pick` 放行。
  - commit `-n`:`-n`、`-qn`、`-nm` 命中;`-mnote`、`-m -n`、`-F -n`、`--message -n`、`-- -n`、`-Sn` 不命中。
  - c-hookspath:`-c`、`--config-env`、`GIT_CONFIG_KEY_n`、`GIT_CONFIG_PARAMETERS`、先 export 的都認得。
  - config:`--unset`、`--unset-all`、`--replace-all`、`--add`、空字串值、`set`/`unset`、`--remove-section core`、`--rename-section core` 命中。讀值(含 `2>/dev/null` 與 `> f`)放行。
  - lumos-skip:段首賦值、`env`、`+=`、`export`、`declare -x`、`typeset -x`、先賦值再 `export 名稱` 命中。`export -n` 與一般參數 `grep -n LUMOS_SKIP_X=1` 放行。
- 拋棄式判定:已實作。
  - 生效目錄的優先序對。
  - `GIT_DIR`、`GIT_WORK_TREE`、`GIT_COMMON_DIR` 的各種形式(段首、`env`、`export`、`declare -x`、`--git-dir`、`--work-tree`)都使 commit、config、push 不豁免。
  - 符號連結加 `..` 問人。
  - 暫存根、已存在、共用 git 目錄在暫存根底下、沒有網路遠端,都要同時成立才豁免。
  - 非 repo 的暫存目錄豁免。
  - 工作樹(`.git` 檔指回真 repo)問人。
  - 有網路遠端問人。
  - `--global`、`--system`、`--file` 問人。
  - push 的本機路徑、`file://`、遠端名稱查 `get-url --push` 都對。
  - 前面動過遠端設定問人。
  - `-c remote.*`、`url.*`、`GIT_CONFIG_KEY_n=remote.*` 問人。
  - `--repo` 指到網路問人,`--repo` 指到本機暫存時豁免。
  - lumos-skip 接 lumos 指令不豁免。
  - 相對路徑的 cwd 與事件 cwd 不是字串都問人。
- cd 追蹤:已實作。
  - 子殼層、管線、背景、`||`、`if !`、大括號群組在管線或背景裡、`&&` 鏈接換行、`cd -`、`cd ~`、`cd` 不帶參數、`pushd` 都照規格。
  - `cd X && true; commit` 因為 cd 本身不是條件式,仍算數。這不是規格以外的行為。
- 變數展開上限:已實作。`A=$A$A` 連續翻倍 30 次只花 0.001 秒,超過 4096 就當判不出。
- 字面判:已實作。
- 命中輸出與三段式、`decide`、`bypass_reasons`、`main`:已實作。
- `merge-claude-settings.py`:已實作。
  - 載入實測:Bash matcher、逾時 5、`--budget 5`。
  - `_codex_entries` 輸出裡沒有 `bypass-ask-hook`。
- `scripts/lumos`:已實作。
  - `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 都有。
  - `governance/anchor-baseline.json` 已含新檔。
- 存活事件修剪:已實作(`_hookevent.py` 的 `_trim` 與 `_clear_stale_trims`,修剪失敗印提示)。這兩項我只讀碼,沒實際跑。

**〈範圍〉**:都有對應。已實作的(含刻意不攔 `merge`、`rebase`、`HUSKY=0`、`LUMOS_STOP_BLOCK_OFF`)我都抽測過,放行或問人與寫的一致。承認攔不到的各項沒有被實作成「攔得到」,沒有多做。

**驗收條款**
- [S1]:已實作。約 70 個案例全部命中。
- [S2]:已實作,除上面第 2 條的規格內部衝突。
- [S3]:已實作。約 75 個案例,與我預期不符的 3 個,查證後都是我的預期寫錯,不是實作偏離:
  - `cd X && true; commit`:cd 在鏈首,本來就算數。
  - `cd X/../../../../..` 落在 `/tmp`,仍在暫存根底下。
  - `--no-ver` 縮寫:規格就只認 `--no-veri` 以上。
- [S4]:已實作。
  - 最壞形狀都在 0.1 秒內。
  - 300 段要查 git 約 0.1 秒,照問。
  - git 卡住整支 4.09 秒,小於 5 秒。
  - 預篩階段不寫事件這一點,我讀碼確認,沒另外量事件檔。
- [S5]:已實作,見上面的 merge-claude-settings 與 scripts/lumos 兩項。
- [S6]:是人工驗收條款,不屬程式實作範圍。

另有一個小觀察,沒列為 finding:`D=/tmp; D+=/x` 的 `+=` 被當成取代而不是附加,結果只會比預期多問(⚠ 規格沒提 `+=` 對變數展開的語意)。

縮水+未實作共 0 條
