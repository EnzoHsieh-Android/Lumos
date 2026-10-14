severity: major

審的是凍結快照,對照 `Word-wild-search-bypass` 的程式。實驗檔在 `/tmp/lumos-seat-work/代理繞閘字樣問人/通才-sonnet/t.py`。派工詞尾端沒有 hook 自動附加的節點,所以沒有節點可逐條判。

結論:照 spec 字面實作,會有幾條很普通的代理指令漏問(該問沒問),掛鉤本身不會壞掉讓 Bash 卡住。`guard`、`mark` 的互動大致如 spec 所說(見最後一節)。

1. 「shlex 把換行當分隔」不成立,而且分段只認程式名在行首
severity: major
blocking: 是。字面實作會讓多行指令、括號、`then` 之後、`env`/`timeout` 包起來的繞閘全部漏問,實作者會做出有洞的分類器。
- 位置:〈做法〉結構分類第一句。
引句:「用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令;每段跳過開頭的 `VAR=值`,看程式名:」
- 重現:我用 `shlex.shlex(c, posix=True, punctuation_chars=True)` 加 `whitespace_split=True` 實跑,結果如下。
  - `echo hi\nLUMOS_SKIP_X=1 git push` 切成 `['echo','hi','LUMOS_SKIP_X=1','git','push']`。換行只是空白,兩行併成一段,程式名是 `echo`,漏問。
  - `(git push --no-verify)` 的第一個詞是 `'('`,`{ git push --no-verify; }` 是 `'{'`,`if …; then git push --no-verify; fi` 的段首是 `then`,全部不是 `git`,漏問。
  - `timeout 60 git push --no-verify` 和 `env LUMOS_SKIP_X=1 git push` 的程式名是 `timeout`、`env`,漏問。
- 應該是:換行要在 shlex 之前自己切,而且要避開引號內的換行(多行 commit 訊息)。程式名前要跳過 `(`、`{`、`!`、`then/do/else`,以及 `env/time/timeout/command/sudo/nice/exec` 這類前綴。〈範圍〉只自承 `bash -c`、`eval`、變數拼接攔不到,沒列這些。
- S1 的 12 個案例都是段首就是 `git` 或 `export`,綁定測試抓不到這個洞。

2. 「用了 mktemp 就放行」的範圍沒定義,字面實作會讓真繞閘借 mktemp 通關
severity: major
blocking: 是。一個常見寫法會成為永久繞過口,而 S3 測試無論哪種實作都綠。
- 位置:〈做法〉拋棄式目標放行。
引句:「或指令裡用了 `mktemp`,該段命中不算」
- 重現:`msg=$(mktemp); printf 'wip' > $msg; git commit -F $msg --no-verify`,cwd 是真 repo。
  - 「指令裡用了 mktemp」若是整條指令只要出現就放行,這條真繞閘會被放掉。
  - 代理用 mktemp 存 commit 訊息檔是常態寫法。
- S3 的 mktemp 案例是 `d=$(mktemp -d); git -C $d … --no-verify`,放行靠的是 `$d` 的追蹤,不靠 mktemp 字樣。
- 沒有「mktemp 只用在別處、命中段落對真 repo」的反例,測試擋不住整條放行的實作。
- 應該是:mktemp 只能算在「賦值給變數、且該變數就是被 `cd`/`-C` 指到的目標」時才拋棄式,並補反例測試。

3. `git config --unset core.hooksPath` 被明文排除,但它正是拆掉所有閘的指令
severity: major
blocking: 是。spec 把最直接的關閘動作歸類成唯讀。
- 位置:〈做法〉git 分類的 `config` 那條。
引句:「`config` 子指令設定 `core.hooksPath`(有值、不是 `--get`/`--list`/`--unset`)→ 命中」
- 重現:
  - `scripts/lumos:23249` 和 `scripts/lumos:23416` 都把 `git config --unset core.hooksPath` 當成「拆閘」。
  - pre-commit 與 pre-push 閘都靠 `core.hooksPath` 指向 `scripts/hooks` 才會跑。
  - 代理在推送被擋時跑 `git config --unset core.hooksPath`,spec 字面會放行,不問人。
