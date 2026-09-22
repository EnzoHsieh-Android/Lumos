severity: major

## F1 pp_touched_file() 的暫存檔在被打斷時不會被清,重演了同檔剛修過的「逐檔 rm 會漏」問題

severity: major
blocking: yes

觀察到什麼:`pp_touched_file()` 用 `mktemp` 建一個暫存檔,整支函式再透過 `_TOUCHED_F="$(pp_touched_file)"` 以 command substitution 呼叫——這會另外起一個子殼層。這支腳本現有的暫存檔慣例(`impact_once`/`impact_done`)是把清理動作放進 `trap 'impact_done; rm -rf "$_PP_TMP"' EXIT INT TERM`(`scripts/hooks/pre-push:100`),任何離開路徑(正常結束、`exit 1`、收到訊號)都會觸發同一個 trap,連 r1 代碼審都已經留了註解說「逐檔 rm 在 exit 1 / Ctrl-C 那條路會漏」。但 `_TOUCHED_F` 的清理是反過來寫的:只在兩個特定的程式碼位置手動 `rm -f`,沒有掛進那個 trap,也沒有放進 `$_PP_TMP`(trap 唯一會清的目錄)。

引句:「_f="$(mktemp "${TMPDIR:-/tmp}/lumos-prepush-touched-XXXXXX" 2>/dev/null || true)"」
引句:「[[ -n "$_TOUCHED_F" ]] && rm -f "$_TOUCHED_F"」

怎麼重現(輸入→錯誤輸出):在 `_TOUCHED_F="$(pp_touched_file)"` 這一行還沒回傳路徑給父殼層之前(也就是子殼層已經 `mktemp` 建好檔、正在跑 `git diff --name-only` 迴圈的當下),如果使用者這時候按 Ctrl-C(訊號會同時打中前景 process group 裡的父殼層與這個子殼層),子殼層會直接被中斷、command substitution 回傳空字串,父殼層裡 `_TOUCHED_F` 變成空的——兩個手動 `rm -f "$_TOUCHED_F"` 都因為變數是空字串而不會執行,`trap` 也只清 `$_PP_TMP`,不知道這個檔案的存在,於是它永遠留在 `$TMPDIR` 裡。

我在 `/tmp/lumos-repro-C` 用逐字複製自 patch 的 `pp_range_for`/`pp_touched_file` 定義(未改一字,只是把 `git diff` 前插一個 `touch 標記檔` 讓時序可控)重現了這件事:在暫存檔已經建好、還沒回傳路徑的那一刻,送 `SIGTERM` 給整條殼層鏈(模擬終端機 Ctrl-C 打中整個前景 process group),結果:

```
開始呼叫 pp_touched_file()(command substitution 起一個子殼層)...
[trap 執行] rm -rf /tmp/.../lumos-prepush-5AZVL5
回來了:_TOUCHED_F=[]
正常結束
[trap 執行] rm -rf /tmp/.../lumos-prepush-5AZVL5
```
`$TMPDIR` 底下留下 `lumos-prepush-touched-eUnJe4`,兩次 trap 執行都沒有清掉它。

為什麼是 bug 而不是風格:這不是命名或排版的差異,是同一支腳本自己剛用一段專門註解記錄過、也已經修掉的同型錯誤(「逐檔 rm 在 exit 1 / Ctrl-C 那條路會漏」,見 `_PP_TMP` 那段的建立理由),這次新增的暫存檔又走回同一條會漏的路。實際後果是每次推送在「doctor 還沒跑完就被中斷」(手動 Ctrl-C、CI runner 逾時砍掉、系統資源不足砍程序)時,都會在 `$TMPDIR` 留一個孤兒暫存檔,長期跑很多次推送會累積。鏡頭③明確要對照 `impact_once`/`impact_done` 那組慣例,這裡對不上。

## F2(觀察,非阻斷)S15 新增的「沒碰到」提醒,advice 沒有給指令,跟同段兩個手足不一致

severity: minor
blocking: no

觀察到什麼:S15 這段本來就有 `_gover`(逾期會擋)跟 `_gsoon`(七天內到期)兩塊,兩塊的 `advice` 都會給一句可以直接貼去跑的指令(`lumos guard settle …`、`lumos signoff …`)。這次新增的 `_gover_other`(逾期但沒碰到、不擋這次推送)緊接在 `_gover` 後面,用的是同一個 `warn_soft` 函式,但它的 `advice` 只寫了一句解釋「這幾條由負責人自己收」,沒有給任何指令。

