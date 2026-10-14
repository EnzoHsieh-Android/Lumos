severity: major

彙總載體,非新增審查席。39 條由四份原報告逐字彙整(各份從第一條發現起),只在每條 severity 行前加 ID 行。


來源:r1-通才-sonnet.md(從第一條發現起)

**finding 1:官方明列的角度(被刪行為、跨檔追呼叫者)產出的發現,會被引句錨定規則系統性丟掉,最後可能整份變 clean**
ID: t1
severity: major
blocking: 是
引句:「去掉首尾空白後至少 10 字、跟凍結 patch 裡某一行」
判準:守衛靜默吞掉真發現,會讓高風險代碼審少一席實質覆蓋,而且帳上看不出來。
- spec 段落:引句、S3、PRIOR-ART。
- 問題:
  - PRIOR-ART 自己寫官方審法含被刪行為和跨檔追呼叫者。
  - 這兩類發現指向的檔案或行,多半不在凍結 patch 裡。被刪行為指向舊檔行,現檔已不存在。跨檔追呼叫者指向 diff 外的呼叫端檔案。
  - 引句要求該行去掉空白後與 patch 某行相同。這兩類在設計上就錨不到,會被列進錨不到段,不寫 severity 行。
  - S3 又規定全部錨不到時報告是 clean。
  - 官方標 CONFIRMED(自己實跑證實)的 blocker,也會因為指向 diff 外的呼叫端而變成一份 clean 報告。
- 佐證:file: `scripts/lumos:48580`(`_seat_import_quote` 只認 `q in patch_lines`)。file: `scripts/lumos:48633`(`top` 只取 kept,kept 為空就是 clean)。
- 建議:錨不到的 CONFIRMED 或 major 以上條目,不要讓報告降成 clean。至少要升級成需編排者人工處置的狀態,或交給辯方或 repro triage 路徑,不能無聲歸零。

**finding 2:官方說沒有發現的判斷是全文搜字,條列式發現加一句 no issues 就會被判 clean(fail-open)**
ID: t2
severity: major
blocking: 是
引句:「官方明說沒有發現(整段或整個 JSON 區塊是 `[]`,或寫明 no findings/沒有發現)」
判準:形狀認不得時 spec 承諾 rc2,實際卻走 clean,守衛方向反了。
- spec 段落:解析(寫明 no findings/沒有發現 則 clean)、S1、實務隱患。
- 問題:`_SEAT_IMPORT_NONE.search(text)` 搜整段文字任何位置。官方輸出若用 bullet 格式寫發現,再補一句其餘沒有問題或 no issues in tests,就既不匹配編號清單,也沒有頂格編號行。程式會判 `zero`,產出 clean。
- 佐證:
  - 我造的輸入是一行 bullet,內容為 race condition 加 `Everything else: no issues found.`,跑 `--list-only`,印出 `[]`,rc 0。
  - 對照 spec 的承諾:認不得就 rc2 擋下,不會產生殘缺的報告。這裡是靜默放行。
  - file: `scripts/lumos:48571`(最後一行 `return [], ("zero" if _SEAT_IMPORT_NONE.search(text) else "bad")`)。
- 另一個漏洞:JSON 陣列只要有一個元素缺 `line`(整體性的一般性發現沒有行號很常見),整個陣列就不被接受。接著掉到編號清單解析,最後 rc2 或 zero。官方整體角度的發現因此無處可去。
- 建議:沒有發現只在整段輸出夠短且只含該句時認定,或在有任何類似發現的語句時一律 rc2。

**finding 3:隔離與禁令名實不符,已排除:對外送出 站不住**
ID: t3
severity: major
blocking: 是
引句:「之後一律禁止 `git push`、`gh`、`git commit`」
判準:`bypassPermissions` 加三條前綴 deny,不足以支撐只讀、不對外的宣稱,且 spec 自己的實驗已出過事件。
- spec 段落:現況與實驗第三點、做法第一段、S5、實務隱患(已排除:對外送出/不可逆)。
- 問題:
  - `git clone --shared` 的 origin 是編排者本機 repo 的路徑,不是 GitHub。實驗出現的推送事件,spec 只查沒東西上 GitHub。真正該查的是原 repo 有沒有被推進新分支或 ref,而且沒有查。
  - deny 清單是 Bash 前綴比對:`git push:*`、`gh:*`、`git commit:*`。`git -C . push`、`git -c k=v push`、`env git push`、`git tag`、`git branch -D`、`git update-ref`、`git reset`、`curl`、`python -c`、`rm` 都不在清單內。
  - `bypassPermissions` 下不受限的有檔案寫入和網路,環境變數裡的 token 也一併繼承。
  - 這份會談讀的是被審 diff,是不可信文字,存在 prompt injection 可能。
  - 專案 `.claude/settings.json` 的 hook 和專案、全域 CLAUDE.md、自動記憶也會在複本裡載入。全新無頭會談不帶脈絡、跟派全新子代理一樣,這兩句不成立。
  - 專案 CLAUDE.md 要求回寫圖譜、跑 lumos 等,這會誘導該會談動手寫檔、提交。
