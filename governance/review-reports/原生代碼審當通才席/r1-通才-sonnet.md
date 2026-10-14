severity: major

以下是同一份報告全文,內容與等級不變。每條 finding 補了一行頂格的 `引句:「…」`,都是從 `/tmp/原生代碼審當通才席-r1.md` 逐字複製的單行原文。除了這些引句行,其他地方不再出現「」。

**finding 1:官方明列的角度(被刪行為、跨檔追呼叫者)產出的發現,會被引句錨定規則系統性丟掉,最後可能整份變 clean**
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
severity: minor
blocking: 否
引句:「摘要與失敗情境原文照抄(不翻譯、不改寫)」
判準:格式漏洞但影響集中在報告可讀性;有 report-normalize 之類下游,不一定直接讓閘誤判。
- spec 段落:產出的席報告、S3。
- 問題:摘要與失敗情境原文照抄,完全不跳脫。官方輸出的 summary 或 failure_scenario 若含換行加 `severity: blocker` 或引句行,就會出現額外的 severity、blocking、引句行。
- 佐證:我造的 JSON 輸入,summary 帶換行後接 `severity: blocker`、`blocking: 是` 和一行引句(內容為 `return result_value`),轉出的報告同一條 finding 下有 3 個 `severity:`、2 個 `blocking:`、2 個引句。`report-normalize` 回報已是正規化格式,沒有擋。
- 建議:把原文逐行縮排或加前綴(例如 `> `),使它們不再是頂格行。

**finding 8:`@{upstream}...HEAD` 是三點差異,可能與凍結 patch 的範圍不一致**
severity: minor
blocking: 否
引句:「審的範圍是 `git diff @{upstream}...HEAD`,要先把被審分支的上游設成這輪的起點。」
判準:範圍錯位只影響這一席的審查範圍,有凍結判定另行把關,但 spec 沒保證一致。
- spec 段落:現況與實驗第三點、做法第一段。
- 問題:官方審的是 `merge-base(seat-base, HEAD)..HEAD`。若這輪起點不是 tip 的祖先(重定基底或合併過主線),它審的範圍與凍結 patch 不同。多出或缺少的檔會直接變成錨不到。這個行為是從五次實驗讀來的,不是官方文件承諾,官方更新後可能變成審未提交差異。
- 建議:轉換前驗證 `seat-base` 是 tip 的祖先,否則 rc2。

**finding 9:失效退路沒有量化,也沒說怎麼記帳**
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
