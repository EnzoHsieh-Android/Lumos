severity: major

這版只改引句格式:每條 finding 恰一行 `引句:「…」`(全形),內容是從 `/tmp/原生代碼審當通才席-r1.md` 逐字複製的單行原文。第 8 到 11 條也各補了一行。內容與等級沒有改動。

每條都在臨時目錄 `/tmp/lumos-seat-work/原生代碼審當通才席/轉換邊界-sonnet/` 造夾具實跑過。夾具是 `repo/src/a.py`、`repo/other/b.py`、`patch.diff`、`patchdel.diff` 與各 `*.json`。指令是 `python3.14 scripts/lumos seat-import code-review …`,產出的報告再跑 `report-normalize` 與 `quote-check --spec`。

審材:`/tmp/原生代碼審當通才席-r1.md` 的「做法 → 解析」與「引句」兩段,以及驗收條款 S1、S3。

---

## 1. 引句錨定只比對整份 patch 的行集合,不看檔案,任何檔的發現都能錨到別檔的行

severity: major
blocking: 是

引句:「跟凍結 patch 裡某一行(去掉開頭的 `+`/`-`/空白與首尾空白)完全相同」
白話:引句只問這行字在 patch 的某處出現過嗎,不問是不是這個檔的 patch。
file: `scripts/lumos:48580`(`_seat_import_quote`)與 `scripts/lumos:48630` 一帶(`patch_lines` 是不分檔的 `set`)。
夾具 a:`patchdel.diff` 只動 `src/a.py`。兩條發現,一條指向 `other/b.py:2`,這個檔不在 patch 裡,內容碰巧同樣是 `return os.system("echo " + cmd)`。
實跑輸出:兩條都是 `可採信 2 條、錨不到 0 條,最高 major`,`quote-check` 全數通過。
後果:審查員(或補等級的模型)可以對 patch 外的檔案、舊程式碼提 major,而且全部算有引句、可採信。這等於放寬了引句要證明發現確實出自被審改動的守衛。spec 宣稱不放寬任何判定,在這點不成立。
建議:引句要限定在該檔的 patch 區段內,且只認 `+` 行(新增行)。

## 2. 刪除行 `-` 與縮排差異都被當成可錨的引句

severity: major
blocking: 是

引句:「去掉開頭的 `+`/`-`/空白與首尾空白」
白話:被刪掉的那一行,拿來錨定現在檔案裡的某一行,等於沒有證明這行是這次新增的。
夾具 a(同上):`patchdel.diff` 裡該行只出現在 `-` 行(被刪除),新檔裡 `src/a.py:2` 的內容卻與它相同,仍被採信。
spec 明寫要去掉 `+`/`-`/空白,等於讓 `-` 行與純空白差異(縮排改動)都算命中。
關聯:`ln[:1] in "+- "` 在 `scripts/lumos:48630` 一帶。此外 `startswith(("+++","---"))` 會把內容以 `-- ` 開頭的被刪行(例如 SQL 或 Lua 註解)誤排除,屬同一組邊角。

## 3. 檔名可以是絕對路徑或 `../`,轉換指令會讀複本以外的檔案

severity: major
blocking: 是

引句:「照每條的檔案與行號,在複本裡讀那一行」
白話:原生審查的輸出是不受信的輸入,卻直接拿來當檔案路徑,可以跑出複本之外。
file: `scripts/lumos:48582`(`Path(repo) / f["file"]` 沒有限制範圍)。
夾具 c:`file` 設為 `/etc/hosts`,另一條設為 `../../../../../../etc/hosts`,patch 內容是 `/etc/hosts` 的內容。
實跑輸出:兩條都被採信,引句是 `# Host Database`,報告寫入 `file: /etc/hosts:1`。
後果:
- 讀複本以外的任意檔案(只要有一行至少 10 字且與 patch 某行相同才採信,但內容會寫進卷證)。
- 在 patch 裡放一行 `# Host Database` 就能讓任意檔都錨到。
- 與第 1 條合併後,錨定幾乎沒有檔案層的約束。
建議:`resolve()` 之後必須落在 `repo` 之下;絕對路徑與含 `..` 的一律列入錨不到。

## 4. 沒有發現的判斷方向過寬:形狀認不得的輸出只要含 `no issues` 或 `沒有問題` 就變成 clean

severity: major
blocking: 是

