severity: minor

我跑了掃描器、here-doc 判斷和三個測試子集。三個子集在清掉 `__pycache__` 後全綠:`prepush_touched` 22 條過、`prepush_cl_reason` 5 條過、`prepush_interrupt_launcher` 11 條過。掛鉤裡目前沒有 here-doc,也沒有 `>|`、反引號、`3>` 這類寫法,所以下面幾條都是守衛本身的缺口,不會讓現在的掛鉤出錯。

severity: minor
blocking: 否 — 這條只讓測試誤紅,不會誤放行,紅了會印出行號。
引句:「heredoc = [i for i, ln in enumerate(hook_txt.splitlines(), 1) if _re.search(r"(?<!<)<<(?!<)[ \t]*[-A-Za-z0-9_'\"\\]", ln)]」
問題:這個判斷逐行比對,不看這行的 `<<` 是在註解、字串還是算術裡。我實測:`x=$(( a << 2 ))`、`x=$((a<<2))`、`echo "a << b"`、`# 把 << EOF 說明` 全部判成 here-doc。`<<<` 本身沒有誤判。
具體失敗情境:有人在掛鉤的註解裡寫「`<< EOF`」,或加一行位移運算 `$(( n << 2 ))`,④前置會紅,訊息卻說「掛鉤裡有 here-doc、要先擴充 `_ppc_bash_logical_lines`」。作者會被誤導去擴充解析器。
佐證:``scripts/test_lumos.py:64595``(修補後該檔,依 patch 第 89 行推算)

severity: minor
blocking: 否 — 守衛只有漏判一側會悄悄失效,但要有人在掛鉤新增 here-doc 才會發生。
引句:「heredoc = [i for i, ln in enumerate(hook_txt.splitlines(), 1) if _re.search(r"(?<!<)<<(?!<)[ \t]*[-A-Za-z0-9_'\"\\]", ln)]」
問題:`<<` 後面的第一個字元只收字母、數字、底線、`-`、引號、反斜線。`cat <<$x`、`cat <<.EOF`、`cat <<%EOF` 在 bash 都是合法的 here-doc,這個判斷看不到。我實測 `cat <<$x` 回 False。
具體失敗情境:新增 `cat <<%EOF` 之類的寫法,本文被掃描器當程式碼掃,④前置不報,守衛靜默失效。
佐證:``scripts/test_lumos.py:64595``(同上)

severity: minor
blocking: 否 — 這些寫法目前都不在掛鉤裡。
引句:「寫檔:> >>(前面不是 fd 數字或別的重導向)、1> 1>>、&> &>>(stdout 與 stderr 一起寫進檔案,代碼審 r4)」
問題:掃描器對下面幾種寫法判錯。
- 漏抓 `>|`:`printf x >| "$_f" 2>/dev/null` 回 [],因為 `|` 先把這段切開了。
- 漏抓其他 fd:`3>>"$f" 2>/dev/null` 回 []。
- 漏抓 `2>>/dev/null`:`printf x >> $_f 2>>/dev/null` 回 [],因為只認 `2>` 後面的 `/dev/null`。
- 誤抓帶引號的 `/dev/null`:`printf x > "/dev/null" 2>/dev/null` 回 [1],因為引號內容被換成 x,與 `/dev/null` 字面比不出。
- 另有一個漏抓:`2>"/dev/null"` 的 `/dev/null` 同樣被換成 x,不會被認成丟棄 stderr 的重導向,於是 `printf x >> $_f 2>"/dev/null"` 沒被抓出。
具體失敗情境:後人在掛鉤寫 `{ …; } >| "$f" 2>/dev/null` 以外的 `>| "$f" 2>/dev/null`(沒包組),④守衛放行,開檔失敗的雜訊又漏出來。
佐證:``scripts/test_lumos.py:64648``(掃描器的 finditer 那行,依 patch 第 187 行推算)

severity: minor
blocking: 否 — 只是殘餘的解析缺口,而且要同時出現在雙引號的 `$(…)` 裡才會觸發。
引句:「if subs and c in "()":」
問題:雙引號裡的 `$(…)` 靠括號計深度,遇到 `case x in a)` 這種不成對的 `)` 就提早收尾,後面整段被當成引號內容。我實測 `v="$(case a in a) echo;; esac)"` 的邏輯行變成 `v="$(case a in a)xxxxxxxxxxxxx"`。
具體失敗情境:`v="$(case $x in a) printf x >> "$f" 2>/dev/null;; esac)"` 的寫檔被吃掉,掃描器回 [],漏抓。
佐證:``scripts/test_lumos.py:64619``(依 patch 第 140 行推算)

severity: minor
blocking: 否 — 這是測試沒釘到新程式碼,不影響現行行為。
引句:「elif c == "\n" and subs:   # 雙引號裡的 $(…) 跨行:換行在裡面是命令分隔」
問題:我把掃描器抽出來,對 17 條手寫例子逐條做變異,結果如下。
- 拿掉跨行換行改成 `;` 的分支,17 條全綠。
- 拿掉括號深度遞減,17 條全綠。
- 這兩段是這輪新寫的邏輯,卻沒有任何手寫例子會對它們翻紅;`&` 單獨切段也沒有例子管。
- 有管到的:拿掉 `$(…)` 內層掃描,例子 11、12 紅;拿掉 `&>` 支援,例子 15、16 紅;拿掉雙引號 `$(` 保留,例子 12 紅;`;` 與 `()` 切段各自有例子紅。
- 補測試前,作者在測試 docstring 寫的「各自對應的 ④前置紅」只有部分成立。
具體失敗情境:有人把跨行處理或巢狀括號深度改壞,測試仍全綠。
佐證:``scripts/test_lumos.py:64626``(依 patch 第 156 行推算)

已讀,無 finding:
- `t_prepush_interrupt_launcher_without_setpgid`:判準由人給(離開碼 0/3/1、START `__main__`、ARGV 逐字、END),沒有照啟動器重算。模擬 Windows(刪 `setpgid`、`execv` 立刻回 0)與 `setpgid` 丟 OSError 兩種情境都有。拿掉 `hasattr` 會因 AttributeError 紅,這點是推論,沒實際變異。
- ⑫(收到 TERM 才生的孫行程):假片在 TERM 處理器裡才生孫行程,只送一發必留孤兒。這點是推論,沒實際變異。掛鉤拆成 TERM 加 0.2 秒後第二發,第二發只送整組且錯誤吞掉,看不出越界。
- `t_prepush_cl_reason_sentences_match_plan`:會真的讀計劃那一行,抽不出四句時①紅,和常數不一致時②紅,判準來源是計劃原文。已讀,無 finding。
- `<<<` 沒被誤判成 here-doc,四處 `<<<` 都是單行。算術 `$(( … ))` 裡的括號在掃描器裡不會因為深度計數出錯,只是單獨的一般括號。

最高等級 minor,blocking 0 條。