- 建議:
  - 複本 `git remote remove origin`,並用 `--no-hardlinks` 或獨立 clone,不用 `--shared`。
  - 用 allowlist(`--allowedTools` 只放讀取類)取代 bypass 加 denylist。
  - 用 `--setting-sources` 或乾淨 `HOME` 隔離專案與全域設定。
  - 清掉環境變數 token,並在收貨時核對原 repo 的 `git for-each-ref` 沒有變動。

**finding 4:`/code-review` 的行為取決於使用者的歷史狀態,跑出來的東西不可重現**
ID: t4
severity: major
blocking: 是
引句:「ultrareview(要使用者觸發而且另外計費,編排者不能自己啟動)」
判準:帳上沒有任何東西能證明這一席用了什麼強度、什麼版本審的,且可能誤觸計費路徑。
- spec 段落:做法指令、範圍(不做 ultrareview)、RETIRE-IF。
- 問題:
  - 技能描述寫明未給等級時會沿用你上次打的等級(`reuses the level you typed last`),而且 `--max-findings` 的選擇會一直保留。指令是裸的 `/code-review`。
  - 若使用者上次手動打過 ultra,無頭會談可能沿用它。那是 spec 明說編排者不得自行啟動的、另外計費的雲端審查。
  - 沒有明示強度,每個迴圈跑的是不同強度。最多 10 條的上限在大 diff 上會截斷。轉換指令沒有偵測截斷,而且 10 條剛好時無法分辨是否被截。
  - 席報告只記指令字串,沒記 `claude --version` 或實際模型 ID。跟著官方更新代表同一個迴圈的前後輪審法可能不同。
  - RETIRE-IF 的 10 迴圈統計因此拿不到可比較的樣本。
- 建議:指令明示強度和 `--max-findings`。報告頭記 claude 版本與實際模型。恰好 10 條時標可能被截斷。

**finding 5:補等級那一步把全部審查結論的嚴重度交給較弱的模型,且只給它看原生審查的文字**
ID: t5
severity: major
blocking: 否
引句:「補等級的是另一個沒有編排者脈絡的模型,算審查員層宣告;編排者不改它」
判準:兩層宣告不互改的設計,讓單點誤判無處修正,也有 prompt injection 入口;這是已知取捨,但 spec 沒有緩解。
- spec 段落:補等級、實務隱患最後一點。
- 問題:
  - haiku 沒看程式碼,只看 summary 與 failure_scenario 的文字,就決定 major 或 minor。規則會做錯行為即 major 過寬,幾乎所有審查發現都符合,實際會偏向 major 而放大折入工作量。
  - 另一方向,haiku 判成 minor 的真問題可以被附理由放行。編排者不能改等級,但放行又是編排者決定的。
  - 輸入含源自被審 diff 的文字(failure_scenario 原文),`--json-schema` 只限形狀,擋不住要求把這條判 minor 之類的注入。
  - 官方判定欄 CONFIRMED 完全沒參與等級判斷。
- 建議:至少把 CONFIRMED 當等級下限(不得低於 major),並讓補等級者也看到對應程式行。

**finding 6:引句變成機械挑選的鄰近行,引句錨定在這一席失去審查員看過這句主張的意義;對不放寬任何判定的宣稱有落差**
ID: t6
severity: major
blocking: 否
引句:「處置閘、引句錨定、收貨三道全照舊;換掉的是一席找問題的人,不放寬任何判定」
判準:守衛形式上通過但保證弱化,spec 卻宣稱不放寬。
- spec 段落:引句、實務隱患(已排除:守衛面)。
- 問題:
  - 其他席的引句由審查員自己挑,證明它讀到那一句。這裡由轉換程式在 ±3 行內挑第一條 ≥10 字且存在於 patch 任何位置的行。
  - 條件很鬆:`return result_value` 之類的行幾乎在任何 patch 都有等值行。上下 3 行內沒有關聯的普通行就能充當引句。
  - 還有檢查錨點的不一致:引句是從 `--repo` 工作樹讀,不是從 tip 提交讀(`git show <tip>:file`)。bypass 權限的會談如果在複本裡為實跑驗證改了檔案,行號與內容會偏,轉換程式也不會發現。
  - 轉換程式沒有驗證複本 HEAD 等於凍結 patch 的 tip。
  - `Path(repo)/f["file"]` 對絕對路徑或 `..` 不設防。實測 `/etc/hosts:1` 被當成合法 file 解析。因為引句必須在 patch 裡,影響有限,但輸入沒有檢查。
