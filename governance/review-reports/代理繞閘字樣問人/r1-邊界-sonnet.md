severity: major

審查對象是凍結快照 r1-snapshot.md。對照的程式碼是 Word-wild-search-bypass(HEAD de48ddd9)。以下所有重現都是實際跑過的:shlex 實測、本機事件帳 28152 條 Bash 指令、既有測試原始碼。

## 派工詞尾端的掛鉤節點
派工詞尾端沒有任何自動附加的節點,所以沒有節點可判。

## Findings

**1. mktemp 例外是整條指令通吃,真繞閘會被放行**
- spec 段落:〈做法〉拋棄式目標放行,以及 S3。
引句:「或指令裡用了 `mktemp`,該段命中不算」
severity: major
blocking: 是。照字面實作,守衛會在常見的「訊息檔用 mktemp」寫法上整個失效。
- S3 的測試案例 `d=$(mktemp -d); git -C $d init -q; git -C $d commit -qm x --no-verify` 只有靠「mktemp 出現在同一條指令的別段」才會放行。因為 `-C $d` 沒有被展開,`$d` 是字面。所以「該段」實際上必須做成整條指令。
- 重現:`msg=$(mktemp) && echo x > $msg && git commit -F $msg --no-verify`,event cwd 是真 repo。照字面實作,這條指令有 mktemp,整條放行,沒有問人。應該是問人。
- 更窄的做法是只追蹤 `VAR=$(mktemp…)` 賦值,而且只讓以該變數為目標的 `cd` / `-C` 放行。這樣 S3 第 4 案仍然通過。

**2. 本使用者的 /tmp 底下有真工作副本,而且會對真遠端推送**
- spec 段落:〈量測〉與〈做法〉拋棄式目標。
引句:「再排除拋棄式目標(`cd` 或 `git -C` 指到 `/tmp/`、`/private/tmp/`、`/var/folders/`,或指令裡用 `mktemp`):剩 4 次」
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
severity: major
blocking: 是。排除清單裡有一項是繞閘本身。
- 〈範圍〉自己寫了推送前閘與提交前閘走 `core.hooksPath` 指向的 `scripts/hooks`。
- `git config --unset core.hooksPath`(或 `--local --unset`)之後,git 退回預設的 `.git/hooks`,Lumos 的 pre-commit 和 pre-push 就不跑了。效果與 `-c core.hooksPath=/dev/null` 相同。
- 重現:`git config --local --unset core.hooksPath && git commit -m x`。照 spec 不問人,應該問。
- 反方向還有一個問題:`git config core.hooksPath scripts/hooks` 是 Lumos 自己安裝時設的值。spec 只看「有沒有值」,不看值指到哪,所以重新設回正確值也會問人。

**4. 「忽略 --budget」與既有的逾時預算守衛測試衝突**
- spec 段落:〈做法〉掛鉤檔與 `merge-claude-settings.py` 兩條。
引句:「命令列參數(安裝時附的 `--budget 5`)一律忽略、不報錯。」
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
severity: minor
blocking: 否。測試一跑就紅,實作者馬上會發現,不會做錯決定。
- `ANCHOR_FILES` 的鍵集合必須等於 `governance/anchor-baseline.json` 的鍵集合。
file: `scripts/test_lumos.py:40206`
- 另有一個測試要求「版控裡每個 hook 檔都在錨點清單」。
- 所以還要做 `lumos anchor approve` 把新檔的雜湊簽進 baseline。spec 的步驟清單漏了這一步。

**7. shlex 不會把換行當分隔,逗號合併的複合標點也沒處理**
- spec 段落:〈做法〉結構分類。
引句:「用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令」
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
severity: minor
blocking: 否。〈範圍〉已聲明這是防順手、不防有心。但下列寫法不是有心改寫,而且〈範圍〉沒列出來,實作者不會知道這是已知漏洞。
- 實測 tokens:`if ! git push; then git push --no-verify; fi` 裡,第二段開頭是 `then`,不是 `git`。`do`、`{`、`!` 開頭同理。
- `timeout 60 git push --no-verify`、`env LUMOS_SKIP_X=1 git push`、`time git …`、`command git …`、`nohup`、`exec`:程式名不是 `git`。
- 我在臨時 repo 實測:`--no-verif`(git 接受唯一前綴縮寫)在 pre-commit 失敗的情況下 rc=0,等於繞過成功。但預篩只看 `--no-verify` 字面,直接退出。
- 建議在〈範圍〉補一行,或把這幾個常見前綴(`then`/`do`/`{`/`!`/`env`/`time`/`timeout`/`command`/`nohup`/`exec`)納入跳過清單。

**11. 「10 萬字 0.5 秒」在 shlex 下是邊緣的**
- spec 段落:S4。
引句:「10 萬字的指令 應 在 0.5 秒內判完」
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
