severity: minor

審查範圍:diff 1494 行全讀。實驗在 /tmp/lumos-seat-work/code-審查席唯讀隔離/r3x/,用 `node --experimental-strip-types probe.mts` 直接 import register.ts 的純函式。試過的字串全部留在 probe.mts,報告不貼可照抄的繞過字串。沒有 blocker 或 major。

### F1 Bash 粗擋把正常的唯讀指令誤擋(搜尋詞與以 claude 結尾的目錄)
severity: minor
blocking: 否 — 是誤擋不是漏擋,擋下訊息有教改法(分兩次呼叫、改用 Read 或 Grep),不影響隔離。

引句:「const words = new Set(toks.map(t => t.slice(t.lastIndexOf('/') + 1)).filter(Boolean))」

類型:誤擋。已實測被擋(probe.mts 的 bash 段):
- 同一行有 git 又有 push 當搜尋詞:`git log --grep push`、`git log --oneline | grep push`、`grep -rn "git push" docs`。這個 repo 的文件滿是「git push」「推送」字樣。
- 搜尋詞本身是 claude 或 gh 或 hub:`grep -rn claude docs`。
- 路徑最後一段剛好是 claude 的目錄:`ls mods/claude`、`cd mods/claude && ls`、`git log -- mods/claude`。`mods/claude` 是本 repo 的真目錄,審這次變更的審查員很可能這樣查。加結尾斜線就過,但擋下訊息講的是「對外動作」,看不出原因。
- 測試只覆蓋 `--grep=push`、`mods/claude/`(結尾斜線)、`echo push`,沒覆蓋上面幾種。
- 測試 :399-400 把「路徑最後一段剛好是這些字」列為接受的誤擋。上面的搜尋詞情境在測試裡沒被提到,應該一起寫進接受清單。
- 建議:至少把擋下訊息的「判準」說到位,例如「因為出現整詞 claude/push,即使只是路徑或搜尋詞」。

### F2 寫壞標記的判準只收「長得像 lumos-seat」,打錯字元的變體整份靜默放行
severity: minor
⚠
blocking: 否 — 是漏擋,但前提是派工者自己把標記打歪,不是被審材料誘導。第二輪修的「寫壞要擋派工」在這幾類沒生效。

引句:「const SEAT_LOOSE_RE = /^lumos-seats?(?![a-z0-9_-])/i」

類型:漏擋(標記寫壞卻判成 none,審查席不受任何限制,也沒有任何提示)。已實測回 none(probe.mts 的標記段):
- 連字號換成全形、不換行連字號,或改成底線、空格。中文輸入法下全形連字號與全形字母很容易打出來。
- 字中間夾零寬字元。
- 零寬字元單獨成一行、真標記在第二行:這會被當成「第一個非空行」,結果是 none。零寬字元放在標記同一行開頭卻判 bad,兩者不一致,因為 trim() 不剝 U+200B。
- 反方向:第一行合格標記後接 U+2028(trim 不認,`$` 不容許),會判 bad 擋下合格派工,屬誤擋。很罕見。
- 一般文字提到標記字樣的情況判得對:`# Lumos-seat plugin review` 判 bad(測試已接受)。`lumos-seat-work …`、`Lumos-seating` 判 none。
- 建議:判斷前先做 NFKC 並剝掉零寬字元,再比對 lumos[-_ ‑–－]seat 這類變體。

### F3 Glob 的 pattern 以大括號選項開頭、選項裡有絕對路徑時,搜尋範圍算成 cwd
severity: minor
⚠
blocking: 否 — 漏擋,但需要 Glob 引擎真的支援大括號內放絕對路徑,我沒能在實際引擎上確認。

引句:「if (/[*?[{]/.test(s)) break」

類型:漏擋。不是以 `/` 開頭的 pattern,第一段就是 `{` 時,固定前綴為空,searchBase 退回 `seat.cwd`,通過 checkTool。實測見 probe.mts(search 段,最後一項回 pass)。以 `/` 開頭、第一段是萬用字元的 pattern 反而擋得對(base 變 `/`,被判成暫存處的上層)。
未能重現實際讀到暫存處的檔,因為不確定 Glob 引擎是否展開含絕對路徑的大括號選項。
建議:pattern 含 `{` 時,把所有選項各自展開判斷,或直接擋。

### F4 路徑段數上限:結尾斜線多算一段(差一)
severity: minor
blocking: 否 — 只在剛好 256 段加結尾斜線時多擋一次。

引句:「if (parts.length > SEGS_MAX) return null」

類型:誤擋,邊界差一。長度剛好 4096 過、4097 擋(符合註解);段數剛好 256 過、257 擋;但 256 段加結尾斜線時,pop 結尾空段是在比較「之後」才做,所以被擋。實測見 probe.mts(segs 段)。把 pop 移到比較之前即可。

### F5 登記子代理時讀 $.state 失敗,孫代理直接放行,跟工具呼叫那一頭的方向相反
severity: minor
⚠
blocking: 否 — 要 $.state 讀取剛好失敗才會觸發;只讀程式推得,沒實際重現。

引句:「const parent = found === 'error' ? undefined : found」

類型:漏擋。lookup 回 'error' 時,spawn 把 parent 當成不存在,改看孫代理自己派工詞的標記。派工詞若沒有標記就 `next(e)` 放行。而 call() 那頭對 'error' 是「Bash 寧可擋」。審查席派的子代理在此刻會變成無限制,且之後也不會被登記。
未能重現:fakeIo 的 loadSeats 可以改成丟錯來試,我沒有加測試。
建議:'error' 且 parentAgentId 是字串時,視同審查席的子代理繼承,或至少放進 pending 讓之後的 call 走一樣的「Bash 擋」路徑。

### F6 空的 cwd 會讓所有不帶 path 的搜尋被擋
severity: minor
blocking: 否 — 要派工參數給空字串 cwd 才會觸發。

引句:「if (p === undefined || p === null || p === '') base = seat.cwd」

類型:誤擋。派工參數 cwd 若是空字串(型別是 string,會通過 typeof 檢查),seat.cwd 就是空字串,searchBase 回 `/`,Grep 與 Glob 全被判成暫存處的上層而擋下。實測見 probe.mts(最後一行)。

### 圖譜鏡頭
- 機械反查三格皆空(受影響測試、共改夥伴、呼叫者都是 0),圖譜沒有釘到節點,沒有席筆記要逐條判。
- 我只看了外掛清單與市集檔那一側的改動(scripts/lumos 的字串、test_lumos.py 的新測試)。沒發現邊界問題:S10 的「市集列出的外掛恰好是清單那幾支」測試會在清單與市集檔不一致時翻紅。市集檔讀取的實作(BOM、plugins 欄位怪)不在這份 diff 裡,只有測試呼叫,所以我沒判。

總結:最嚴重 minor,blocking 0 條