- 另外:舊的 canary/repro triage 規則以引句錨不到當可疑席訊號。這一席錨不到的條目只寫進錨不到段,不會觸發任何東西。
- 佐證:file: `scripts/lumos:48580`、`scripts/lumos:48586`、`scripts/lumos:48637`。
- 建議:引句一律從 tip 提交讀(`git show`)。複本 HEAD 不等於 tip 時 rc2。檔案路徑限制在 repo 內。

**finding 7:席報告格式可被輸出內容注入,破壞每條恰一行 severity 的不變量**
ID: t7
severity: minor
blocking: 否
引句:「摘要與失敗情境原文照抄(不翻譯、不改寫)」
判準:格式漏洞但影響集中在報告可讀性;有 report-normalize 之類下游,不一定直接讓閘誤判。
- spec 段落:產出的席報告、S3。
- 問題:摘要與失敗情境原文照抄,完全不跳脫。官方輸出的 summary 或 failure_scenario 若含換行加 `severity: blocker` 或引句行,就會出現額外的 severity、blocking、引句行。
- 佐證:我造的 JSON 輸入,summary 帶換行後接 `severity: blocker`、`blocking: 是` 和一行引句(內容為 `return result_value`),轉出的報告同一條 finding 下有 3 個 `severity:`、2 個 `blocking:`、2 個引句。`report-normalize` 回報已是正規化格式,沒有擋。
- 建議:把原文逐行縮排或加前綴(例如 `> `),使它們不再是頂格行。

**finding 8:`@{upstream}...HEAD` 是三點差異,可能與凍結 patch 的範圍不一致**
ID: t8
severity: minor
blocking: 否
引句:「審的範圍是 `git diff @{upstream}...HEAD`,要先把被審分支的上游設成這輪的起點。」
判準:範圍錯位只影響這一席的審查範圍,有凍結判定另行把關,但 spec 沒保證一致。
- spec 段落:現況與實驗第三點、做法第一段。
- 問題:官方審的是 `merge-base(seat-base, HEAD)..HEAD`。若這輪起點不是 tip 的祖先(重定基底或合併過主線),它審的範圍與凍結 patch 不同。多出或缺少的檔會直接變成錨不到。這個行為是從五次實驗讀來的,不是官方文件承諾,官方更新後可能變成審未提交差異。
- 建議:轉換前驗證 `seat-base` 是 tip 的祖先,否則 rc2。

**finding 9:失效退路沒有量化,也沒說怎麼記帳**
ID: t9
severity: minor
blocking: 否
引句:「轉換指令認不得就 rc2 擋下,不會產生殘缺的報告;編排者這輪改派同門通才補位。」
判準:退路存在但成本與帳面處理未寫,屬流程完整性。
- spec 段落:回退、實務隱患第一條、RETIRE-IF。
- 問題:
  - 實驗五次裡有兩次沒照 append-system-prompt,形狀不固定。rc2 的發生率沒有估計。
  - 每次 rc2 要多花 1.5–2 分鐘加 0.2–0.4 美元才能知道失敗,然後改派同門通才。
  - 改派同門通才補位時,帳上席名是 `鏡頭5-…` 還是 `原生審查-sonnet`,spec 沒寫。
  - RETIRE-IF 把錨不到而被丟掉的發現超過三成當撤除條件,卻沒有說 rc2 整席失敗是否計入。
  - 到 11-30 才回看,中間 10 個迴圈都沒有任何機械訊號。
- 建議:寫明 rc2 後的席名、記帳方式,並把 rc2 次數也計入撤除條件。

**finding 10:家族判定在 Codex 當編排者時會變成外家**
ID: t10
severity: minor
blocking: 否
引句:「對帳時家族算同門,比較靠審查員名」
判準:spec 說家族算同門,程式的家族判定是相對於編排者,在 Codex 編排時這句話不成立。
- spec 段落:RETIRE-IF、編制。
- 問題:`_roster_family` 在 `orchestrator=codex` 時把名字含 sonnet 的當外家。`claude -p` 本身是否能在 Codex 編排下被呼叫,spec 也沒討論。
- 佐證:file: `scripts/lumos:13428`(`_roster_family`)。
- 建議:在 spec 寫明僅限 Claude 編排,或處理 Codex 編排時的席名與編制。

