severity: major

# r1 正確性席(sonnet)審查報告

對照的程式碼:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`(HEAD f369e9c7)。spec 引用的既有函式與測試名都開檔核過,全數存在(`_probe_parse`、`_probe_value_err`、`_probe_norm_value`、`_drift_cond_split`、`_DriftProbeTree.one/prefetch/unread_for/_read`、`_drift_probe_one/line/cond_candidate/check/judge/scan`、`cmd_drift_scan`、`_retire_lines`、`_drift_split_acked`、`_drift_exam_*`、`t_drift_when_probes_evaluate_and_trigger` 的 ⑨)。文件內的 `[[…]]` 交叉引用目標都在,「漂移防治路線圖」裡確有「另案待開」那句。以下只列照字面實作會做錯事的點。

## 逐節

- 檔頭、白話、依據、PRIOR-ART、RETIRE-IF、REVISIT、範圍:已讀,無 finding。
- 做法 1(條件鍵):C2、C3、C4、C5、C8。
- 做法 2(寫下時就已成立):C1、C6、C7。
- 做法 3(說明與同步):已讀,無 finding。
- 實務隱患:見文末逐類回答;跨環境那條見 C6。
- 驗收條款、回退、天花板:已讀,缺口分別掛在 C1、C3、C6、C8 之下。

---

**C1 往回查用 `git log -S` 找「第一次出現這一行」,會找錯提交**
severity: major
blocking: 是 — 找錯提交就在錯的那一版判「寫下時成不成立」,產出的「從沒提醒過」標記是假的,整個第 11 項的結論不可信
引句:「用 `git log --format=%H --reverse -S<那一行原文> -- <筆記路徑>` 找第一次出現這一行的提交」

1. 做法 2.1。`-S` 比的是「這段位元組在檔裡出現的次數有沒有變」的子字串比對,不是「整行」比對;`--reverse` 取最舊的一筆。兩個具體失敗:
   - 子字串:筆記早期有一行更長的 `REVISIT:[when-file:a.py][by:2027-01-01] 補測試 (舊版較長)`,後來改短成 `REVISIT:[when-file:a.py][by:2027-01-01] 補測試`。短的那行是長的那行的子字串,`-S<短行>` 會把「長行第一次出現」的提交當成答案,在那一版判條件;真正寫下現在這一行的提交根本沒被選到。
   - 同一行寫過兩次:這一行寫下、刪掉(例如當時處理完)、很久以後原樣又寫回來。取最舊的一筆會把第一世的提交當成這一條的出生,第二世寫下時的狀態沒被看。
2. 我在臨時 repo 實驗(`/tmp/rv1x`):c1 寫長行、c2 改成別的內容、c3 寫短行;`git log --format=%h --reverse -S'<短行>' -- n/x.md` 輸出 `f032749 c1`、`db7aef2 c2`、`456c2c3 c3`。三個提交都命中,取第一個是 c1(長行那版),不是 c3。再補 c4 刪掉、c5 原樣寫回,輸出 c1 到 c5 全部五筆,第一筆仍是 c1。
3. 缺的規矩:spec 沒說「`-S` 命中後要再確認那個提交的檔裡真的有逐字相同的一整行」,也沒說同一行多世時取哪一世(現行這一行對應的是最後一次「從無到有」)。驗收條款 S5、S6 也沒有任何一條覆蓋這兩種輸入。
4. 查證佐證:實驗輸出如上;現有程式沒有可借的「逐行第一次出現」輔助。`_probe_lines` 回的原文是 `ln.strip()`(file: `scripts/lumos:32014`),就是要拿去當 `-S` 參數的那一串。

---

**C2 字串「不在全文裡」就算成立,但讀得出來不等於讀對了;誤讀會讓條件提早成立**
severity: major
blocking: 是 — 這是唯一一個「讀壞了就觸發」的條件鍵,spec 只保護「讀不出」,沒保護「讀出垃圾」
引句:「字串不在全文裡 → 成立」

1. 做法 1.2。其他四個鍵都是「等東西出現」:讀壞了只會讓條件不成立(安全方向)。`when-gone` 反過來,「找不到」就是「成立」,所以任何讓字串變得找不到的誤讀都變成假觸發。spec 只處理了 `_read` 回 None(讀不出)。
2. 具體輸入:`[when-gone:legacy/old.sql::tmp_audit]`,目標檔是 Big5 或 UTF-16 編碼。`_DriftProbeTree._read` 用 `_drift_decode`(`utf-8-sig`、`errors="replace"`)解碼,不丟錯、不回 None;UTF-16 檔解出來每個字元後面夾 NUL,字串永遠找不到 → 照字面實作回成立。另一例:檔被換成 Git LFS 指標檔(內容只有 `version https://git-lfs…`)或 git-crypt 加密檔,同樣讀得出、字串找不到、成立。
3. 這個不對稱 spec 沒講:實務隱患只寫了「帶字串時讀一支檔(同帶路徑的 symbol,有預讀)」,沒承認 symbol 的讀壞是安全方向、gone 不是。驗收條款 S1 只有「檔讀不出 → 判不了」。
4. 查證佐證:`scripts/lumos:32180-32183`(`_drift_decode`)、`scripts/lumos:32270-32290` 一帶的 `_read`(disk 模式只在 `OSError` 時記 None,git 模式只在 blob 為 None 時記 None)。

