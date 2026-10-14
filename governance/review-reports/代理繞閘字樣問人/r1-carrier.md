severity: major

彙總載體,非新增審查席。33 條由四份原報告逐字彙整,只在每條 severity 行前加 ID 行,severity 與引句不變。


來源:r1-通才-sonnet.md


審的是凍結快照,對照 `Word-wild-search-bypass` 的程式。實驗檔在 `/tmp/lumos-seat-work/代理繞閘字樣問人/通才-sonnet/t.py`。派工詞尾端沒有 hook 自動附加的節點,所以沒有節點可逐條判。

結論:照 spec 字面實作,會有幾條很普通的代理指令漏問(該問沒問),掛鉤本身不會壞掉讓 Bash 卡住。`guard`、`mark` 的互動大致如 spec 所說(見最後一節)。

1. 「shlex 把換行當分隔」不成立,而且分段只認程式名在行首
ID: t1
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
ID: t2
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
ID: t3
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
ID: t4
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
ID: t5
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
ID: t6
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
ID: t7
severity: minor
blocking: 否。只影響帶全域選項的 commit/push,頻率低。
- 位置:〈做法〉git 分類。
引句:「跳過全域選項(`-c 鍵=值`、`-C 目錄`、`--git-dir`、`--work-tree`)找到子指令」
- 重現:`git --no-pager commit -n`、`git -p push --no-verify`、`git --bare …`、`git --exec-path=… push --no-verify`。這些選項不在清單裡,子指令被判成 `--no-pager`,漏問。
- 另外,`--git-dir=X`(黏著)與 `--git-dir X`(分開)兩種寫法 spec 沒寫處理方式。
- 應該是:任何以 `-` 開頭的詞都跳過(吃值的 `-c`、`-C`、`--git-dir`、`--work-tree`、`--namespace` 再多吃一個詞)。

8. 拋棄式目標追蹤沒說相對路徑與狀態範圍
ID: t8
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
ID: t9
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

來源:r1-邊界-sonnet.md


審查對象是凍結快照 r1-snapshot.md。對照的程式碼是 Word-wild-search-bypass(HEAD de48ddd9)。以下所有重現都是實際跑過的:shlex 實測、本機事件帳 28152 條 Bash 指令、既有測試原始碼。

## 派工詞尾端的掛鉤節點
派工詞尾端沒有任何自動附加的節點,所以沒有節點可判。

## Findings

**1. mktemp 例外是整條指令通吃,真繞閘會被放行**
- spec 段落:〈做法〉拋棄式目標放行,以及 S3。
引句:「或指令裡用了 `mktemp`,該段命中不算」
ID: b1
severity: major
blocking: 是。照字面實作,守衛會在常見的「訊息檔用 mktemp」寫法上整個失效。
- S3 的測試案例 `d=$(mktemp -d); git -C $d init -q; git -C $d commit -qm x --no-verify` 只有靠「mktemp 出現在同一條指令的別段」才會放行。因為 `-C $d` 沒有被展開,`$d` 是字面。所以「該段」實際上必須做成整條指令。
- 重現:`msg=$(mktemp) && echo x > $msg && git commit -F $msg --no-verify`,event cwd 是真 repo。照字面實作,這條指令有 mktemp,整條放行,沒有問人。應該是問人。
- 更窄的做法是只追蹤 `VAR=$(mktemp…)` 賦值,而且只讓以該變數為目標的 `cd` / `-C` 放行。這樣 S3 第 4 案仍然通過。

**2. 本使用者的 /tmp 底下有真工作副本,而且會對真遠端推送**
- spec 段落:〈量測〉與〈做法〉拋棄式目標。
引句:「再排除拋棄式目標(`cd` 或 `git -C` 指到 `/tmp/`、`/private/tmp/`、`/var/folders/`,或指令裡用 `mktemp`):剩 4 次」
ID: b2
severity: major
blocking: 是。「暫存目錄等於拋棄式」這個前提在本使用者的實際工作流程裡不成立。
- 查本機事件帳(`/Users/enzo/harness/lumos-toolchain/governance/runtime/events`),同一週內有 5 次這樣的指令:`cd /tmp/lumos-readme-oct-audit && git push origin HEAD:refs/heads/audit/...`。這是 /tmp 底下的工作副本,對真遠端推送,推送前閘是真的在跑。
- 另有一次 `cd /private/tmp/claude-501/.../scratchpad/r2-seat-正確性/w && git push`。
- 照 S3,這些目錄裡的 `git push --no-verify` 一律放行。但這正是掛鉤要防的事。
- 〈量測〉的「剩 4 次」是把這類路徑全當拋棄式排除之後的數字。它沒有檢查「被排除的 38 減 4 次」裡有沒有對真遠端的推送。
- 這個例外至少要區分 commit 與 push。例如 push 時看目標 repo 有沒有網路遠端,有就不放行。

**3. `git config --unset core.hooksPath` 被明文排除,但它會關掉閘**
- spec 段落:〈做法〉git 分支的 config 規則。
引句:「`config` 子指令設定 `core.hooksPath`(有值、不是 `--get`/`--list`/`--unset`)→ 命中」
ID: b3
severity: major
blocking: 是。排除清單裡有一項是繞閘本身。
- 〈範圍〉自己寫了推送前閘與提交前閘走 `core.hooksPath` 指向的 `scripts/hooks`。
- `git config --unset core.hooksPath`(或 `--local --unset`)之後,git 退回預設的 `.git/hooks`,Lumos 的 pre-commit 和 pre-push 就不跑了。效果與 `-c core.hooksPath=/dev/null` 相同。
- 重現:`git config --local --unset core.hooksPath && git commit -m x`。照 spec 不問人,應該問。
- 反方向還有一個問題:`git config core.hooksPath scripts/hooks` 是 Lumos 自己安裝時設的值。spec 只看「有沒有值」,不看值指到哪,所以重新設回正確值也會問人。

