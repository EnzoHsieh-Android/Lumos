severity: major

核對範圍:殺傷力配方修補體驗計劃的〈做法〉三條與〈條款〉S1~S3,在我自己的 clone 跑現有 guard kill / kill-add / kill-rm 驗前提。kill-rm 列出尚未實作,所以列出那段是照 spec 字面加讀 `_kill_read_recipes`、`_kill_show`、`_kill_recipe_id` 推演。
各節:範圍、回退、實務隱患已讀無 finding(「guard kill 的判法、回傳碼、`--json` 輸出內容(`recipe_id` 欄本來就有)都不改」與程式一致)。

## F1 S3 與做法 3 把「格式壞的配方」當成 guard kill 印得出結果行,但 guard kill 遇到不是物件、file/invariant/new 型別錯的配方會直接崩潰,根本印不出結果行
severity: major
blocking: 是
引句:「配方格式壞時(缺 old、file 是數字)跟 kill-rm 用的 `_kill_recipe_id` 不同」
file: `scripts/lumos:13964`
1. 我在 clone 實測現有 guard kill:`kill_recipes` 含不是物件的元素(如 `3`)時,在分組那行 `r.get("platform")` 就丟 AttributeError(`scripts/lumos:13792`);`file` 是數字時,在 `os.path.join(wt, r.get("file",""))` 丟 TypeError;`invariant` 是數字時,worktree 跑完後才在人讀輸出那行 `r.get('invariant','')[:30]` 丟 TypeError(`scripts/lumos:13964`);`new` 是數字時在 `src.replace(r["old"], r["new"], 1)` 丟 TypeError(`scripts/lumos:13877`)。四種都是 rc1、沒有任何結果行(崩潰在印出之前或印到一半)。
2. 所以 spec 舉的例子「file 是數字」就是會崩潰的那一型;S3「格式壞的配方也一樣」的 [test:t_guard_kill_prints_recipe_id] 只要用 spec 舉的壞法造資料,就會得到崩潰而不是 `id=`,測試寫不出來,或實作者為了讓它綠而順手改 guard kill 的判法(與〈範圍〉「guard kill 的判法、回傳碼…都不改」衝突)。
3. 能印出結果行的壞形狀只有:缺 old(判 drifted、old 命中 48 次的怪行為)、缺 test(error)、platform 是數字(error)。spec 應明講 S3 的「格式壞」只涵蓋這幾型,並對崩潰型改說:這些配方 guard kill 本來就印不出行,要查身分靠 kill-rm 不帶 --id 的列出(S2 已涵蓋)。
4. 連帶:缺 old 時 `_kill_recipe_key(old=None)` 與 `_kill_recipe_id` 的壞格式雜湊不同(spec 已提),但崩潰型根本沒有 `recipe_id`,spec 〈做法〉理由裡「格式壞時兩者不同」的敘述對崩潰型是空話。

## F2 kill-rm「沒帶 --id」的判定若用「值為空」會讓 `--id ""` 由 rc2 變成 rc0 列出
severity: minor
blocking: 否
引句:「`cmd_guard_kill_rm` 開頭先分流——沒帶 `--id` 走唯讀列出(不拿寫入鎖、不寫檔),帶了照既有驗證與移除」
file: `scripts/lumos:13516`
1. 現況 `--id ""` 會過 argparse,落到 `re.fullmatch` 擋下回 2(我實測,訊息「收到 ''」)。
2. 分流若寫成 `if not rid` 而不是 `rid is None`,腳本 `kill-rm 筆記 --id "$ID"` 在變數為空時,以前 rc2 擋下,現在印一堆列出、回 0,被當成移除成功。spec 沒定義「帶了但是空字串」。建議條款明寫:只有參數整個沒出現(None)才列出,空字串照舊擋下回 2,並加一個斷言。

## F3 列出那一行對缺欄位、型別錯的配方,「old 前 30 字」與 `_kill_show` 的先後沒定義,字面實作會在 S2 要求的壞配方上崩潰或印出誤導字樣
severity: minor
blocking: 否
引句:「`<短身分前 12 字元>  平台 <platform 或預設>  檔 <file>  原文 <old 前 30 字>  test <test>`,各欄經 `_kill_show`(會帶引號)」
file: `scripts/lumos:13056`
1. 做法先寫「old 前 30 字」再說各欄經 `_kill_show`:若照字面先切片 `old[:30]`,`old` 是數字(spec 自己說格式壞的要列出)會 TypeError;若是物件缺 old,`r.get("old")` 是 None,`_kill_show(None)` 印出 `"None"`,看起來像原文就是字面 None。file、test 缺欄同樣印 `"None"`。
2. 先切片再跳脫還是先跳脫再切片也沒定:`_kill_esc` 會把控制字元展開成 6 字元的 `\uXXXX`,先跳脫再切會把跳脫序列切到一半,印出殘缺的 `\u20`。
3. 「平台 <platform 或預設>」:guard kill 用 `r.get("platform") or override or default`,所以 `platform` 是空字串、null 都算預設;若實作用 `r.get("platform","預設")`,空字串會印成 `""`、null 印成 `"None"`。「預設」要不要加引號(每欄都經 `_kill_show`)也沒說。建議寫明:欄位缺或型別錯一律印固定字樣(如「(沒寫)」),先轉字串再切 30 再跳脫。