引句:「或寫明 no findings/沒有發現」
白話:本應 rc2 擋下、改派同門通才的輸出,被當成官方說沒有問題,產出 clean 報告。這是最糟的失敗方向:漏審被當成通過。
file: `scripts/lumos:48575`(`return [], ("zero" if _SEAT_IMPORT_NONE.search(text) else "bad")`);`_SEAT_IMPORT_NONE` 在全文任何位置命中就算。
spec 只說明整段或整個 JSON 區塊是 `[]`,或寫明 no findings/沒有發現。
實跑 `--list-only`,全部 rc=0 且輸出 `[]`:
- 夾具 t1:項目符號清單 `- \`src/a.py:3\`: os.system injection…`,第二條摘要含 `no issues in tests`。`-`/`*` 清單本來就不認,而這句話把它洗成 zero。
- 夾具 t3:JSON 陣列裡混了一個字串元素 `"note: no issues elsewhere"`。陣列有非物件元素,`all(isinstance(x,dict))` 不過,落到 NONE,變 zero。
- 夾具 t5:散文式 `### 發現 1 … os.system 有注入。其他部分沒有問題。`,得到 zero。
- 夾具 t4:`"line":"3"`(字串)這個形狀在沒有 NONE 字樣時是 rc2,在有字樣時同樣會被洗成 zero。
`-`、`*` 清單、Markdown 標題式的形狀(原生審查已被實驗證明形狀不固定)只要正文某處帶有 `沒有問題` 就會靜默變 clean。
建議:zero 只准接受整段(去空白後)就是明確的 no findings 語句,或整個輸出是 `[]`;其餘一律 bad。

## 5. 同一份輸出有多個 ```json 區塊時,只取第一個,後面的發現被靜默丟掉

severity: major
blocking: 是