**4. 「忽略 --budget」與既有的逾時預算守衛測試衝突**
- spec 段落:〈做法〉掛鉤檔與 `merge-claude-settings.py` 兩條。
引句:「命令列參數(安裝時附的 `--budget 5`)一律忽略、不報錯。」
ID: b4
severity: major
blocking: 是。照 spec 做,既有測試會紅。
- spec 要在 `HOOK_BUDGET` 加 `"bypass-ask-hook.py": 5`。測試 `t_hook_inner_timeout_always_below_outer` 會掃表裡每個存在的 hook 檔,並呼叫 `mod._inner_budget(default=...)`。
file: `scripts/test_lumos.py:17916`
- 一支不認 `--budget`、也沒有 `_inner_budget` 的掛鉤,會在這裡丟 AttributeError。
- 該測試還要求用掉 0.35 秒後的第二次呼叫回傳值變小,並要求已耗加下次上限不超過天花板。
- 另有「複本不准漂」守衛,要求各 hook 的 `_BUDGET_RATIO … return max(_BUDGET_FLOOR,…)` 區塊逐字相同。
file: `scripts/test_lumos.py:17961`
- 照 spec 二選一都不通:不放進 `HOOK_BUDGET`,就違反「註冊表不准裸數字 timeout」的守衛;放進去,就得抄一份預算區塊進掛鉤。spec 完全沒提這件事。

**5. 存活事件名稱與 enforcement 列名對不上,而且 spec 說的 unknown 不是程式的行為**
- spec 段落:〈做法〉guard 與 enforcement 兩處。
引句:「才進 `guard("bypass-ask-hook", __file__, main, swallow=True)`」
引句:「近期沒命中過時它照既有規則顯示 unknown」
ID: b5
severity: major
blocking: 是。這支掛鉤的「活著沒」列永遠不會是 active,實際行為還和 spec 的描述不符。
- `enforcement_status` 比對事件時用「列名」當 hook 名稱。列名是 `pretooluse-bypass-ask-hook`。
file: `scripts/lumos:27232`
- 比對條件是事件的 hook 欄位等於列名,而且 kind 是 ok。
file: `scripts/lumos:23333`
- 既有五支掛鉤的 guard 名稱都與列名一致,例如 `"pretooluse-impact-hook"`。spec 寫的 `"bypass-ask-hook"` 不一致,測試也把它釘死。
file: `scripts/test_lumos.py:41089`
- 後果:事件永遠對不上列名,這一列永遠不是 active。
- 行為與 spec 不同:事件檔存在但 7 天內沒有符合的 ok 事件時,`_hook_recent_ok` 回 stale,不是 unknown。只有事件檔不存在才是 unknown。
- stale 同樣被排出分母(`enforcement_summary`),所以不會假紅。但「列不為 active」這件事不是 spec 描述的路徑。
- 〈實務隱患〉說「會記 error 事件讓 `lumos enforcement` 看得到」也站不住。`_hook_recent_ok` 只認 ok,error 事件不會出現在這一列。
- 需要裁定:guard 名稱要不要改成 `pretooluse-bypass-ask-hook`,並同步改 S4 測試。

**6. 算漏了 anchor-baseline.json**
- spec 段落:〈做法〉scripts/lumos 的最後一條。
引句:「`_VENDORED_TREE_FILES` 與 `ANCHOR_FILES` 加 `scripts/hooks/claude/bypass-ask-hook.py`」
ID: b6
severity: minor
blocking: 否。測試一跑就紅,實作者馬上會發現,不會做錯決定。
- `ANCHOR_FILES` 的鍵集合必須等於 `governance/anchor-baseline.json` 的鍵集合。
file: `scripts/test_lumos.py:40206`
- 另有一個測試要求「版控裡每個 hook 檔都在錨點清單」。
- 所以還要做 `lumos anchor approve` 把新檔的雜湊簽進 baseline。spec 的步驟清單漏了這一步。

**7. shlex 不會把換行當分隔,逗號合併的複合標點也沒處理**
- spec 段落:〈做法〉結構分類。
引句:「用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令」
ID: b7
severity: major
blocking: 是。多行指令是代理最常見的寫法,照 spec 實作會整個漏掉。
- 實測 `shlex.shlex(s, posix=True, punctuation_chars=True)`:
  - `git status\ngit push --no-verify` 的 tokens 是 `['git','status','git','push','--no-verify']`。換行被當空白。第一個 token 之後的子指令是 `status`,後面的真 push 被吞進同一段,所以不問人。應該問。
  - `git push \<換行> --no-verify` 的 tokens 有 `'\n'` 殘留。
  - `( cd /tmp/x && … ); git push --no-verify` 的 tokens 含 `');'`,是括號與分號合併成一個 token。若分段只認單獨的 `;`,這個分隔會漏掉。同理還有 `2>&1` 產生的 `'>&'`。
- 若先把換行替換成 `;` 再交給 shlex,會把引號內的多行訊息切碎,也會把 `\<換行>` 續行切壞。換行必須只在引號外切。
- spec 要明寫:換行只在引號外是分隔;`);`、`&&`、`||`、`|&` 等複合標點 token 怎麼分段;反斜線續行怎麼處理。S1 到 S4 的測試沒有任何多行案例(`cat <<EOF` 那幾個是在 heredoc 剝除之後才與換行有關)。

