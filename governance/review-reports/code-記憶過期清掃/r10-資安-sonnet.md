severity: major

## 發現1

severity: major

引句:「_LINKED_REF = re.compile(r"\[\[([^\]|#]+)\]\]")」

觀察到什麼:

r10 的兩條處置(①單篇 64KB 上限 ②`cross_check`/`shadow_copies`/`pointer_problems` 吃同一個 `_Clock`)都是在「迴圈邊界」上檢查時間,對「單一篇檔案在正常大小內、單一次呼叫本身就很慢」這種洞完全沒有覆蓋——而 `_LINKED_REF` 這個正則剛好就是這種洞。

`_LINKED_REF = re.compile(r"\[\[([^\]|#]+)\]\]")` 用在 `_nodes_in()`(`| {_stem(n.split("/")[-1]) for n in _LINKED_REF.findall(chunk)}`)與 `pointer_problems()` 裡 `linked = {_stem(n.split("/")[-1]) for n in _LINKED_REF.findall(scan)}`——這兩處都是對整份(或整段)檔案文字一次性呼叫 `.findall()`,呼叫中間沒有任何 `clock.up()` 檢查點。這個 pattern 對「大量 `[[` 但完全沒有配對的 `]]`」的輸入是 O(n²):每個 `[[` 起始位置都會讓 `[^\]|#]+` 貪婪吃光後面所有的 `[`,失敗後逐字元回溯到底(因為永遠找不到 `]]`),再換下一個起點重來一次。

實測(直接呼叫模組函式,64KB 的內容全是 `"[["` 重複):

```
_LINKED_REF findall on repeated unmatched '[[': 24.4876s
_LINKED_REF findall on '[' * MAXB: 24.2642s
```

再實測整支 hook 真跑(記憶目錄裡只放「一篇」65435 位元組、內容是 `"---\nname: attack\n---\n" + "[["*N` 的檔,size 在 64KB 上限之內,cwd 設在本 repo 根目錄以便真的觸發跟圖譜對帳):

```
$ time python3 scripts/hooks/claude/memory-sweep.py --budget 12 --quiet --dir /tmp/ms-attack
python3 scripts/hooks/claude/memory-sweep.py --budget 12 --quiet --dir  71.62s user 0.30s system 99% cpu 1:12.18 total
```

整支跑了 72 秒(因為 `pointer_problems()` 對同一份 `scan` 文字呼叫了兩次含 `_LINKED_REF.findall` 的路徑,加上 `_paragraphs(body)` 對同一段內容又跑一次,三次疊加約 3×24s)。這遠遠超過 `--budget 12` 對應的內層預算(8.4 秒)與外層 SIGKILL 逾時(12 秒)。

會造成什麼:
在題目的威脅前提下,攻擊者只要讓「一篇」64KB 以內、格式合法(能通過 frontmatter 解析、能被 `read_memories` 正常讀進來)的記憶檔落進記憶目錄,檔案本體塞滿無配對的 `[[` 字元,就能讓整支 hook 在真正呼叫任何 `clock.up()` 檢查點之前,單一次 `.findall()` 呼叫就吃光超過一分鐘。外層 12 秒的 SIGKILL 會在 `_emit()` 印出任何東西(包括「結果不完整」的喊聲)之前就把整支 process 砍掉——這正是 r9 兩條處置合起來宣稱已經「結構性歸零」的失敗模式(從「不完整但有喊」退化成「完全不出聲」),而且門檻比 r9 report 裡「240MB 假連結檔」低了三個數量級:不需要超大檔案、不需要超過檔案數量上限,一篇在所有現有上限(`MAX_BYTES`=64KB、`MAX_FILES`=300、`MAX_CLAIMS_PER_FILE`=30、`MAX_CLAIMS_TOTAL`=600)以內的正常大小記憶檔就夠。而且這條路徑完全繞過 r10 新增的 `_Clock`:`clock.up()` 只在 for 迴圈的「每篇檔案」或「每個節點」邊界被呼叫,單一次 `_LINKED_REF.findall()` 的執行時間本身不受任何時間預算節流。

建議怎麼修:
`_LINKED_REF` 這個 pattern 要換成不會回溯爆炸的寫法——例如把 `[^\]|#]+` 的量詞收斂(不允許連續 `[` 造成的模稜兩可路徑),或改用「先用簡單掃描找出所有 `[[`/`]]` 的位置再配對」取代單一正則,或者對捕獲組加上長度上限(`{1,200}` 這類有界量詞可以把最壞情況壓成線性而不是平方);另外無論正則本身修不修,對「單一次可能很貴的操作」應該加上獨立的 wall-clock 逾時(例如用 `signal.alarm` 或把這類 findall 丟進有 timeout 的子行程/執行緒),不能只靠「迴圈邊界查時間」這種粒度——這條 pattern 已經證明「迴圈邊界」粒度可以被單一步驟直接繞過。

## 發現2