引句:「推送前的閘只擋你這次碰到的;這幾條由負責人自己收,CI 會擋全部」

為什麼算個問題但不到擋的程度:這個 repo 的長期輸出標準要求「發生什麼→為何在意→指令獨立一行」,同一段裡另外兩塊都照做了(`scripts/lumos:2337`、`scripts/lumos:2347`),只有這塊沒有給出「這條到底該找誰、用什麼指令去看」的下一步——讀到這行的人只知道「不是我的問題」,但如果他想確認自己判斷得對不對(例如想自己查一下這條合約掛在哪個守衛節點),訊息裡沒有指路。不過這不是唯一的違例:同檔案裡本來就有不少 `warn_soft` 呼叫完全不給 `advice`(例如 `scripts/lumos:1366`、`scripts/lumos:2049`),所以「advice 沒指令」在這支檔案裡不算全新的例外,只是跟緊鄰的兩個手足比明顯偏弱,列成觀察而非擋。

## 其他已驗過、沒發現問題的路徑

- ②(shell 範圍推導抽成 `pp_range_for`):比對過抽出來的邏輯跟原本 `_range` 那段 if/elif/else 的三個分支語意一致(`$1`=remote_sha 對應舊的 `_rsha`,`$2`=local_sha 對應舊的 `_lsha`);`_hrange` 那組「每支檔有家」用的範圍完全沒有被改動、也沒有共用到 `pp_range_for`,兩套範圍維持分開,沒有像作者宣稱要避免的那樣被混在一起。
- ①(命名與位置):shell 這邊 `pp_range_for`/`pp_touched_file` 沒加底線前綴,跟同檔既有的 `impact_once`/`impact_done`/`bound_tests_advisory` 一致;python 這邊 `_read_touched_list`/`_guard_touches` 都是底線前綴,`_guard_touches` 放在 `_guard_home_of` 正下方(同一個 `_guard_*` 家族),`_read_touched_list` 放在它唯一的呼叫者 `run_doctor` 定義正上方,都合乎既有慣例。至於「抽取函式跟它的正則放一起」,這次沒有新增任何正則(`_guard_touches` 純粹讀欄位、取交集),不適用。
- ③ 之外的暫存檔:`_gover`/`_gsoon`/`_gover_other` 三段共用同一份 `env.notes` 掃描,沒有另外建暫存檔,不受這個問題影響。
- ④ 新旗標 `--touched-from` 的 `--help` 文字:比其他 `doctor` 旗標(`--strict`/`--ci`/`--verbose`)長,但那三個本身也不是照「發生什麼→為何在意→指令獨立一行」的完整格式寫的(它們是精簡片語),`--touched-from` 只是把機制講清楚一點,沒有偏離到不合理的程度。
- ⑤ 新測試:三支新測試(`t_guard_overdue_local_blocks_only_touched`、`t_prepush_passes_touched_list_to_doctor`、`t_guard_overdue_local_skips_home_without_code`)都有翻紅釘描述,格式跟既有 `t_context_shows_planned_contract` 等測試一致；斷言用 `_section_of` 把範圍縮到 `S15` 那段再逐行比對兩條不同的宣稱字串,不是對整段 stdout 做寬鬆的 substring 搜尋;`_issues()` 這個小 closure 是照抄緊鄰的既有測試 `t_guard_overdue_blocks_doctor` 裡同名 closure 的寫法(這支檔案本來就是每支測試各自複製一份,不是共用頂層函式)。`t_prepush_passes_touched_list_to_doctor` 特別真跑整支 `pre-push`(不是 grep 腳本裡有沒有那個字串),避免自己在文件裡都寫出來的「假綠形態」。用 `python3 scripts/test_lumos.py -k guard_overdue` 與 `-k touched_list_to_doctor` 實跑過,24+4+5 (含 C3 反事實) 案例全線通過。
- 作者宣稱「只是把既有的兩跳查詢接起來,沒有新的判定引擎」:核對 `_guard_touches` 的實作,確實只是 `_guard_home_of`(既有 getter)→ `env.find`/`env.notes`(既有節點解析)→ `about_code` 欄位(既有欄位)取交集,沒有新的比對演算法或狀態機,這句話成立。