- 同一條還有幾個缺口:
  - 「有值」若用真值判斷,`git config core.hooksPath ""` 會漏。
  - `--unset-all`、`--replace-all` 也沒處理。
  - 旗標在鍵名前面(`git config --local core.hooksPath x`)時怎麼找鍵,spec 沒說。
- 應該是:`--unset`/`--unset-all` 針對 `core.hooksPath` 也要命中。只有 `--get`、`--list`、純讀(無值)才放行。

4. `LUMOS_SKIP_*` 只認「設在 git 前」,但有些旗標是 lumos 命令本身讀的
severity: major
blocking: 是。S2 明文把「LUMOS_SKIP_* 設在 git 以外的程式前」定成放行,與程式現況衝突。
- 位置:S2 條款與〈做法〉的 LUMOS_SKIP 規則。
引句:「或 `LUMOS_SKIP_*` 設在 git 以外的程式前(例如跑測試)時,掛鉤 應 不輸出、放行」
- 重現:`scripts/lumos:14164` 的 `LUMOS_SKIP_FIX_CHECK` 在 lumos 的修正關卡命令裡被讀,`scripts/lumos:35894` 的 `LUMOS_SKIP_NOTE_AUDIT`、`scripts/lumos:29783` 的 `LUMOS_SKIP_LINT_NEW` 也是。
  - `LUMOS_SKIP_FIX_CHECK=1 lumos code-loop …` 沒經過 git,spec 會放行。
  - 它關掉的是整道修正關卡,是 Lumos 自己的閘。
- 我沒有逐一追到是哪個子命令讀它們,實際影響範圍交編排者定。
- 應該是:程式名為 `lumos`(或 `scripts/lumos`)時,前綴 `LUMOS_SKIP_*=` 也命中。

5. heredoc 剝除的邊界沒定義,可能吞掉後面真正的指令,也可能放行被當腳本執行的內容
severity: minor
blocking: 否。需要特定寫法才發作,且 〈範圍〉已自承攔不到刻意改寫。
- 位置:〈做法〉剝掉 heredoc。
引句:「之後到結束字那一行的內容整段拿掉(heredoc 運算子本身留著)」
- 沒定義的情形:
  - `<<<`(here-string)、算術 `$((1<<2))`,以及引號內的 `<<EOF` 字樣(例如 `grep -n "<<EOF" f; git push --no-verify`)。
  - 若用 `<<WORD` 字面規則匹配且找不到結束字就刪到結尾,那些寫法會把後面的真指令一起吞掉,漏問。
  - `bash <<'EOF'`、`sh <<EOF`、`ssh host <<EOF` 的內文就是會被執行的腳本,spec 把所有 heredoc 內容一律當字面。
- 應該是:規則要寫明「結束字找不到就不剝」「`<<<` 與引號內不算」,對 `bash/sh/zsh` 的 heredoc 不剝(或另列為已知攔不到)。