severity: minor

引句:「shown = tally.lines if not quiet else tally.lines[:MAX_LINES]」

觀察到什麼:

r10 新增的 `MAX_LINES = 80` 只截 `tally.lines`,但 `tally.lines` 的內容是「先 `sweep()` 逐檔案 append,再由 `cross_check()` 在最後 append 兩段跟圖譜對帳的結果(`shadow_copies`/`pointer_problems`)」——也就是說,`main()` 裡 cross_check 在 sweep 之後才跑,cross_check 的訊息永遠排在 `tally.lines` 的最尾端。只要 sweep 階段自己先湊出超過 80 行(這完全在現有上限之內,不需要觸發任何 `tally.flood`),`_emit()` 就會把 cross_check 這種「記憶跟圖譜真的打架」的訊息整段截掉,只留一句通用的「還有 N 行沒印⋯完整報告用指令看」。

實測(直接呼叫 `sweep()`/`cross_check()`/`_emit()`,模擬真正的呼叫順序):造 15 篇無害的記憶檔,每篇帶 10 條打錯字的 `verify` 型別鍵(合法格式、遠低於 `MAX_CLAIMS_PER_FILE=30`、15 篇遠低於 `MAX_FILES=300`),讓 `sweep()` 產生 150 行「這條驗不了」訊息;另外放一篇檔案 `[[某個 status: done 的真實圖譜節點]] 還沒做`,製造一條真正的 `pointer_problems` 衝突。跑完:

```
tally.lines count after sweep(): 150
tally.flood: []
crossed: True
tally.lines count after cross_check(): 154
```

`--quiet` 模式印出的注入內容裡,只看得到前 80 行「填充宣稱」的「這條驗不了」雜訊,以及最後一句「……還有 74 行沒印(開場只印前 80 行),完整報告用下面那行指令看。」——那條真正重要的「說還沒做,但節點已 done」衝突訊息(在第 151~154 行)完全沒有出現在會被自動讀到的 additionalContext 裡:`"節點已 done" in ctx or "說還沒做" in ctx` 回傳 `False`。

會造成什麼:
攻擊者(或單純雜訊多的正常使用情境)只要讓記憶目錄裡先出現夠多「格式錯誤但無害」的檢查(打錯字的 `verify` 型別鍵是完全合法、任何人都可能不小心寫出來的東西),就能把本輪 r10 才新增的、真正有意義的「記憶跟圖譜對不上」警告擠到 80 行視窗之外——而這正是這整支 hook 存在的核心目的(CLAUDE.md 開頭就講「行為事實和圖譜衝突時...立一篇事故筆記」)。雖然報告最後有一句通用的「還有 N 行沒印」提示技術上滿足「不完整但有喊」,但被自動讀進對話的內容裡看不到具體是什麼被砍掉,使用者/Claude 不會主動去跑後面那行「完整報告」指令,等於這條真正的警訊在正常使用流程裡被埋沒。這不是「完全不出聲」,所以我沒有把它定為 major;但它確實是 r10 這批新增的行數上限本身引入的排序缺陷,不是既有問題的重報。

建議怎麼修:
`tally.lines` 的截斷順序應該按「訊息重要程度」排,而不是按「產生順序」——至少應該讓 `cross_check()` 產生的「記憶跟圖譜對不上」/「shadow copy」訊息排在 `sweep()` 的逐檔「驗不了」訊息之前(或者兩類分開各自保留名額),這樣攻擊者/雜訊灌爆其中一類時,另一類還留得下來。

## 已確認

- r9 資安席原始情境(單篇 240MB 檔讓 `cross_check` 不看時間跑到 15 秒以上)已被 `MAX_BYTES=64*1024` 的單篇讀取上限(`_read_own_file`/`_opened_reason` 兩處都擋)結構性排除:超過上限的檔案在 `read_memories()` 階段就被拒讀並記進 `tally.lines`(`! big.md 有 X KB,超過單篇上限...`),不會進入 `sweep`/`cross_check` 的檔案清單;`scripts/test_lumos.py` 的 t_memory_sweep_core ㉓ 案例與本機重跑一致。
- `cross_check()`/`shadow_copies()`/`pointer_problems()` 三者現在共用同一個 `_Clock(deadline)`,對「檔案數量多、單篇大小在 64KB 上限內、單篇處理成本正常(非發現1那種病態正則輸入)」的情境,逐檔與逐節點的時間檢查確實會在合理粒度內停下並在 `tally.flood` 記「跟圖譜對帳時時間預算用完」——用 509 個真實節點名塞滿單篇 64KB 檔案、量到單次 `_claims_near` 呼叫成本落在個位數毫秒等級(0.5~17ms)的情境下實測驗證:給 0.5 秒截止時間,`pointer_problems` 對這種(非 ReDoS)worst-case 檔案的實際超時量只有 3.7 毫秒,遠小於外層逾時餘裕,不構成發現1那類洞。