**固定席逐條判**:我在 repo 內只看得到 `Systems/pitfalls-code-loop` 一個節點的合約行,沒有另外附上的固定席清單,所以只判這一篇。
- 資安席 required-gated(d6):不影響。資安席與鏡頭5 在編制表分開,鏡頭5 只改備註,寬度維持 5。
- 三道防污染:不影響。它規範 canary 植入,而 canary 協議已於 2026-08-14 停用。
- 席報告留痕慣例加收貨 quote-check(2026-08-05):部分影響。引句由機械挑選,見 finding 6。
- missed 席 repro triage(觸發為引句錨不到):部分影響。這一席錨不到只寫進錨不到段,不觸發 repro,見 finding 1、6。
- panel 判準與 capture_counts:不影響。轉換後的報告走同一套帳。

最嚴重等級:major;blocking 共 4 條(finding 1、2、3、4)。

來源:r1-轉換邊界-sonnet.md(從第一條發現起)

## 1. 引句錨定只比對整份 patch 的行集合,不看檔案,任何檔的發現都能錨到別檔的行

ID: e1
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

ID: e2
severity: major
blocking: 是

引句:「去掉開頭的 `+`/`-`/空白與首尾空白」
白話:被刪掉的那一行,拿來錨定現在檔案裡的某一行,等於沒有證明這行是這次新增的。
夾具 a(同上):`patchdel.diff` 裡該行只出現在 `-` 行(被刪除),新檔裡 `src/a.py:2` 的內容卻與它相同,仍被採信。
spec 明寫要去掉 `+`/`-`/空白,等於讓 `-` 行與純空白差異(縮排改動)都算命中。
關聯:`ln[:1] in "+- "` 在 `scripts/lumos:48630` 一帶。此外 `startswith(("+++","---"))` 會把內容以 `-- ` 開頭的被刪行(例如 SQL 或 Lua 註解)誤排除,屬同一組邊角。

## 3. 檔名可以是絕對路徑或 `../`,轉換指令會讀複本以外的檔案

ID: e3
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

ID: e4
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

ID: e5
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

ID: e6
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

ID: e7
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

ID: e8
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

ID: e9
severity: minor
blocking: 否

引句:「編號清單裡有頂格的編號行認不得 → 整份 rc2」
file: `scripts/lumos:48537`(`_SEAT_IMPORT_LIST_HEAD` 的檔名部分是 `[^`*\s]+?`)。
夾具 e:`1. \`src/my file.py:3\`: spaced` 加一條正常的第 2 條。
實跑輸出:rc=2,訊息是 `擋下:認不得原生審查的輸出形狀`。
評估:方向是安全的(擋下而非誤收),spec 也說明認不得就 rc2。但是整份輸出因為一條就整份作廢,而且 rc2 的處置是改派同門通才,成本不小。屬於可記錄的已知限制,建議在計畫的〈實務隱患〉裡寫出來。

## 10. 全部錨不到時產生 `severity: clean` 的報告,而錨不到的 major 完全不進任何等級統計

ID: e10
severity: minor
blocking: 否

引句:「取有引句的發現裡最高的,一條都沒有就 clean」
夾具 g:`src/a.py:999`(超出檔案行數),等級 `major`。
實跑輸出:報告第一行 `severity: clean`、結尾 `可採信 0 條、錨不到 1 條`;`quote-check` rc=2(零引句,訊息是驗不了不等於通過)。
評估:這是 spec S3 明寫的行為,不是實作偏離。但行號超出、檔名寫錯、路徑帶 `./` 之類的情況也會落到這裡,審查員的真發現就被當成沒有。與第 4 條合起來:沒有發現有兩條路徑得到 clean,一條是形狀誤判,一條是全錨不到。
spec 的 RETIRE-IF 把錨不到超過三成當換席條件,但沒有任何機制保證錨不到那段被人看到。
建議:錨不到含 major 時,報告的總結行與檔級行不要用 clean,至少提示編排者人工檢視;或 rc 非零。

## 11. 沒有出問題的邊界(判不影響,附原因)

ID: e11
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

來源:r1-流程整合-sonnet.md(從第一條發現起)

## F1 無頭 bypassPermissions 席的隔離比「跟派全新子代理一樣」弱得多
ID: f1
severity: major
blocking: 是