6. 預篩的「同一行」可能漏掉多行指令末尾的 `-n`
severity: minor
blocking: 否。只影響 `-n` 這一條路徑,`--no-verify` 等字樣的預篩不受影響。
- 位置:〈做法〉便宜的預篩。
引句:「`commit` 之後同一行出現以 `-` 開頭且含 `n` 的短旗標」
- 重現:`git commit -m "標題\n\n內文" -n`,或用反斜線續行的 `git commit \`(換行)`-n`。
  - `commit` 與 `-n` 不在同一行,預篩若以解碼後的指令逐行比對就直接放行。
  - 後段的分類其實能判出這條,漏的是預篩。
- 另外,S4 的壞事件測試要求「事件不是 JSON 也過預篩」,等於預篩吃的是原始 stdin 文字,不是解碼後的指令。spec 的〈做法〉沒有明講預篩吃哪個。
- 應該是:拿掉「同一行」限制,並寫明預篩吃原始 stdin。

7. 全域選項清單是封閉的
severity: minor
blocking: 否。只影響帶全域選項的 commit/push,頻率低。
- 位置:〈做法〉git 分類。
引句:「跳過全域選項(`-c 鍵=值`、`-C 目錄`、`--git-dir`、`--work-tree`)找到子指令」
- 重現:`git --no-pager commit -n`、`git -p push --no-verify`、`git --bare …`、`git --exec-path=… push --no-verify`。這些選項不在清單裡,子指令被判成 `--no-pager`,漏問。
- 另外,`--git-dir=X`(黏著)與 `--git-dir X`(分開)兩種寫法 spec 沒寫處理方式。
- 應該是:任何以 `-` 開頭的詞都跳過(吃值的 `-c`、`-C`、`--git-dir`、`--work-tree`、`--namespace` 再多吃一個詞)。

8. 拋棄式目標追蹤沒說相對路徑與狀態範圍
severity: minor
blocking: 否。誤判方向有限,代價是少數誤問或漏問。
- 位置:〈做法〉拋棄式目標放行。
引句:「追蹤段落中的 `cd <目錄>` 與 `git -C <目錄>`(展開同一條指令裡先賦值的變數)」
- 沒定義的情形:
  - `cd /tmp/x && cd repo && git commit --no-verify`:相對的 `cd repo` 要接在上一個目錄後面,規則沒寫,字面實作可能判成非拋棄式(誤問)。
  - `git -C . …`、`git -C ../x …` 同理。
  - `cd ~/…`、`cd -`、`cd $(…)` 怎麼算沒寫。
  - `(cd /tmp/x && …); git push --no-verify` 的子殼層範圍沒寫:`cd` 狀態若外漏,第二段會被誤放行。
- 另外,「`$TMPDIR` 底下」指的是掛鉤程序的環境值,還是指令裡字面的 `$TMPDIR/…`,也沒說。
- 應該是:規則寫明相對路徑以追蹤中的目錄解析、`~`/`cd -`/`$(…)` 視為未知(非拋棄式),子殼層括號內的 `cd` 不外漏。

9. 驗收測試的缺口,以及兩處與程式不符的小宣稱
severity: minor
blocking: 否。不改也不會做出壞系統,但綠燈蓋不到下列行為。
- 位置:S1–S5 綁的 `t_bypass_ask_*`,在 `scripts/test_lumos.py` 約第 40982 至 41139 行。
- 測試缺口(照綠但行為可能錯):
  - 沒有「commit 訊息本身引號內含 `--no-verify` 或 `hookspath`」的反例,例如 `git commit -m "docs: 說明 --no-verify 的風險"`。這個功能自己的提交訊息就會這樣寫。
  - 規則寫「後面有 `--no-verify`」,沒說是整詞相等還是子字串,而這類訊息會過預篩,是最容易誤問的情形。
  - 沒有 mktemp 反例(見 finding 2)。
  - 沒有 `git config --unset` 案例(見 finding 3)。
  - 10 萬字的測試只用「一個 10 萬字元的單詞」。我實測 `shlex` 單獨處理它就要 0.27 秒,加上預篩、heredoc 規則後,離 0.5 秒門檻的餘裕很小。
- 與程式現況不符的宣稱:
  - 〈做法〉說近期沒命中時 enforcement 顯示 unknown:
    引句:「近期沒命中過時它照既有規則顯示 unknown」
  - 實際:事件檔存在但七天內無成功事件時,`_hook_recent_ok` 回 `stale`(`scripts/lumos:23352`),只有事件檔不存在才回 unknown。
  - `enforcement_summary` 把 `stale` 與 `unknown` 同樣排出分母(`scripts/lumos:27497`),所以不會假紅,措辭不精確但無害。

已讀、無 finding 的部分:
- `_hookevent.guard`/`mark` 互動:`guard` 只在 `main()` 正常回來才記一筆事件,`mark("ok","ask:…")` 能帶出 note,與 spec 描述一致。
- 預篩放在 `guard` 之外,避免每條 Bash 都跑 `git rev-parse` 並寫事件,理由成立。
- `swallow=True` 下例外會被記成 error 並回 0。
- 壞 JSON 要記 error,前提是預篩吃原始 stdin(見 finding 6)。
- S5:`_codex_entries` 目前把 Bash 的 PreToolUse 原樣寫過去,所以「Codex 要跳過」需要新增分支,spec 這點是對的。
- 測試 `scripts/test_lumos.py:36231` 已改成 25 列。
- 新掛鉤的 ask 與 `mods/claude/lumos-guard` 的 deny 同時出現時,我預期 deny 優先,這點沒有實際驗證。

最嚴重 severity:major;blocking:是共 4 條(finding 1、2、3、4)。