**8. 路徑與 cd 的語意只列了詞,沒定義**
- spec 段落:〈做法〉拋棄式目標放行。
引句:「追蹤段落中的 `cd <目錄>` 與 `git -C <目錄>`(展開同一條指令裡先賦值的變數)」
引句:「沒有任何 `cd`/`-C` 時用事件的 `cwd` 判。」
ID: b8
severity: major
blocking: 是。S3 只測了「前面 cd 到暫存目錄、後面 cd 到真目錄」這一種順序,其餘都留給實作者猜,而且猜錯的方向都是放行。
- 子 shell 作用域:`( cd /tmp/x && git commit -qn -m a ); git push --no-verify`。子 shell 結束後 cwd 回到真 repo,第二段應該問。若實作把「最後一次 cd」當全域狀態,就會誤放行。
- `cd -`、`cd ~`、`cd`(無參數)、`pushd` / `popd`、相對路徑如 `cd ../../tmp/x`:全部沒定義。`cd /tmp/x; …; cd -; git push --no-verify` 中,`cd -` 是回到真 repo。
- `git -C` 的作用域:它是單一段的,不該延續到下一段。S3 沒有這個案例。
- 路徑沒有正規化:`cd /tmp/../Users/enzo/repo` 的字面開頭是 `/tmp/`。
- 符號連結:`/tmp/r` 是指到真 repo 的連結時,字面看是拋棄式。
- `$TMPDIR` 的取得沒說。spec 只說「展開同一條指令裡先賦值的變數」,沒說 `$TMPDIR` 從哪來。兩種自然寫法都有洞:
  - 讀環境變數,沒設時取空字串,前綴比對 `startswith('')` 恆真,等於所有路徑都放行。
  - 帶結尾斜線(macOS 的 `TMPDIR` 就是 `/var/folders/.../T/`)再接 `/`,會成 `//`,比對不到。
- event 的 `cwd` 缺欄位、為 null、為非字串時怎麼判,也沒說。

**9. heredoc 剝除規則有幾個邊界沒定義,自然的寫法會漏判或誤判**
- spec 段落:〈做法〉剝掉 heredoc。
引句:「之後到結束字那一行的內容整段拿掉(heredoc 運算子本身留著)」
ID: b9
severity: minor
blocking: 否。每一種都是少見的輸入,方向有放行也有誤問,但沒有一種是常態。
- 我寫了一個最直接的 regex 實作對照(`/tmp/lumos-seat-work/代理繞閘字樣問人/邊界-sonnet/h.py`),結果如下:
  - here-string 被當 heredoc:`cat <<< "x"\n<真正的繞閘指令>\nx\n` 剝完剩 `cat <<<x`,後面的真指令被一起吞掉,漏問。
  - 引號內的 `<<`:`echo "<<EOF"\n<真正的繞閘指令>\nEOF\n` 同樣被吞掉,漏問。因為剝除在 shlex 之前,regex 不知道哪個 `<<` 在引號裡。
  - 同一行兩個 heredoc:`cat <<A <<B`,第二個 body 沒被剝,body 裡的繞閘字樣被當指令誤問。
  - 沒結束字的 heredoc:body 留著被當指令,也會誤問。spec 沒說這時要剝到結尾還是不剝。
  - 非 `<<-` 的 heredoc 結束字能不能縮排:bash 規定 `<<EOF` 的結束字必須在行首,只有 `<<-` 吃 Tab。spec 的 S2 測試只涵蓋 `<<-` 加 Tab。
- 需要定義:`<<<` 不算 heredoc;引號內的 `<<` 不算;同行多個 heredoc 依序配對;沒結束字時的處理。

**10. 〈範圍〉沒列的漏網寫法**
- spec 段落:〈做法〉結構分類。
引句:「每段跳過開頭的 `VAR=值`,看程式名」
ID: b10
severity: minor
blocking: 否。〈範圍〉已聲明這是防順手、不防有心。但下列寫法不是有心改寫,而且〈範圍〉沒列出來,實作者不會知道這是已知漏洞。
- 實測 tokens:`if ! git push; then git push --no-verify; fi` 裡,第二段開頭是 `then`,不是 `git`。`do`、`{`、`!` 開頭同理。
- `timeout 60 git push --no-verify`、`env LUMOS_SKIP_X=1 git push`、`time git …`、`command git …`、`nohup`、`exec`:程式名不是 `git`。
- 我在臨時 repo 實測:`--no-verif`(git 接受唯一前綴縮寫)在 pre-commit 失敗的情況下 rc=0,等於繞過成功。但預篩只看 `--no-verify` 字面,直接退出。
- 建議在〈範圍〉補一行,或把這幾個常見前綴(`then`/`do`/`{`/`!`/`env`/`time`/`timeout`/`command`/`nohup`/`exec`)納入跳過清單。

**11. 「10 萬字 0.5 秒」在 shlex 下是邊緣的**
- spec 段落:S4。
引句:「10 萬字的指令 應 在 0.5 秒內判完」
ID: b11
severity: major
blocking: 是。驗收條件和設計手段之間沒有銜接,spec 也沒有定上限策略。
- 實測(Python 3.14.6,本機):
  - 單一 10 萬字元 token(與測試 `"echo " + "x"*100000 + " && git push --no-verify"` 同形):shlex 本身要 0.24 到 0.26 秒。
  - 20 萬字元:0.77 秒。超線性。
  - 10 萬字加跳脫字元:0.32 到 0.34 秒。
  - 多 token 的 10 萬字(3 萬 3 千個詞,或 5 萬個 `a;`)只要 0.02 到 0.06 秒。
