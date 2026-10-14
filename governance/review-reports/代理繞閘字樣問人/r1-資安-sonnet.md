severity: major

我讀完整份 spec 和 `_hookevent.py`、五支 `t_bypass_ask_*` 測試。官方文件我只讀了 hooks 頁前 100000 字。下面三段是我直接查證到的事實,其餘各條是對 spec 與測試字面的推論,我沒有跑實驗。

- 官方文件有寫:掛鉤逾時「doesn't block the tool call」,輸出 JSON 無效或掛鉤丟例外是 non-blocking,動作照常執行。
- 官方文件沒寫:`ask` 在略過權限模式、自動接受模式下的語意。我看過的那段沒有寫,permissions 頁我沒查。
- 沙箱擋下了我跑 shlex 的實驗(同一行含 git 與 push),所以下面第 2 到 5 條只依 spec 字面和 `test_lumos.py` 裡的測試案例推論,我沒有執行驗證。

1. 拋棄式目標判定沒有規定多個目標同時出現時以誰為準
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
severity: minor
blocking: 否。需要字面裡有 `<<WORD`,不是主要路徑,但落在 fail-open 方向。
- 位置:〈做法〉的「剝掉 heredoc」。
引句:「把 `<<WORD`、`<<-WORD`、`<<'WORD'`、`<<"WORD"` 之後到結束字那一行的內容整段拿掉(heredoc 運算子本身留著)」
- 問題:這句沒說運算子在引號裡、在 `$((1<<n))` 這類算式裡、或後面找不到結束字時怎麼辦。
- 重現:`git commit -m "doc: explain <<EOF handling" --no-verify`。若實作用正規式找 `<<EOF`、找不到結束字就剝到結尾,後面真正的 `--no-verify` 被一起拿掉,放行。
- 應該是:只剝未被引號包住、且之後真的有結束字那一行的 heredoc。找不到結束字就不剝(寧可多問)。S2 的 heredoc 案例都有結束字,沒涵蓋這條。

5. 掛鉤自己壞掉或逾時的放行,spec 只承認「例外」,沒承認逾時與可被觸發
severity: minor
blocking: 否。〈實務隱患〉明講這不是安全邊界,但它只講了丟例外,沒講逾時也是同一個放行路徑。
- 位置:〈實務隱患〉的「自我治理」。
引句:「這是守衛本身;掛鉤壞掉時放行(問人層不是安全邊界),但會記 error 事件讓 `lumos enforcement` 看得到。」
- 問題:官方文件寫逾時掛鉤不擋工具呼叫、照走正常權限流程(我查證到的)。所以「記 error 事件」只覆蓋丟例外,逾時時 Python 被砍,`guard` 根本寫不出事件。
- 重現:指令長且結構特殊,讓切段或變數展開超過 5 秒。S4 的 10 萬字測試只測 `echo xxx… && git push --no-verify` 這一種形狀,沒測大量 `;` 分段、深層引號、很多變數賦值。
- 應該是:〈實務隱患〉補一句「逾時同樣放行且不留事件」,並加最壞形狀的效能測試。
- 補充:官方文件另有 `onFailure: "block"` 可讓失敗變成阻擋(需 Claude Code v2.1.295 以上),spec 沒討論要不要用。

6. 略過權限模式下 `ask` 的語意,spec 的實測段說對了範圍,但 S6 的回退條件不夠
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