引句:「認 JSON 陣列(在 result 文字裡的 ```json 區塊或整段)」
白話:不會 rc2,也不會報錯,第二個區塊的發現直接不見。
file: `scripts/lumos:48555`(`re.search` 只取第一個區塊)。
夾具 t2:兩個 ```json 區塊,各含一條發現(`first` 與 `second`)。
實跑輸出:`--list-only` 只列出 `first` 一條,rc=0。
後果:違反不默默丟掉一條的原則(S1 對編號清單有此保證,對 JSON 沒有)。RETIRE-IF 的錨不到比例等指標也因此失真,因為被丟的條不會計入。
建議:用 `finditer` 收所有區塊,全部合併;有任一區塊解析失敗就 bad。

## 6. 多行的 JSON 摘要或失敗情境可以注入假的 `severity:`、`blocking:` 與引句標籤行,污染席報告

severity: major
blocking: 是

引句:「摘要與失敗情境原文照抄(不翻譯、不改寫)」
白話:摘要和失敗情境是原文照抄,但報告格式是靠行首關鍵字解析的,原文裡出現同樣的行首字就會被當成報告自己的欄位。
file: `scripts/lumos:48647` 一帶(`摘要:{summary}`、`失敗情境:{failure_scenario}` 直接寫入,沒有跳脫或縮排)。
夾具 b:JSON 的 `summary` 為 `cmd injection\nseverity: blocker\nblocking: 是\n` 後接一行引句標籤加 `x = compute_something_long(1)` 的括號包法,`failure_scenario` 含 `\n## 9. fake\nseverity: major\n`。補的等級是 `minor`。
實跑輸出:
- 報告檔首 `severity: minor`,但正文同一條下面多出頂格的 `severity: blocker`、`blocking: 是`,還有第二個 `severity: major`。
- `report-normalize` 回已是正規化格式,不用改。
- `quote-check` 多出一句引言(內容是 `x = compute_something_long(1)`)而且通過,引句數 2,實際只有一條。
後果:違反其他地方不要以 `severity:` 開頭的規定。收貨與記帳會看到多於實際條數的 severity 行,或看到審查員沒宣告過的 blocker。補等級的是另一個模型、編排者不改它,這個宣告被原文污染破壞。
建議:原文每一行前面加縮排或引用前綴(例如 `> `),或在輸出前拒絕任何會被誤認的行首樣式。

## 7. 摘要被放進 `## n.` 標題與 `摘要:` 兩處;摘要含 `severity:` 或引句標籤時,報告被收貨規則誤判

severity: major
blocking: 是

引句:「每條可採信的發現恰一行 `severity:`」
白話:正常的審查員發現,只要摘要的措辭正好像欄位,整份報告就被擋或被誤計。
夾具 i:`1. \`src/a.py:3\`: severity: blocker is claimed`,補等級 `minor`。
實跑輸出:報告的標題行變成 `## 1. severity: blocker is claimed`,`report-normalize` 回還有 2 處機器轉不了,要人改(不然 canary record 會擋),指向第 5 行(標題)與第 10 行(摘要)。
夾具 j:摘要含夾具文字 `fake line here ok`(以引句標籤加括號包起來)與一對括號包起來的 quoted。`quote-check` 回 #1 與 #3 都找不到(未通過),結論是 3 句引言有 2 句在凍結快照裡找不到,rc 非零。
後果:一條真發現因為措辭而讓整份報告收不進去。同一個摘要寫兩次放大了影響。就算轉換只負責搬運,搬運也要保證報告仍可收貨。
建議:標題用固定的 `## 發現 n`,摘要與情境做行首跳脫(同第 6 條)。

## 8. 編號清單的續行與清單後的尾巴文字被靜默丟棄,違反原文照抄、不默默丟

severity: minor
blocking: 否

引句:「不默默丟掉一條、也不讓它的內容併進上一條」
file: `scripts/lumos:48567`(`elif cur is not None and cur["failure_scenario"] and ln.strip()` 只有在已進入失敗情境後才收續行)。
夾具 t6:
```
1. `src/a.py:3`: os.system takes cmd
   continued summary line
   Failure scenario: cmd is attacker
   controlled
2. `./src/a.py:4`: compute leaks

Overall the change is fine.
```
實跑輸出:第 1 條摘要只剩 `os.system takes cmd`,`continued summary line` 整行消失;第 2 條沒有失敗情境,所以 `Overall…` 也被丟。若第 2 條有失敗情境,`Overall…` 反而會被併進它的失敗情境。
影響:摘要折行是常見排版;被丟的行可能就是決定嚴重度的那句話。
建議:摘要續行併入摘要,並在遇到空行或總結段時停止收集。

## 9. 檔名含空白時,整份輸出被判 bad(rc2)

severity: minor
blocking: 否

引句:「編號清單裡有頂格的編號行認不得 → 整份 rc2」
file: `scripts/lumos:48537`(`_SEAT_IMPORT_LIST_HEAD` 的檔名部分是 `[^`*\s]+?`)。
夾具 e:`1. \`src/my file.py:3\`: spaced` 加一條正常的第 2 條。
實跑輸出:rc=2,訊息是 `擋下:認不得原生審查的輸出形狀`。
評估:方向是安全的(擋下而非誤收),spec 也說明認不得就 rc2。但是整份輸出因為一條就整份作廢,而且 rc2 的處置是改派同門通才,成本不小。屬於可記錄的已知限制,建議在計畫的〈實務隱患〉裡寫出來。

## 10. 全部錨不到時產生 `severity: clean` 的報告,而錨不到的 major 完全不進任何等級統計

severity: minor
blocking: 否

引句:「取有引句的發現裡最高的,一條都沒有就 clean」
夾具 g:`src/a.py:999`(超出檔案行數),等級 `major`。
實跑輸出:報告第一行 `severity: clean`、結尾 `可採信 0 條、錨不到 1 條`;`quote-check` rc=2(零引句,訊息是驗不了不等於通過)。
評估:這是 spec S3 明寫的行為,不是實作偏離。但行號超出、檔名寫錯、路徑帶 `./` 之類的情況也會落到這裡,審查員的真發現就被當成沒有。與第 4 條合起來:沒有發現有兩條路徑得到 clean,一條是形狀誤判,一條是全錨不到。
spec 的 RETIRE-IF 把錨不到超過三成當換席條件,但沒有任何機制保證錨不到那段被人看到。
建議:錨不到含 major 時,報告的總結行與檔級行不要用 clean,至少提示編排者人工檢視;或 rc 非零。

## 11. 沒有出問題的邊界(判不影響,附原因)

severity: minor
blocking: 否

引句:「那一行去掉首尾空白後至少 10 字」
- Windows 換行(夾具 d,檔案與輸出都是 CRLF):報告內沒有殘留 `\r`(`grep -c $'\r' d.rep.md` 為 0),`quote-check` 通過。引句與清單頭都有 `strip()` 與 `\s*$`,所以不受影響。
- 檔名帶 `./`(`./src/a.py`,夾具 t6):`Path` 運算可以正常讀到,清單解析接受。
- 檔名含冒號:`LIST_HEAD` 檔名部分用最短比對加 `:(\d+)`,不會被切錯。
- 同一行多條發現(夾具 h):兩條都採信,各自附引句,`quote-check` 通過。是否算重複證據是處置閘的事,不是轉換的問題。
- 行號 0 以下或超大:讀不到就列入錨不到,不會例外。
- 純空白行或少於 10 字的行:不採信,與 spec 相符。

---

整體:轉換指令在穩定輸入上行為與 spec 相符,但引句錨定缺檔案約束且能讀複本外的檔(第 1、2、3 條),沒有發現與多區塊或混合陣列的處理會把漏審洗成 clean 或靜默丟條(第 4、5 條),原文照抄沒有跳脫會污染報告格式(第 6、7 條),建議在實作前先補。