---

**C3 「路徑不在樹上」把目錄、符號連結、子模組、被忽略的檔全判成「已經消失」**
severity: major
blocking: 是 — 檔明明在,條件卻立刻成立,而且既有的 `when-file` 有的防呆(指到資料夾要提醒)沒有被列進這次要改的地方
引句:「路徑不在樹上 → 成立;帶字串時讀那支檔」

1. 做法 1.2。`_DriftProbeTree.files` 只裝「一般檔」(mode 100644/100755);`_nodehome_list` 明文把連結檔(120000)與子模組(160000)排除在一般檔之外,`_drift_disk_list`(scan 預設走的 disk 模式)又排除符號連結與 `.gitignore` 掉的檔。照字面實作 `v not in self.files` 就回成立。
2. 具體輸入:
   - `[when-gone:vendor/lib]`,`vendor/lib` 是子模組或是目錄 → 沒有任何一個「檔」叫這名字 → 當下就成立。`[when-gone:src/old/]`(尾斜線)同理,而且 `_probe_bad_path` 不擋尾斜線。
   - `[when-gone:build/out.js]`,檔被 `.gitignore` 掉(磁碟上有、git 樹上沒有)→ scan 看 disk 清單排除被忽略的檔 → 成立;推送看提交的樹 → 也成立。作者寫的是「等這支產物檔消失」,工具永遠說已經消失。
3. 既有的 `when-file` 有補這個洞:`_drift_probe_row_problems` 對 `file` 指到資料夾會報「指到資料夾(要指一支檔)」。spec 的做法 1 列了要動的函式,但沒有列 `_drift_probe_row_problems`(與 `_drift_probe_path_warn`);結果是 `when-gone` 的目錄寫法沒有任何提示,只會在推送時被說「已經成立」,作者看不出是自己指到了目錄。
4. 驗收條款沒有任何一條覆蓋目錄、連結、子模組、被忽略檔。
5. 查證佐證:`scripts/lumos:26222`(只有 100644/100755 進 `files`)、`scripts/lumos:32141-32142`(disk 清單排除符號連結)、`scripts/lumos:32641-32643`(file 指到資料夾的提示,只認 `k == "file"`)。

---

**C4 字串裡的反引號會被剝掉,實際比對的字串不是作者寫的那一串**
severity: major
blocking: 是 — 文法只禁 `]` 與換行,沒禁反引號,而條件解析前一步會把反引號整段剝掉,字串被悄悄改寫
引句:「字串去頭尾空白後不能是空的,不能含 `]` 與換行(既有標記的切法)」

1. 做法 1.1。條件是從 `_probe_lines` 來的,它在解析前先對整行做 `_strip_inline_markup`:成對反引號的內容整段刪掉,不成對的反引號之後整段截掉。`when-gone` 的字串是程式碼片段,含反引號很常見(JS 樣板字串、shell 的 `` `date` ``、Markdown 範例)。
2. 具體輸入(我用 `when-file` 當替身跑 `_probe_lines`,走的是同一段解析):
   - `REVISIT:[when-file:src/a.py::x `a` y][by:2027-01-01] 追蹤2` → 解出的值是 `src/a.py::x  y`(中間兩個空白)。換成 `[when-gone:src/a.py::x `a` y]`,比對的字串是 `x  y`,檔裡不會有這串 → 條件寫下就成立,推送被點名「已成立」,作者看不出為什麼。
   - `[when-gone:src/a.py::echo `date`]` → 比對的字串縮成 `echo`,幾乎永遠還在,條件永遠不成立,而且沒有任何提示。
   - 不成對的反引號 → 後面的 `[by:…]` 一起被截掉,報「沒帶期限」,錯誤訊息跟真正原因對不上。
