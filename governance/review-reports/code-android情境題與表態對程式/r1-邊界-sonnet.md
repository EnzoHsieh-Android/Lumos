severity: major

我在 `/tmp/lumos-seat-work/code-android情境題與表態對程式/邊界-sonnet/` 下建了臨時 repo 與腳本,載入 `scripts/lumos` 實際跑過。沒有動 repo。

下面的行號是 patch 內的行號,另一邊是 repo 內的檔案行號。

### F1 切段讀 `git diff -U0` 沒有釘住輸出參數,使用者的 git 設定會讓整段消失
severity: major
blocking: 是

引句:「r = _sp.run(["git", "-c", "core.quotePath=false", "diff", "--no-ext-diff", "--no-textconv", "-U0", diff_range, "--", "*.kt"],」

位置:patch 第 384 行,對應 `scripts/lumos` 的 `_kt_sit_hunks`。解析迴圈只推進 `+` 行的行號,不認得脈絡行(第 402 行附近)。

repo 內已有同類防護,新碼沒用:
- `scripts/lumos:46973` 的 `_DIFF_PIN_HUNK_ARGS` 就是為了釘 hunk 形狀。
- `scripts/lumos:61187` 的註解寫明要固定前綴,否則 `diff.noprefix` 會讓檔名抽不出來。

重現:
- 輸入:`Vm.kt` 有 7 行,第 3 行改成 `val x = coroutineScope { }`,第 7 行改成 `val t = supervisorScope { }`。範圍是 `h0..h`。
- 預設設定:`[('Vm.kt',1,6,['D-1','D-8']), ('Vm.kt',4,9,['D-9'])]`,兩段都在。
- 加 `git config diff.interHunkContext 10` 後:只剩 `[('Vm.kt',1,6,['D-1','D-8'])]`。D-9 那段消失。
- 原因:`-U0` 的 hunk 被併起來,中間的脈絡行不推進 `new_ln`,第二個命中行算成第 4 行,而第 4 行沒有觸發字。
- 加 `diff.noprefix=true`、`color.ui=always` 或 `color.diff=always`:全部回傳 `[]`,整題消失。

後果:段被吃掉後,`_kt_sit_verdict_one` 對「切不出段」視同不適用,表態核對直接放行,什麼都沒核。`diff.noprefix` 與 color 兩種,旁邊的 `_pitfall_diff_collect` 也同樣會壞,只有 `interHunkContext` 是新碼獨有。

### F2 D-20 的標準寫法(建構子注入 dispatcher)答不出對得上的證據
severity: major
blocking: 是

引句:「if pth != sg["file"] or not sg["start"] <= ln <= sg["end"]:」

另一處引句:「if not re.search(pats[0], sg["_code"].get(ln, "")):」

型錄 `skills/kotlin-idioms/checks-catalog.md:690`(D-20)的標準寫法是「dispatcher 從建構子注入」。它的觸發字只有 `CoroutineDispatcher`,證據樣式第一條是 `\bwithContext\(\s*\w*[dD]ispatcher\s*\)`。

重現輸入:`UserRepository.kt` 新檔,建構子在第 5 行 `private val ioDispatcher: CoroutineDispatcher,`,第 12 行 `return withContext(ioDispatcher) {`。

實際輸出:
- 切出的段是 `start=2, end=8`,命中行只有第 5 行。
- 把 evidence 依序填 `UserRepository.kt:2` 到 `:8`,每一個都回「D-20(main)證據樣式對不上:第一條 … 不在 evidence 那一行」。
- 第 12 行在段範圍外,填它會回「不在段範圍」。
- 照型錄寫的正確程式,只要建構子與 `withContext` 相隔超過 3 行,main 就無解。
- 剩下的出路是選 alt(D-20 的 alt 是 `(無)`,什麼行都過),或誠實度更差的 `applies:false`。
- 同族疑慮:D-3 觸發字是 `Semaphore` 等,main 第一條卻要 `\.awaitAll\(\)` 在同一行 ±3 行內。我沒有逐列跑,未能重現。

### F3 D-1 的 main 擋住帶 dispatcher 的 `async`,而這列又不准選 alt
severity: major
blocking: 是

引句:「if not re.search(pats[0], sg["_code"].get(ln, "")):」

輸入:`suspend fun f() = coroutineScope { val a = async(Dispatchers.IO) { api.a() } ; val b = async(Dispatchers.IO) { … } ; Ui(a.await(), b.await()) }`。這是 D-1 的標準寫法,只多了 dispatcher 參數。

實際輸出:段 `1-5`,把 evidence 填 `A.kt:1` 到 `:5`,全部回「D-1(main)證據樣式對不上:第一條 `\basync\s*\{` 不在 evidence 那一行」。

D-1 的 `switch` 為真,選 alt 會回「不准選 alt」。正確寫法只剩 `applies:false` 一條路,也就是被逼著說謊。`\basync\s*\{` 應放寬成能接 `async(…)` 與 `async<T>`。

### F4 檔名含雙引號的 `.kt` 被切段略過
severity: minor
blocking: 否

引句:「cur = _diff_header_path(line, "b")          # 整檔刪除是 +++ /dev/null → None,這支不收」

輸入:新增 `app/q"uo te.kt`,內容有觸發字。實際輸出:`a b.kt`、`sp.kt`、`tab\tx.kt`、`é.kt`、`我 的 Vm.kt` 都切出段,只有這支沒有。git 的檔頭是 `+++ "b/q\"uo te.kt"<TAB>`。我沒有確認根因,推測是引號加尾端 tab 的組合還原失敗。這種檔名很罕見。

### F5 git 失敗或版本讀不到時,結果是「靜默沒有段」而不是「無法驗證」
severity: minor
blocking: 否

引句:「hunks = _kt_sit_hunks(repo_root, diff_range) or {}」

另一處:「        text = _kt_sit_read(repo_root, at_sha, rel)」

輸入與輸出:
- 範圍 `nope..alsonope` 回 `[]`。
- 範圍正常、`at_sha` 傳不存在的 sha(`0123…4567`)也回 `[]`。
- 沒帶 `at_sha`,但檔案不在 base 版本,同樣回 `[]`。
- 上面三種都讓 `_kt_sit_verdict_one` 回 `None`,也就是放行。

知識圖譜 `Systems/棧別提問表態閘.md` 寫的是「核對每題包例外→無法驗證擋下不 fail-open」。逾時有守住,git 非 0 離開與讀不到版本沒有。

### 其他鏡頭的結論(跑過、沒有發現)

**Kotlin 怪寫法**
- 巢狀註解、未閉合的區塊註解、`"""` 內有 `"`、`"${ if (a) "x" else "y" }"`、`'"'`、`'\''`、註解裡的 `{`、`"${foo("}")}"`:剝法都正確。
- 反引號識別字的內容照留,與設計一致。
- 4000 筆隨機 Kotlin 記號組合丟進 `_kt_sit_file_segments`:零例外,最慢 4 ms。
- 5000 行檔、5000 行單一函式:約 1 到 2 秒。
- 30 萬個 `{` 的超長單行約 3.6 秒;10 萬個巢狀 `/*` 約 11 秒;10 萬個字串約 8 秒。後兩者是人造的極端輸入,不當 finding。
- CRLF、BOM、Tab、無結尾換行、二進位 `.kt`、非 UTF-8 位元組都不爆。
- `.kts` 不在 pathspec,不會被切段。

**決策表讀取**
- 欄位順序換、多一欄、列號跳號、壞正規式、缺節、空檔、CRLF、BOM、`(停用)` 列:都回明確的原因字串。
- `LUMOS_KT_CATALOG` 指到不存在的檔、目錄、`/dev/null` 或二進位檔:都不會讓 import 掛掉。

**表態檔**
- 錯一字的 seg、`4-5` 範圍、行號 0 或超出段範圍、variant 大小寫錯、`applies` 為字串、`auto` 加 `na`:都被擋。
- `seg` 寫成清單(不可雜湊)時 `_kt_sit_check` 會丟 TypeError,但被外層 `except Exception` 接成「無法驗證」擋下,行為正確。

**圖譜**
- 我另外用 `pitfalls --diff` 與 `--dispositions-template` 跑通了端到端,段與樣板正常。

總結:最嚴重是 git 輸出參數沒釘住導致整段漏擋(另有 D-20 與 D-1 的標準寫法答不出證據),會擋 3 條。