引句:「全新的無頭會談不帶編排者的脈絡,席位獨立性跟派全新子代理一樣。」

file: `skills/lumos-design-loop/templates.md:453`:指令只用 `--disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(git commit:*)"` 擋三個前綴,其餘全放行。

- **擋法繞得過**:這類前綴擋法只比對指令開頭。`git -C . push`、`env gh ...`、`/opt/homebrew/bin/gh`、先 `cd` 再 push 都不會被攔。`curl`、WebFetch 也沒擋。
- **複本指回本機真 repo**:我實測 `git clone --shared` 之後,複本的 `origin` 就是本機真 repo 的路徑。繞過前綴擋法的 push 會直接在真 repo 建分支。
- **沒有 lumos-guard 的保護**:`Systems/lumos-guard.md` 說它只認派工詞第一行有 `LUMOS-SEAT` 的子代理,擋掉含 `gh`、`git push`、`claude` 字樣的 Bash、限定寫檔目錄。無頭會談不是子代理,這些保護都不在。
- **複本含被審的 commit**:複本切到被審的頂端提交,裡面若有 `.claude/settings.json` 的 hooks 或 CLAUDE.md,無頭模式很可能不問信任就載入並執行(此點未實測)。被審的是「外部投稿」,這等於讓被審材料在無沙盒、全放行的會談裡跑程式。
- **自我宣稱不成立**:spec 的〈實務隱患〉寫「守衛面:處置閘、引句錨定、收貨三道全照舊;換掉的是一席找問題的人,不放寬任何判定」。但這一席的隔離確實放寬了。
- **建議**:改成白名單(只開 Read/Grep/Glob 與唯讀 git);移除複本的 `origin`;用 `--setting-sources` 之類的旗標排除複本裡的專案設定;並實測一次含惡意 hooks 的複本。

## F2 轉出來的席報告原文照抄,會讓 `canary record` 擋下或數錯條數
ID: f2
severity: major
blocking: 是

引句:「摘要與失敗情境原文照抄(不翻譯、不改寫)」

file: `scripts/lumos:48640`:標題直接拿摘要第一行,失敗情境整段多行貼進報告。三種結果我都實跑到了:

- **標題含等級字樣被擋**:摘要寫「Cache: major regression when x has backticks」(c1),標題變成 `## 1. Cache: major regression...`。`lumos report-normalize` 回 rc1,指出第 5 行是殘留的嚴重度寫法。`_SEV_HEADING_LEVEL_RE` 會把標題裡的「: major」、「non-major」、「— minor」都當殘留。`canary record` 的 `_report_normalize_issues` 因此 rc2,席報告就記不了帳。
  - 編排者又不准改報告,只剩改派一途。
  - 英文摘要裡出現 major/minor/blocker 這幾個字並不罕見。
  - 這條路徑在 spec 與計劃的 S1–S3 都沒測到。