3. 同時 scan 往回查用的是未剝的原文 `ln.strip()`(見 C1),「解析用剝過的、找提交用沒剝的」兩邊不一致。
4. 查證佐證:實驗輸出(行 7 解出 `src/a.py::echo`、行 8 解出 `src/a.py::x  y`);`scripts/lumos:368-377`(`_strip_inline_markup`)、`scripts/lumos:32012-32014`(`_probe_lines` 先剝再解析)。

---

**C5 「共用同一支拆條件」的清單漏了驗證那支,另有兩處讀鍵的地方沒列**
severity: minor
blocking: 否 — 漂移風險與過時文字,不會讓當下的判定做錯,但這個 repo 的代碼審歷史已經因為同一件事連修三輪
引句:「判定、預讀、點名讀不出的檔、候選篩選、正規化共用它」

1. 做法 1.1 把共用 `_drift_gone_split` 的點列成五個,做法 1.4 另寫「值驗證走一支新的 `_probe_gone_err`」,但沒有說 `_probe_gone_err` 也用 `_drift_gone_split`。`_drift_cond_split` 的 docstring 明講過「原本四處各自 rsplit,點名的範圍跟判定的範圍連三輪對不上」。驗證那支自己切一次,就是第六處。
2. 其他讀條件鍵、spec 沒提的地方:
   - `_slot_retire_err` 的最後一句 `不是機器式(只收 when-file/when-symbol/when-test/when-status、度量、人裁)`(`scripts/lumos:3891`)與 RULE 範本 `[retire:when-file:路徑]`(`scripts/lumos:28371`)。做法 1.4 說「RULE 的撤除條件…自動支援,不另寫」,功能上對(`_slot_retire_err` 呼叫 `_probe_value_err`),但提示文字仍只列四個。
   - `_probe_parse` 裡 `val.replace("\\", "/") if k in ("file", "symbol", "test")`(`scripts/lumos:31982`):spec 沒說 `gone` 要不要進這個元組。⚠ 加進去會把字串裡的反斜線(例如要等 `\n` 字面消失)也改掉;不加,路徑裡的反斜線要靠後面「正規化後再驗一次」才接得住。字面實作兩種都說得通。
3. 查證佐證:上列行號。

---

**C6 淺層 clone 的處理兩處講法不一致,而且沒有驗收條款**
severity: minor
blocking: 否 — 影響的是標記的呈現與 CI 行為,不是閘的判定
引句:「標成判不了寫下時成不成立(淺層時不往回查)」

1. 〈實務隱患〉跨環境:淺層時「標成判不了寫下時成不成立」;〈天花板〉第 4 點:「淺層 clone 不往回查」。前者每條成立的條件都要出一個 `born: "unknown"`,後者讀起來是不標、不查。S5、S6 都沒有淺層的情境(S6 只列「找不到提交或超過預算」)。
2. 偵測手段 spec 沒指名。repo 已有 `_git_is_shallow(root)`,可以直接用;但另一種淺層的失敗沒處理:`--depth N` 的淺層裡,第一次出現的可能剛好是邊界提交(邊界提交把全部檔案當新增),被判成「寫下時就已成立」。spec 想靠「淺層時不往回查」擋掉,前提是淺層判定先做,順序沒寫。
3. 查證佐證:`scripts/lumos:5549`(`_git_is_shallow`)。

---

**C7 `git log` 的路徑、起點版本沒指定,標記的字面比實際查到的強**
severity: minor
blocking: 否 — spec 已在天花板 2 承認改名的部分,其餘是沒講清楚的實作前提
引句:「只看這一篇的歷史;筆記改過名就在改名後的第一個提交找到」