- 測試只測了最壞形狀,而且已經用掉一半預算。再加上預篩、heredoc 剝除、事件寫入,以及本 repo 測試會多分片同時跑(`test_lumos.py --shard`),在慢一點的 CI 跑 0.5 秒很可能翻紅。
- 一支每次 Bash 都跑的掛鉤,遇到超長指令還有 5 秒的外層逾時。逾時被砍是 fail-open,不是壞事,但延遲是真的。
- 建議 spec 明定一個長度上限(例如超過 N 字元就跳過 shlex、走字面退回判),並把 0.5 秒的測試設在那個上限的兩倍以下。
- 我另測了 3000 個未結束的 `<<EOF` 配懶惰量詞的 regex:1.07 秒,也是超線性。這是實作選擇,但 spec 沒有提醒要避免。

**12. 預篩的規模數字不對,輸入來源也有兩個含糊處**
- spec 段落:〈做法〉預篩,以及〈實務隱患〉存活事件檔。
引句:「`commit` 之後同一行出現以 `-` 開頭且含 `n` 的短旗標」
引句:「量測裡過預篩的指令一週約 175 次量級,不會擠掉其他掛鉤的紀錄」
ID: b12
severity: minor
blocking: 否。事件檔大概擠得下,實作時測試也會顯出問題。
- 我用同一本事件帳(約一週、28152 條 Bash 指令)照預篩字面統計:
  - 字面三詞(`--no-verify`、`hookspath`、`LUMOS_SKIP_`):268 次。
  - 再加「`commit` 之後同一行出現含 `n` 的單橫線旗標」:多出 124 次。多數是 `sed -n … scripts/hooks/pre-commit; sed -n …`、`grep -n … pre-commit` 這類。路徑名裡的 `pre-commit` 也含 `commit`。
  - 若「短旗標」連 `--amend`、`--no-edit` 這種雙橫線也算,再多 218 次。
- 所以實際約 392 次(最寬鬆讀法約 610 次),不是 175 次。要在 `commit` 前加 `git` 的限定,才不會被路徑名誤中。
- 預篩對象是原始 stdin 文字還是剖析後的 command 欄,spec 說「指令裡」。但 S4 測試用壞 JSON 加繞閘字樣(`{壞掉的事件 git push --no-verify`)要求記一筆 error 事件。壞 JSON 取不到 command 欄,所以只能是對原始文字預篩。兩邊要統一。
- 若是對原始 JSON 文字預篩,「同一行」就變成整個事件,與 command 內的單行語意不同。
- 預篩在 `guard` 之外會先讀走 stdin。而 spec 又說 `main` 要「讀 stdin」。stdin 是管道,不能讀第二次。實作要把預篩已讀的文字傳進去。
- 預篩在 `guard` 之外,就沒有 fail-open 保護。stdin 解碼錯誤(Windows 非 UTF-8 locale 的中文指令)、command 不是字串(清單、數字)、tool_input 不是物件,都會變成未捕捉例外,rc 1 加 traceback,每條 Bash 都吵。
- 壞事件放行這件事 S4 只在 `guard` 之內測。

## 已讀、無 finding 的項目
- `_codex_entries` 跳過 `matcher: "Bash"`:既有 Codex 測試(五支都註冊、沒有 Agent matcher)不會因此紅。只要在迴圈裡 `continue`,不影響其他條目。
- `_GLOBAL_CLAUDE_HOOKS` 加檔名:註冊與複製白名單的雙向對稱守衛(`registered <= copied` 與 `copied <= registered`)天然滿足。
- `_VENDORED_TREE_FILES` 加檔名:逐檔比對測試會要求加,方向正確。
- `enforcement_status` 加一列、測試 25 列:測試已經改成 25。
- `_GLOBAL_HOOKS` 與 `_GLOBAL_CLAUDE_HOOKS` 是同一個 tuple,Codex 也會把這個檔複製到 `~/.codex/hooks/`,但不註冊。沒有測試比對 Codex 目錄裡的檔案清單等於註冊清單,所以不會紅。
- 沒找到第二份名單:除了上述檔案,`memory-sweep.py` 等名字只出現在 `governance/anchor-baseline.json`(見 finding 6)和歷史審查卷證。