- **圍欄吃掉後面的 severity 行**(c2):失敗情境裡有落單的 ``` 時,`_report_severities` 看不到後面條目的 `severity:` 行。reported 變成 1(實際 2 條),而 `quote-check` 兩條都看得到。`--findings` 填 2 會被「不能多於報告條數」擋下。
- **失敗情境夾帶 severity 行會被計入**(c3):失敗情境多一行 `severity: blocker`,`report-normalize` 判為合格,reported 變成 2(實際 1 條),帳面下限被抬到 blocker,而檔首宣告是 major。
  - 失敗情境是模型讀了被審的 diff 後寫的,屬於投稿方可影響的文字。
  - 失敗情境若多帶一行以「引句」為標籤的內容,也會多出一筆 quote-check 的引句。
- **建議**:轉換時把失敗情境放進縮排的引用區塊,或改寫行首的 `severity:`、`引句:`、圍欄標記。標題改用編號加檔案行號,不用摘要。同時為這三種輸入各補一支先紅的測試。

## F3 headless 席不是子代理,`seat-check` 與 dispatch 單怎麼寫沒交代
ID: f3
severity: major
blocking: 是

引句:「對帳時家族算同門,比較靠審查員名」

file: `skills/lumos-design-loop/templates.md:473` 與 `scripts/lumos:13459`(`_roster_dispatch_entries`):

- **派工單漏列的後果**:席位對帳只讀 `rN-dispatch*.json` 的 `auditor` 欄,按家族數人頭。§7.9 沒寫要把這一席加進 dispatch 單,漏列就會印 `seat_shortfall`。
- **seat-check 一律吵**:`seat-check` 的 `unreported` 看的是報告有沒有提到 dispatch 列的 materials 路徑或檔名。我拿含 `patch.diff` 與 `a.py` 的 dispatch 單跑,轉出來的報告都回 `unreported 1`。這一席從沒收到過 materials,每輪必然吵一次。
- **Codex 編排的迴圈會誤判**:`_roster_family("原生審查-sonnet","codex")` 回 `('external', False)`。Codex 編排時它被算成外家,鏡頭5 的同門缺額會印 `seat_shortfall`,同時像多派了一席外家。
- **spec 的說法站不住**:上面那句只在 claude 編排時成立。
- **建議**:§7.9 補寫這一席的 dispatch 條目(`materials` 留空走 vacuous 豁免,或指定為凍結 patch),並聲明 Codex 編排時此席的家族算法。

## F4 轉換直接寫進卷證目錄,違反「席報告收齊前不落地」
ID: f4
severity: major
blocking: 是

引句:「再用一支轉換指令把它的結果變成 Lumos 收得下的席報告」

file: `skills/lumos-design-loop/templates.md:455`:第 3 段指令的 `--out` 是 `governance/review-reports/{loop}/{rN}-原生審查-sonnet.md`,`.unparsed.txt` 也落在旁邊。

- **規則內容**:`skills/lumos-code-loop/SKILL.md` 第 3 步、templates §0 要求所有席收齊前,先到的報告留在對話裡、不寫進硬碟,免得後到的席讀到先到那席的報告。
- **衝突**:這一席要跑約 2 分鐘再轉換,必然比其他席早或晚寫進 repo。同輪其他席還在跑時,報告已躺在 repo 內。
- **建議**:`--out` 改寫到 `$W`,收齊後再一次搬進卷證;`.unparsed.txt` 也一樣。

## F5 錨不到的發現不進帳,RETIRE-IF 的量測無從算起
ID: f5
severity: major
blocking: 是

引句:「它錨不到引句而被丟掉的發現超過三成」

file: `scripts/lumos:48645` 與 `scripts/lumos:10250`(`_report_reported_count`):

- **現象**:c4 的案例中,唯一一條發現引了 repo 外的路徑 `/etc/hosts:1`,被丟進「錨不到」段,席報告變成 `severity: clean`、`reported=0`。
- **後果**:帳上跟一席真的沒發現完全分不出來。
- **其他席的對照**:其他席錨不到的條目仍留著 severity 行,處置閘看得到,這一席卻悄悄蒸發。
- **量測落空**:RETIRE-IF 要量「錨不到而被丟掉的比例」,`gov --stats` 與 `canary record` 都沒有這個數字。
- **建議**:在報告末尾的錨不到段與總結句外,另在 `canary record` 的 note 或 intake 留一個機器可讀的條數;或對「全部錨不到」的報告給出明確警告,而不是安靜地變 clean。

## F6 無頭呼叫在對話裡跑會被 2 分鐘上限砍掉
ID: f6
severity: minor
blocking: 否

file: `skills/lumos-design-loop/templates.md:453`:指令是前景執行。spec 自己量到每次約 1.5–2 分鐘。專案 CLAUDE.md 與 `skills/lumos-code-loop/SKILL.md` 第 5 步(fix-check 條)都記載對話裡指令預設 2 分鐘上限,fix-check 因此要求在背景跑。§7.9 應照同樣寫法加 `run_in_background`。

## F7 引句只比對「patch 裡任一行」,沒綁定到該發現所在的檔案
ID: f7
severity: minor
blocking: 否

引句:「跟凍結 patch 裡某一行(去掉開頭的 `+`/`-`/空白與首尾空白)完全相同」

file: `scripts/lumos:48571`(`_seat_import_quote`):

- 比對用的是整份 patch 的行集合,不分檔案。複本的檔案若有一行恰好等於 patch 裡別檔的某行(例如 `return None`、`import os, sys`),就當引句通過。
- 被刪行為的發現,複本 HEAD 版沒有那一行,上下 3 行內就可能挑到無關的行當引句。
- `f["file"]` 沒限制在複本根底下,`Path(repo)/"/etc/hosts"` 這種絕對路徑或 `../` 都能讀到 repo 外的檔。
- 比對方式與 spec 寫的一致,但「引句全錨」的意義被稀釋。
- **建議**:引句限定來自 patch 裡同一個檔案,路徑用 `resolve()` 後必須落在 `--repo` 底下。

## F8 `@{upstream}...HEAD` 的三點 diff 可能與凍結 patch 的範圍不一致
ID: f8
severity: minor
blocking: 否

引句:「審的範圍是 `git diff @{upstream}...HEAD`,要先把被審分支的上游設成這輪的起點。」

三點 diff 取的是 merge-base 到頂端。若這一輪的起點不是頂端的祖先(例如分支中途合過主線),`/code-review` 審到的範圍會比凍結 patch 大。多出來的部分在轉換時被判錨不到,安靜丟棄(接 F5),而不是被標示為超出範圍。§7.9 應要求 `seat-base` 必須是頂端的祖先,不是就停下回報。

## F9 補等級那一步與暫存清理的缺口
ID: f9
severity: minor
blocking: 否

file: `skills/lumos-design-loop/templates.md:455-464`:

- **haiku 呼叫在哪跑沒寫**:若在 repo 工作目錄跑,會載入專案的 CLAUDE.md 與 hooks,並吃進被審 diff 的文字(`--json-schema` 的 enum 能限制輸出,但輸入面沒隔離)。
- **severity.json 沒存證**:`severity.json` 與 `raw.json` 在收貨後隨 `$W` 一起被刪,補等級是「審查員層宣告」,卻不在卷證裡,日後不能重現或稽核。
- **筆數不符無去向**:`severity.json` 條數不符時 rc2,但 §7.9 只寫「形狀認不得就改派同門通才」,沒寫筆數不符怎麼辦。
- **無頭呼叫的會談紀錄不歸清理規則管**:每次 `claude -p` 在 `~/.claude/projects/` 留下以暫存路徑命名的會談紀錄,內含完整 diff。全域暫存清理規則只管 `/tmp/lumos-seat-work`,這批殘留不在其中。

## F10 回退路徑對歷史帳安全,但會留下懸空的測試綁定
ID: f10
severity: minor
blocking: 否

引句:「編制改回同門通才:把 `_TIER_ROSTER` 鏡頭5 的備註還原,手冊那一節刪掉;轉換指令留著不影響其他流程。」

我查了 `_roster_family` 與 `_disposal_security_step`/`_auditor_matches_slot`。歷史帳裡的 `原生審查-sonnet` 只靠名字含 `sonnet` 判成同門,不依賴備註,不是資安席。所以舊迴圈回放不會出錯。但回退後 S4 的 `t_seat_import_roster_slot` 會對不上備註,計劃裡的 `[test:]` 綁定要一併撤掉,spec 沒寫。

blocking 的有 F1、F2、F3、F4、F5 五條,其餘 F6 到 F10 都是 minor;最高等級 major。

來源:r1-架構對齊-sonnet.md(從第一條發現起)

1. 引句由轉換器代產,是第二種引句錨定做法
ID: a1
severity: major
blocking: 是
引句:「照每條的檔案與行號,在複本裡讀那一行;那一行去掉首尾空白後至少 10 字」
- 既有做法是審查席自己逐字寫引句,quote-check 再回頭對凍結 patch,錨不到就不採信,見 file: `scripts/lumos:27364` 與 file: `skills/lumos-code-loop/SKILL.md:43`。
- 新設計是轉換器自己讀複本那一行,在上下 3 行內挑第一個符合的當引句。
  - 引句改成轉換器從 patch 挑出來的,對 patch 的比對天然會過。
  - 過了 quote-check,也不能說明原審查員真的看過這一行。
- 計劃的 PRIOR-ART 說「引句錨定…沿用既有規則,不另立」,但這裡自帶了一套「±3 行、至少 10 字、不含括號」的錨定規則。
- 這等於在既有「席宣告引句、機器驗」之外,另立「機器代產引句」。

2. 等級由第三個模型依一套新規則補,是第二種等級規則
ID: a2
severity: major
blocking: 是
引句:「會做錯行為、破壞合約、資料損壞或可被利用的是 major,會造成無法還原的損害的是 blocker,命名、風格、效率、文件精度是 minor」
- 既有做法是審查員自己標 severity。
  - 審查員標 blocker 或 major 時要附翻紅重現,附不出就自降一級,見 file: `skills/lumos-design-loop/templates.md:189`。
  - 等級規則寫在 file: `skills/lumos-design-loop/templates.md:56` 一帶和 §7.8 的 `templates.md:438`,各自單源。
- 新設計讓另一個沒有編排者脈絡的 haiku 呼叫,按計劃內自寫的三行規則補等級。
  - 規則在計劃、手冊、轉換器來源三處各抄一份,沒有指回 §3 單源。
  - 原生審查給的失敗情境也不經「附重現否則自降」那條。
  - 計劃把這個等級當「審查員層宣告」,與 file: `skills/lumos-design-loop/templates.md:307` 的兩層不互改綁在一起,但來源的信任模型已經變了。

3. 派席方式脫離既有隔離機制
ID: a3
severity: major
blocking: 是
引句:「--permission-mode bypassPermissions --disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(git commit:*)"」
- 既有審查席是子代理,帶 `LUMOS-SEAT` 標記,受 lumos-guard 唯讀隔離,見 file: `skills/lumos-design-loop/templates.md:20`。
  - 派工另有 `rN-dispatch.json`,供 seat-check 對帳,見 file: `skills/lumos-code-loop/SKILL.md:43`。
- 新席是用 `bypassPermissions` 開高權限,只靠黑名單擋三個指令。
  - 計劃自己記錄過一次實驗中出現「推送」狀態事件(第 31 行)。
  - 黑名單擋不到 `git remote`、`curl` 這類其他外送途徑。
- 這與「審查席不能做對外動作」的既有策略是兩種方式。
- 它也沒有 dispatch manifest,「收貨三道全照舊」中的 seat-check 沒有輸入。這一點建議釐清。

4. 旗標名 `--list-only` 與既有輸出旗標慣例不同
ID: a4
severity: minor
blocking: 否
引句:「只解析、印出清單(JSON),再把清單交給另一次無頭呼叫」
- 既有 vault-free 小工具要機器可讀輸出時一律用 `--json`,例如 file: `scripts/lumos:54796` 一帶的 quote-check、seat-check。
- 新設計用 `--list-only` 同時表示「只解析」和「輸出 JSON」,把模式與格式綁在一起。
- 結構是對的,只是命名不齊。

5. 席名與編制格子脫鉤,家族辨識靠席名
ID: a5
severity: minor
blocking: 否
引句:「對帳時家族算同門,比較靠審查員名」
- 編制格子是「鏡頭5」,席名卻是 `原生審查-sonnet`。
- 既有慣例是席名 `<鏡頭>-<模型>`,見 file: `scripts/lumos:13552`。
  - 資安席有專屬別名比對,見 file: `scripts/lumos:26631`。
- 鏡頭5 這格沒有類似的別名比對。
  - 席位對帳是否會把這席當成鏡頭5,計劃沒寫。
  - RETIRE-IF 還要靠席名辨識家族。
- 判不準,⚠。

6. 認不得時另存 `.unparsed.txt`,在席報告路徑旁新增副檔
ID: a6
severity: minor
blocking: 否
引句:「其他抽不出 → rc2,原文另存成」
- rc2 的語意與既有一致。
- 但既有的 rc2 路徑都不寫副檔,例如 file: `scripts/lumos:10221` 的 report-normalize。
- 新增的副檔放在卷證目錄旁,卷證目錄有「不准放腳本」之類的測試守衛,見 file: `skills/lumos-code-loop/SKILL.md:40`。
  - 計劃沒說副檔會不會被這些守衛或收貨流程誤認為席報告。
  - 計劃也沒寫寫入失敗時怎麼辦。
- ⚠。

7. 三段長指令寫在手冊散文裡,沒有固定成腳本
ID: a7
severity: minor
blocking: 否
引句:「新增一節〈原生審查席〉寫上面三段指令;收貨、記帳照既有規則。」
- 外家席的先例是把手打的 curl 固定成 `scripts/external-seat.sh`,理由是呼叫方式不再漂,見 file: `scripts/external-seat.sh:1`。
- 新席有三段含 `rm -rf`、clone、分支設定的指令,只靠編排者照抄,漂移風險正是那個腳本要解的問題。
- 章節寫法本身(§7.8、§7.9 的「為什麼有這一席」加指令區塊)與 file: `skills/lumos-design-loop/templates.md:406` 一致。

8. lands_in 漏了管編制與手冊的家
ID: a8
severity: minor
blocking: 否
引句:「  - Systems/pitfalls-code-loop」
- 被改的檔至少有 `_TIER_ROSTER`(在 `scripts/lumos`)、`templates.md`、`SKILL.md` 和新的轉換指令。
- 圖譜裡 `_TIER_ROSTER` 與 `skills/lumos-design-loop/templates.md` 的家是 Systems/design-loop,report-normalize、quote-check 也在那裡。
- 只列 pitfalls-code-loop 與資安席計劃的先例相同,所以不算違反慣例。
  - 但轉換指令、編制表、templates 新節的說明該寫進 design-loop,計劃沒列。
  - 依 CLAUDE.md 鐵則 5,改到哪支檔就要寫進它的家。

不對齊共 8 條,其中 major 3 條