1. 做法 2.1 的 `-- <筆記路徑>`:`_drift_probe_scan` 回的 `path` 是相對圖譜資料夾、而且已 NFC 正規化的路徑。`git log` 要的是相對 repo 根的路徑,得補上 `vault_rel`;且 `_drift_vault_rel(root, sha)` 這支存在的原因就是圖譜資料夾改過名。圖譜資料夾改名之前的歷史,路徑限定的 `git log` 看不見,第一次出現會落在改名那一刻。
2. NFD 路徑:`_nodehome_name_status` 的 docstring 明講「NFC 過的路徑對 NFD 樹查不到」。本 repo 大半是中文檔名;用 NFC 路徑去限定一個以 NFD 存的檔,`git log` 回空 → 全部標成判不了。
3. `scan --at <提交>` 的情況:spec 沒說 `git log` 要以 `<提交>` 為起點,不指定就是從 HEAD 往回。
4. 標記字樣:找到的是「改名後第一個提交」(天花板 2)或「圖譜改名那一刻」,輸出仍寫「寫下時就已成立(提交 <短碼>)」並說「從沒提醒過」。作為事實陳述它比實際查到的強;天花板 2 只在 spec 裡講,輸出給讀的人看不到。
5. 查證佐證:`scripts/lumos:26440-26442`(norm=False 的理由)、`scripts/lumos:34906-34913`(`--at` 用那個提交自己的圖譜位置)。

---

**C8 檔被改名或搬家時,帶字串的 `when-gone` 會因為「檔不在」成立,字串其實還在**
severity: minor
blocking: 否 — 誤擋的方向,作者可表態,但規則沒提也沒測
引句:「那支檔不在、或檔裡不再出現這段字(照字面、分大小寫、整檔比對,含註解)就成立」

1. 做法 1.1 把「檔不在」與「字串不在」都算成立,帶字串的寫法也一樣。作者寫帶字串的 `when-gone`,意思是「這段字不要再出現」。
2. 具體情境:`[when-gone:src/a.py::time.time()]`,之後有人把 `src/a.py` 改名成 `src/core/a.py`,內容原封不動。推送判定:路徑在改到的檔裡(改名兩端都算,`_nodehome_name_status`),終點樹上沒有 `src/a.py` → 「這次推送讓條件成立了」。字串其實一個字都沒少。
3. 天花板 3 只講了同義改寫會提早成立,沒講搬家;驗收條款 S1、S2 沒有改名情境。
4. 查證佐證:`scripts/lumos:26447-26452`(改名兩端都進 touched)、`scripts/lumos:32430-32436`(候選只看路徑在不在 touched)。

---

## 實務隱患鏡頭(逐類)

- 併發:無。`scan` 與推送判定都是唯讀(讀 git 物件與磁碟,不寫帳);spec 在 `cmd_drift_scan` 的現況也成立(讀指令不寫帳)。一點小補充:scan 預設讀工作目錄,不是只讀 git 物件,不影響結論。
- 效能(往回查、建歷史樹、推送判定多一種鍵):我實測了。本 repo 最大的筆記 34 個提交,`git log --reverse -S` 找不到的字串 0.05 秒;任選 HEAD~50 建圖譜環境 0.19 秒、建樹 0.005 秒(638 篇筆記、8.6MB)。「成立的條件通常是個位數」的量級在這個 repo 沒問題。spec 沒寫的是單次 `git log` 的逾時要用剩餘預算算,以免單次卡住吃光預算;預算不足時的處理 spec 已寫(判不了),所以這裡不另開 finding。推送判定多一種鍵,候選篩選靠路徑在不在 touched,成本跟 symbol 帶路徑的寫法相同,成立。
- 回滾:對。還原後 `gone` 變成不認得的鍵 → `_probe_value_err` 回錯、`_probe_parse` 標 `bad`,`_drift_probe_check` 與 `_drift_probe_scan` 都過濾掉 `bad`(`scripts/lumos:32459`、`:32669`)。無資料要收。
- 誤擋與繞過:誤擋見 C2(誤讀)、C3(目錄、連結、子模組、忽略檔)、C4(字串被改寫)、C8(改名)。繞過:spec 寫「表態照留」,表態檔機制本來就有(`_drift_split_acked`),對。
- 金流、對外送出、不可逆:無。理由同 spec:只讀、不呼叫網路、還原提交就回去。
- 守衛面:新鍵加進推送判定;候選篩選與轉變判定的結構沒動,風險集中在上面四條 major,而這四條都出在「條件值怎麼被讀成一個字串、怎麼算成立」,不在轉變判定本身。

---

最高 severity:major;blocking 共 4 條(C1、C2、C3、C4)。