## F4 同一身分的重複配方,列出時會印出多行同一個短身分,卻沒說明移除會一起拿掉
severity: minor
blocking: 否
引句:「最後印一句「移除:lumos guard kill-rm <節點> --id <短身分>」。」
file: `scripts/lumos:13540`
1. 既有行為:對到的全是同一完整身分就一起移除(`_guard_kill_rm_locked`)。同身分(invariant、file、old 相同)但 new、test、platform、covers 不同的兩條,列出會是兩行同一個 12 字元身分,只有 test 欄可能不同。
2. 人看列出想只移其中一條,照印的指令移除會兩條都沒了(此時範本與完整內容才在移除前印出,而且沒有確認步驟)。我實測 `[R(), R(new=...)]` 兩條 guard kill 各印一行、身分相同。建議列出時對重複身分加標記(例如「同身分 N 條,移除會一起拿掉」),並在 S2 加一條重複配方的斷言。

## F5 S3 把 `id=` 放在原樣印出的 `[<test>]` 之後,人寫的 test/invariant 可以偽造出另一個 `id=`,或把結果行拆成多行
severity: minor
blocking: 否
引句:「每條結果行在 `[<test>]` 之後、說明之前加 `id=<短身分>`(說明可能很長,放後面會被吃掉)」
file: `scripts/lumos:13964`
1. 我實測:`test` 設為 `X\n  id=deadbeefdead` 時,guard kill 判 error(test 名不合法),人讀輸出是 `⚠ error 上限恆為5 [X` 換行 `  id=deadbeefdead] test 名不合法…`,偽造的 id 出現在真正 id 之前;`invariant` 含 ESC 與換行時整段原樣印出(rc0 的正常 killed 也一樣)。
2. 這是既有的原樣輸出問題,但 spec 新增了一個機器與人都會照抄去 `--id` 的欄位,又只在 S2 要求「人寫的欄位不應原樣印出控制字元」,S3 沒要求。實務隱患宣稱「加 id 後仍單行」只在合法欄位成立。S3 的測試若用 `re.search(r"id=([0-9a-f]+)")` 取第一個,碰到上述輸入會取到偽造值。建議條款要求 S3 測試取最後一個 `id=`,或把 test、invariant 也過 `_kill_esc` 並明說會改到既有人讀輸出。

## F6 範本 `--new` 改成待填後,kill-add 會原樣把待填字樣寫進筆記,而且沒有任何提醒
severity: minor
blocking: 否
引句:「`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`(現在是把舊壞法原樣抄進去)」
file: `scripts/lumos:13484`
1. 我實測:`kill-add … --old "n <= LIMIT" --new "<照新原文改寫的壞法>"` 回 0、寫入成功,沒有任何提醒(kill-add 的失配提醒只驗 old 的出現次數,不看 new)。之後 guard kill 判 `killed_unattributed`(紅燈來自把待填字樣塞進程式造成的語法錯,不是綁定測試),全部都是這種就 rc1。
2. 以前人只填 old 忘了 new,至少寫進去的是上一版壞法(通常仍是有效的壞法);改成待填後,漏填 new 的失誤會寫成一條永遠假紅的配方。`--old` 的待填有 0 次命中提醒擋著,`--new` 沒有。建議 kill-add 對 `--new` 含 `<照新原文改寫的壞法>` 字樣擋下或提醒,或在〈實務隱患〉明講這個缺口並記回頭條件。
3. 另外 S1 說範本「不應出現舊配方的壞法原文」:範本其他欄位原樣抄(`--note`),note 常寫「壞法是把 5 改成 99」這類描述,會把舊壞法帶進範本;S1 的測試資料若 note 空白就看不出,字面條款比實作能保證的強。建議把條款限縮成「`--new` 欄位」。
4. covers/note/platform/test 的各種組合我逐一核對,既有 `ok()` 控制字元佔位邏輯不受影響,`val("new",…)` 的 `'<壞法>'` 佔位字樣改完後成為死分支,實作時順手刪。

最高等級:major;blocking 共 1 條