## 實務隱患(逐類)
- 效能:每條 Bash 多一次 Python 啟動。預篩在 guard 之外是對的,但過了預篩的規模被低估(finding 12),shlex 對單一長 token 超線性(finding 11)。
- 共用檔:存活事件檔 512KB 上限。實際過預篩約 392 次一週,加上 impact-hook 每次 Edit 都寫,不會擠掉其他紀錄,但 spec 的論證數字是錯的。
- 相容:Windows 路徑與 `\` 在 posix shlex 下被吃掉,結果是不認得暫存目錄,偏向問人,無害。Windows 非 UTF-8 stdin 見 finding 12。
- 無人值守:`claude -p` 或排程迴圈(如記憶裡的每天 09:30 自主迭代)遇到 `ask`,沒有人可以按允許,會停在原地。spec 的實測只證明「ask 會讓指令不執行」,沒有說這些迴圈裡該怎麼處理,也沒有列入〈實務隱患〉。
- 注入:理由文字若夾帶原指令片段,可被偽造成像系統話的內容。spec 說理由是三段式、命中理由是代號,若維持固定詞彙就沒事。
- 金流、對外送出、正式環境不可逆:無,原因同 spec 所述(只讀本機事件,只回 ask)。

## 總結
最嚴重 severity: major。blocking 共 7 條(finding 1、2、3、4、5、7、8、11 中,1、2、3、4、5、7、8、11 為 blocking 是,實為 8 條)。

更正:blocking 為「是」的是 finding 1、2、3、4、5、7、8、11,共 8 條;blocking 為「否」的是 finding 6、9、10、12,共 4 條。

來源:r1-資安-sonnet.md


我讀完整份 spec 和 `_hookevent.py`、五支 `t_bypass_ask_*` 測試。官方文件我只讀了 hooks 頁前 100000 字。下面三段是我直接查證到的事實,其餘各條是對 spec 與測試字面的推論,我沒有跑實驗。

- 官方文件有寫:掛鉤逾時「doesn't block the tool call」,輸出 JSON 無效或掛鉤丟例外是 non-blocking,動作照常執行。
- 官方文件沒寫:`ask` 在略過權限模式、自動接受模式下的語意。我看過的那段沒有寫,permissions 頁我沒查。
- 沙箱擋下了我跑 shlex 的實驗(同一行含 git 與 push),所以下面第 2 到 5 條只依 spec 字面和 `test_lumos.py` 裡的測試案例推論,我沒有執行驗證。

1. 拋棄式目標判定沒有規定多個目標同時出現時以誰為準
ID: s1
severity: major
blocking: 是。不定義優先序,實作者可能照字面「看到暫存路徑就放行」,讓這道判定被一個 `cd /tmp` 騙過。
- 位置:〈做法〉的「拋棄式目標放行」。
引句:「追蹤段落中的 `cd <目錄>` 與 `git -C <目錄>`(展開同一條指令裡先賦值的變數),目標落在」
- 問題:這句沒說同一條指令有多個目標時以哪個為準,也沒說 `cd` 的效果是否隨 `&&`、`;`、子殼層結束。
- 重現 A:`cd /tmp && git -C ~/repo push --no-verify`。`-C` 指向真 repo,但前面有 `cd /tmp`。照「落在暫存目錄就放行」的字面,實作者可能放行,實際是對真 repo 推送。
- 重現 B:`cd /tmp; cd ~/repo; git push --no-verify`。最後有效的是第二個 `cd`,但實作若只記第一個或任一個暫存目標,就會放行。
- 重現 C:`(cd /tmp/x && true); git push --no-verify`。子殼層裡的 `cd` 不影響外面,實際目錄是事件的 `cwd`。
- 重現 D:`cd /tmp/x && cd - && git push --no-verify`,以及 `cd` 不帶參數、`cd $HOME`、`cd ~` 這類目標展開。
- 應該是:拋棄式要求「該段實際生效的目錄」整體落在暫存目錄。`-C` 優先於 `cd`,後一個 `cd` 覆蓋前一個,子殼層與 `-` 無法判定就當非拋棄式。
- S3 的 `mixed` 測試只涵蓋「前段暫存、後段真 repo、各自獨立一段」,沒涵蓋上述同一段內的衝突。

2. 判斷拋棄式只看本機目錄,不看推送目的地
ID: s2
severity: major
blocking: 是。會讓「在暫存 clone 裡推真遠端」一律放行,而 spec 的 RETIRE-IF 與量測都沒把這種形狀算進去。
- 位置:〈做法〉的「拋棄式目標放行」,以及〈量測〉的排除步驟。
引句:「再排除拋棄式目標(`cd` 或 `git -C` 指到 `/tmp/`、`/private/tmp/`、`/var/folders/`,或指令裡用 `mktemp`)」
- 問題:代理在 `/tmp` 克隆真專案、或用 `git worktree add /tmp/wt` 開工作樹,是常見做法。
- 重現:`git clone git@github.com:org/real.git /tmp/c && cd /tmp/c && git commit -qm x --no-verify && git push --no-verify`。照 spec 全部放行,但最後一步把繞過閘的提交推上真遠端。
- 重現 2:`/tmp/wt` 是真 repo 的 worktree,共用 `.git` 與 `core.hooksPath` 設定。
- 應該是:至少在 spec 的〈範圍〉承認這條,或把 `push` 命中改成「遠端不是本機路徑時照問」。
- 同類:`mktemp` 放行只看指令裡有 `mktemp` 這個詞,沒檢查它的結果真的被用作目標。`mktemp -d >/dev/null; git push --no-verify` 照字面會放行。

3. 順手形狀:程式名前綴、包裝指令、子殼層沒有被列入攔不到
ID: s3
severity: major
blocking: 是。這些都是不需要刻意混淆、代理正常會寫出來的形狀,spec 沒列進〈範圍〉的攔不到清單,測試也只涵蓋 `/usr/bin/git`。
- 位置:〈做法〉的「結構分類」。
引句:「每段跳過開頭的 `VAR=值`,看程式名:」
- 重現,每條照 spec 字面程式名都不是 `git`,所以不命中:
  - `env LUMOS_SKIP_X=1 git push`(`env` 前綴是 `VAR=值` 的常見替代寫法)
  - `timeout 600 git push --no-verify`、`time git push --no-verify`、`nohup git push --no-verify`、`command git push --no-verify`
  - `( cd ~/repo && git push --no-verify )`(第一個詞是 `(`,切段規則只列 `; & | 換行`)
  - `if ...; then git push --no-verify; fi`(段首詞是 `then`)
  - `git --no-pager commit -n -m x`(`--no-pager`、`-p`、`--no-optional-locks` 不在「跳過全域選項」清單 `-c`、`-C`、`--git-dir`、`--work-tree`,子指令可能被誤認)
  - `git commit --no-verif`(git 接受長選項的唯一前綴縮寫)
- 應該是:程式名解析要跳過 `env`、`timeout [秒數]`、`time`、`nohup`、`command`、`exec`、`nice` 等包裝詞,並把 `( ) { } then do` 當分隔符,全域選項清單補 `--no-pager` 等不帶值的旗標。不做的話,把它們明列進〈範圍〉攔不到的清單。

4. heredoc 剝除對沒有結束字的 `<<WORD` 行為沒定義
ID: s4
severity: minor
blocking: 否。需要字面裡有 `<<WORD`,不是主要路徑,但落在 fail-open 方向。
- 位置:〈做法〉的「剝掉 heredoc」。
引句:「把 `<<WORD`、`<<-WORD`、`<<'WORD'`、`<<"WORD"` 之後到結束字那一行的內容整段拿掉(heredoc 運算子本身留著)」
- 問題:這句沒說運算子在引號裡、在 `$((1<<n))` 這類算式裡、或後面找不到結束字時怎麼辦。
- 重現:`git commit -m "doc: explain <<EOF handling" --no-verify`。若實作用正規式找 `<<EOF`、找不到結束字就剝到結尾,後面真正的 `--no-verify` 被一起拿掉,放行。
- 應該是:只剝未被引號包住、且之後真的有結束字那一行的 heredoc。找不到結束字就不剝(寧可多問)。S2 的 heredoc 案例都有結束字,沒涵蓋這條。

5. 掛鉤自己壞掉或逾時的放行,spec 只承認「例外」,沒承認逾時與可被觸發
ID: s5
severity: minor
blocking: 否。〈實務隱患〉明講這不是安全邊界,但它只講了丟例外,沒講逾時也是同一個放行路徑。
- 位置:〈實務隱患〉的「自我治理」。
引句:「這是守衛本身;掛鉤壞掉時放行(問人層不是安全邊界),但會記 error 事件讓 `lumos enforcement` 看得到。」
- 問題:官方文件寫逾時掛鉤不擋工具呼叫、照走正常權限流程(我查證到的)。所以「記 error 事件」只覆蓋丟例外,逾時時 Python 被砍,`guard` 根本寫不出事件。
- 重現:指令長且結構特殊,讓切段或變數展開超過 5 秒。S4 的 10 萬字測試只測 `echo xxx… && git push --no-verify` 這一種形狀,沒測大量 `;` 分段、深層引號、很多變數賦值。
- 應該是:〈實務隱患〉補一句「逾時同樣放行且不留事件」,並加最壞形狀的效能測試。
- 補充:官方文件另有 `onFailure: "block"` 可讓失敗變成阻擋(需 Claude Code v2.1.295 以上),spec 沒討論要不要用。

6. 略過權限模式下 `ask` 的語意,spec 的實測段說對了範圍,但 S6 的回退條件不夠
ID: s6
severity: minor
blocking: 否。spec 已誠實標明「互動模式未驗」,並用 [manual:] 條款兜底。
- 位置:〈做法〉末段的實測,與 S6。
- 我查證的結果:官方 hooks 頁沒有寫 `ask` 在 bypassPermissions、acceptEdits、auto 模式的行為,與 spec 自述「官方文件沒寫」一致。
- 缺口:S6 的回退是「沒跳就改成回 deny」,而 deny 對使用者是硬擋,與整份 spec「寧可漏問、不訓練人反射按允許」的取捨相反,而且 spec 沒說改 deny 要重過 RETIRE-IF。
- 應該是:S6 的回退條款補一句改 deny 後的誤擋處理(例如保留 `LUMOS_BYPASS_ASK_OFF` 之類的人工放行路徑,或說明使用者怎麼臨時關掉)。

已讀、無 finding 的項目:
- 三段式理由的內容:spec 只寫入固定的 `<命中理由>` 代號與固定說明文字,沒有原樣嵌入指令內容,沒看到終端控制字元或偽造提示文字的路徑。實作若把 `git config core.hooksPath <值>` 的值寫進理由才會有,spec 沒要求這樣做。
- 存活事件的 note:`_hookevent.record` 把 note 截到 200 字、以 `json.dumps` 寫入,spec 的 `ask:<理由代號>` 是固定代號。所以不可信內容不會經由 `ask:` 的 note 寫入。
- 註冊與 Codex 跳過、`_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 計數:邏輯一致,已與驗收測試 S5 對照。

最後一行總結:最嚴重 severity 是 major,blocking 共 3 條(第 1、2、3 條)。

來源:r1-架構對齊-sonnet.md


審查席暫存:本席沒有建立任何暫存檔或實驗目錄,不需要清理。

## 問 1 分層與依賴方向:部分不對齊

新掛鉤放在 `scripts/hooks/claude/`,只依賴 `_hookevent`,方向和鄰居一致。呼叫端也一致,都由 `merge-claude-settings.py` 註冊。差別在判斷放哪裡:

- file: `scripts/hooks/claude/dispatch-lens-hook.py:6-13` 是薄殼。它只做三件事(讀派工詞、叫 `lumos dispatch-lens`、接回傳文字),其餘判斷全在 lumos。
- file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭注入_計劃.md:104` 記了「hook 是薄殼,邏輯進 lumos」的 r3 裁定。
- file: `scripts/hooks/claude/impact-hook.py:133-160` 是混合型。檔案過濾 `hook_decide` 在 hook 內,重活交給 lumos。
- file: `scripts/hooks/claude/memory-sweep.py` 約 970 行,判斷都在 hook 內。
- file: `docs/lumos-toolchain-knowledge/Projects/Codex行為精修_計劃.md:58` 先例:厚 hook 要寫成「有意識偏離」並附理由。

新掛鉤把整套 heredoc 剝除、shlex 切段、git 全域選項解析、拋棄式路徑判斷全放在 hook 內,屬於厚 hook。鄰居本身不一致,所以厚本身我不硬判(見 F4)。依賴方向上沒有跨層直呼。我 grep 了 `scripts/lumos`,沒有可重用的函式。

## 問 2 命名與錯誤處理:不對齊(F1、F2、F3、F5)

以下幾項一致:

- stdin 用 `json.loads(sys.stdin.read())`,和 `impact-hook.py:771`、`dispatch-lens-hook.py:403` 相同。
- 輸出的 `hookSpecificOutput` 外層形狀相同,見 `impact-hook.py:824-829`。
- 呼叫 `guard` 的外殼也相同,見 `impact-hook.py:919-928`。

不一致的有四項:

- 預算區塊(F1)。
- 事件名(F2)。
- `mark("ok", …)` 的新用法(F3)。
- 預篩放在 `guard` 之外(F5)。

`swallow=True` 的對照:同為 PreToolUse 的鄰居(impact、dispatch-lens)是 `swallow=False`,`swallow=True` 的是 SessionStart 兩支(`ci-status-hook.py:254`、`memory-sweep.py:972`)。這裡的取捨有理由(spec 寫明問人層不是安全邊界),放行方向也比較保守,我不列為 finding。

## 問 3 第二種做法:不對齊(F1、F3、F6)

- shlex 切段:`scripts/lumos` 裡的 `shlex.split` 只有 `:26852`(解析掛鉤註冊命令,不是切 shell 段),其餘都是 `shlex.quote`。沒有現成的 shell 切段或 heredoc 剝除函式,自寫不算第二種做法。
- 註冊方式:HOOK_ENTRIES、HOOK_BUDGET、`_GLOBAL_CLAUDE_HOOKS`、ANCHOR_FILES、`_VENDORED_TREE_FILES`、`enforcement_status` 這幾處,我拿 `memory-sweep.py` 對照,出現的位置就是 spec 列的那幾處,沒有漏列。
- 新的做法有三個:預算區塊缺席(F1)、用存活事件計問人次數(F3)、另一份拋棄式目錄名單加字串前綴判斷(F6)。

## 問 4 落點:對齊

- 既有慣例是「一支掛鉤一個 Systems 節點」,例如 `Systems/改檔前推播.md:9` 管 `impact-hook.py`,`Systems/記憶過期清掃.md:9` 管 `memory-sweep.py`,`Systems/CI回流開場提醒.md:9` 管 `ci-status-hook.py`。新開 `Systems/代理繞閘問人` 管新掛鉤檔,符合這個慣例。
- file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:103-110` 的 `about_code` 已列 `scripts/lumos` 與 `scripts/merge-claude-settings.py`。這兩支檔的改動寫進它是對的。
- 沒有專門的 enforcement 節點。這個落點沒有 finding。

## 不對齊條目

**F1. HOOK_BUDGET 登記了 5,但掛鉤忽略 `--budget`,會讓現有守衛測試崩潰**

spec 〈做法〉與〈範圍〉。

引句:「命令列參數(安裝時附的 `--budget 5`)一律忽略、不報錯。」

具體重現:

- file: `scripts/test_lumos.py:17908-17924`(`t_hook_inner_timeout_always_below_outer`)對 HOOK_BUDGET 每個項目,只要檔案存在,就載入該掛鉤並呼叫 `mod._inner_budget(default=...)`。
- 照 spec 實作:HOOK_BUDGET 加 `"bypass-ask-hook.py": 5`,新掛鉤沒有 `_inner_budget`。
- 新檔一出現,這支測試在 `mod._inner_budget` 上丟 AttributeError。
- 應該是:新掛鉤也帶那段逐字複本(`_BUDGET_RATIO` 到 `return max(_BUDGET_FLOOR,…)`)。那段複本有 `len(_sigs)==1` 的漂移守衛。或者 spec 明寫這支不進 HOOK_BUDGET 表,並說明 `t_bypass_ask_registered` 要求的 `timeout 5` 從哪來。

ID: a1
severity: major
blocking: 是 — 照字面實作會讓現有全套測試翻紅,而且 spec 沒有交代怎麼處理。

**F2. 存活事件名和 `enforcement_status` 的列名不一致,新那一列永遠不會是 active**

spec 〈做法〉`guard` 呼叫與 `enforcement_status` 段。

引句:「過了預篩才進 `guard("bypass-ask-hook", __file__, main, swallow=True)`」

引句:「`enforcement_status` 的 Claude 掛鉤列舉加 `("pretooluse-bypass-ask-hook", "bypass-ask-hook.py")`」

具體重現:

- file: `scripts/lumos:27224-27237` 的 `_hook_recent_ok(root, layer, …)` 把列名 `layer` 直接當 hook 名。
- file: `scripts/lumos:23333` 比對 `e.get("hook") != hook_name`,hook 名必須和列名完全相同。
- 鄰居都是事件名和列名同字串:`guard("pretooluse-impact-hook", …)`(`impact-hook.py:928`)、`guard("pretooluse-dispatch-lens-hook", …)`(`dispatch-lens-hook.py:555`)、`guard("sessionstart-memory-sweep", …)`(`memory-sweep.py:972`)。
- 照 spec 實作:事件寫成 `hook: "bypass-ask-hook"`,列名是 `pretooluse-bypass-ask-hook`,兩邊永遠對不上。
- 結果:該列最好只顯示 unknown。spec 〈做法〉把這個狀態說成「近期沒命中過時照既有規則顯示 unknown」,等於把永遠對不上的 bug 說成預期行為。
- `scripts/test_lumos.py:41089` 的驗收測試也斷言 `"bypass-ask-hook"`,會把這個錯綠掉。
- 應該是 `guard("pretooluse-bypass-ask-hook", …)`,測試跟著改。

ID: a2
severity: major
blocking: 是 — 照字面實作會做出一個永遠觀測不到的掛鉤,而且驗收測試會跟著錯。

**F3. 用存活事件記「問了」的次數,違反既有「只記活著沒、不記成效」的界線,也是 `mark` 的新用法**

spec 〈做法〉命中段與〈前言〉PRIOR-ART。

引句:「並用 `mark("ok", "ask:<理由代號>")` 讓存活事件帶上」

引句:「事後量測掃 Claude 事件帳與掛鉤自己的存活事件」

具體重現:

- file: `scripts/hooks/claude/_hookevent.py:26-27`:「★不記「注入 N 次」★:那是成效…本批只做「活著沒」」。
- file: `docs/lumos-toolchain-knowledge/Projects/enforcement可觀測性_計劃.md:18` 與 `:201-206`:明列「不做注入 N 次」,因為那是成效量測。
- file: `scripts/hooks/claude/_hookevent.py:111-125`:`mark` 的語意是「內部吞掉逾時或失敗時自己講一聲」。
- 我 grep 了 `scripts/hooks/claude/` 下所有 `mark`,現有呼叫只有 `error` 與 `timeout`,沒有 `ok`。
- spec 把存活事件拿去計「問了幾次」,供 RETIRE-IF 與 REVISIT 量測。這等於在同一本帳上開了第二種用途(成效計數)。
- spec 也誤引上述計劃:該計劃只決定「記帳不新開端點」,並沒有授權存活事件當成效帳。
- 應該是二選一:
  - 不在存活事件放 `ask:` 備註,量測改走 Claude 事件帳。
  - 或先用 `lumos decision-add` 翻案,再改 `_hookevent` 的界線與 `mark` 的定義。

ID: a3
severity: major
blocking: 是 — 引入第二種記事件的做法,並且推翻既有的明文界線,spec 沒走翻案流程。

**F4. 厚 hook 沒有宣告對「薄殼」裁定的偏離**

spec 〈前言〉PRIOR-ART 與〈做法〉。

引句:「由 `scripts/merge-claude-settings.py` 註冊、讀 stdin 事件、印 JSON;這支照同一種做法」

引句:「用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令」

具體重現:

- PRIOR-ART 說「照同一種做法」,但最近的同事件鄰居是薄殼(`dispatch-lens-hook.py:6-13`)。
- spec 通篇沒提「薄殼」裁定,也沒寫「有意識偏離」。`Codex行為精修_計劃.md:58` 是先例:有厚 hook,但偏離要明寫。
- ⚠ 交編排者:厚本身不是 finding。`impact-hook.py` 的 `hook_decide` 與 `memory-sweep.py` 證明厚 hook 有先例。「掛鉤不叫主程式」的效能理由在 spec〈實務隱患〉成立。
- 要補的是明寫偏離的理由,並用 `decision-add` 記進決策。

ID: a4
severity: minor
blocking: 否 — 結構可用,缺的是脈絡紀錄,不會讓實作者做錯。

**F5. 預篩放在 `guard` 之外,出現一條不受 fail-open 包覆、也不記事件的執行路徑**

spec 〈做法〉預篩段。

引句:「便宜的預篩(在 `_hookevent.guard` 之外)」

具體重現:

- file: `scripts/hooks/claude/_hookevent.py:127-160`(`guard`)的語意是「每次執行都記一筆」。鄰居的早退(例如 dispatch-lens 的「不帶標記就放行」)全在 `main` 內、`guard` 之下。
- 新掛鉤的預篩在 `main`/`guard` 之前,讀 stdin 和判斷出錯時,spec 的 `swallow=True` 與 `mark("error")` 都沒有包到。
- spec 的 S4 只驗「過預篩之後」丟例外會放行。
- 不確定的點:預篩階段丟例外的實際結果。這取決於 stdin 解碼等實作細節,我沒有實測,所以不下結論。
- 這個取捨(避免灌爆存活事件檔)有理由,所以只列為與鄰居的差異。要補的是預篩階段自己的 try/except 放行。

ID: a5
severity: minor
blocking: 否 — 設計意圖成立,只是缺一道包覆,補一個 try/except 即可。

**F6. 拋棄式目錄判斷用字串前綴,和 lumos-guard 的真實路徑判斷、名單都不一致**

spec 〈做法〉拋棄式目標放行段。

引句:「目標落在 `/tmp/`、`/private/tmp/`、`/var/folders/`、`/private/var/folders/`、`$TMPDIR` 底下」

具體重現:

- file: `mods/claude/lumos-guard/hooks/register.ts:39` 的暫存根是 `/private/tmp`、`/private/var/tmp`、`/tmp`、`/var/tmp`。
- file: `mods/claude/lumos-guard/hooks/register.ts:112-114` 先轉真實路徑,路徑含 `.` 或 `..` 段就當看不懂。
- file: `scripts/lumos:18217` 也用 `os.path.realpath(tempfile.gettempdir())`。
- 輸入:`cd /tmp/../Users/x/repo && git push --no-verify`。
- 照 spec 的字串前綴判斷:落在 `/tmp/` 底下,放行,不問人。
- 應該是:路徑含 `..` 就不當拋棄式,或先 realpath。
- 另一處不一致:`/var/tmp` 在 lumos-guard 算暫存,在 spec 名單裡沒有。因為 `/var/tmp` 和 `/var/folders` 兩邊各漏一半,用到 `/var/tmp` 的指令會被誤問。
- 兩邊語言不同(TS 與 Python)無法共用程式,但名單和 `..` 處理應該對齊。

ID: a6
severity: minor
blocking: 否 — 影響範圍是「寧可漏問」方向的誤放行與少量誤問,不會讓系統壞掉。

不對齊共 6 條,其中 major 3 條(F1、F2、F3)。

最嚴重的是 major,blocking 共 3 條。
